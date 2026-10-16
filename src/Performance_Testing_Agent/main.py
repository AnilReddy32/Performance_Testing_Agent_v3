from __future__ import annotations

import asyncio
import hmac
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from Performance_Testing_Agent.artifact_store import (
    artifact_retention_days,
    purge_expired_artifact_directories,
    resolve_registered_artifact,
)
from Performance_Testing_Agent.config import APP_NAME, APP_VERSION
from Performance_Testing_Agent.orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


async def _artifact_retention_worker() -> None:
    while True:
        await asyncio.sleep(3600)
        expired_jobs = await asyncio.to_thread(
            purge_expired_artifact_directories
        )
        if expired_jobs:
            logger.info("Purged %s expired artifact job directories.", len(expired_jobs))


@asynccontextmanager
async def lifespan(app: FastAPI):
    retention_days = artifact_retention_days()
    expired_jobs = await asyncio.to_thread(
        purge_expired_artifact_directories
    )
    if expired_jobs:
        logger.info("Purged %s expired artifact job directories.", len(expired_jobs))
    logger.info(
        "Artifact retention is configured for %s days; downloads require "
        "a bearer token of at least 32 characters.",
        retention_days,
    )
    cleanup_task = asyncio.create_task(_artifact_retention_worker())
    try:
        yield
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


#---------------------------------
# FastAPI Application
#---------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI Multi-Agent Performance Testing System",
    lifespan=lifespan,
)

#---------------------------- 
# Initialize Orchestrator
#----------------------------

orchestrator = Orchestrator()
 
#---------------------------- 
# Request Schema
#----------------------------

class UserQuery(BaseModel):
    query: str
 
#-------------------------
# Home Application
# ------------------------


@app.get("/")
async def home():
    return {
        "application": APP_NAME,
        "status": "Running",
        "version": APP_VERSION
    }
 
#Health check
@app.get("/health")
async def health():
    return{
        "status": "Healthy"
    } 

#main Endpoint

@app.post("/chat")
async def chat(request: UserQuery):
    """
    Accepts a user query and passes it to the Orchestrator.
    """
 
    try:
        result = await orchestrator.execute(request.query)
 
        return {
            "success": True,
            "data": result
        }
 
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
 
@app.get("/artifacts/{job_id}/{artifact_key}")
async def download_artifact(
    job_id: str,
    artifact_key: str,
    authorization: str | None = Header(default=None),
):
    configured_token = os.getenv("ARTIFACT_ACCESS_TOKEN", "")
    if len(configured_token) < 32:
        raise HTTPException(
            status_code=503,
            detail="Artifact downloads are disabled until a 32-character "
            "ARTIFACT_ACCESS_TOKEN is configured.",
        )
    scheme, separator, supplied_token = (authorization or "").partition(" ")
    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(
            supplied_token.encode("utf-8"),
            configured_token.encode("utf-8"),
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="A valid bearer token is required for artifact downloads.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        artifact_path, expires_at = resolve_registered_artifact(
            job_id,
            artifact_key,
        )
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Artifact not found.") from exc

    response = FileResponse(
        path=artifact_path,
        filename=Path(artifact_path).name,
    )
    response.headers["X-Artifact-Expires-At"] = expires_at.isoformat()
    response.headers["Cache-Control"] = "private, no-store"
    if (
        artifact_key == "native_report"
        and artifact_path.name == "index.html"
        and artifact_path.parent.name == "jmeter_native_report"
    ):
        return RedirectResponse(
            url=f"/artifacts/{job_id}/native_report/",
            status_code=307,
            headers={
                "X-Artifact-Expires-At": expires_at.isoformat(),
                "Cache-Control": "private, no-store",
            },
        )
    return response


@app.get("/artifacts/{job_id}/native_report/{asset_path:path}")
async def download_jmeter_dashboard_asset(
    job_id: str,
    asset_path: str,
    authorization: str | None = Header(default=None),
):
    """Serve JMeter's multi-file dashboard beneath its registered artifact."""
    configured_token = os.getenv("ARTIFACT_ACCESS_TOKEN", "")
    if len(configured_token) < 32:
        raise HTTPException(
            status_code=503,
            detail="Artifact downloads are disabled until a 32-character "
            "ARTIFACT_ACCESS_TOKEN is configured.",
        )
    scheme, separator, supplied_token = (authorization or "").partition(" ")
    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(
            supplied_token.encode("utf-8"), configured_token.encode("utf-8")
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="A valid bearer token is required for artifact downloads.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        registered_index, expires_at = resolve_registered_artifact(job_id, "native_report")
        if registered_index.name != "index.html" or registered_index.parent.name != "jmeter_native_report":
            raise FileNotFoundError("A JMeter dashboard is not registered for this job.")
        relative = Path(asset_path) if asset_path else Path("index.html")
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise FileNotFoundError("Dashboard asset not found.")
        dashboard_root = registered_index.parent.resolve()
        candidate = dashboard_root.joinpath(relative)
        resolved = candidate.resolve()
        if (
            not resolved.is_relative_to(dashboard_root)
            or not resolved.is_file()
            or any(
                dashboard_root.joinpath(*relative.parts[:index]).is_symlink()
                for index in range(1, len(relative.parts) + 1)
            )
        ):
            raise FileNotFoundError("Dashboard asset not found.")
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Artifact not found.") from exc

    response = FileResponse(path=resolved)
    response.headers["X-Artifact-Expires-At"] = expires_at.isoformat()
    response.headers["Cache-Control"] = "private, no-store"
    return response

 
 
if __name__ == "__main__":
    import uvicorn
    from Performance_Testing_Agent.config import HOST,PORT
 
    uvicorn.run(
        "Performance_Testing_Agent.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
