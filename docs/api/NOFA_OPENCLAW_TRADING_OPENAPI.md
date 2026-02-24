# NOFA x OpenClaw Trading OpenAPI Contract (Demo Integration SSOT, 2026-02-24)

## Purpose

OpenAPI-style contract for the NOFA x OpenClaw demo integration (mock-only on 2026-02-24), covering:

- account credential submission (mock)
- trade suggestion push for approval
- approval callback (`yes` / `no`)
- task status/result polling

Mock-only declaration:

- This document defines the contract for a demo workflow.
- It does **not** imply real executable backend logic exists today.
- No live trading, no real Binance validation, no real OpenClaw transport in demo page.

## Base URLs and Environments

### Demo (frontend mock only)

- Route: `/nofa-agent-native`
- Mock implementation file: `/Users/bowenwang/NOF2 /TradingAgents-CN/frontend/src/views/NofaAgentNative/index.vue`

### Production (proposed)

- `https://api.nofa.ai`

## Conventions

- Content type: `application/json`
- Timestamps: **absolute ISO 8601 UTC** (example `2026-02-24T15:06:12Z`)
- `decision`: canonical lowercase `yes` or `no`
- Idempotency key: `suggestion_id`

## Security Headers and Reliability Requirements

Required cross-system headers (production contract):

- `X-Request-ID: <uuid-or-unique-id>`
- `X-NOFA-Signature: sha256=<hex>`
- `X-OpenClaw-Signature: sha256=<hex>`

Rules:

- NOFA-originated requests should include `X-NOFA-Signature`
- OpenClaw-originated callbacks should include `X-OpenClaw-Signature`
- Signature verification is required in production, optional/no-op in demo frontend mock
- `Timeout default cancel` applies to approval waiting state
- Idempotency is enforced by `suggestion_id`

## Canonical Schemas (Aligned with Frontend Demo Types)

### `ApiKeyConnection`

```json
{
  "user_id": "u_001",
  "exchange": "binance",
  "api_key": "BNANCEKEY_DEMO_123456",
  "api_secret": "secret-demo-only",
  "label": "main-binance",
  "mode": "copilot"
}
```

### `TradeSuggestion`

```json
{
  "suggestion_id": "sug_123",
  "user_id": "u_001",
  "account_id": "acc_binance_demo_001",
  "mode": "copilot",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "action": "OPEN_NEW_ORDER",
  "side": "BUY",
  "quantity": 0.1,
  "leverage": 8,
  "tp": 65000,
  "sl": 62500,
  "rationale": "MACD reversal with bullish funding rate",
  "expires_at": "2026-02-24T15:10:00Z",
  "risk": {
    "confidence": 0.72,
    "risk_level": "medium"
  }
}
```

### `ApprovalDecision`

```json
{
  "task_id": "task_abc123",
  "suggestion_id": "sug_123",
  "decision": "yes",
  "approved_by": "u_001",
  "channel": "slack",
  "decided_at": "2026-02-24T15:06:12Z"
}
```

### `TradeDecisionTask`

```json
{
  "task_id": "task_abc123",
  "state": "executed",
  "suggestion": {
    "suggestion_id": "sug_123",
    "user_id": "u_001",
    "account_id": "acc_binance_demo_001",
    "mode": "copilot",
    "exchange": "binance",
    "symbol": "BTCUSDT",
    "action": "OPEN_NEW_ORDER",
    "side": "BUY",
    "quantity": 0.1,
    "leverage": 8,
    "tp": 65000,
    "sl": 62500,
    "rationale": "MACD reversal with bullish funding rate",
    "expires_at": "2026-02-24T15:10:00Z",
    "risk": {
      "confidence": 0.72,
      "risk_level": "medium"
    }
  },
  "approval": {
    "task_id": "task_abc123",
    "suggestion_id": "sug_123",
    "decision": "yes",
    "approved_by": "u_001",
    "channel": "slack",
    "decided_at": "2026-02-24T15:06:12Z"
  },
  "execution_result": {
    "status": "success",
    "mock_order_id": "order_demo_001",
    "message": "Mock execution completed. No live order was sent."
  },
  "audit_events": [
    {
      "time": "2026-02-24T15:05:00Z",
      "type": "suggestion.generated",
      "actor": "nofa-copilot",
      "summary": "NOFA Copilot generated a trade suggestion.",
      "payload": {
        "suggestion_id": "sug_123",
        "symbol": "BTCUSDT"
      }
    }
  ]
}
```

State enum for `TradeDecisionTask.state` (authoritative):

- `suggested`
- `pushed`
- `pending_approval`
- `approved`
- `rejected`
- `executing`
- `executed`
- `failed`
- `expired`

## Endpoint 1: Submit User Exchange Credentials (Mock Today)

`POST /api/nofa/openclaw/accounts`

Purpose:

- OpenClaw submits user exchange credentials to create/bind a NOFA account context.
- Demo behavior is **mock-only** and returns `connected_mock`.

### Request Body

