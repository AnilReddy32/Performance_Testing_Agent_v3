"""Shared Swagger / OpenAPI settings for the project's FastAPI apps.

Every app (main API, Jira API, mock API) takes its "show the docs pages or not"
setting from here, so there is one switch and one set of common error texts.

Switch the interactive docs off (for example outside development) with:

    ENABLE_API_DOCS=false
"""

import os

_OFF_VALUES = {"false", "0", "no", "off"}


def docs_enabled() -> bool:
    """Swagger is ON unless ENABLE_API_DOCS is set to false, 0, no or off."""
    return os.getenv("ENABLE_API_DOCS", "true").strip().lower() not in _OFF_VALUES


def docs_urls() -> dict:
    """Keyword arguments for FastAPI(...) that show or hide the docs pages.

    Usage:  app = FastAPI(title="...", **docs_urls())
    """
    if docs_enabled():
        return {
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json",
        }
    return {"docs_url": None, "redoc_url": None, "openapi_url": None}


def ok(example: dict) -> dict:
    """Show `example` as the sample answer (HTTP 200) of an endpoint in Swagger.

    It only changes the documentation. It never changes what the endpoint returns.

    Usage:  @app.get("/x", responses=ok({"id": "1"}))
    """
    return {200: {"content": {"application/json": {"example": example}}}}


# Ready-made error descriptions for the `responses=` argument of an endpoint.
# They keep the wording identical across all three APIs. Example:
#
#     @router.get("/items/{item_id}", responses={404: ERROR_RESPONSES[404]})
ERROR_RESPONSES = {
    401: {"description": "Missing or invalid credentials."},
    404: {"description": "The requested item was not found."},
    409: {"description": "The request conflicts with the current state, for example a duplicate."},
    410: {"description": "The item has expired and was removed."},
    422: {"description": "The request could not be understood, for example no matching test case."},
    500: {"description": "Unexpected server error."},
    503: {"description": "The service is not configured or not available."},
}