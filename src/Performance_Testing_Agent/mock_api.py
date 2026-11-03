"""Local-only banking mock API used for safe performance-script validation."""

from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from Performance_Testing_Agent.api_docs import docs_urls, ok


# The groups that Swagger shows, in this order.
TAGS_METADATA = [
    {"name": "System", "description": "Health check used by the load-test scripts."},
    {"name": "Customers", "description": "Create, read, update and delete bank customers."},
    {
        "name": "Accounts",
        "description": "Create, read, update and delete accounts. Also read an "
        "account's balance and statements.",
    },
    {
        "name": "Transactions",
        "description": "List and create the transactions of an account. There is "
        "deliberately no update or delete: financial transactions are append-only.",
    },
    {"name": "Payments", "description": "Create, read, update and cancel payments."},
    {"name": "Transfers", "description": "Create, read, update and cancel transfers."},
    {
        "name": "Beneficiaries",
        "description": "Create, read, update and delete saved payees.",
    },
    {
        "name": "Cards",
        "description": "Create, read, update and delete cards, and change a card's controls.",
    },
    {
        "name": "Loans",
        "description": "Create, read, update and withdraw loan applications.",
    },
    {
        "name": "Legacy",
        "description": "An old route that is kept unchanged so test case PTC-012 still works.",
    },
]

API_DESCRIPTION = """Local-only banking mock used to validate k6 and JMeter scripts.

**How it behaves.** Every endpoint returns a fixed, made-up answer and **nothing is
stored**. Create always returns the same new id, Get returns sample data for any id,
and Update and Delete simply echo back what you sent.

**Request bodies are strict.** Unknown fields, wrong types (for example a number sent
as text) and values outside the allowed range are rejected with HTTP 422.
"""

app = FastAPI(
    title="Local Performance Test Mock API",
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    **docs_urls(),
)


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

class CustomerRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"name": "Alex Morgan", "segment": "retail"}]}
    )

    name: Annotated[str, Field(min_length=1, max_length=100)]
    segment: Annotated[str, Field(min_length=1, max_length=40)] = "retail"


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    responses=ok({"status": "healthy"}),
)
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get(
    "/api/customers/{customer_id}",
    tags=["Customers"],
    summary="Get a customer",
    responses=ok(
        {"customer_id": "CUST-1001", "name": "Alex Morgan", "status": "active", "segment": "retail"}
    ),
)
async def get_customer(customer_id: str) -> dict[str, object]:
    return {
        "customer_id": customer_id,
        "name": "Alex Morgan",
        "status": "active",
        "segment": "retail",
    }


@app.post(
    "/api/customers",
    tags=["Customers"],
    summary="Create a customer",
    responses=ok(
        {"customer_id": "CUST-MOCK-001", "name": "Alex Morgan", "segment": "retail", "status": "active"}
    ),
)
async def create_customer(request: CustomerRequest) -> dict[str, object]:
    return {
        "customer_id": "CUST-MOCK-001",
        "name": request.name,
        "segment": request.segment,
        "status": "active",
    }


@app.put(
    "/api/customers/{customer_id}",
    tags=["Customers"],
    summary="Update a customer",
    responses=ok(
        {
            "customer_id": "CUST-1001",
            "name": "Alex Morgan",
            "segment": "retail",
            "status": "active",
            "updated": True,
        }
    ),
)
async def update_customer(customer_id: str, request: CustomerRequest) -> dict[str, object]:
    return {
        "customer_id": customer_id,
        "name": request.name,
        "segment": request.segment,
        "status": "active",
        "updated": True,
    }


@app.delete(
    "/api/customers/{customer_id}",
    tags=["Customers"],
    summary="Delete a customer",
    responses=ok({"customer_id": "CUST-1001", "deleted": True}),
)
async def delete_customer(customer_id: str) -> dict[str, object]:
    return {"customer_id": customer_id, "deleted": True}


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

class AccountRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"customer_id": "CUST-1001", "account_type": "checking", "currency": "USD"}
            ]
        }
    )

    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    account_type: Annotated[str, Field(min_length=1, max_length=20)] = "checking"
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"


@app.get(
    "/api/accounts/{account_id}",
    tags=["Accounts"],
    summary="Get an account",
    responses=ok(
        {
            "account_id": "ACCT-1001",
            "customer_id": "CUST-1001",
            "account_type": "checking",
            "currency": "USD",
            "status": "open",
        }
    ),
)
async def get_account(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "customer_id": "CUST-1001",
        "account_type": "checking",
        "currency": "USD",
        "status": "open",
    }