```json
{
  "user_id": "u_001",
  "exchange": "binance",
  "api_key": "BNANCEKEY_DEMO_123456",
  "api_secret": "secret-demo-only",
  "label": "main-binance",
  "mode": "copilot"
}
```

### 200 Response (Demo Example)

```json
{
  "success": true,
  "data": {
    "account_id": "acc_binance_demo_001",
    "status": "connected_mock",
    "permissions_detected": ["trade", "read"],
    "masked_key": "BNAN***3456"
  },
  "message": "OpenClaw connected to NOFA account (mock)",
  "request_id": "req_001",
  "timestamp": "2026-02-24T15:01:00Z"
}
```

Notes:

- `status` is `connected_mock` in demo
- Production must encrypt and validate credentials/permissions before returning success

## Endpoint 2: Create/Push Trade Suggestion for Human Approval

`POST /api/nofa/openclaw/suggestions`

Purpose:

- NOFA publishes a trade suggestion to OpenClaw runtime/adapter for human approval.
- `suggestion_id` is the idempotency key.

### Required Headers (Production Contract)

- `X-Request-ID`
- `X-NOFA-Signature`

### Request Body

```json
{
  "suggestion_id": "sug_123",
  "user_id": "u_001",
  "account_id": "acc_binance_demo_001",
  "mode": "copilot",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "action": "OPEN_NEW_ORDER",
  "side": "BUY",
  "quantity": 0.1,
  "leverage": 8,
  "tp": 65000,
  "sl": 62500,
  "rationale": "MACD reversal with bullish funding rate",
  "expires_at": "2026-02-24T15:10:00Z",
  "risk": {
    "confidence": 0.72,
    "risk_level": "medium"
  }
}
```

### 200 Response (Demo Example)

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "delivery_status": "sent_mock",
    "approval_status": "pending_approval"
  },
  "message": "Suggestion delivered to OpenClaw approval channel (mock)",
  "request_id": "req_002",
  "timestamp": "2026-02-24T15:05:01Z"
}
```

### Idempotency behavior

- Same `suggestion_id` retried with identical payload: return same `task_id` (idempotent success)
- Same `suggestion_id` with conflicting payload: return conflict error, no new task created

## Endpoint 3: Receive Human Approval Decision (`yes` / `no`)

`POST /api/nofa/openclaw/approvals`

Purpose:

- OpenClaw sends normalized human approval decision to NOFA.

### Required Headers (Production Contract)

- `X-Request-ID`
- `X-OpenClaw-Signature`

### Request Body (Canonical)

```json
{
  "task_id": "task_abc123",
  "suggestion_id": "sug_123",
  "decision": "yes",
  "approved_by": "u_001",
  "channel": "slack",
  "decided_at": "2026-02-24T15:06:12Z"
}
```

### Optional callback metadata (recommended)

```json
{
  "task_id": "task_abc123",
  "suggestion_id": "sug_123",
  "decision": "yes",
  "approved_by": "u_001",
  "channel": "slack",
  "decided_at": "2026-02-24T15:06:12Z",
  "message_id": "slack_msg_001",
  "raw_response_text": "YES"
}
```

### 200 Response (Approved, Demo Example)

```json
{
  "success": true,
  "data": {
    "status": "accepted",
    "next_state": "approved",
    "execution_status": "executing_mock"
  },
  "message": "Approval accepted",
  "request_id": "req_003",
  "timestamp": "2026-02-24T15:06:12Z"
}
```

### 200 Response (Rejected, Demo Example)

```json
{
  "success": true,
  "data": {
    "status": "accepted",
    "next_state": "rejected",
    "execution_status": "canceled"
  },
  "message": "Rejection accepted",
  "request_id": "req_004",
  "timestamp": "2026-02-24T15:06:14Z"
}
```

### yes/no parsing rule (required, case-insensitive)

OpenClaw must normalize human input before callback.

Accepted as `yes`:

- `yes`
- `y`
- `approve`
- `approved`

Accepted as `no`:

- `no`
- `n`
- `cancel`
- `reject`

Rules:

- Case-insensitive (`YES`, `Yes`, `yEs` => `yes`)
- Trim whitespace before matching
- Unknown text => `needs_confirmation` (do not call approvals endpoint with ambiguous value)
- Button actions should directly submit `yes` or `no`

### Timeout / expiry behavior (required)

- `Timeout default cancel`
- If `expires_at` is reached before a valid decision is accepted, task transitions to `expired`
- Approval callback received after expiration should return expiry error (no execution)

### Idempotency behavior (required)

- Idempotency key: `suggestion_id`
- Duplicate callback for same `suggestion_id` after accepted decision must not trigger duplicate execution
- Duplicate same-decision callback may return idempotent success
- Conflicting decision after terminal state returns conflict or expired error

## Endpoint 4: Query Task Status / Result

`GET /api/nofa/openclaw/tasks/{task_id}`

Purpose:

- Return current task state for UI polling and audit rendering.

### Path Parameters

- `task_id` (string, required)

### 200 Response (Executed, Demo Example)

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "state": "executed",
    "suggestion": {
      "suggestion_id": "sug_123",
      "user_id": "u_001",
      "account_id": "acc_binance_demo_001",
      "mode": "copilot",
      "exchange": "binance",
      "symbol": "BTCUSDT",
      "action": "OPEN_NEW_ORDER",
      "side": "BUY",
      "quantity": 0.1,
      "leverage": 8,
      "tp": 65000,
      "sl": 62500,
      "rationale": "MACD reversal with bullish funding rate",
      "expires_at": "2026-02-24T15:10:00Z",
      "risk": {
        "confidence": 0.72,
        "risk_level": "medium"
      }
    },
    "approval": {
      "task_id": "task_abc123",
      "suggestion_id": "sug_123",
      "decision": "yes",
      "approved_by": "u_001",
      "channel": "slack",
      "decided_at": "2026-02-24T15:06:12Z"
    },
    "execution_result": {
      "status": "success",
      "mock_order_id": "order_demo_001",
      "message": "Mock execution completed. No live order was sent."
    },
    "audit_events": [
      {
        "time": "2026-02-24T15:05:00Z",
        "type": "suggestion.generated",
        "actor": "nofa-copilot",
        "summary": "NOFA Copilot generated a trade suggestion.",
        "payload": {
          "suggestion_id": "sug_123",
          "symbol": "BTCUSDT"
        }
      },
      {
        "time": "2026-02-24T15:05:01Z",
        "type": "openclaw.delivery.sent",
        "actor": "openclaw-runtime",
        "summary": "OpenClaw sent a Slack/Telegram-style approval request (mock).",
        "payload": {
          "channel": "slack",
          "task_id": "task_abc123"
        }
      },
      {
        "time": "2026-02-24T15:06:12Z",
        "type": "approval.received",
        "actor": "human",
        "summary": "Human replied YES to the trade suggestion.",
        "payload": {
          "decision": "yes",
          "channel": "slack"
        }
      },
      {
        "time": "2026-02-24T15:06:13Z",
        "type": "execution.mock.success",
        "actor": "nofa-execution-simulator",
        "summary": "Mock order execution completed after approval.",
        "payload": {
          "status": "success"
        }
      }
    ]
  },
  "message": "Task fetched",
  "request_id": "req_005",
  "timestamp": "2026-02-24T15:06:14Z"
}
```

