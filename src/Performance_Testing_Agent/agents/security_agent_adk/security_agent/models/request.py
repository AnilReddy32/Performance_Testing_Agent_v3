from pydantic import BaseModel, Field


class SecurityRequest(BaseModel):
    """
    Standard input contract for the Security Agent.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Security assessment request provided to the Security Agent."
    )