@app.post(
    "/api/accounts",
    tags=["Accounts"],
    summary="Create an account",
    responses=ok(
        {
            "account_id": "ACCT-MOCK-001",
            "customer_id": "CUST-1001",
            "account_type": "checking",
            "currency": "USD",
            "status": "open",
        }
    ),
)
async def create_account(request: AccountRequest) -> dict[str, object]:
    return {
        "account_id": "ACCT-MOCK-001",
        "customer_id": request.customer_id,
        "account_type": request.account_type,
        "currency": request.currency,
        "status": "open",
    }


@app.put(
    "/api/accounts/{account_id}",
    tags=["Accounts"],
    summary="Update an account",
    responses=ok(
        {
            "account_id": "ACCT-1001",
            "customer_id": "CUST-1001",
            "account_type": "checking",
            "currency": "USD",
            "status": "open",
            "updated": True,
        }
    ),
)
async def update_account(account_id: str, request: AccountRequest) -> dict[str, object]:
    return {
        "account_id": account_id,
        "customer_id": request.customer_id,
        "account_type": request.account_type,
        "currency": request.currency,
        "status": "open",
        "updated": True,
    }


@app.delete(
    "/api/accounts/{account_id}",
    tags=["Accounts"],
    summary="Delete an account",
    responses=ok({"account_id": "ACCT-1001", "deleted": True}),
)
async def delete_account(account_id: str) -> dict[str, object]:
    return {"account_id": account_id, "deleted": True}


@app.get(
    "/api/accounts/{account_id}/balance",
    tags=["Accounts"],
    summary="Get an account's balance",
    responses=ok({"account_id": "ACCT-1001", "currency": "USD", "available_balance": 1250.75}),
)
async def get_account_balance(account_id: str) -> dict[str, object]:
    return {"account_id": account_id, "currency": "USD", "available_balance": 1250.75}


# Transactions: Create added (append a new transaction); intentionally no
# PUT/DELETE - real financial transaction records are immutable/append-only
# once created, even in a mock.

class TransactionRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"amount": -25.0, "currency": "USD"}]}
    )

    amount: Annotated[float, Field(allow_inf_nan=False)]
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"


@app.get(
    "/api/accounts/{account_id}/transactions",
    tags=["Transactions"],
    summary="List an account's transactions",
    responses=ok(
        {
            "account_id": "ACCT-1001",
            "transactions": [
                {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
                {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
            ],
        }
    ),
)
async def get_transactions(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "transactions": [
            {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
            {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
        ],
    }


@app.post(
    "/api/accounts/{account_id}/transactions",
    tags=["Transactions"],
    summary="Create a transaction on an account",
    description="Appends a transaction. A negative amount is money going out.",
    responses=ok(
        {
            "account_id": "ACCT-1001",
            "transaction_id": "TXN-MOCK-001",
            "amount": -25.0,
            "currency": "USD",
            "status": "posted",
        }
    ),
)
async def create_transaction(account_id: str, request: TransactionRequest) -> dict[str, object]:
    return {
        "account_id": account_id,
        "transaction_id": "TXN-MOCK-001",
        "amount": request.amount,
        "currency": request.currency,
        "status": "posted",
    }


@app.get(
    "/api/accounts/{account_id}/statements",
    tags=["Accounts"],
    summary="List an account's statements",
    responses=ok(
        {
            "account_id": "ACCT-1001",
            "statements": [
                {"statement_id": "STMT-2026-09", "period": "2026-09", "status": "ready"}
            ],
        }
    ),
)
async def get_statements(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "statements": [
            {"statement_id": "STMT-2026-09", "period": "2026-09", "status": "ready"}
        ],
    }


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class PaymentRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"transaction_id": "TXN-9001", "amount": 45.25}]}
    )

    transaction_id: Annotated[str, Field(min_length=1, max_length=128)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


@app.post(
    "/api/payments",
    tags=["Payments"],
    summary="Create a payment",
    responses=ok(
        {
            "accepted": True,
            "payment_id": "PAY-MOCK-001",
            "transaction_id": "TXN-9001",
            "amount": 45.25,
            "status": "accepted",
        }
    ),
)
async def create_payment(request: PaymentRequest) -> dict[str, object]:
    return {
        "accepted": True,
        "payment_id": "PAY-MOCK-001",
        "transaction_id": request.transaction_id,
        "amount": request.amount,
        "status": "accepted",
    }


@app.get(
    "/api/payments/{payment_id}",
    tags=["Payments"],
    summary="Get a payment",
    responses=ok(
        {
            "payment_id": "PAY-MOCK-001",
            "transaction_id": "TXN-MOCK-001",
            "amount": 45.25,
            "status": "accepted",
        }
    ),
)
async def get_payment(payment_id: str) -> dict[str, object]:
    return {
        "payment_id": payment_id,
        "transaction_id": "TXN-MOCK-001",
        "amount": 45.25,
        "status": "accepted",
    }


@app.put(
    "/api/payments/{payment_id}",
    tags=["Payments"],
    summary="Update a payment",
    responses=ok(
        {
            "payment_id": "PAY-MOCK-001",
            "transaction_id": "TXN-9001",
            "amount": 45.25,
            "status": "updated",
            "updated": True,
        }
    ),
)
async def update_payment(payment_id: str, request: PaymentRequest) -> dict[str, object]:
    return {
        "payment_id": payment_id,
        "transaction_id": request.transaction_id,
        "amount": request.amount,
        "status": "updated",
        "updated": True,
    }


@app.delete(
    "/api/payments/{payment_id}",
    tags=["Payments"],
    summary="Cancel a payment",
    description="A payment is cancelled, not removed, so the answer shows status \"cancelled\".",
    responses=ok({"payment_id": "PAY-MOCK-001", "status": "cancelled", "deleted": True}),
)
async def delete_payment(payment_id: str) -> dict[str, object]:
    return {"payment_id": payment_id, "status": "cancelled", "deleted": True}


# ---------------------------------------------------------------------------
# Transfers
# ---------------------------------------------------------------------------

class TransferRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source_account_id": "ACCT-2001",
                    "destination_account_id": "ACCT-2002",
                    "amount": 7.5,
                    "reference": "Rent October",
                }
            ]
        }
    )

    source_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    destination_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    reference: Annotated[str, Field(min_length=1, max_length=128)]


