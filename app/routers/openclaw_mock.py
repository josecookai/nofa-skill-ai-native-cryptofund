from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/nofa/openclaw", tags=["nofa-openclaw-mock"])


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _masked_key(value: str) -> str:
    if len(value) <= 7:
        return value[:2] + "***"
    return f"{value[:4]}***{value[-4:]}"


def _error(status_code: int, message: str, code: int, request: Optional[Request] = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "message": message,
            "code": code,
            "request_id": getattr(getattr(request, "state", None), "request_id", None),
            "timestamp": _utc_now_iso(),
        },
    )


class RiskPayload(BaseModel):
    confidence: float
    risk_level: str


class AccountConnectRequest(BaseModel):
    user_id: str
    exchange: str
    api_key: str
    api_secret: str
    label: Optional[str] = None
    mode: str


class SuggestionRequest(BaseModel):
    suggestion_id: str
    user_id: str
    account_id: str
    mode: str
    exchange: str
    symbol: str
    action: str
    side: str
    quantity: float
    leverage: Optional[float] = None
    tp: Optional[float] = None
    sl: Optional[float] = None
    rationale: str
    expires_at: str
    risk: Optional[RiskPayload] = None


class ApprovalRequest(BaseModel):
    task_id: str
    suggestion_id: str
    decision: str
    approved_by: str
    channel: str
    decided_at: str
    message_id: Optional[str] = None
    raw_response_text: Optional[str] = None


