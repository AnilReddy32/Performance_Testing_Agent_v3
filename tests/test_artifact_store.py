import asyncio
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from Performance_Testing_Agent.artifact_store import (
    purge_expired_artifact_directories,
    resolve_registered_artifact,
    write_artifact_manifest,
)


class TestArtifactStore(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.environment = patch.dict(
            os.environ,
            {
                "EXECUTION_ARTIFACTS_ROOT": self.temporary_directory.name,
                "ARTIFACT_RETENTION_DAYS": "30",
                "ARTIFACT_ACCESS_TOKEN": "t" * 40,
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.job_id = "JOB-1234567890abcdef1234567890abcdef"
        self.job_directory = Path(self.temporary_directory.name) / self.job_id
        self.job_directory.mkdir()
        self.artifact = self.job_directory / "report.pdf"
        self.artifact.write_bytes(b"%PDF-test")
        self.now = datetime(2026, 10, 15, tzinfo=timezone.utc)

    def _write_manifest(self, created_at=None):
        return write_artifact_manifest(
            self.job_id,
            "REAL",
            {"consolidated_report": self.artifact.name},
            created_at=created_at or self.now,
        )

    def test_artifact_resolves_only_from_registered_manifest_until_expiry(self):
        manifest = self._write_manifest()

        artifact_path, expires_at = resolve_registered_artifact(
            self.job_id,
            "consolidated_report",
            now=self.now,
        )

        self.assertEqual(artifact_path, self.artifact.resolve())
        self.assertEqual(
            expires_at,
            datetime.fromisoformat(manifest["expires_at"]),
        )
        with self.assertRaises(FileNotFoundError):
            resolve_registered_artifact(
                self.job_id,
                "unregistered_file",
                now=self.now,
            )
        with self.assertRaises(ValueError):
            resolve_registered_artifact(
                self.job_id,
                "../report.pdf",
                now=self.now,
            )

    def test_expired_job_directory_is_purged_without_touching_other_directories(self):
        expired_at = self.now - timedelta(days=31)
        self._write_manifest(created_at=expired_at)
        other_job_id = "JOB-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        other_directory = (
            Path(self.temporary_directory.name) / other_job_id
        )
        other_directory.mkdir()
        (other_directory / "keep.txt").write_text("new", encoding="utf-8")
        non_job_directory = Path(self.temporary_directory.name) / "unrelated"
        non_job_directory.mkdir()

        purged = purge_expired_artifact_directories(now=self.now)

        self.assertEqual(purged, [self.job_id])
        self.assertFalse(self.job_directory.exists())
        self.assertTrue((other_directory / "keep.txt").is_file())
        self.assertTrue(non_job_directory.is_dir())

    def test_artifact_lookup_rejects_symlinked_job_directory(self):
        external_directory = Path(self.temporary_directory.name).parent / (
            f"{Path(self.temporary_directory.name).name}-external"
        )
        external_directory.mkdir()
        self.addCleanup(lambda: external_directory.rmdir())
        external_file = external_directory / "report.pdf"
        external_file.write_bytes(b"%PDF-external")
        self.addCleanup(external_file.unlink)

        self.artifact.unlink()
        self.job_directory.rmdir()
        self.job_directory.symlink_to(external_directory, target_is_directory=True)

        with self.assertRaises(ValueError):
            resolve_registered_artifact(
                self.job_id,
                "consolidated_report",
                now=self.now,
            )

    def test_api_artifact_download_requires_token_and_returns_registered_file(self):
        from fastapi import HTTPException

        from Performance_Testing_Agent.main import download_artifact

        self._write_manifest()
        with self.assertRaises(HTTPException) as unauthorized:
            asyncio.run(
                download_artifact(
                    self.job_id,
                    "consolidated_report",
                    "Bearer wrong-token",
                )
            )
        self.assertEqual(unauthorized.exception.status_code, 401)

        response = asyncio.run(
            download_artifact(
                self.job_id,
                "consolidated_report",
                f"Bearer {'t' * 40}",
            )
        )
        self.assertEqual(response.path, self.artifact.resolve())
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertIn("X-Artifact-Expires-At", response.headers)

    def test_orchestrator_returns_download_urls_for_registered_artifacts(self):
        from Performance_Testing_Agent.orchestrator.orchestrator import Orchestrator

        raw_results = self.job_directory / "raw.json"
        consolidated_report = self.job_directory / "report.pdf"
        raw_results.write_text("{}", encoding="utf-8")
        consolidated_report.write_bytes(b"%PDF-test")

        state = {
            "job_id": self.job_id,
            "execution_mode": "REAL",
            "execution_status": "completed",
            "execution_artifacts": {
                "job_id": self.job_id,
                "execution_mode": "REAL",
                "artifacts": {"raw_results": raw_results.name},
            },
            "report_result": {
                "artifacts": {"consolidated_report": consolidated_report.name},
            },
        }

        class FakeSessionService:
            async def create_session(self, **kwargs):
                return None

            async def get_session(self, **kwargs):
                return SimpleNamespace(state=state)

        class FakeRunner:
            async def run_async(self, **kwargs):
                if False:
                    yield None

        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.session_service = FakeSessionService()
        orchestrator.runner = FakeRunner()

        response = asyncio.run(
            orchestrator.execute(
                "Generate report",
                execution_context={
                    "execution_mode": "REAL",
                    "job_id": self.job_id,
                },
            )
        )
        execution_job = response["execution_job"]

        self.assertEqual(
            execution_job["artifacts"],
            {
                "raw_results": f"/artifacts/{self.job_id}/raw_results",
                "consolidated_report": (
                    f"/artifacts/{self.job_id}/consolidated_report"
                ),
            },
        )
        self.assertEqual(execution_job["artifact_retention_days"], 30)
        self.assertEqual(
            set(
                resolve_registered_artifact(self.job_id, key)[0].name
                for key in execution_job["artifacts"]
            ),
            {"raw.json", "report.pdf"},
        )


if __name__ == "__main__":
    unittest.main()