@app.post(
    "/api/transfers",
    tags=["Transfers"],
    summary="Create a transfer",
    responses=ok(
        {
            "accepted": True,
            "transfer_id": "TRF-MOCK-001",
            "source_account_id": "ACCT-2001",
            "destination_account_id": "ACCT-2002",
            "amount": 7.5,
            "reference": "Rent October",
            "status": "accepted",
        }
    ),
)
async def create_transfer(request: TransferRequest) -> dict[str, object]:
    return {
        "accepted": True,
        "transfer_id": "TRF-MOCK-001",
        "source_account_id": request.source_account_id,
        "destination_account_id": request.destination_account_id,
        "amount": request.amount,
        "reference": request.reference,
        "status": "accepted",
    }


@app.get(
    "/api/transfers/{transfer_id}",
    tags=["Transfers"],
    summary="Get a transfer",
    responses=ok(
        {
            "transfer_id": "TRF-MOCK-001",
            "source_account_id": "ACCT-2001",
            "destination_account_id": "ACCT-2002",
            "amount": 7.5,
            "status": "accepted",
        }
    ),
)
async def get_transfer(transfer_id: str) -> dict[str, object]:
    return {
        "transfer_id": transfer_id,
        "source_account_id": "ACCT-2001",
        "destination_account_id": "ACCT-2002",
        "amount": 7.5,
        "status": "accepted",
    }


@app.put(
    "/api/transfers/{transfer_id}",
    tags=["Transfers"],
    summary="Update a transfer",
    responses=ok(
        {
            "transfer_id": "TRF-MOCK-001",
            "source_account_id": "ACCT-2001",
            "destination_account_id": "ACCT-2002",
            "amount": 7.5,
            "reference": "Rent October",
            "status": "updated",
            "updated": True,
        }
    ),
)
async def update_transfer(transfer_id: str, request: TransferRequest) -> dict[str, object]:
    return {
        "transfer_id": transfer_id,
        "source_account_id": request.source_account_id,
        "destination_account_id": request.destination_account_id,
        "amount": request.amount,
        "reference": request.reference,
        "status": "updated",
        "updated": True,
    }


@app.delete(
    "/api/transfers/{transfer_id}",
    tags=["Transfers"],
    summary="Cancel a transfer",
    description="A transfer is cancelled, not removed, so the answer shows status \"cancelled\".",
    responses=ok({"transfer_id": "TRF-MOCK-001", "status": "cancelled", "deleted": True}),
)
async def delete_transfer(transfer_id: str) -> dict[str, object]:
    return {"transfer_id": transfer_id, "status": "cancelled", "deleted": True}


# ---------------------------------------------------------------------------
# Beneficiaries
# ---------------------------------------------------------------------------

class BeneficiaryRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"account_id": "ACCT-2001", "name": "Alex Morgan", "nickname": "alex"}]
        }
    )

    account_id: Annotated[str, Field(min_length=1, max_length=32)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    nickname: Annotated[str, Field(min_length=1, max_length=50)]


@app.post(
    "/api/beneficiaries",
    tags=["Beneficiaries"],
    summary="Create a beneficiary",
    responses=ok(
        {
            "beneficiary_id": "BEN-MOCK-001",
            "account_id": "ACCT-2001",
            "name": "Alex Morgan",
            "nickname": "alex",
            "status": "active",
        }
    ),
)
async def create_beneficiary(request: BeneficiaryRequest) -> dict[str, object]:
    return {
        "beneficiary_id": "BEN-MOCK-001",
        "account_id": request.account_id,
        "name": request.name,
        "nickname": request.nickname,
        "status": "active",
    }


@app.get(
    "/api/beneficiaries/{beneficiary_id}",
    tags=["Beneficiaries"],
    summary="Get a beneficiary",
    responses=ok(
        {
            "beneficiary_id": "BEN-MOCK-001",
            "account_id": "ACCT-2001",
            "name": "Alex Morgan",
            "nickname": "alex",
            "status": "active",
        }
    ),
)
async def get_beneficiary(beneficiary_id: str) -> dict[str, object]:
    return {
        "beneficiary_id": beneficiary_id,
        "account_id": "ACCT-2001",
        "name": "Alex Morgan",
        "nickname": "alex",
        "status": "active",
    }


@app.put(
    "/api/beneficiaries/{beneficiary_id}",
    tags=["Beneficiaries"],
    summary="Update a beneficiary",
    responses=ok(
        {
            "beneficiary_id": "BEN-MOCK-001",
            "account_id": "ACCT-2001",
            "name": "Alex Morgan",
            "nickname": "alex",
            "status": "active",
            "updated": True,
        }
    ),
)
async def update_beneficiary(beneficiary_id: str, request: BeneficiaryRequest) -> dict[str, object]:
    return {
        "beneficiary_id": beneficiary_id,
        "account_id": request.account_id,
        "name": request.name,
        "nickname": request.nickname,
        "status": "active",
        "updated": True,
    }


@app.delete(
    "/api/beneficiaries/{beneficiary_id}",
    tags=["Beneficiaries"],
    summary="Delete a beneficiary",
    responses=ok({"beneficiary_id": "BEN-MOCK-001", "deleted": True}),
)
async def delete_beneficiary(beneficiary_id: str) -> dict[str, object]:
    return {"beneficiary_id": beneficiary_id, "deleted": True}


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

class CardRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"customer_id": "CUST-1001", "card_type": "debit"}]}
    )

    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    card_type: Annotated[str, Field(min_length=1, max_length=20)] = "debit"


class CardControlsRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"freeze": False, "online_enabled": True, "international_enabled": False}
            ]
        }
    )

    freeze: bool
    online_enabled: bool
    international_enabled: bool


@app.get(
    "/api/cards/{card_id}",
    tags=["Cards"],
    summary="Get a card",
    responses=ok(
        {
            "card_id": "CARD-MOCK-001",
            "customer_id": "CUST-1001",
            "card_type": "debit",
            "status": "active",
            "currency": "USD",
        }
    ),
)
async def get_card(card_id: str) -> dict[str, object]:
    return {
        "card_id": card_id,
        "customer_id": "CUST-1001",
        "card_type": "debit",
        "status": "active",
        "currency": "USD",
    }


@app.post(
    "/api/cards",
    tags=["Cards"],
    summary="Create a card",
    responses=ok(
        {
            "card_id": "CARD-MOCK-001",
            "customer_id": "CUST-1001",
            "card_type": "debit",
            "status": "active",
        }
    ),
)
async def create_card(request: CardRequest) -> dict[str, object]:
    return {
        "card_id": "CARD-MOCK-001",
        "customer_id": request.customer_id,
        "card_type": request.card_type,
        "status": "active",
    }


@app.put(
    "/api/cards/{card_id}",
    tags=["Cards"],
    summary="Update a card",
    responses=ok(
        {
            "card_id": "CARD-MOCK-001",
            "customer_id": "CUST-1001",
            "card_type": "debit",
            "status": "active",
            "updated": True,
        }
    ),
)
async def update_card(card_id: str, request: CardRequest) -> dict[str, object]:
    return {
        "card_id": card_id,
        "customer_id": request.customer_id,
        "card_type": request.card_type,
        "status": "active",
        "updated": True,
    }


