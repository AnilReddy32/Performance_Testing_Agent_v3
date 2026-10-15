"""Local-only banking mock API used for safe performance-script validation."""

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(
    title="Local Performance Test Mock API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PaymentRequest(StrictRequest):
    transaction_id: Annotated[str, Field(min_length=1, max_length=128)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


class TransferRequest(StrictRequest):
    source_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    destination_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    reference: Annotated[str, Field(min_length=1, max_length=128)]


class BeneficiaryRequest(StrictRequest):
    account_id: Annotated[str, Field(min_length=1, max_length=32)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    nickname: Annotated[str, Field(min_length=1, max_length=50)]


class CardControlsRequest(StrictRequest):
    freeze: bool
    online_enabled: bool
    international_enabled: bool


class LoanApplicationRequest(StrictRequest):
    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    loan_type: Annotated[str, Field(min_length=1, max_length=40)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    term_months: Annotated[int, Field(gt=0, le=480)]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str) -> dict[str, object]:
    return {
        "customer_id": customer_id,
        "name": "Alex Morgan",
        "status": "active",
        "segment": "retail",
    }


@app.get("/api/accounts/{account_id}")
async def get_account(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "customer_id": "CUST-1001",
        "account_type": "checking",
        "currency": "USD",
        "status": "open",
    }


@app.get("/api/accounts/{account_id}/balance")
async def get_account_balance(account_id: str) -> dict[str, object]:
    return {"account_id": account_id, "currency": "USD", "available_balance": 1250.75}


@app.get("/api/accounts/{account_id}/transactions")
async def get_transactions(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "transactions": [
            {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
            {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
        ],
    }


@app.post("/api/payments")
async def create_payment(request: PaymentRequest) -> dict[str, object]:
    return {
        "accepted": True,
        "payment_id": "PAY-MOCK-001",
        "transaction_id": request.transaction_id,
        "amount": request.amount,
        "status": "accepted",
    }


@app.post("/api/transfers")
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


@app.post("/api/beneficiaries")
async def create_beneficiary(request: BeneficiaryRequest) -> dict[str, object]:
    return {
        "beneficiary_id": "BEN-MOCK-001",
        "account_id": request.account_id,
        "name": request.name,
        "nickname": request.nickname,
        "status": "active",
    }


@app.get("/api/cards/{card_id}")
async def get_card(card_id: str) -> dict[str, object]:
    return {
        "card_id": card_id,
        "customer_id": "CUST-1001",
        "card_type": "debit",
        "status": "active",
        "currency": "USD",
    }


@app.patch("/api/cards/{card_id}/controls")
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


@app.post("/api/loans/applications")
async def create_loan_application(request: LoanApplicationRequest) -> dict[str, object]:
    return {
        "application_id": "LOAN-MOCK-001",
        "customer_id": request.customer_id,
        "loan_type": request.loan_type,
        "amount": request.amount,
        "term_months": request.term_months,
        "status": "received",
    }


@app.get("/api/accounts/{account_id}/statements")
async def get_statements(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "statements": [
            {"statement_id": "STMT-2026-09", "period": "2026-09", "status": "ready"}
        ],
    }


@app.post("/api/payment")
async def create_mock_payment(request: PaymentRequest) -> dict[str, object]:
    """Legacy payment route retained for PTC-012 compatibility."""
    return {
        "accepted": True,
        "transaction_id": request.transaction_id,
        "amount": request.amount,
    }


__all__ = ["app"]
