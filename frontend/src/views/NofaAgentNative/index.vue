<template>
  <div class="nofa-agent-native">
    <div class="bg-grid"></div>

    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">NOFA x OpenClaw Demo</p>
        <h1>NOFA - Agent Native Trading</h1>
        <p class="subtitle">AI suggest trade, Human approve, 24/7 non-stop</p>
        <p class="desc">
          把 NOFA 作为策略大脑，把 OpenClaw 作为 agent runtime 与推送/审批层。今天 Demo 为全模拟流程，
          用于展示 API 接口、审批链路和产品体验。
        </p>
        <div class="hero-actions">
          <el-button type="warning" size="large" @click="scrollToDemo">Try Demo Flow</el-button>
          <el-button size="large" @click="scrollToDocs">Read API Docs</el-button>
        </div>
        <div class="disclaimer-inline">
          <el-tag type="warning" effect="dark">Demo only</el-tag>
          <el-tag effect="plain">No live trading</el-tag>
          <el-tag effect="plain">Timeout defaults to cancel</el-tag>
        </div>
      </div>
      <div class="hero-panel">
        <div class="terminal-card">
          <div class="terminal-header">
            <span>OpenClaw Push (Mock)</span>
            <span class="status-dot"></span>
          </div>
          <div class="terminal-body">
            <div class="msg-title">NOFA Trading Opportunity</div>
            <div class="msg-row"><span>Symbol</span><strong>BTCUSDT</strong></div>
            <div class="msg-row"><span>Side</span><strong class="buy">BUY</strong></div>
            <div class="msg-row"><span>Qty</span><strong>0.1</strong></div>
            <div class="msg-row"><span>Leverage</span><strong>8x</strong></div>
            <div class="msg-reason">MACD reversal with bullish funding rate</div>
            <div class="msg-actions">
              <button>YES</button>
              <button class="ghost">NO</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-title">Why Agent Native</div>
      <div class="three-col">
        <div class="info-card">
          <h3>NOFA = Strategy Brain</h3>
          <p>生成交易建议、风险解释、模式策略（Pilot / Co-Pilot）。</p>
        </div>
        <div class="info-card">
          <h3>OpenClaw = Runtime</h3>
          <p>负责消息推送、审批采集、任务状态回传、审计轨迹。</p>
        </div>
        <div class="info-card">
          <h3>Human = Final Control</h3>
          <p>Co-Pilot 模式中由人类确认 yes/no，避免自动执行风险。</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-title">Product Modes</div>
      <div class="modes">
        <div class="mode-card">
          <h3>Pilot Mode</h3>
          <p>Auto-approve policy（文案说明）</p>
          <ul>
            <li>NOFA 自动执行策略</li>
            <li>适合受控账户/阈值内场景</li>
            <li>今日不演示真实执行</li>
          </ul>
        </div>
        <div class="mode-card active">
          <h3>Co-Pilot Mode (Demo)</h3>
          <p>Human approval required</p>
          <ul>
            <li>NOFA 生成建议</li>
            <li>OpenClaw 推送给人类</li>
            <li>人类 Yes/No 后再执行（mock）</li>
          </ul>
        </div>
      </div>
    </section>

    <section ref="demoRef" class="section demo-section">
      <div class="section-title">Demo Flow Panel (Co-Pilot Mode)</div>
      <el-alert type="warning" :closable="false" show-icon>
        <template #title>Demo only / No live trading / No real exchange request</template>
        所有 API Key 仅保存在本页内存态；不会发起真实 Binance 下单或校验。
      </el-alert>

      <div class="demo-grid">
        <div class="demo-card">
          <div class="card-hd">Step A · Connect Binance API Key (Mock)</div>
          <el-form label-width="112px" class="demo-form">
            <el-form-item label="Mode">
              <el-radio-group v-model="mode">
                <el-radio-button label="copilot">Co-Pilot</el-radio-button>
                <el-radio-button label="pilot" disabled>Pilot (text only)</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Exchange">
              <el-select v-model="exchange" style="width: 100%">
                <el-option label="Binance" value="binance" />
                <el-option label="Aster" value="aster" />
                <el-option label="Hyperliquid" value="hyperliquid" />
              </el-select>
            </el-form-item>
            <el-form-item label="User ID">
              <el-input v-model="userId" />
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="apiKey" placeholder="Enter API key (mock only)" />
            </el-form-item>
            <el-form-item label="API Secret">
              <el-input v-model="apiSecret" type="password" show-password placeholder="Enter API secret (mock only)" />
            </el-form-item>
            <div class="form-actions">
              <el-button type="warning" :loading="submittingAccount" @click="submitAccount">Submit API Key</el-button>
              <el-button @click="resetDemo">Reset Demo</el-button>
            </div>
          </el-form>

          <div v-if="accountConnected" class="result-box">
            <div class="result-title">OpenClaw connected to NOFA account (mock)</div>
            <div class="result-line"><span>Account ID</span><code>{{ accountId }}</code></div>
            <div class="result-line"><span>Status</span><el-tag type="success">connected_mock</el-tag></div>
            <div class="result-line"><span>Masked Key</span><code>{{ maskedKey }}</code></div>
            <div class="result-line"><span>Permissions</span><code>trade, read (mock)</code></div>
          </div>
        </div>

        <div class="demo-card">
          <div class="card-hd">Step B · NOFA Suggestion + Step C · Human Approval</div>
          <div class="action-row">
            <el-button type="warning" :disabled="!accountConnected || !!task" :loading="generatingSuggestion" @click="generateSuggestion">
              Generate Suggestion
            </el-button>
            <el-button text @click="showSampleCurl = !showSampleCurl">Toggle sample curl</el-button>
          </div>

          <pre v-if="showSampleCurl" class="curl-block"><code>{{ sampleCurl }}</code></pre>

          <div v-if="task" class="push-card">
            <div class="push-header">
              <div>
                <div class="push-title">OpenClaw Push (Slack/Telegram style mock)</div>
                <div class="push-sub">Task {{ task.task_id }}</div>
              </div>
              <el-tag :type="stateTagType">{{ task.state }}</el-tag>
            </div>

            <div class="suggestion-grid">
              <div><span>Symbol</span><strong>{{ task.suggestion.symbol }}</strong></div>
              <div><span>Side</span><strong :class="task.suggestion.side === 'BUY' ? 'buy' : 'sell'">{{ task.suggestion.side }}</strong></div>
              <div><span>Qty</span><strong>{{ task.suggestion.quantity }}</strong></div>
              <div><span>Leverage</span><strong>{{ task.suggestion.leverage }}x</strong></div>
              <div><span>TP</span><strong>{{ task.suggestion.tp }}</strong></div>
              <div><span>SL</span><strong>{{ task.suggestion.sl }}</strong></div>
            </div>
            <div class="reason-box">{{ task.suggestion.rationale }}</div>
            <div class="reason-box subtle">Expires at {{ task.suggestion.expires_at }}</div>

            <div class="approval-actions" v-if="task.state === 'pending_approval'">
              <el-button type="success" :loading="approving" @click="approve('yes')">Yes / Approve</el-button>
              <el-button type="danger" plain :loading="approving" @click="approve('no')">No / Cancel</el-button>
            </div>

            <div v-if="task.approval" class="decision-box">
              Human reply: <strong>{{ task.approval.decision.toUpperCase() }}</strong>
              via {{ task.approval.channel }} at {{ task.approval.decided_at }}
            </div>

            <div v-if="task.execution_result" class="exec-box">
              <div class="exec-title">Step D · Mock execution result</div>
              <div>{{ task.execution_result.message }}</div>
              <div v-if="task.execution_result.mock_order_id">
                Mock Order ID: <code>{{ task.execution_result.mock_order_id }}</code>
              </div>
            </div>
          </div>
        </div>

        <div class="demo-card">
          <div class="card-hd">State Machine + Audit Timeline</div>
          <div class="state-strip">
            <span
              v-for="s in stateMachine"
              :key="s"
              :class="['state-pill', { active: currentMachineState === s }]"
            >
              {{ s }}
            </span>
          </div>

          <div class="timeline">
            <div v-for="(event, idx) in auditEvents" :key="`${event.time}-${idx}`" class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="tl-meta">{{ event.time }} · {{ event.actor }}</div>
                <div class="tl-title">{{ event.type }}</div>
                <div class="tl-summary">{{ event.summary }}</div>
              </div>
            </div>
            <el-empty v-if="!auditEvents.length" description="No audit events yet" />
          </div>
        </div>
      </div>
    </section>

    <section ref="docsRef" class="section">
      <div class="section-title">API Integration Preview</div>
      <div class="docs-grid">
        <div class="info-card">
          <h3>Core Endpoints (OpenAPI)</h3>
          <ul class="endpoint-list">
            <li><code>POST /api/nofa/openclaw/accounts</code></li>
            <li><code>POST /api/nofa/openclaw/suggestions</code></li>
            <li><code>POST /api/nofa/openclaw/approvals</code></li>
            <li><code>GET /api/nofa/openclaw/tasks/{task_id}</code></li>
          </ul>
        </div>
        <div class="info-card">
          <h3>Docs Files (repo paths)</h3>
          <p><code>/Users/bowenwang/NOF2 /TradingAgents-CN/docs/integration/NOFA_OPENCLAW_AGENT_NATIVE_DEMO.md</code></p>
          <p><code>/Users/bowenwang/NOF2 /TradingAgents-CN/docs/api/NOFA_OPENCLAW_TRADING_OPENAPI.md</code></p>
          <p class="muted">Landing route: <code>/nofa-agent-native</code></p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-title">Risk & Disclaimer</div>
      <div class="three-col">
        <div class="info-card"><h3>Demo only</h3><p>无真实下单、无真实交易所请求。</p></div>
        <div class="info-card"><h3>Not financial advice</h3><p>页面建议仅用于展示 agent approval flow。</p></div>
        <div class="info-card"><h3>Timeout = Cancel</h3><p>生产建议默认超时取消，避免静默执行。</p></div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { AuditEvent, Exchange, Mode, TradeDecisionTask } from '@/types/nofaAgentNative'
