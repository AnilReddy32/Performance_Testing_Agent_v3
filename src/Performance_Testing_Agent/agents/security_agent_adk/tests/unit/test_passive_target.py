"""Scope rules: what the passive assessment may and may not be pointed at."""

import pytest

from security_agent.passive.target import (
    TargetRejected,
    looks_like_external_https_target,
    resolve_target,
)

PUBLIC = ["93.184.216.34"]


def profile(**overrides):
    base = {
        "target_url": "https://api.example.com",
        "endpoint": "/posts/1",
        "method": "GET",
        "environment": "external_api",
    }
    base.update(overrides)
    return {k: v for k, v in base.items() if v is not None}


def resolve(prof, addresses=PUBLIC):
    return resolve_target(prof, resolver=lambda host, port: list(addresses))


def rejected_code(prof, addresses=PUBLIC):
    with pytest.raises(TargetRejected) as caught:
        resolve(prof, addresses)
    return caught.value.code


def test_a_public_https_target_is_accepted_and_pinned_to_its_addresses():
    target = resolve(profile(endpoint="/comments?postId=1"))

    assert target.host == "api.example.com"
    assert target.origin == "https://api.example.com"
    assert target.request_target == "/comments?postId=1"
    assert target.path == "/comments"
    assert target.addresses == tuple(PUBLIC)
    assert target.environment == "external_api" and target.environment_inferred is False


def test_a_missing_environment_is_inferred_not_a_reason_to_block():
    target = resolve(profile(environment=None))

    assert target.environment == "external_api"
    assert target.environment_inferred is True


def test_a_declared_environment_is_kept():
    assert resolve(profile(environment="staging")).environment == "staging"


def test_it_does_not_depend_on_the_load_test_host_allowlist(monkeypatch):
    monkeypatch.setenv("REAL_EXECUTION_ALLOWED_HOSTS", "localhost,127.0.0.1")
    monkeypatch.setenv("SECURITY_LIVE_ALLOWED_HOSTS", "somewhere-else.example.org")

    assert resolve(profile()).host == "api.example.com"


@pytest.mark.parametrize(
    "overrides,code",
    [
        ({"target_url": "http://api.example.com"}, "not_https"),
        ({"target_url": "https://user:pw@api.example.com"}, "credentials_in_url"),
        ({"target_url": "https://93.184.216.34"}, "ip_literal"),
        ({"target_url": "https://[2606:2800:220:1::1]"}, "ip_literal"),
        ({"target_url": "https://api.example.com:8443"}, "non_standard_port"),
        ({"target_url": "https://localhost"}, "non_public_host"),
        ({"target_url": "https://payments.internal"}, "non_public_host"),
        ({"target_url": "https://printer.local"}, "non_public_host"),
        ({"target_url": "https://intranet"}, "non_public_host"),
        ({"target_url": "https://api.example.com/v1"}, "invalid_target"),
        ({"target_url": "https://api.example.com?x=1"}, "invalid_target"),
        ({"target_url": None}, "no_target"),
        ({"endpoint": None}, "no_target"),
        ({"endpoint": "posts/1"}, "invalid_endpoint"),
        ({"endpoint": "https://evil.example.net/x"}, "invalid_endpoint"),
        ({"endpoint": "//evil.example.net/x"}, "invalid_endpoint"),
        ({"endpoint": "/a/../../etc/passwd"}, "invalid_endpoint"),
        ({"endpoint": "/a%2fb"}, "invalid_endpoint"),
        ({"endpoint": "/a#frag"}, "invalid_endpoint"),
        ({"endpoint": "/" + "a" * 2000}, "invalid_endpoint"),
    ],
)
def test_targets_outside_the_scope_are_rejected_before_any_request(overrides, code):
    assert rejected_code(profile(**overrides)) == code


def test_no_trusted_profile_is_rejected():
    for missing in (None, "text", 5):
        with pytest.raises(TargetRejected) as caught:
            resolve_target(missing, resolver=lambda h, p: PUBLIC)
        assert caught.value.code == "no_target"


@pytest.mark.parametrize(
    "addresses",
    [
        ["10.0.0.5"],
        ["192.168.1.10"],
        ["172.16.0.9"],
        ["127.0.0.1"],
        ["169.254.169.254"],          # cloud metadata endpoint
        ["100.64.0.1"],               # carrier-grade NAT
        ["::1"],
        ["fd00::1"],
        ["fe80::1"],
        ["::ffff:10.0.0.1"],          # private IPv4 hidden in an IPv6 form
        ["93.184.216.34", "10.0.0.5"],  # one public, one private: still refused
    ],
)
def test_a_name_that_resolves_to_a_non_public_address_is_refused(addresses):
    assert rejected_code(profile(), addresses) == "non_public_address"


def test_dns_failures_are_reported_not_raised():
    def failing(host, port):
        raise OSError("name not known")

    with pytest.raises(TargetRejected) as caught:
        resolve_target(profile(), resolver=failing)
    assert caught.value.code == "dns_failure"
    assert rejected_code(profile(), []) == "dns_failure"


