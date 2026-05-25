from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEVTOOLS_JSON_PATH = (
    PROJECT_ROOT / ".well-known" / "appspecific" / "com.chrome.devtools.json"
)
DEVTOOLS_URL_PATH = "/.well-known/appspecific/com.chrome.devtools.json"
_WORKSPACE_NAMESPACE = uuid.UUID("822f7bc5-aa31-4b9f-9c14-df23d95578a1")

router = APIRouter(include_in_schema=False)


def devtools_workspace_payload() -> dict[str, dict[str, str]]:
    root = str(PROJECT_ROOT)
    return {
        "workspace": {
            "root": root,
            "uuid": str(uuid.uuid5(_WORKSPACE_NAMESPACE, root)),
        }
    }


def ensure_devtools_json() -> None:
    """Write com.chrome.devtools.json for local Chrome DevTools workspace discovery."""
    payload = devtools_workspace_payload()
    DEVTOOLS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEVTOOLS_JSON_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


@router.get(DEVTOOLS_URL_PATH)
async def chrome_devtools_json() -> dict[str, dict[str, str]]:
    return devtools_workspace_payload()
