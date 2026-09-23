import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL;
if (!BASE_URL) {
    throw new Error('BASE_URL environment variable is required');
}

const API_PATH = __ENV.API_PATH || '/api/v1/payment';
const VUS = Number(__ENV.VUS || 1);
const DURATION = __ENV.DURATION || '60s';
const EXPECTED_STATUS = Number(__ENV.EXPECTED_STATUS || 200);

export const options = {
    vus: VUS,
    duration: DURATION,
};

export default function () {
    const transactionId = `test-transaction-${__VU}-${__ITER}`;
    const payload = JSON.stringify({
        amount: __ENV.TEST_AMOUNT || 1000,
        upiId: __ENV.TEST_UPI_ID || 'test@upi',
        transactionId: transactionId,
    });

    const headers = {
        'Content-Type': 'application/json',
    };

    const response = http.post(`${BASE_URL}${API_PATH}`, payload, { headers: headers });

    check(response, {
        'HTTP response received': (r) => r.status > 0,
        'HTTP status is expected': (r) => r.status === EXPECTED_STATUS,
    });

    sleep(1);
}