"""Local-only banking mock API used for safe performance-script validation."""

from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(
    title="Local Performance Test Mock API",
)


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

class CustomerRequest(StrictRequest):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    segment: Annotated[str, Field(min_length=1, max_length=40)] = "retail"


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


@app.post("/api/customers")
async def create_customer(request: CustomerRequest) -> dict[str, object]:
    return {
        "customer_id": "CUST-MOCK-001",
        "name": request.name,
        "segment": request.segment,
        "status": "active",
    }


@app.put("/api/customers/{customer_id}")
async def update_customer(customer_id: str, request: CustomerRequest) -> dict[str, object]:
    return {
        "customer_id": customer_id,
        "name": request.name,
        "segment": request.segment,
        "status": "active",
        "updated": True,
    }


@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str) -> dict[str, object]:
    return {"customer_id": customer_id, "deleted": True}


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

class AccountRequest(StrictRequest):
    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    account_type: Annotated[str, Field(min_length=1, max_length=20)] = "checking"
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"


@app.get("/api/accounts/{account_id}")
async def get_account(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "customer_id": "CUST-1001",
        "account_type": "checking",
        "currency": "USD",
        "status": "open",
    }


@app.post("/api/accounts")
async def create_account(request: AccountRequest) -> dict[str, object]:
    return {
        "account_id": "ACCT-MOCK-001",
        "customer_id": request.customer_id,
        "account_type": request.account_type,
        "currency": request.currency,
        "status": "open",
    }


@app.put("/api/accounts/{account_id}")
async def update_account(account_id: str, request: AccountRequest) -> dict[str, object]:
    return {
        "account_id": account_id,
        "customer_id": request.customer_id,
        "account_type": request.account_type,
        "currency": request.currency,
        "status": "open",
        "updated": True,
    }


@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: str) -> dict[str, object]:
    return {"account_id": account_id, "deleted": True}


@app.get("/api/accounts/{account_id}/balance")
async def get_account_balance(account_id: str) -> dict[str, object]:
    return {"account_id": account_id, "currency": "USD", "available_balance": 1250.75}


# Transactions: Create added (append a new transaction); intentionally no
# PUT/DELETE - real financial transaction records are immutable/append-only
# once created, even in a mock.

class TransactionRequest(StrictRequest):
    amount: Annotated[float, Field(allow_inf_nan=False)]
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"


