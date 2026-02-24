export type Exchange = 'binance' | 'aster' | 'hyperliquid'
export type Mode = 'pilot' | 'copilot'

export interface ApiKeyConnection {
  user_id: string
  exchange: Exchange
  api_key: string
  api_secret: string
  label?: string
  mode: Mode
}

export interface TradeSuggestion {
  suggestion_id: string
  user_id: string
  account_id: string
  mode: Mode
  exchange: Exchange
  symbol: string
  action: 'OPEN_NEW_ORDER' | 'CLOSE_ORDER' | 'ADJUST_SLTP'
  side: 'BUY' | 'SELL'
  quantity: number
  leverage?: number
  tp?: number
  sl?: number
  rationale: string
  expires_at: string
  risk?: {
    confidence?: number
    risk_level?: 'low' | 'medium' | 'high'
  }
}

export interface ApprovalDecision {
  task_id: string
  suggestion_id: string
  decision: 'yes' | 'no'
  approved_by: string
  channel: 'slack' | 'telegram' | 'openclaw_chat'
  decided_at: string
}

export interface ExecutionResult {
  status: 'success' | 'failed' | 'canceled'
  mock_order_id?: string
  message: string
}

export interface AuditEvent {
  time: string
  type: string
  actor: string
  summary: string
  payload?: Record<string, unknown>
}

export interface TradeDecisionTask {
  task_id: string
  state: 'suggested' | 'pushed' | 'pending_approval' | 'approved' | 'rejected' | 'executing' | 'executed' | 'failed' | 'expired'
  suggestion: TradeSuggestion
  approval?: ApprovalDecision
  execution_result?: ExecutionResult
  audit_events: AuditEvent[]
}