class InMemoryTaskRepo:
    def __init__(self) -> None:
        self._lock = Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._suggestion_index: Dict[str, str] = {}

    def create_task(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            suggestion_id = suggestion["suggestion_id"]
            existing_task_id = self._suggestion_index.get(suggestion_id)
            if existing_task_id and existing_task_id in self._tasks:
                existing = self._tasks[existing_task_id]
                return {
                    "duplicate": True,
                    "task": {
                        "task_id": existing["task_id"],
                        "state": existing["state"],
                        "suggestion": existing["suggestion"],
                        "approval": existing["approval"],
                        "execution_result": existing["execution_result"],
                        "audit_events": list(existing["audit_events"]),
                    }
                }

            task_id = f"task_{uuid4().hex[:8]}"
            now = _utc_now_iso()
            task = {
                "task_id": task_id,
                "state": "pending_approval",
                "suggestion": suggestion,
                "approval": None,
                "execution_result": None,
                "audit_events": [
                    {
                        "time": now,
                        "type": "suggestion.generated",
                        "actor": "nofa-copilot",
                        "summary": "NOFA Copilot generated a trade suggestion.",
                    },
                    {
                        "time": now,
                        "type": "suggestion.delivered",
                        "actor": "adapter",
                        "summary": "Suggestion delivered to OpenClaw approval channel (mock).",
                    },
                ],
            }
            self._tasks[task_id] = task
            self._suggestion_index[suggestion_id] = task_id
            return {"duplicate": False, "task": task.copy()}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self._tasks.get(task_id)
            return None if task is None else {
                "task_id": task["task_id"],
                "state": task["state"],
                "suggestion": task["suggestion"],
                "approval": task["approval"],
                "execution_result": task["execution_result"],
                "audit_events": list(task["audit_events"]),
            }

    def apply_approval(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            task = self._tasks.get(payload["task_id"])
            if not task:
                raise KeyError("task_not_found")

            if payload["suggestion_id"] != task["suggestion"]["suggestion_id"]:
                raise ValueError("suggestion_mismatch")

            normalized = _normalize_decision(payload["decision"])
            if normalized == "needs_confirmation":
                raise RuntimeError("needs_confirmation")

            existing = task["approval"]
            if existing:
                same = all(existing.get(k) == payload.get(k) for k in payload.keys())
                if same:
                    return {"duplicate": True, "task": task}
                raise RuntimeError("duplicate_conflict")

            if task["state"] != "pending_approval":
                raise RuntimeError("invalid_state")

            approval = dict(payload)
            approval["decision"] = normalized
            task["approval"] = approval

            if normalized == "yes":
                task["state"] = "approved"
                task["audit_events"].append({
                    "time": _utc_now_iso(),
                    "type": "approval.accepted",
                    "actor": approval["approved_by"],
                    "summary": "Human approval received: yes.",
                })
                task["audit_events"].append({
                    "time": _utc_now_iso(),
                    "type": "execution.started",
                    "actor": "execution-simulator",
                    "summary": "Mock execution started.",
                })
                task["execution_result"] = {
                    "status": "success",
                    "mock_order_id": f"order_demo_{uuid4().hex[:6]}",
                    "message": "Mock execution completed. No live order was sent.",
                }
                task["state"] = "executed"
                task["audit_events"].append({
                    "time": _utc_now_iso(),
                    "type": "execution.completed",
                    "actor": "execution-simulator",
                    "summary": "Mock execution completed.",
                })
            else:
                task["state"] = "rejected"
                task["execution_result"] = {
                    "status": "canceled",
                    "message": "Execution canceled by human rejection.",
                }
                task["audit_events"].append({
                    "time": _utc_now_iso(),
                    "type": "approval.rejected",
                    "actor": approval["approved_by"],
                    "summary": "Human approval received: no.",
                })

            return {"duplicate": False, "task": task}


def _normalize_decision(decision: str) -> str:
    value = (decision or "").strip().lower()
    yes_values = {"yes", "y", "approve", "approved"}
    no_values = {"no", "n", "cancel", "reject"}
    if value in yes_values:
        return "yes"
    if value in no_values:
        return "no"
    return "needs_confirmation"


repo = InMemoryTaskRepo()


@router.post("/accounts")
async def connect_account(
    body: AccountConnectRequest,
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_nofa_signature: Optional[str] = Header(None, alias="X-NOFA-Signature"),
):
    _ = (x_request_id, x_nofa_signature)  # signature placeholder: header accepted but not enforced in mock
    return {
        "success": True,
        "data": {
            "account_id": f"acc_{body.exchange}_demo_{body.user_id}",
            "status": "connected_mock",
            "permissions_detected": ["trade", "read"],
            "masked_key": _masked_key(body.api_key),
        },
        "message": "OpenClaw connected to NOFA account (mock)",
    }


@router.post("/suggestions")
async def create_suggestion(
    body: SuggestionRequest,
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_nofa_signature: Optional[str] = Header(None, alias="X-NOFA-Signature"),
):
    _ = (request, x_request_id, x_nofa_signature)
    create_result = repo.create_task(body.dict())
    task = create_result["task"]
    is_duplicate = create_result["duplicate"]
    return {
        "success": True,
        "data": {
            "task_id": task["task_id"],
            "delivery_status": "sent_mock",
            "approval_status": task["state"] if task["state"] in {"pending_approval", "approved", "rejected", "executed"} else "pending_approval",
        },
        "message": "Suggestion delivered to OpenClaw approval channel (mock)" if not is_duplicate else "Duplicate suggestion ignored (idempotent)",
    }


@router.post("/approvals")
async def submit_approval(
    body: ApprovalRequest,
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_openclaw_signature: Optional[str] = Header(None, alias="X-OpenClaw-Signature"),
):
    _ = (x_request_id, x_openclaw_signature)
    try:
        result = repo.apply_approval(body.dict())
    except KeyError:
        raise _error(404, "Task not found", 40401, request)
    except ValueError:
        raise _error(403, "User/account or suggestion mismatch", 40301, request)
    except RuntimeError as exc:
        if str(exc) == "needs_confirmation":
            raise _error(422, "Unknown decision text, needs_confirmation", 42201, request)
        if str(exc) == "duplicate_conflict":
            raise _error(409, "Duplicate approval callback (conflict payload)", 40901, request)
        raise _error(409, "Task state does not accept approval", 40901, request)

    task = result["task"]
    if result["duplicate"]:
        # Safe idempotent replay: return current state instead of failing.
        if task["state"] == "rejected":
            return {
                "success": True,
                "data": {
                    "status": "accepted",
                    "next_state": "rejected",
                    "execution_status": "canceled",
                },
                "message": "Duplicate approval ignored (idempotent)",
            }
        return {
            "success": True,
            "data": {
                "status": "accepted",
                "next_state": "approved" if task["state"] != "executed" else "executed",
                "execution_status": "executing_mock" if task["state"] != "rejected" else "canceled",
            },
            "message": "Duplicate approval ignored (idempotent)",
        }

    decision = task["approval"]["decision"]
    if decision == "yes":
        return {
            "success": True,
            "data": {
                "status": "accepted",
                "next_state": "approved",
                "execution_status": "executing_mock",
            },
            "message": "Approval accepted",
        }

    return {
        "success": True,
        "data": {
            "status": "accepted",
            "next_state": "rejected",
            "execution_status": "canceled",
        },
        "message": "Rejection accepted",
    }


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_nofa_signature: Optional[str] = Header(None, alias="X-NOFA-Signature"),
):
    _ = (x_request_id, x_nofa_signature)
    task = repo.get_task(task_id)
    if not task:
        raise _error(404, "Task not found", 40401, request)

    return {
        "success": True,
        "data": task,
        "message": "Task fetched",
    }