@app.get("/api/accounts/{account_id}/transactions")
async def get_transactions(account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "transactions": [
            {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
            {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
        ],
    }


@app.post("/api/accounts/{account_id}/transactions")
async def create_transaction(account_id: str, request: TransactionRequest) -> dict[str, object]:
    return {
        "account_id": account_id,
        "transaction_id": "TXN-MOCK-001",
        "amount": request.amount,
        "currency": request.currency,
        "status": "posted",
    }


@app.get("/api/accounts/{account_id}/statements")
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
    transaction_id: Annotated[str, Field(min_length=1, max_length=128)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


@app.post("/api/payments")
async def create_payment(request: PaymentRequest) -> dict[str, object]:
    return {
        "accepted": True,
        "payment_id": "PAY-MOCK-001",
        "transaction_id": request.transaction_id,
        "amount": request.amount,
        "status": "accepted",
    }


@app.get("/api/payments/{payment_id}")
async def get_payment(payment_id: str) -> dict[str, object]:
    return {
        "payment_id": payment_id,
        "transaction_id": "TXN-MOCK-001",
        "amount": 45.25,
        "status": "accepted",
    }


@app.put("/api/payments/{payment_id}")
async def update_payment(payment_id: str, request: PaymentRequest) -> dict[str, object]:
    return {
        "payment_id": payment_id,
        "transaction_id": request.transaction_id,
        "amount": request.amount,
        "status": "updated",
        "updated": True,
    }


@app.delete("/api/payments/{payment_id}")
async def delete_payment(payment_id: str) -> dict[str, object]:
    return {"payment_id": payment_id, "status": "cancelled", "deleted": True}


# ---------------------------------------------------------------------------
# Transfers
# ---------------------------------------------------------------------------

class TransferRequest(StrictRequest):
    source_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    destination_account_id: Annotated[str, Field(min_length=1, max_length=32)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    reference: Annotated[str, Field(min_length=1, max_length=128)]


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


@app.get("/api/transfers/{transfer_id}")
async def get_transfer(transfer_id: str) -> dict[str, object]:
    return {
        "transfer_id": transfer_id,
        "source_account_id": "ACCT-2001",
        "destination_account_id": "ACCT-2002",
        "amount": 7.5,
        "status": "accepted",
    }


@app.put("/api/transfers/{transfer_id}")
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


@app.delete("/api/transfers/{transfer_id}")
async def delete_transfer(transfer_id: str) -> dict[str, object]:
    return {"transfer_id": transfer_id, "status": "cancelled", "deleted": True}


# ---------------------------------------------------------------------------
# Beneficiaries
# ---------------------------------------------------------------------------

class BeneficiaryRequest(StrictRequest):
    account_id: Annotated[str, Field(min_length=1, max_length=32)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    nickname: Annotated[str, Field(min_length=1, max_length=50)]


@app.post("/api/beneficiaries")
async def create_beneficiary(request: BeneficiaryRequest) -> dict[str, object]:
    return {
        "beneficiary_id": "BEN-MOCK-001",
        "account_id": request.account_id,
        "name": request.name,
        "nickname": request.nickname,
        "status": "active",
    }


@app.get("/api/beneficiaries/{beneficiary_id}")
async def get_beneficiary(beneficiary_id: str) -> dict[str, object]:
    return {
        "beneficiary_id": beneficiary_id,
        "account_id": "ACCT-2001",
        "name": "Alex Morgan",
        "nickname": "alex",
        "status": "active",
    }


@app.put("/api/beneficiaries/{beneficiary_id}")
async def update_beneficiary(beneficiary_id: str, request: BeneficiaryRequest) -> dict[str, object]:
    return {
        "beneficiary_id": beneficiary_id,
        "account_id": request.account_id,
        "name": request.name,
        "nickname": request.nickname,
        "status": "active",
        "updated": True,
    }


@app.delete("/api/beneficiaries/{beneficiary_id}")
async def delete_beneficiary(beneficiary_id: str) -> dict[str, object]:
    return {"beneficiary_id": beneficiary_id, "deleted": True}


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

class CardRequest(StrictRequest):
    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    card_type: Annotated[str, Field(min_length=1, max_length=20)] = "debit"


class CardControlsRequest(StrictRequest):
    freeze: bool
    online_enabled: bool
    international_enabled: bool


@app.get("/api/cards/{card_id}")
async def get_card(card_id: str) -> dict[str, object]:
    return {
        "card_id": card_id,
        "customer_id": "CUST-1001",
        "card_type": "debit",
        "status": "active",
        "currency": "USD",
    }


@app.post("/api/cards")
async def create_card(request: CardRequest) -> dict[str, object]:
    return {
        "card_id": "CARD-MOCK-001",
        "customer_id": request.customer_id,
        "card_type": request.card_type,
        "status": "active",
    }


@app.put("/api/cards/{card_id}")
async def update_card(card_id: str, request: CardRequest) -> dict[str, object]:
    return {
        "card_id": card_id,
        "customer_id": request.customer_id,
        "card_type": request.card_type,
        "status": "active",
        "updated": True,
    }


@app.delete("/api/cards/{card_id}")
async def delete_card(card_id: str) -> dict[str, object]:
    return {"card_id": card_id, "deleted": True}


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


# ---------------------------------------------------------------------------
# Loan Applications
# ---------------------------------------------------------------------------

class LoanApplicationRequest(StrictRequest):
    customer_id: Annotated[str, Field(min_length=1, max_length=32)]
    loan_type: Annotated[str, Field(min_length=1, max_length=40)]
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    term_months: Annotated[int, Field(gt=0, le=480)]


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


@app.get("/api/loans/applications/{application_id}")
async def get_loan_application(application_id: str) -> dict[str, object]:
    return {
        "application_id": application_id,
        "customer_id": "CUST-1001",
        "loan_type": "personal",
        "amount": 63.4,
        "term_months": 36,
        "status": "received",
    }


@app.put("/api/loans/applications/{application_id}")
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


@app.delete("/api/loans/applications/{application_id}")
async def delete_loan_application(application_id: str) -> dict[str, object]:
    return {"application_id": application_id, "status": "withdrawn", "deleted": True}


# ---------------------------------------------------------------------------
# Legacy route, intentionally left untouched (excluded from CRUD expansion -
# see PTC-020 discussion)
# ---------------------------------------------------------------------------

@app.post("/api/payment")
async def create_mock_payment(request: PaymentRequest) -> dict[str, object]:
    """Legacy payment route retained for PTC-012 compatibility."""
    return {
        "accepted": True,
        "transaction_id": request.transaction_id,
        "amount": request.amount,
    }


__all__ = ["app"]














# """Local-only banking mock API used for safe performance-script validation."""

# from typing import Annotated

# from fastapi import FastAPI
# from pydantic import BaseModel, ConfigDict, Field


# app = FastAPI(
#     title="Local Performance Test Mock API",
# )


# class StrictRequest(BaseModel):
#     model_config = ConfigDict(extra="forbid", strict=True)


# class PaymentRequest(StrictRequest):
#     transaction_id: Annotated[str, Field(min_length=1, max_length=128)]
#     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


# class TransferRequest(StrictRequest):
#     source_account_id: Annotated[str, Field(min_length=1, max_length=32)]
#     destination_account_id: Annotated[str, Field(min_length=1, max_length=32)]
#     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
#     reference: Annotated[str, Field(min_length=1, max_length=128)]


# class BeneficiaryRequest(StrictRequest):
#     account_id: Annotated[str, Field(min_length=1, max_length=32)]
#     name: Annotated[str, Field(min_length=1, max_length=100)]
#     nickname: Annotated[str, Field(min_length=1, max_length=50)]


# class CardControlsRequest(StrictRequest):
#     freeze: bool
#     online_enabled: bool
#     international_enabled: bool


# class LoanApplicationRequest(StrictRequest):
#     customer_id: Annotated[str, Field(min_length=1, max_length=32)]
#     loan_type: Annotated[str, Field(min_length=1, max_length=40)]
#     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
#     term_months: Annotated[int, Field(gt=0, le=480)]


# @app.get("/health")
# async def health() -> dict[str, str]:
#     return {"status": "healthy"}


# @app.get("/api/customers/{customer_id}")
# async def get_customer(customer_id: str) -> dict[str, object]:
#     return {
#         "customer_id": customer_id,
#         "name": "Alex Morgan",
#         "status": "active",
#         "segment": "retail",
#     }


# @app.get("/api/accounts/{account_id}")
# async def get_account(account_id: str) -> dict[str, object]:
#     return {
#         "account_id": account_id,
#         "customer_id": "CUST-1001",
#         "account_type": "checking",
#         "currency": "USD",
#         "status": "open",
#     }


# @app.get("/api/accounts/{account_id}/balance")
# async def get_account_balance(account_id: str) -> dict[str, object]:
#     return {"account_id": account_id, "currency": "USD", "available_balance": 1250.75}


# @app.get("/api/accounts/{account_id}/transactions")
# async def get_transactions(account_id: str) -> dict[str, object]:
#     return {
#         "account_id": account_id,
#         "transactions": [
#             {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
#             {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
#         ],
#     }


# @app.post("/api/payments")
# async def create_payment(request: PaymentRequest) -> dict[str, object]:
#     return {
#         "accepted": True,
#         "payment_id": "PAY-MOCK-001",
#         "transaction_id": request.transaction_id,
#         "amount": request.amount,
#         "status": "accepted",
#     }


# @app.post("/api/transfers")
# async def create_transfer(request: TransferRequest) -> dict[str, object]:
#     return {
#         "accepted": True,
#         "transfer_id": "TRF-MOCK-001",
#         "source_account_id": request.source_account_id,
#         "destination_account_id": request.destination_account_id,
#         "amount": request.amount,
#         "reference": request.reference,
#         "status": "accepted",
#     }


# @app.post("/api/beneficiaries")
# async def create_beneficiary(request: BeneficiaryRequest) -> dict[str, object]:
#     return {
#         "beneficiary_id": "BEN-MOCK-001",
#         "account_id": request.account_id,
#         "name": request.name,
#         "nickname": request.nickname,
#         "status": "active",
#     }


# @app.get("/api/cards/{card_id}")
# async def get_card(card_id: str) -> dict[str, object]:
#     return {
#         "card_id": card_id,
#         "customer_id": "CUST-1001",
#         "card_type": "debit",
#         "status": "active",
#         "currency": "USD",
#     }


# @app.patch("/api/cards/{card_id}/controls")
# async def update_card_controls(
#     card_id: str, request: CardControlsRequest
# ) -> dict[str, object]:
#     return {
#         "card_id": card_id,
#         "freeze": request.freeze,
#         "online_enabled": request.online_enabled,
#         "international_enabled": request.international_enabled,
#         "updated": True,
#     }


# @app.post("/api/loans/applications")
# async def create_loan_application(request: LoanApplicationRequest) -> dict[str, object]:
#     return {
#         "application_id": "LOAN-MOCK-001",
#         "customer_id": request.customer_id,
#         "loan_type": request.loan_type,
#         "amount": request.amount,
#         "term_months": request.term_months,
#         "status": "received",
#     }


# @app.get("/api/accounts/{account_id}/statements")
# async def get_statements(account_id: str) -> dict[str, object]:
#     return {
#         "account_id": account_id,
#         "statements": [
#             {"statement_id": "STMT-2026-09", "period": "2026-09", "status": "ready"}
#         ],
#     }


# @app.post("/api/payment")
# async def create_mock_payment(request: PaymentRequest) -> dict[str, object]:
#     """Legacy payment route retained for PTC-012 compatibility."""
#     return {
#         "accepted": True,
#         "transaction_id": request.transaction_id,
#         "amount": request.amount,
#     }


# __all__ = ["app"]











# # """Local-only banking mock API used for safe performance-script validation."""

# # from typing import Annotated

# # from fastapi import FastAPI
# # from pydantic import BaseModel, ConfigDict, Field


# # app = FastAPI(
# #     title="Local Performance Test Mock API",
# #     docs_url=None,
# #     redoc_url=None,
# #     openapi_url=None,
# # )


# # class StrictRequest(BaseModel):
# #     model_config = ConfigDict(extra="forbid", strict=True)


# # class PaymentRequest(StrictRequest):
# #     transaction_id: Annotated[str, Field(min_length=1, max_length=128)]
# #     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


# # class TransferRequest(StrictRequest):
# #     source_account_id: Annotated[str, Field(min_length=1, max_length=32)]
# #     destination_account_id: Annotated[str, Field(min_length=1, max_length=32)]
# #     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
# #     reference: Annotated[str, Field(min_length=1, max_length=128)]


# # class BeneficiaryRequest(StrictRequest):
# #     account_id: Annotated[str, Field(min_length=1, max_length=32)]
# #     name: Annotated[str, Field(min_length=1, max_length=100)]
# #     nickname: Annotated[str, Field(min_length=1, max_length=50)]


# # class CardControlsRequest(StrictRequest):
# #     freeze: bool
# #     online_enabled: bool
# #     international_enabled: bool


# # class LoanApplicationRequest(StrictRequest):
# #     customer_id: Annotated[str, Field(min_length=1, max_length=32)]
# #     loan_type: Annotated[str, Field(min_length=1, max_length=40)]
# #     amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]
# #     term_months: Annotated[int, Field(gt=0, le=480)]


# # @app.get("/health")
# # async def health() -> dict[str, str]:
# #     return {"status": "healthy"}


# # @app.get("/api/customers/{customer_id}")
# # async def get_customer(customer_id: str) -> dict[str, object]:
# #     return {
# #         "customer_id": customer_id,
# #         "name": "Alex Morgan",
# #         "status": "active",
# #         "segment": "retail",
# #     }


# # @app.get("/api/accounts/{account_id}")
# # async def get_account(account_id: str) -> dict[str, object]:
# #     return {
# #         "account_id": account_id,
# #         "customer_id": "CUST-1001",
# #         "account_type": "checking",
# #         "currency": "USD",
# #         "status": "open",
# #     }


# # @app.get("/api/accounts/{account_id}/balance")
# # async def get_account_balance(account_id: str) -> dict[str, object]:
# #     return {"account_id": account_id, "currency": "USD", "available_balance": 1250.75}


# # @app.get("/api/accounts/{account_id}/transactions")
# # async def get_transactions(account_id: str) -> dict[str, object]:
# #     return {
# #         "account_id": account_id,
# #         "transactions": [
# #             {"transaction_id": "TXN-9001", "amount": -25.0, "currency": "USD"},
# #             {"transaction_id": "TXN-9002", "amount": 100.0, "currency": "USD"},
# #         ],
# #     }


# # @app.post("/api/payments")
# # async def create_payment(request: PaymentRequest) -> dict[str, object]:
# #     return {
# #         "accepted": True,
# #         "payment_id": "PAY-MOCK-001",
# #         "transaction_id": request.transaction_id,
# #         "amount": request.amount,
# #         "status": "accepted",
# #     }


# # @app.post("/api/transfers")
# # async def create_transfer(request: TransferRequest) -> dict[str, object]:
# #     return {
# #         "accepted": True,
# #         "transfer_id": "TRF-MOCK-001",
# #         "source_account_id": request.source_account_id,
# #         "destination_account_id": request.destination_account_id,
# #         "amount": request.amount,
# #         "reference": request.reference,
# #         "status": "accepted",
# #     }


# # @app.post("/api/beneficiaries")
# # async def create_beneficiary(request: BeneficiaryRequest) -> dict[str, object]:
# #     return {
# #         "beneficiary_id": "BEN-MOCK-001",
# #         "account_id": request.account_id,
# #         "name": request.name,
# #         "nickname": request.nickname,
# #         "status": "active",
# #     }


# # @app.get("/api/cards/{card_id}")
# # async def get_card(card_id: str) -> dict[str, object]:
# #     return {
# #         "card_id": card_id,
# #         "customer_id": "CUST-1001",
# #         "card_type": "debit",
# #         "status": "active",
# #         "currency": "USD",
# #     }


# # @app.patch("/api/cards/{card_id}/controls")
# # async def update_card_controls(
# #     card_id: str, request: CardControlsRequest
# # ) -> dict[str, object]:
# #     return {
# #         "card_id": card_id,
# #         "freeze": request.freeze,
# #         "online_enabled": request.online_enabled,
# #         "international_enabled": request.international_enabled,
# #         "updated": True,
# #     }


# # @app.post("/api/loans/applications")
# # async def create_loan_application(request: LoanApplicationRequest) -> dict[str, object]:
# #     return {
# #         "application_id": "LOAN-MOCK-001",
# #         "customer_id": request.customer_id,
# #         "loan_type": request.loan_type,
# #         "amount": request.amount,
# #         "term_months": request.term_months,
# #         "status": "received",
# #     }


# # @app.get("/api/accounts/{account_id}/statements")
# # async def get_statements(account_id: str) -> dict[str, object]:
# #     return {
# #         "account_id": account_id,
# #         "statements": [
# #             {"statement_id": "STMT-2026-09", "period": "2026-09", "status": "ready"}
# #         ],
# #     }


# # @app.post("/api/payment")
# # async def create_mock_payment(request: PaymentRequest) -> dict[str, object]:
# #     """Legacy payment route retained for PTC-012 compatibility."""
# #     return {
# #         "accepted": True,
# #         "transaction_id": request.transaction_id,
# #         "amount": request.amount,
# #     }


# # __all__ = ["app"]