@app.delete(
    "/api/cards/{card_id}",
    tags=["Cards"],
    summary="Delete a card",
    responses=ok({"card_id": "CARD-MOCK-001", "deleted": True}),
)
async def delete_card(card_id: str) -> dict[str, object]:
    return {"card_id": card_id, "deleted": True}


@app.patch(
    "/api/cards/{card_id}/controls",
    tags=["Cards"],
    summary="Change a card's controls",
    description="Switches freeze, online use and international use. All three values must be sent.",
    responses=ok(
        {
            "card_id": "CARD-MOCK-001",
            "freeze": False,
            "online_enabled": True,
            "international_enabled": False,
            "updated": True,
        }
    ),
)
async def update_card_controls(
    card_id: str, request: CardControlsRequest
) -> dict[str, object]:
    return {
        "card_id": card_id,
        "freeze": request.freeze,
        "online_enabled": request.online_enabled,
        "international_enabled": request.international_enabled,
        "updated": True,
    }


# ---------------------------------------------------------------------------
# Loan Applications
# ---------------------------------------------------------------------------

class LoanApplicationRequest(StrictRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "customer_id": "CUST-1001",
                    "loan_type": "personal",
                    "amount": 5000.0,
                    "term_months": 36,
                }
            ]
        }
    )

    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    loan_type: Annotated[str, Field(min_length=1, max_length=40)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    term_months: Annotated[int, Field(gt=0, le=480)]


@app.post(
    "/api/loans/applications",
    tags=["Loans"],
    summary="Create a loan application",
    responses=ok(
        {
            "application_id": "LOAN-MOCK-001",
            "customer_id": "CUST-1001",
            "loan_type": "personal",
            "amount": 5000.0,
            "term_months": 36,
            "status": "received",
        }
    ),
)
async def create_loan_application(request: LoanApplicationRequest) -> dict[str, object]:
    return {
        "application_id": "LOAN-MOCK-001",
        "customer_id": request.customer_id,
        "loan_type": request.loan_type,
        "amount": request.amount,
        "term_months": request.term_months,
        "status": "received",
    }


@app.get(
    "/api/loans/applications/{application_id}",
    tags=["Loans"],
    summary="Get a loan application",
    responses=ok(
        {
            "application_id": "LOAN-MOCK-001",
            "customer_id": "CUST-1001",
            "loan_type": "personal",
            "amount": 63.4,
            "term_months": 36,
            "status": "received",
        }
    ),
)
async def get_loan_application(application_id: str) -> dict[str, object]:
    return {
        "application_id": application_id,
        "customer_id": "CUST-1001",
        "loan_type": "personal",
        "amount": 63.4,
        "term_months": 36,
        "status": "received",
    }


@app.put(
    "/api/loans/applications/{application_id}",
    tags=["Loans"],
    summary="Update a loan application",
    responses=ok(
        {
            "application_id": "LOAN-MOCK-001",
            "customer_id": "CUST-1001",
            "loan_type": "personal",
            "amount": 5000.0,
            "term_months": 36,
            "status": "updated",
            "updated": True,
        }
    ),
)
async def update_loan_application(
    application_id: str, request: LoanApplicationRequest
) -> dict[str, object]:
    return {
        "application_id": application_id,
        "customer_id": request.customer_id,
        "loan_type": request.loan_type,
        "amount": request.amount,
        "term_months": request.term_months,
        "status": "updated",
        "updated": True,
    }


@app.delete(
    "/api/loans/applications/{application_id}",
    tags=["Loans"],
    summary="Withdraw a loan application",
    description="An application is withdrawn, not removed, so the answer shows status \"withdrawn\".",
    responses=ok({"application_id": "LOAN-MOCK-001", "status": "withdrawn", "deleted": True}),
)
async def delete_loan_application(application_id: str) -> dict[str, object]:
    return {"application_id": application_id, "status": "withdrawn", "deleted": True}


# ---------------------------------------------------------------------------
# Legacy route, intentionally left untouched (excluded from CRUD expansion -
# see PTC-020 discussion)
# ---------------------------------------------------------------------------

@app.post(
    "/api/payment",
    tags=["Legacy"],
    summary="Create a payment (old route)",
    description="Old route kept so test case PTC-012 still works. New work should use "
    "`POST /api/payments`.",
    responses=ok({"accepted": True, "transaction_id": "TXN-9001", "amount": 45.25}),
)
async def create_mock_payment(request: PaymentRequest) -> dict[str, object]:
    """Legacy payment route retained for PTC-012 compatibility."""
    return {
        "accepted": True,
        "transaction_id": request.transaction_id,
        "amount": request.amount,
    }


__all__ = ["app"]