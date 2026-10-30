"""Pure verdict logic for the passive checks.

Nothing here touches the network. Each check turns what was observed into
exactly one verdict:

  passed        the observation shows the control is in place
  failed        the observation shows a weakness
  inconclusive  the observation cannot support either claim

A response that does not exercise the application normally (HTTP 401, 403, 404,
405, 429 or 5xx on the resource itself) never counts as a pass, and a missing
header on such a response is never counted as a failure.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone

from security_agent.passive.config import FOREIGN_ORIGIN
from security_agent.passive.models import (
    BLOCKING_SEVERITIES,
    FAILED,
    INCONCLUSIVE,
    PASSED,
    SEVERITY_WEIGHT,
    WARNING_SEVERITIES,
    CheckResult,
    HttpObservation,
    Observations,
    TlsObservation,
)

_HSTS_MIN_SECONDS = 15_552_000  # 180 days
_CERT_EXPIRY_WARNING_DAYS = 14
_WEAK_CIPHER = re.compile(
    r"(?<![A-Z0-9])(?:RC4|3DES|DES|NULL|EXPORT|ANON|MD5|RC2)(?![A-Z0-9])", re.I
)
_RATE_LIMIT_HEADERS = (
    "ratelimit", "ratelimit-limit", "ratelimit-remaining", "ratelimit-policy",
    "x-ratelimit-limit", "x-ratelimit-remaining", "x-rate-limit-limit",
    "x-rate-limit-remaining",
)
_DANGEROUS_METHODS = {
    "TRACE", "TRACK", "CONNECT", "PROPFIND", "PROPPATCH", "MKCOL", "COPY",
    "MOVE", "LOCK", "UNLOCK",
}
_ERROR_STATUSES_WITH_APP_PAGE = {400, 404, 410, 422, 500}
_LEAK_SIGNATURES: tuple[tuple[str, re.Pattern], ...] = (
    ("stack trace", re.compile(
        r"Traceback \(most recent call last\)"
        r"|\bat [\w.$<>]+\([\w.]+\.(?:java|kt|scala|cs|php|py|rb):\d+\)"
        r"|\bat \S+ \((?:/|[A-Za-z]:\\)[^)\n]*:\d+:\d+\)"
        r"|\bSystem\.\w+Exception\b|\bjava\.lang\.\w+Exception\b"
        r"|Stack trace:|Exception in thread"
    )),
    ("database error", re.compile(
        r"SQLSTATE\[|You have an error in your SQL syntax|\bORA-\d{4,5}\b"
        r"|\bPG::\w+Error|\bpsycopg2\.\w+|Unclosed quotation mark"
        r"|syntax error at or near|\bmysqli?_\w+\(|SQLite3?::"
    )),
    ("debug page", re.compile(
        r"Whitelabel Error Page|Werkzeug Debugger|Django Debug|DEBUG = True"
        r"|Server Error in '/' Application|ASP\.NET is configured to show"
    )),
    # A file path on the server, not a link in an HTML page: it must name a source
    # or config file, so "/home/index" or "/usr/" in a normal 404 page never match.
    ("server file path", re.compile(
        r"(?<![\w./\"'=-])/(?:var|usr|home|opt|srv|etc|app|root)/[\w.-]+(?:/[\w.-]+)*"
        r"\.(?:py|php|rb|js|mjs|ts|java|kt|cs|go|rs|conf|ini|xml|ya?ml|log|so|dll|jar|class)\b"
        r"|[A-Za-z]:\\(?:Users|inetpub|Windows|Program Files)\\[\w \\.-]*\.\w{1,8}\b"
    )),
)


def _result(
    check_id: str, title: str, category: str, verdict: str, severity: str,
    summary: str, *, evidence: dict | None = None, recommendation: str | None = None,
) -> CheckResult:
    return CheckResult(
        check_id=check_id, title=title, category=category, verdict=verdict,
        severity=severity, summary=summary, evidence=evidence or {},
        recommendation=recommendation if verdict == FAILED else None,
    )


def _clip(value: str | None, limit: int = 200) -> str | None:
    if value is None:
        return None
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _not_observed(obs: HttpObservation | None, what: str) -> str | None:
    """Explain why a request produced nothing to judge, or None if it did."""
    if obs is None:
        return f"The {what} was not performed."
    if not obs.received:
        return f"The {what} received no response ({obs.error_kind}: {obs.error})."
    return None


# --------------------------------------------------------------------- TLS --

def check_tls_protocol(tls: TlsObservation | None) -> CheckResult:
    cid, title, cat, sev = "tls_protocol", "TLS protocol and cipher", "transport", "high"
    if tls is not None and not tls.ok and tls.error_kind == "legacy_protocol":
        # The client offers TLS 1.2 and newer only; a protocol-version alert or an
        # older ServerHello back means the server cannot speak anything newer.
        return _result(
            cid, title, cat, FAILED, sev,
            "The server could not negotiate TLS 1.2 or newer; it appears to support "
            "only deprecated protocol versions.",
            evidence={"offered": "TLS 1.2 and newer", "error": tls.error},
            recommendation="Enable TLS 1.2 and TLS 1.3 and disable TLS 1.0 and 1.1.",
        )
    if tls is None or not tls.ok:
        why = (
            "The TLS handshake was not performed."
            if tls is None
            else (
                "Certificate verification stopped the handshake before the protocol "
                "was negotiated; see the certificate check."
                if tls.error_kind == "cert_verify"
                else f"The TLS handshake did not complete ({tls.error_kind}: {tls.error})."
            )
        )
        return _result(cid, title, cat, INCONCLUSIVE, sev, why)
    evidence = {
        "negotiated_version": tls.version,
        "cipher": tls.cipher_name,
        "cipher_bits": tls.cipher_bits,
        "note": "Only the negotiated version was observed; support for older "
                "protocol versions was not probed.",
    }
    if tls.version not in {"TLSv1.2", "TLSv1.3"}:
        return _result(
            cid, title, cat, FAILED, sev,
            f"The server negotiated {tls.version}, which is deprecated.",
            evidence=evidence,
            recommendation="Disable TLS versions below 1.2 and prefer TLS 1.3.",
        )
    if tls.cipher_name and _WEAK_CIPHER.search(tls.cipher_name):
        return _result(
            cid, title, cat, FAILED, sev,
            f"The negotiated cipher {tls.cipher_name} is considered weak.",
            evidence=evidence,
            recommendation="Remove RC4, 3DES, DES, NULL, EXPORT and MD5-based cipher suites.",
        )
    return _result(
        cid, title, cat, PASSED, sev,
        f"The server negotiated {tls.version} with {tls.cipher_name}.",
        evidence=evidence,
    )


def check_tls_certificate(tls: TlsObservation | None, *, now: float | None = None) -> CheckResult:
    cid, title, cat, sev = "tls_certificate", "TLS certificate", "transport", "high"
    if tls is None:
        return _result(cid, title, cat, INCONCLUSIVE, sev, "The TLS handshake was not performed.")
    if not tls.ok and tls.error_kind == "cert_verify":
        return _result(
            cid, title, cat, FAILED, sev,
            f"Certificate verification failed: {tls.verify_message}.",
            evidence={"verify_message": tls.verify_message},
            recommendation="Serve a valid, unexpired certificate issued by a trusted CA "
                           "that covers this hostname.",
        )
    if not tls.ok:
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            f"The TLS handshake did not complete ({tls.error_kind}: {tls.error}).",
        )
    current = now if now is not None else datetime.now(timezone.utc).timestamp()
    days = None if tls.not_after is None else (tls.not_after - current) / 86400
    evidence = {
        "subject": tls.subject,
        "issuer": tls.issuer,
        "days_until_expiry": None if days is None else round(days, 1),
        "alternative_names": tls.san_count,
    }
    if days is not None and days < _CERT_EXPIRY_WARNING_DAYS:
        return _result(
            cid, title, cat, FAILED, "medium",
            "The certificate"
            + (f" (issuer: {tls.issuer})" if tls.issuer else "")
            + f" is valid but expires in {max(days, 0):.0f} day(s).",
            evidence=evidence,
            recommendation="Renew the certificate and automate renewal.",
        )
    issuer = f" (issuer: {tls.issuer})" if tls.issuer else ""
    return _result(
        cid, title, cat, PASSED, sev,
        f"The certificate chain and hostname verified{issuer}"
        + (f"; it expires in {days:.0f} days." if days is not None else "."),
        evidence=evidence,
    )


def check_https_redirect(obs: HttpObservation | None) -> CheckResult:
    cid, title, cat, sev = "https_redirect", "HTTP to HTTPS redirect", "transport", "medium"
    if obs is None:
        return _result(cid, title, cat, INCONCLUSIVE, sev, "The plain-HTTP request was not performed.")
    if obs.error_kind == "connection_refused":
        return _result(
            cid, title, cat, PASSED, sev,
            "Port 80 refused the connection, so no plain-HTTP service is offered.",
            evidence={"port_80": "connection refused"},
        )
    if not obs.received:
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            f"The plain-HTTP request received no response ({obs.error_kind}).",
        )
    status = obs.status
    location = obs.header("location")
    evidence = {"http_status": status, "location": _clip(location)}
    if 300 <= status < 400 and status != 304:
        if not location:
            return _result(
                cid, title, cat, INCONCLUSIVE, sev,
                f"HTTP {status} had no Location header, so the target is unknown.",
                evidence=evidence,
            )
        if location.lower().startswith("https://"):
            return _result(
                cid, title, cat, PASSED, sev,
                f"Plain HTTP is redirected (HTTP {status}) to an HTTPS location.",
                evidence=evidence,
            )
        return _result(
            cid, title, cat, FAILED, sev,
            f"Plain HTTP is redirected (HTTP {status}) to a location that is not HTTPS.",
            evidence=evidence,
            recommendation="Redirect all HTTP requests to the HTTPS origin.",
        )
    if 200 <= status < 300:
        return _result(
            cid, title, cat, FAILED, sev,
            f"The resource is served over plain HTTP (HTTP {status}) without a redirect to HTTPS.",
            evidence=evidence,
            recommendation="Redirect HTTP to HTTPS or close port 80, and enable HSTS.",
        )
    return _result(
        cid, title, cat, INCONCLUSIVE, sev,
        f"Plain HTTP returned HTTP {status}, which does not show whether it redirects to HTTPS.",
        evidence=evidence,
    )


# ----------------------------------------------------------------- headers --

def _hsts(obs: HttpObservation):
    value = obs.header("strict-transport-security")
    if not value:
        return "absent", "Strict-Transport-Security is not set.", {}
    match = re.search(r"max-age\s*=\s*\"?(\d+)", value, re.I)
    seconds = int(match.group(1)) if match else 0
    evidence = {
        "value": _clip(value),
        "max_age_seconds": seconds,
        "include_subdomains": "includesubdomains" in value.lower(),
    }
    if seconds < _HSTS_MIN_SECONDS:
        return "weak", (
            f"HSTS max-age is {seconds} seconds; at least {_HSTS_MIN_SECONDS} "
            "(180 days) is recommended."
        ), evidence
    return "good", f"HSTS is set with max-age={seconds}.", evidence


def _content_type_options(obs: HttpObservation):
    value = obs.header("x-content-type-options")
    if not value:
        return "absent", "X-Content-Type-Options is not set.", {}
    if "nosniff" in value.lower():
        return "good", "X-Content-Type-Options is nosniff.", {"value": _clip(value)}
    return "weak", f"X-Content-Type-Options is '{_clip(value, 40)}', not nosniff.", {"value": _clip(value)}


def _frame_protection(obs: HttpObservation):
    xfo = (obs.header("x-frame-options") or "").strip().lower()
    csp = obs.header("content-security-policy") or ""
    ancestors = re.search(r"(?:^|;)\s*frame-ancestors\s+([^;]*)", csp, re.I)
    sources = ancestors.group(1).split() if ancestors else []
    # "frame-ancestors *" or a bare scheme such as "https:" lets any site frame it.
    open_ancestors = any(
        source == "*" or re.fullmatch(r"[a-z][a-z0-9+.-]*:", source, re.I)
        for source in sources
    )
    has_ancestors = bool(sources) and not open_ancestors
    evidence = {
        "x_frame_options": _clip(xfo or None),
        "csp_frame_ancestors": " ".join(sources)[:100] or None,
    }
    if has_ancestors or xfo in {"deny", "sameorigin"}:
        return "good", "Framing is restricted.", evidence
    if open_ancestors:
        return "weak", "The CSP frame-ancestors directive allows any site to frame this API.", evidence
    if xfo:
        return "weak", f"X-Frame-Options '{_clip(xfo, 40)}' does not restrict framing.", evidence
    return "absent", "Neither X-Frame-Options nor CSP frame-ancestors is set.", evidence


def _csp(obs: HttpObservation):
    value = obs.header("content-security-policy")
    if not value:
        return "absent", "Content-Security-Policy is not set.", {}
    lowered = value.lower()
    evidence = {"policy": _clip(value, 160)}
    if "unsafe-eval" in lowered or re.search(r"(?:default|script)-src[^;]*\s\*(?:\s|;|$)", lowered):
        return "weak", "The CSP allows unsafe-eval or a wildcard script source.", evidence
    return "good", "A Content-Security-Policy is set.", evidence


def _referrer_policy(obs: HttpObservation):
    value = obs.header("referrer-policy")
    if not value:
        return "absent", "Referrer-Policy is not set.", {}
    effective = value.split(",")[-1].strip().lower()
    safe = {"no-referrer", "same-origin", "strict-origin", "strict-origin-when-cross-origin"}
    evidence = {"value": _clip(value, 80)}
    if effective in safe:
        return "good", f"Referrer-Policy is {effective}.", evidence
    return "weak", f"Referrer-Policy '{_clip(effective, 40)}' can leak the full URL.", evidence


def _permissions_policy(obs: HttpObservation):
    value = obs.header("permissions-policy") or obs.header("feature-policy")
    if not value:
        return "absent", "Permissions-Policy is not set.", {}
    return "good", "A Permissions-Policy is set.", {"policy": _clip(value, 120)}


def _cache_control(obs: HttpObservation):
    value = obs.header("cache-control")
    if not value:
        return "absent", "Cache-Control is not set.", {}
    lowered = value.lower()
    evidence = {"value": _clip(value, 120)}
    if any(token in lowered for token in ("no-store", "no-cache", "private")):
        return "good", "Responses are marked non-cacheable by shared caches.", evidence
    return "weak", (
        "Cache-Control allows shared caching of this response; fine for public data, "
        "but responses that carry user data should be no-store or private."
    ), evidence


_HEADER_SPECS: tuple[tuple[str, str, str, Callable, str], ...] = (
    ("header_hsts", "Strict-Transport-Security", "medium", _hsts,
     "Send Strict-Transport-Security with max-age of at least 15552000 and includeSubDomains."),
    ("header_x_content_type_options", "X-Content-Type-Options", "low", _content_type_options,
     "Send X-Content-Type-Options: nosniff."),
    ("header_frame_protection", "Clickjacking protection", "low", _frame_protection,
     "Send X-Frame-Options: DENY or a CSP frame-ancestors directive."),
    ("header_csp", "Content-Security-Policy", "low", _csp,
     "Send a restrictive Content-Security-Policy such as default-src 'none'; frame-ancestors 'none'."),
    ("header_referrer_policy", "Referrer-Policy", "low", _referrer_policy,
     "Send Referrer-Policy: no-referrer or strict-origin-when-cross-origin."),
    ("header_permissions_policy", "Permissions-Policy", "low", _permissions_policy,
     "Send a Permissions-Policy that disables features the API does not use."),
    ("header_cache_control", "Cache-Control", "info", _cache_control,
     "Mark responses that carry user data as no-store or private."),
)


def _disclosed_headers(obs: HttpObservation) -> dict[str, str]:
    leaked: dict[str, str] = {}
    server = obs.header("server")
    if server and re.search(r"\d+\.\d+|/\d", server):
        leaked["server"] = _clip(server, 80)
    for name in ("x-powered-by", "x-aspnet-version", "x-aspnetmvc-version"):
        value = obs.header(name)
        if value:
            leaked[name] = _clip(value, 80)
    return leaked


def _cookie_problems(obs: HttpObservation) -> list[str]:
    problems = []
    for cookie in obs.header_values("set-cookie"):
        name = cookie.split("=", 1)[0].strip()[:40] or "cookie"
        attributes = {part.strip().lower().split("=")[0] for part in cookie.split(";")[1:]}
        missing = [flag for flag, key in (("Secure", "secure"), ("HttpOnly", "httponly"),
                                          ("SameSite", "samesite")) if key not in attributes]
        if missing:
            problems.append(f"{name} is missing {', '.join(missing)}")
    return problems


def check_security_headers(obs: Observations) -> list[CheckResult]:
    source = obs.primary if obs.primary is not None else obs.options
    category = "headers"
    specs = [(cid, title, severity) for cid, title, severity, _, _ in _HEADER_SPECS]
    specs.append(("header_information_disclosure", "Technology disclosure headers", "low"))

    def all_inconclusive(why: str) -> list[CheckResult]:
        return [_result(cid, title, category, INCONCLUSIVE, sev, why) for cid, title, sev in specs]

    reason = _not_observed(source, "request that carries the security headers")
    if reason:
        return all_inconclusive(reason)
    status = source.status
    if not 200 <= status < 400:
        return all_inconclusive(
            f"The {source.method} response was HTTP {status}. Headers on denied, missing, "
            "throttled or error responses are not representative, so they cannot be judged."
        )
    # Absence only counts against the target when a normal HEAD or GET answered
    # with success. A redirect or an OPTIONS reply may legitimately omit them.
    absence_conclusive = source.method in {"HEAD", "GET"} and 200 <= status < 300
    basis = {"observed_on": f"{source.method} {source.target.split('?')[0]}", "http_status": status}
    results: list[CheckResult] = []

    for cid, title, severity, classify, recommendation in _HEADER_SPECS:
        state, detail, evidence = classify(source)
        evidence = {**basis, **evidence}
        if state == "good":
            results.append(_result(cid, title, category, PASSED, severity, detail, evidence=evidence))
        elif state == "weak" or absence_conclusive:
            results.append(_result(cid, title, category, FAILED, severity, detail,
                                   evidence=evidence, recommendation=recommendation))
        else:
            results.append(_result(
                cid, title, category, INCONCLUSIVE, severity,
                f"{detail} The {source.method} response (HTTP {status}) may not carry "
                "the headers a normal request would, so this is not counted as a failure.",
                evidence=evidence,
            ))

    leaked = _disclosed_headers(source)
    cid, title = "header_information_disclosure", "Technology disclosure headers"
    if leaked:
        results.append(_result(
            cid, title, category, FAILED, "low",
            "Response headers reveal server technology or versions: "
            + ", ".join(f"{k}: {v}" for k, v in leaked.items()) + ".",
            evidence={**basis, "headers": leaked},
            recommendation="Remove X-Powered-By and version numbers from the Server header.",
        ))
    elif absence_conclusive:
        results.append(_result(cid, title, category, PASSED, "low",
                               "No technology or version disclosure headers were observed.",
                               evidence=basis))
    else:
        results.append(_result(cid, title, category, INCONCLUSIVE, "low",
                               f"No disclosure headers appeared on the {source.method} response "
                               f"(HTTP {status}), which is not enough to rule them out.",
                               evidence=basis))

    problems = _cookie_problems(source)
    if source.header_values("set-cookie"):
        if problems:
            results.append(_result(
                "header_cookie_attributes", "Cookie attributes", category, FAILED, "medium",
                "Cookies set by the response lack protective attributes: " + "; ".join(problems) + ".",
                evidence={**basis, "problems": problems},
                recommendation="Set Secure, HttpOnly and SameSite on every cookie.",
            ))
        else:
            results.append(_result(
                "header_cookie_attributes", "Cookie attributes", category, PASSED, "medium",
                "Every cookie set by the response has Secure, HttpOnly and SameSite.",
                evidence=basis,
            ))
    return results


# -------------------------------------------------------- CORS and methods --

def check_cors(obs: HttpObservation | None) -> CheckResult:
    cid, title, cat, sev = "cors_foreign_origin", "CORS policy for a foreign origin", "cors", "medium"
    reason = _not_observed(obs, "CORS preflight")
    if reason:
        return _result(cid, title, cat, INCONCLUSIVE, sev, reason)
    status = obs.status
    if not 200 <= status < 300:
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            f"The preflight returned HTTP {status}, so the CORS policy could not be read.",
            evidence={"http_status": status},
        )
    allow_origin = (obs.header("access-control-allow-origin") or "").strip()
    credentials = (obs.header("access-control-allow-credentials") or "").strip().lower() == "true"
    evidence = {
        "tested_origin": FOREIGN_ORIGIN,
        "http_status": status,
        "access_control_allow_origin": _clip(allow_origin or None, 100),
        "allow_credentials": credentials,
        "note": "Evaluated from an OPTIONS preflight; simple requests were not tested.",
    }
    if allow_origin == FOREIGN_ORIGIN:
        return _result(
            cid, title, cat, FAILED, "high" if credentials else "medium",
            "The server reflects an arbitrary foreign origin"
            + (" and allows credentials, so any website could read responses that depend on "
               "cookies or other ambient credentials."
               if credentials else "."),
            evidence=evidence,
            recommendation="Allow only an explicit list of trusted origins; never reflect Origin.",
        )
    if allow_origin.lower() == "null":
        return _result(cid, title, cat, FAILED, "medium",
                       "The server allows the 'null' origin.", evidence=evidence,
                       recommendation="Do not allow the null origin.")
    if allow_origin == "*" and credentials:
        return _result(cid, title, cat, FAILED, "medium",
                       "The server combines a wildcard origin with Allow-Credentials, "
                       "an invalid and risky configuration.", evidence=evidence,
                       recommendation="Use an explicit origin list when credentials are allowed.")
    if allow_origin == "*":
        return _result(cid, title, cat, PASSED, sev,
                       "The API allows any origin without credentials, which is acceptable "
                       "only for intentionally public data.", evidence=evidence)
    return _result(cid, title, cat, PASSED, sev,
                   "The foreign origin was not granted cross-origin access.", evidence=evidence)


def check_methods(obs: HttpObservation | None) -> CheckResult:
    cid, title, cat, sev = "http_methods_exposed", "HTTP methods advertised by OPTIONS", "methods", "medium"
    reason = _not_observed(obs, "OPTIONS request")
    if reason:
        return _result(cid, title, cat, INCONCLUSIVE, sev, reason)
    status = obs.status
    if not 200 <= status < 300:
        return _result(cid, title, cat, INCONCLUSIVE, sev,
                       f"OPTIONS returned HTTP {status}, so the allowed methods are unknown.",
                       evidence={"http_status": status})
    # Servers list methods in Allow, or only in the CORS Access-Control-Allow-Methods.
    sources = [
        name for name in ("allow", "access-control-allow-methods") if obs.header(name)
    ]
    listed = ",".join(obs.header(name) or "" for name in sources)
    methods = sorted({m.strip().upper() for m in listed.split(",") if m.strip() and m.strip() != "*"})
    if not methods:
        return _result(cid, title, cat, INCONCLUSIVE, sev,
                       "OPTIONS succeeded but the server did not list its allowed methods.",
                       evidence={"http_status": status})
    dangerous = sorted(set(methods) & _DANGEROUS_METHODS)
    evidence = {"allow": methods, "listed_in": sources, "http_status": status}
    if dangerous:
        return _result(cid, title, cat, FAILED, sev,
                       f"The server advertises methods that should be disabled: {', '.join(dangerous)}.",
                       evidence=evidence,
                       recommendation="Disable TRACE, CONNECT and WebDAV methods on the API.")
    return _result(cid, title, cat, PASSED, sev,
                   f"The advertised methods are {', '.join(methods)}; none are risky diagnostics.",
                   evidence=evidence)


# ------------------------------------------------------- error handling ---

def check_error_leakage(obs: HttpObservation | None) -> CheckResult:
    cid, title, cat, sev = "error_leakage", "Error-message information leakage", "error_handling", "medium"
    reason = _not_observed(obs, "request for a non-existent resource")
    if reason:
        return _result(cid, title, cat, INCONCLUSIVE, sev, reason)
    status = obs.status
    if status not in _ERROR_STATUSES_WITH_APP_PAGE:
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            f"The request for a missing resource returned HTTP {status}, not an application "
            "error response, so error handling was not exercised.",
            evidence={"http_status": status},
        )
    encoding = (obs.header("content-encoding") or "").strip().lower()
    if encoding and encoding != "identity":
        # We ask for an uncompressed body; if the server compressed it anyway the
        # bytes cannot be scanned, so no claim is made either way.
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            f"The error response was {encoding}-encoded, so its content could not be inspected.",
            evidence={"http_status": status, "content_encoding": encoding},
        )
    if status == 500 and not obs.body.strip():
        return _result(
            cid, title, cat, INCONCLUSIVE, sev,
            "The error response had no body, so there was nothing to inspect.",
            evidence={"http_status": status},
        )
    body = obs.body.replace(obs.target, "").replace(obs.target.split("?")[0], "")
    found = [name for name, pattern in _LEAK_SIGNATURES if pattern.search(body)]
    evidence = {"http_status": status, "body_bytes_scanned": len(obs.body)}
    if found:
        return _result(cid, title, cat, FAILED, sev,
                       f"The error response exposes internal detail ({', '.join(found)}).",
                       evidence={**evidence, "signatures": found},
                       recommendation="Return generic error messages and log details server-side.")
    return _result(cid, title, cat, PASSED, sev,
                   f"The HTTP {status} error response contained no stack trace, database error, "
                   "debug page or server path.", evidence=evidence)


# --------------------------------------------------------- rate limiting ---

def check_rate_limit_evidence(obs: Observations) -> CheckResult:
    cid, title, cat, sev = "rate_limit_evidence", "Rate-limiting evidence", "rate_limiting", "low"
    advertised: dict[str, str] = {}
    for observation in (obs.primary, obs.options, obs.not_found):
        if observation is None or not observation.received:
            continue
        # Headers on a denied, missing or failing response (401, 403, 404, 405,
        # 5xx) are not evidence about the API: only a normal reply or a 429 counts.
        if not (200 <= observation.status < 400 or observation.status == 429):
            continue
        for name in _RATE_LIMIT_HEADERS:
            value = observation.header(name)
            if value:
                advertised[name] = _clip(value, 80)
        if observation.status == 429 and observation.header("retry-after"):
            advertised["retry-after"] = _clip(observation.header("retry-after"), 40)
    traffic = obs.traffic
    throttled = traffic.throttled_requests if traffic else 0
    evidence: dict = {}
    if traffic:
        evidence["performance_run"] = {
            "source": traffic.source,
            "requests": traffic.total_requests,
            "status_counts": traffic.status_counts,
            "partial_read": traffic.truncated,
        }
    if advertised:
        evidence["rate_limit_headers"] = advertised
    if throttled:
        return _result(cid, title, cat, PASSED, sev,
                       f"The target throttled the performance run: {throttled} of "
                       f"{traffic.total_requests} requests received HTTP 429.", evidence=evidence)
    if advertised:
        return _result(cid, title, cat, PASSED, sev,
                       "The target advertises rate-limit headers: " + ", ".join(advertised) + ".",
                       evidence=evidence)
    if traffic:
        why = (f"The performance run sent {traffic.total_requests} requests and none were "
               "throttled (no HTTP 429, no rate-limit headers). That shows no limit was reached "
               "at this load; it does not show that rate limiting is absent.")
    else:
        why = ("No rate-limit headers were returned and the performance run's response "
               "statuses were unavailable, so rate limiting could not be judged.")
    return _result(cid, title, cat, INCONCLUSIVE, sev, why, evidence=evidence)


# ---------------------------------------------------------------- rollup ---

def evaluate(obs: Observations, *, now: float | None = None) -> list[CheckResult]:
    results = [
        check_tls_protocol(obs.tls),
        check_tls_certificate(obs.tls, now=now),
        check_https_redirect(obs.http_redirect),
        *check_security_headers(obs),
        check_cors(obs.options),
        check_methods(obs.options),
        check_error_leakage(obs.not_found),
        check_rate_limit_evidence(obs),
    ]
    if obs.skipped_reason:
        results = [
            r if r.verdict != INCONCLUSIVE
            else replace(r, summary=f"{r.summary} {obs.skipped_reason}")
            for r in results
        ]
    return results


def summarize(results: list[CheckResult]) -> dict:
    """Overall status, score and counts, from the assessed checks only."""
    counts = Counter(r.verdict for r in results)
    assessed = [r for r in results if r.verdict != INCONCLUSIVE]
    failed = [r for r in assessed if r.verdict == FAILED]
    summary = {
        "total": len(results),
        "assessed": len(assessed),
        "passed": counts[PASSED],
        "failed": counts[FAILED],
        "inconclusive": counts[INCONCLUSIVE],
    }
    if not assessed:
        return {**summary, "status": "WARNING", "outcome": "not_assessed",
                "security_score": "N/A",
                "security_score_basis": "No passive check could be assessed, so there is no score."}
    if any(r.severity in BLOCKING_SEVERITIES for r in failed):
        status = "FAIL"
    elif any(r.severity in WARNING_SEVERITIES for r in failed):
        status = "WARNING"
    else:
        status = "PASS"
    weighted = [r for r in assessed if SEVERITY_WEIGHT.get(r.severity, 0) > 0]
    total_points = sum(SEVERITY_WEIGHT[r.severity] for r in weighted)
    earned = sum(SEVERITY_WEIGHT[r.severity] for r in weighted if r.verdict == PASSED)
    if total_points:
        score = f"{int(100 * earned / total_points + 0.5)}%"
        basis = (
            f"{earned} of {total_points} severity-weighted points (high=5, medium=3, low=1) "
            f"across {len(weighted)} assessed passive checks; informational checks carry no "
            f"weight and {counts[INCONCLUSIVE]} inconclusive check(s) are neither passed nor failed."
        )
    else:
        score, basis = "N/A", "Only informational checks were assessed, so there is no weighted score."
    outcome = "assessed" if not counts[INCONCLUSIVE] else "partially_assessed"
    return {**summary, "status": status, "outcome": outcome,
            "security_score": score, "security_score_basis": basis}
