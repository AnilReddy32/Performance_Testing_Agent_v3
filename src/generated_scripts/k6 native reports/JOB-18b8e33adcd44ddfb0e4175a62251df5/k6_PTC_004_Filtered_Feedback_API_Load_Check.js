import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.BASE_URL;
const ENDPOINT = "/comments?postId=1";
const METHOD = "GET";
const BODY_TEMPLATE = null;
const EXPECTED_STATUS = 200;
const HEADER_ENV = {};

if (!BASE_URL) {
  throw new Error('BASE_URL must be provided by the trusted execution runner.');
}

export const options = {
  stages: [{"duration":"5s","target":20},{"duration":"50s","target":20},{"duration":"5s","target":0}],
  rps: 12,
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<5000'],
    checks: ['rate>0.99'],
  },
  tags: {"test_case_id":"PTC-004","endpoint":"/comments?postId=1","environment":"external_api"},
};

export default function () {
  const headers = {
  };
  if (__ENV.AUTHORIZATION_HEADER) {
    headers.Authorization = __ENV.AUTHORIZATION_HEADER;
  }
  for (const [headerName, envName] of Object.entries(HEADER_ENV)) {
    const headerValue = __ENV[envName];
    if (!headerValue) {
      throw new Error(`Required header environment variable ${envName} is missing.`);
    }
    headers[headerName] = headerValue;
  }
  const requestBody = BODY_TEMPLATE === null
    ? null
    : BODY_TEMPLATE
        .replace(/\{\{__VU\}\}/g, String(__VU))
        .replace(/\{\{__ITER\}\}/g, String(__ITER));

  const response = http.request(
    METHOD,
    `${BASE_URL.replace(/\/+$/, '')}${ENDPOINT}`,
    requestBody,
    {
      headers,
      redirects: 0,
      tags: {
        test_case_id: "PTC-004",
        endpoint: ENDPOINT,
      },
    },
  );

  check(response, {
    [`expected HTTP ${EXPECTED_STATUS}`]: (res) => res.status === EXPECTED_STATUS,
  });
}
