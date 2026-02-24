import type {
  ApiKeyConnection,
  ApprovalDecision,
  AuditEvent,
  TradeDecisionTask,
  TradeSuggestion
} from '@/types/nofaAgentNative'

const nowIso = () => new Date().toISOString()

const rand = (prefix: string) => `${prefix}_${Math.random().toString(36).slice(2, 10)}`

export interface MockAccountResponse {
  account_id: string
  status: 'connected_mock'
  permissions_detected: string[]
  masked_key: string
}

export const maskApiKey = (key: string) => {
  if (!key) return ''
  if (key.length <= 8) return `${key.slice(0, 2)}***${key.slice(-2)}`
  return `${key.slice(0, 4)}***${key.slice(-4)}`
}

export async function submitMockAccount(payload: ApiKeyConnection): Promise<MockAccountResponse> {
  await delay(500)
  return {
    account_id: rand('acc_binance'),
    status: 'connected_mock',
    permissions_detected: ['trade', 'read'],
    masked_key: maskApiKey(payload.api_key)
  }
}

export async function generateMockSuggestion(userId: string, accountId: string): Promise<TradeDecisionTask> {
  await delay(600)

  const suggestion: TradeSuggestion = {
    suggestion_id: rand('sug'),
    user_id: userId,
    account_id: accountId,
    mode: 'copilot',
    exchange: 'binance',
    symbol: 'BTCUSDT',
    action: 'OPEN_NEW_ORDER',
    side: 'BUY',
    quantity: 0.1,
    leverage: 8,
    tp: 65000,
    sl: 62500,
    rationale: 'MACD reversal with bullish funding rate',
    expires_at: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
    risk: {
      confidence: 0.72,
      risk_level: 'medium'
    }
  }

  const audit_events: AuditEvent[] = [
    {
      time: nowIso(),
      type: 'suggestion.generated',
      actor: 'nofa-copilot',
      summary: 'NOFA Copilot generated a trade suggestion.',
      payload: { suggestion_id: suggestion.suggestion_id, symbol: suggestion.symbol }
    },
    {
      time: nowIso(),
      type: 'openclaw.delivery.sent',
      actor: 'openclaw-runtime',
      summary: 'OpenClaw sent a Slack/Telegram-style approval request (mock).',
      payload: { channel: 'slack', task_id: rand('task') }
    }
  ]

  return {
    task_id: rand('task'),
    state: 'pending_approval',
    suggestion,
    audit_events
  }
}

export async function submitMockApproval(
  task: TradeDecisionTask,
  decision: 'yes' | 'no'
): Promise<TradeDecisionTask> {
  await delay(450)

  const approval: ApprovalDecision = {
    task_id: task.task_id,
    suggestion_id: task.suggestion.suggestion_id,
    decision,
    approved_by: task.suggestion.user_id,
    channel: 'slack',
    decided_at: nowIso()
  }

  const next: TradeDecisionTask = {
    ...task,
    state: decision === 'yes' ? 'approved' : 'rejected',
    approval,
    audit_events: [
      ...task.audit_events,
      {
        time: approval.decided_at,
        type: 'approval.received',
        actor: 'human',
        summary: `Human replied ${decision.toUpperCase()} to the trade suggestion.`,
        payload: { decision, channel: approval.channel }
      }
    ]
  }

  return next
}

export async function runMockExecution(task: TradeDecisionTask): Promise<TradeDecisionTask> {
  await delay(700)
  return {
    ...task,
    state: 'executed',
    execution_result: {
      status: 'success',
      mock_order_id: rand('order'),
      message: 'Mock execution completed. No live order was sent.'
    },
    audit_events: [
      ...task.audit_events,
      {
        time: nowIso(),
        type: 'execution.mock.success',
        actor: 'nofa-execution-simulator',
        summary: 'Mock order execution completed after approval.',
        payload: { status: 'success' }
      }
    ]
  }
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