### Polling guidance (demo/prod)

- Poll every 1-2 seconds in demo UI
- Stop polling when `state` is terminal: `rejected`, `executed`, `failed`, `expired`

## Skill Contract Summary (OpenClaw)

Skill name:

- `nofa-trading-copilot-approval`

### Skill input payload (NOFA -> OpenClaw)

```json
{
  "task_id": "task_abc123",
  "suggestion_id": "sug_123",
  "user_id": "u_001",
  "account_id": "acc_binance_demo_001",
  "mode": "copilot",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "action": "OPEN_NEW_ORDER",
  "side": "BUY",
  "quantity": 0.1,
  "leverage": 8,
  "tp": 65000,
  "sl": 62500,
  "rationale": "MACD reversal with bullish funding rate",
  "expires_at": "2026-02-24T15:10:00Z",
  "risk": {
    "confidence": 0.72,
    "risk_level": "medium"
  },
  "approval_actions": ["yes", "no"],
  "deep_link": "https://app.nofa.ai/copilot?suggestion_id=sug_123"
}
```

### Skill output payload (OpenClaw -> NOFA)

```json
{
  "task_id": "task_abc123",
  "suggestion_id": "sug_123",
  "decision": "yes",
  "approved_by": "u_001",
  "channel": "slack",
  "decided_at": "2026-02-24T15:06:12Z",
  "message_id": "slack_msg_001",
  "raw_response_text": "YES"
}
```

## Error Model (Recommended)

### Standard error envelope

```json
{
  "success": false,
  "message": "Invalid signature",
  "code": 40101,
  "request_id": "req_err_001",
  "timestamp": "2026-02-24T15:08:00Z"
}
```

### Suggested error codes

- `40001` invalid request payload
- `40002` invalid decision value (must be `yes` or `no`)
- `40101` invalid signature
- `40102` missing signature header
- `40301` user/account mismatch
- `40401` task not found
- `40402` suggestion not found
- `40901` duplicate approval callback (conflicting state)
- `40902` duplicate suggestion_id with different payload
- `42201` suggestion expired
- `42202` task already terminal
- `42901` too many retries / rate limited
- `50001` internal error / execution simulator failure
- `50401` upstream OpenClaw delivery timeout

## Demo vs Production Checklist (Required Distinction)

### Demo (2026-02-24)

- Mock-only responses (`connected_mock`, `sent_mock`, `executing_mock`)
- In-memory task lifecycle
- Signature headers may be present but not verified
- No real exchange calls

### Production (future)

- Real signature verification (`X-NOFA-Signature`, `X-OpenClaw-Signature`)
- Persistent idempotency store keyed by `suggestion_id`
- Timeout worker to enforce `expired` and default cancel
- Secure secret storage and exchange permission checks