import {
  generateMockSuggestion,
  submitMockAccount,
  submitMockApproval,
  runMockExecution
} from '@/api/nofaAgentNative'

const demoRef = ref<HTMLElement | null>(null)
const docsRef = ref<HTMLElement | null>(null)

const mode = ref<Mode>('copilot')
const exchange = ref<Exchange>('binance')
const userId = ref('u_001')
const apiKey = ref('BNANCEKEY_DEMO_123456')
const apiSecret = ref('secret-demo-only')

const submittingAccount = ref(false)
const generatingSuggestion = ref(false)
const approving = ref(false)
const showSampleCurl = ref(false)

const accountConnected = ref(false)
const accountId = ref('')
const maskedKey = ref('')
const task = ref<TradeDecisionTask | null>(null)

const stateMachine = [
  'idle',
  'api_key_submitted',
  'pending_approval',
  'approved',
  'rejected',
  'executed_mock'
]

const currentMachineState = computed(() => {
  if (!accountConnected.value) return 'idle'
  if (accountConnected.value && !task.value) return 'api_key_submitted'
  if (!task.value) return 'idle'
  if (task.value.state === 'pending_approval') return 'pending_approval'
  if (task.value.state === 'approved') return 'approved'
  if (task.value.state === 'rejected') return 'rejected'
  if (task.value.state === 'executed') return 'executed_mock'
  return task.value.state
})

