from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
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


class SkillOpportunityRequest(BaseModel):
    pair: str
    action: str
    qty: float
    lev: str
    rationale: Optional[str] = None
    source: Optional[str] = "NOFA Trading Opportunity"
    requested_by: Optional[str] = "nofa-admin"


class SkillDecisionRequest(BaseModel):
    user_id: str
    decision: str  # yes / no
    channel: str = "openclaw_chat"
    raw_text: Optional[str] = None


class InMemoryTaskRepo:
    def __init__(self) -> None:
        self._lock = Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._suggestion_index: Dict[str, str] = {}
        self._skill_opportunities: Dict[str, Dict[str, Any]] = {}
        self._skill_order: List[str] = []
        self._skill_decisions: List[Dict[str, Any]] = []

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

    def create_skill_opportunity(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            opp_id = f"opp_{uuid4().hex[:8]}"
            now = _utc_now_iso()
            item = {
                "id": opp_id,
                "title": payload.get("source") or "NOFA Trading Opportunity",
                "pair": payload["pair"],
                "action": payload["action"].upper(),
                "qty": payload["qty"],
                "lev": payload["lev"],
                "rationale": payload.get("rationale"),
                "status": "pending_human",
                "created_at": now,
                "requested_by": payload.get("requested_by", "nofa-admin"),
                "decision": None,
            }
            self._skill_opportunities[opp_id] = item
            self._skill_order.insert(0, opp_id)
            return item.copy()

    def list_skill_opportunities(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self._skill_opportunities[i].copy() for i in self._skill_order if i in self._skill_opportunities]

    def get_next_pending_opportunity(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            for opp_id in self._skill_order:
                item = self._skill_opportunities.get(opp_id)
                if item and item["status"] == "pending_human":
                    return item.copy()
            return None

    def apply_skill_decision(self, opp_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            item = self._skill_opportunities.get(opp_id)
            if not item:
                raise KeyError("opportunity_not_found")

            normalized = _normalize_decision(payload["decision"])
            if normalized == "needs_confirmation":
                raise RuntimeError("needs_confirmation")

            if item["status"] != "pending_human":
                existing = item.get("decision")
                if existing and existing.get("decision") == normalized and existing.get("user_id") == payload["user_id"]:
                    return {"duplicate": True, "item": item.copy()}
                raise RuntimeError("invalid_state")

            decision_record = {
                "opportunity_id": opp_id,
                "user_id": payload["user_id"],
                "decision": normalized,
                "channel": payload.get("channel", "openclaw_chat"),
                "raw_text": payload.get("raw_text"),
                "decided_at": _utc_now_iso(),
            }
            item["decision"] = decision_record
            item["status"] = "approved" if normalized == "yes" else "rejected"
            self._skill_decisions.insert(0, decision_record)
            return {"duplicate": False, "item": item.copy()}

    def list_skill_decisions(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [d.copy() for d in self._skill_decisions]

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


@router.post("/skill/opportunities")
async def create_skill_opportunity(
    body: SkillOpportunityRequest,
    x_nofa_signature: Optional[str] = Header(None, alias="X-NOFA-Signature"),
):
    _ = x_nofa_signature
    item = repo.create_skill_opportunity(body.dict())
    return {
        "success": True,
        "data": item,
        "message": "NOFA Trading Opportunity created for OpenClaw",
    }


@router.get("/skill/opportunities")
async def list_skill_opportunities():
    return {
        "success": True,
        "data": repo.list_skill_opportunities(),
        "message": "Opportunity list fetched",
    }


@router.get("/skill/opportunities/next")
async def get_next_skill_opportunity():
    item = repo.get_next_pending_opportunity()
    return {
        "success": True,
        "data": item,
        "message": "Next pending opportunity fetched" if item else "No pending opportunity",
    }


@router.post("/skill/opportunities/{opportunity_id}/decision")
async def submit_skill_decision(
    opportunity_id: str,
    body: SkillDecisionRequest,
    request: Request,
    x_openclaw_signature: Optional[str] = Header(None, alias="X-OpenClaw-Signature"),
):
    _ = x_openclaw_signature
    try:
        result = repo.apply_skill_decision(opportunity_id, body.dict())
    except KeyError:
        raise _error(404, "Opportunity not found", 40411, request)
    except RuntimeError as exc:
        if str(exc) == "needs_confirmation":
            raise _error(422, "Unknown decision text, needs_confirmation", 42211, request)
        raise _error(409, "Opportunity does not accept decision in current state", 40911, request)

    item = result["item"]
    return {
        "success": True,
        "data": {
            "opportunity_id": item["id"],
            "status": item["status"],
            "decision": item["decision"],
            "duplicate": result["duplicate"],
        },
        "message": "Decision recorded",
    }


@router.get("/skill/decisions")
async def list_skill_decisions():
    return {
        "success": True,
        "data": repo.list_skill_decisions(),
        "message": "Decision log fetched",
    }


@router.get("/skill/admin", response_class=HTMLResponse)
async def skill_admin_console():
    # Lightweight admin console to inspect human yes/no decisions without adding frontend build steps.
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NOFA Skill Admin Console</title>
  <style>
    body { font-family: ui-sans-serif, system-ui; background:#0b0b0c; color:#f2efe8; margin:0; }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 20px; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .card { background:#121216; border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:14px; }
    h1,h2 { margin:0 0 10px; }
    h1 { font-size:22px; }
    h2 { font-size:16px; color:#f5d28f; }
    .row { display:flex; justify-content:space-between; gap:8px; margin:8px 0; color:#c5c0b1; }
    .pill { border:1px solid rgba(255,255,255,.12); border-radius:999px; padding:2px 8px; font-size:12px; }
    .yes { color:#55d88a; } .no { color:#ff7a7a; } .pending { color:#f5d28f; }
    button { background:#f5ad22; color:#17120a; border:0; border-radius:8px; padding:8px 10px; cursor:pointer; font-weight:700; }
    .muted { color:#a49d8d; font-size:13px; }
    code { color:#f5d28f; }
    pre { white-space:pre-wrap; background:#0d0d10; border:1px solid rgba(255,255,255,.06); border-radius:8px; padding:8px; overflow:auto; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>NOFA Skill Admin Console</h1>
    <p class="muted">Tracks NOFA Trading Opportunity items and human yes/no decisions submitted from OpenClaw via REST API.</p>
    <div class="grid">
      <div class="card">
        <h2>Pending / Recent Opportunities</h2>
        <div id="opps" class="muted">Loading...</div>
      </div>
      <div class="card">
        <h2>Human Decisions (Yes / No)</h2>
        <div id="decisions" class="muted">Loading...</div>
      </div>
    </div>
    <div class="card" style="margin-top:12px;">
      <h2>REST API Quick Start</h2>
      <pre>POST /api/nofa/openclaw/skill/opportunities
{
  "pair": "BTCUSDT",
  "action": "BUY",
  "qty": 0.1,
  "lev": "8x",
  "rationale": "MACD reversal with bullish funding rate"
}

GET  /api/nofa/openclaw/skill/opportunities/next
POST /api/nofa/openclaw/skill/opportunities/{id}/decision {"user_id":"alice","decision":"yes"}</pre>
    </div>
  </div>
  <script>
    async function load() {
      const [oppsRes, decRes] = await Promise.all([
        fetch('/api/nofa/openclaw/skill/opportunities'),
        fetch('/api/nofa/openclaw/skill/decisions')
      ]);
      const opps = await oppsRes.json();
      const decs = await decRes.json();

      const oppWrap = document.getElementById('opps');
      const decWrap = document.getElementById('decisions');

      const oppItems = (opps.data || []).slice(0, 20);
      if (!oppItems.length) {
        oppWrap.innerHTML = '<div class="muted">No opportunities yet</div>';
      } else {
        oppWrap.innerHTML = oppItems.map(o => `
          <div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05);">
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">
              <strong>${o.title}</strong>
              <span class="pill ${o.status === 'approved' ? 'yes' : (o.status === 'rejected' ? 'no' : 'pending')}">${o.status}</span>
            </div>
            <div class="row"><span>Pair</span><code>${o.pair}</code></div>
            <div class="row"><span>Action</span><span class="${o.action === 'BUY' ? 'yes' : ''}">${o.action}</span></div>
            <div class="row"><span>Qty</span><span>${o.qty}</span></div>
            <div class="row"><span>Lev</span><span>${o.lev}</span></div>
            ${o.decision ? `<div class="row"><span>Human</span><span>${o.decision.user_id} · ${o.decision.decision.toUpperCase()}</span></div>` : ''}
          </div>
        `).join('');
      }

      const decItems = (decs.data || []).slice(0, 30);
      if (!decItems.length) {
        decWrap.innerHTML = '<div class="muted">No decisions yet</div>';
      } else {
        decWrap.innerHTML = decItems.map(d => `
          <div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05);">
            <div style="display:flex;justify-content:space-between;gap:8px;">
              <strong>${d.user_id}</strong>
              <span class="${d.decision === 'yes' ? 'yes' : 'no'}">${d.decision.toUpperCase()}</span>
            </div>
            <div class="row"><span>Opportunity</span><code>${d.opportunity_id}</code></div>
            <div class="row"><span>Channel</span><span>${d.channel}</span></div>
            <div class="row"><span>Time</span><span>${d.decided_at}</span></div>
          </div>
        `).join('');
      }
    }
    load();
    setInterval(load, 5000);
  </script>
</body>
</html>
    """