def test_global_ipv6_addresses_are_allowed():
    target = resolve(profile(), ["2606:2800:220:1:248:1893:25c8:1946"])

    assert target.addresses == ("2606:2800:220:1:248:1893:25c8:1946",)


def test_at_most_four_addresses_are_kept():
    target = resolve(profile(), [f"93.184.216.{n}" for n in range(1, 9)])

    assert len(target.addresses) == 4


@pytest.mark.parametrize(
    "method,expected",
    [("get", "GET"), ("PUT", "PUT"), ("Patch", "PATCH"), (None, "GET"), ("FETCH", "GET"), (5, "GET")],
)
def test_the_declared_method_is_normalised(method, expected):
    assert resolve(profile(method=method)).method == expected


@pytest.mark.parametrize(
    "prof,expected",
    [
        (profile(), True),
        (profile(environment=None), True),
        (profile(environment="mock_api", target_url="http://localhost:8000"), False),
        (profile(environment="mock_api"), False),
        (profile(environment="development"), False),
        (profile(target_url="http://api.example.com"), False),
        (profile(target_url="https://93.184.216.34"), False),
        (profile(target_url="https://localhost"), False),
        (profile(target_url="https://api.example.com:8443"), False),
        (profile(target_url=None), False),
        ({}, False),
        (None, False),
    ],
)
def test_the_cheap_external_target_test_matches_the_scope_rules(prof, expected):
    assert looks_like_external_https_target(prof) is expected


# ------------------------------------------------ regressions from the review --

@pytest.mark.parametrize("url", [
    "https://api.example.com%00.evil.com",
    "https://api example.com",
    "https://a..b.com",
    "https://-bad.example.com",
    "https://bad-.example.com",
    "https://api.example.com%2f.evil.com",
])
def test_a_host_that_is_not_a_valid_dns_name_never_reaches_a_header_or_resolver(url):
    reached = []

    def resolver(host, port):
        reached.append(host)
        return PUBLIC

    with pytest.raises(TargetRejected) as caught:
        resolve_target(profile(target_url=url), resolver=resolver)

    assert caught.value.code in {"invalid_target", "non_public_host"}
    assert reached == []


def test_international_host_names_are_sent_as_punycode_and_case_is_normalised():
    target = resolve(profile(target_url="https://München.Example.DE"))

    assert target.host == "xn--mnchen-3ya.example.de"
    assert resolve(profile(target_url="https://API.Example.COM")).host == "api.example.com"


def test_underscores_in_host_names_are_allowed_because_they_exist_in_practice():
    assert resolve(profile(target_url="https://api_v2.example.com")).host == "api_v2.example.com"


@pytest.mark.parametrize("address", [
    "64:ff9b::a9fe:a9fe",        # NAT64 form of 169.254.169.254
    "64:ff9b::7f00:1",           # NAT64 form of 127.0.0.1
    "::a9fe:a9fe",               # IPv4-compatible form of the metadata address
    "::10.0.0.1",
    "::ffff:0:127.0.0.1",        # IPv4-translated form of loopback
    "2002:a9fe:a9fe::1",         # 6to4 form of the metadata address
    "2002:0a00:0001::1",         # 6to4 form of 10.0.0.1
    "fec0::1",                   # deprecated site-local
    "168.63.129.16",             # Azure platform endpoint
    "::", "::1",
])
def test_encodings_of_internal_addresses_are_refused(address):
    assert rejected_code(profile(), [address]) == "non_public_address"


@pytest.mark.parametrize("address", [
    "93.184.216.34",
    "2606:2800:220:1:248:1893:25c8:1946",
    "64:ff9b::5db8:d822",        # NAT64 form of the public 93.184.216.34
    "2002:5db8:d822::1",         # 6to4 form of the public 93.184.216.34
])
def test_public_addresses_stay_allowed_in_every_encoding(address):
    assert resolve(profile(), [address]).addresses == (address,)


def test_a_non_ascii_endpoint_is_percent_encoded_for_the_request_line():
    target = resolve(profile(endpoint="/café/naïve?q=über&x=a b"))

    assert target.path == "/caf%C3%A9/na%C3%AFve"
    assert target.request_target == "/caf%C3%A9/na%C3%AFve?q=%C3%BCber&x=a%20b"
    assert target.request_target.isascii()


def test_existing_percent_escapes_are_not_double_encoded():
    assert resolve(profile(endpoint="/a%20b?x=%41")).request_target == "/a%20b?x=%41"


def test_crlf_in_an_endpoint_cannot_inject_a_header():
    target = resolve(profile(endpoint="/x\r\nHost: evil.example.net"))

    assert "\r" not in target.request_target and "\n" not in target.request_target
    assert target.request_target.isascii()


@pytest.mark.parametrize("target_url", [
    "https://user:pw@api.example.com",
    "https://api.example.com/v1",
    "https://api.example.com?x=1",
    "https://api.example.com%00.evil.com",
])
def test_the_cheap_pre_check_mirrors_the_url_rules(target_url):
    assert looks_like_external_https_target(profile(target_url=target_url)) is False