const auditEvents = computed<AuditEvent[]>(() => task.value?.audit_events ?? [])

const sampleCurl = computed(() => `curl -X POST https://api.nofa.ai/api/nofa/openclaw/approvals \\
  -H "Content-Type: application/json" \\
  -H "X-OpenClaw-Signature: sha256=demo-signature" \\
  -d '{
    "task_id": "${task.value?.task_id || 'task_demo_001'}",
    "suggestion_id": "${task.value?.suggestion.suggestion_id || 'sug_demo_001'}",
    "decision": "yes",
    "approved_by": "${userId.value}",
    "channel": "slack",
    "decided_at": "2026-02-24T15:10:00Z"
  }'`)

const stateTagType = computed(() => {
  const state = task.value?.state
  if (state === 'pending_approval') return 'warning'
  if (state === 'approved' || state === 'executed') return 'success'
  if (state === 'rejected' || state === 'failed' || state === 'expired') return 'danger'
  return 'info'
})

function scrollToDemo() {
  demoRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function scrollToDocs() {
  docsRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function submitAccount() {
  if (!apiKey.value || !apiSecret.value) {
    ElMessage.warning('Please enter API key and secret (mock).')
    return
  }
  submittingAccount.value = true
  try {
    const res = await submitMockAccount({
      user_id: userId.value,
      exchange: exchange.value,
      api_key: apiKey.value,
      api_secret: apiSecret.value,
      mode: mode.value
    })
    accountConnected.value = true
    accountId.value = res.account_id
    maskedKey.value = res.masked_key
    ElMessage.success('OpenClaw connected to NOFA account (mock).')
  } finally {
    submittingAccount.value = false
  }
}

async function generateSuggestion() {
  if (!accountConnected.value) return
  generatingSuggestion.value = true
  try {
    task.value = await generateMockSuggestion(userId.value, accountId.value)
    ElMessage.success('NOFA Copilot suggestion generated (mock).')
  } finally {
    generatingSuggestion.value = false
  }
}

async function approve(decision: 'yes' | 'no') {
  if (!task.value) return
  approving.value = true
  try {
    task.value = await submitMockApproval(task.value, decision)
    if (decision === 'yes' && task.value) {
      task.value.state = 'executing'
      task.value.audit_events.push({
        time: new Date().toISOString(),
        type: 'execution.mock.started',
        actor: 'nofa-execution-simulator',
        summary: 'Starting mock execution after human approval.'
      })
      task.value = await runMockExecution(task.value)
      ElMessage.success('Approved and executed (mock).')
      return
    }
    ElMessage.info('Suggestion canceled by human (mock).')
  } finally {
    approving.value = false
  }
}

function resetDemo() {
  accountConnected.value = false
  accountId.value = ''
  maskedKey.value = ''
  task.value = null
  showSampleCurl.value = false
  ElMessage.success('Demo state reset.')
}
</script>

<style scoped lang="scss">
.nofa-agent-native {
  --bg: #070809;
  --bg2: #101218;
  --panel: rgba(16, 18, 24, 0.92);
  --line: rgba(246, 190, 0, 0.22);
  --gold: #f6be00;
  --gold-soft: #ffd54a;
  --text: #f7f4e8;
  --muted: #9ea3b0;
  position: relative;
  min-height: 100vh;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 10%, rgba(246, 190, 0, 0.15), transparent 40%),
    radial-gradient(circle at 85% 15%, rgba(79, 132, 255, 0.12), transparent 35%),
    linear-gradient(180deg, #040506, #090b11 35%, #08090b);
  padding: 28px;
  overflow: hidden;
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
}

.hero, .section {
  position: relative;
  z-index: 1;
}

.hero {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 22px;
  align-items: center;
  margin-bottom: 24px;
}

.hero-copy, .hero-panel, .demo-card, .info-card, .mode-card {
  background: linear-gradient(180deg, rgba(18, 20, 28, 0.95), rgba(10, 12, 18, 0.95));
  border: 1px solid rgba(255, 215, 64, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 12px 32px rgba(0, 0, 0, 0.35);
  border-radius: 14px;
}

.hero-copy {
  padding: 24px;
}

.eyebrow {
  color: var(--gold-soft);
  letter-spacing: 0.12em;
  font-size: 12px;
  margin: 0 0 8px 0;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  line-height: 1.05;
  font-size: 42px;
  color: #fff2bf;
}

.subtitle {
  margin: 12px 0 8px;
  color: #ffe18a;
  font-size: 18px;
}

.desc {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.hero-actions {
  margin-top: 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.disclaimer-inline {
  margin-top: 14px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-panel {
  padding: 18px;
}

.terminal-card {
  border-radius: 12px;
  border: 1px solid rgba(246, 190, 0, 0.25);
  background: #0b0d14;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(246, 190, 0, 0.12);
  color: #d4d7df;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ad97b;
  box-shadow: 0 0 10px rgba(74, 217, 123, 0.7);
}

.terminal-body {
  padding: 14px;
}

.msg-title {
  font-weight: 700;
  margin-bottom: 10px;
  color: #ffe39a;
}

.msg-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  color: #aeb3bf;
}

.msg-row strong {
  color: #fff;
}

.buy { color: #4ad97b; }
.sell { color: #ff6c6c; }

.msg-reason {
  margin: 10px 0;
  padding: 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  color: #c6cad4;
  font-size: 13px;
}

.msg-actions {
  display: flex;
  gap: 8px;
}

.msg-actions button {
  border: 1px solid rgba(246, 190, 0, 0.4);
  background: #f6be00;
  color: #121212;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 700;
}

.msg-actions button.ghost {
  background: transparent;
  color: #ffe39a;
}

.section {
  margin-top: 18px;
}

.section-title {
  margin-bottom: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #fff2c1;
}

.three-col {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.info-card {
  padding: 16px;
}

.info-card h3 {
  margin: 0 0 8px;
  color: #ffe18a;
}

.info-card p, .info-card li {
  color: var(--muted);
  line-height: 1.5;
}

.modes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.mode-card {
  padding: 16px;
}

.mode-card.active {
  border-color: rgba(246, 190, 0, 0.45);
  box-shadow: inset 0 0 0 1px rgba(246, 190, 0, 0.1), 0 12px 32px rgba(246, 190, 0, 0.07);
}

.mode-card h3 {
  margin: 0 0 8px;
}

.mode-card p {
  margin: 0 0 8px;
  color: #ffe18a;
}

.mode-card ul {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}

.demo-section {
  scroll-margin-top: 20px;
}

.demo-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1.05fr 1fr 1fr;
  gap: 14px;
}

.demo-card {
  padding: 14px;
}

.card-hd {
  font-weight: 700;
  color: #ffe39a;
  margin-bottom: 12px;
}

.demo-form {
  margin-top: 8px;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.result-box, .decision-box, .exec-box {
  margin-top: 12px;
  padding: 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.result-title, .exec-title {
  color: #d6ffb3;
  font-weight: 700;
  margin-bottom: 8px;
}

.result-line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
  color: var(--muted);
}

.result-line code {
  color: #fce29f;
  word-break: break-all;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.curl-block {
  margin: 0 0 10px;
  background: #0b0d14;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 10px;
  color: #c4cad6;
  font-size: 12px;
  overflow-x: auto;
}

.push-card {
  border: 1px solid rgba(246, 190, 0, 0.2);
  border-radius: 10px;
  padding: 12px;
  background: rgba(10, 12, 18, 0.9);
}

.push-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.push-title {
  font-weight: 700;
  color: #fff1bb;
}

.push-sub {
  margin-top: 2px;
  color: var(--muted);
  font-size: 12px;
}

.suggestion-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.suggestion-grid > div {
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: #b5bbca;
}

.suggestion-grid strong {
  color: #fff;
}

.reason-box {
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  color: #d0d4de;
}

.reason-box.subtle {
  color: #a4aabc;
  font-size: 12px;
}

.approval-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

.state-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.state-pill {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 4px 10px;
  color: #9ea3b0;
  font-size: 12px;
}

.state-pill.active {
  border-color: rgba(246, 190, 0, 0.35);
  background: rgba(246, 190, 0, 0.1);
  color: #ffe18a;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 440px;
  overflow: auto;
  padding-right: 2px;
}

.timeline-item {
  display: grid;
  grid-template-columns: 12px 1fr;
  gap: 10px;
}

.timeline-dot {
  width: 8px;
  height: 8px;
  margin-top: 6px;
  border-radius: 50%;
  background: #f6be00;
  box-shadow: 0 0 12px rgba(246, 190, 0, 0.6);
}

.timeline-content {
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 8px 10px;
}

.tl-meta {
  color: #9ba1af;
  font-size: 11px;
}

.tl-title {
  color: #fbe3a0;
  font-weight: 600;
  margin-top: 2px;
}

.tl-summary {
  color: #c6cad4;
  margin-top: 4px;
  font-size: 13px;
}

.docs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.endpoint-list {
  margin: 0;
  padding-left: 18px;
}

.endpoint-list li {
  margin-bottom: 6px;
}

.muted {
  color: var(--muted);
}

code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}

@media (max-width: 1200px) {
  .hero, .demo-grid {
    grid-template-columns: 1fr;
  }
  .three-col, .modes, .docs-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    scroll-behavior: auto !important;
    transition: none !important;
    animation: none !important;
  }
}
</style>
