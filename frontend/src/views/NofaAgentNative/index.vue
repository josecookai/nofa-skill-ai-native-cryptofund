<template>
  <div class="nofa-agent-native">
    <div class="noise"></div>

    <section class="hero-shell">
      <div class="topline">
        <div class="brand-pill">NOFA x OpenClaw</div>
        <div class="hero-links">
          <button @click="scrollToDemo">Demo</button>
          <button @click="scrollToDocs">API Docs</button>
        </div>
      </div>

      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Agent-native trading workflow</p>
          <h1>
            AI suggests the trade.<br>
            Human approves the trade.<br>
            The system runs 24/7.
          </h1>
          <p class="hero-sub">
            用 NOFA 做策略大脑，用 OpenClaw 做 runtime、push 与审批。把「交易建议」变成一个可审计、可回放、
            可接入的 agent task，而不是一条聊天消息。
          </p>

          <div class="hero-cta">
            <el-button type="warning" size="large" @click="scrollToDemo">Try Demo Flow</el-button>
            <el-button size="large" @click="scrollToDocs">Read API Docs</el-button>
          </div>

          <div class="hero-proof">
            <div class="proof-item">
              <span class="proof-k">Flow</span>
              <strong>Suggest → Approve → Execute</strong>
            </div>
            <div class="proof-item">
              <span class="proof-k">Mode</span>
              <strong>Co-Pilot (human-in-the-loop)</strong>
            </div>
            <div class="proof-item">
              <span class="proof-k">Status</span>
              <strong>Demo only / mock execution</strong>
            </div>
          </div>
        </div>

        <div class="hero-aside">
          <div class="mini-card metrics-card">
            <div class="mini-title">What this demo proves</div>
            <ul>
              <li>OpenClaw can onboard exchange credentials (mock)</li>
              <li>NOFA can publish a typed trade suggestion</li>
              <li>Human can reply yes / no before execution</li>
              <li>Every step is tracked as an audit timeline</li>
            </ul>
          </div>

          <div class="mini-card message-card">
            <div class="message-head">
              <span>OpenClaw push</span>
              <span class="badge-live">pending approval</span>
            </div>
            <div class="message-title">NOFA Trading Opportunity</div>
            <div class="message-grid">
              <div><span>Pair</span><strong>BTCUSDT</strong></div>
              <div><span>Action</span><strong class="buy">BUY</strong></div>
              <div><span>Qty</span><strong>0.1</strong></div>
              <div><span>Lev</span><strong>8x</strong></div>
            </div>
            <p class="message-note">MACD reversal with bullish funding rate.</p>
            <div class="message-buttons">
              <button class="btn-primary" type="button">Yes</button>
              <button class="btn-secondary" type="button">No</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="band">
      <div class="band-head">
        <h2>Why this is agent-native (not just chat-native)</h2>
        <p>
          YC 风格的核心不是“炫 UI”，而是把产品价值讲清楚。这里的价值是：建议、审批、执行、审计在同一条任务链上。
        </p>
      </div>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>NOFA = strategy engine</h3>
          <p>生成交易建议、风险解释、symbol 选择和模式策略（pilot / co-pilot）。</p>
        </div>
        <div class="feature-card">
          <h3>OpenClaw = runtime + approvals</h3>
          <p>推送建议、采集 yes/no、回调结果，并作为任务执行轨迹的 runtime 层。</p>
        </div>
        <div class="feature-card">
          <h3>Human = decision checkpoint</h3>
          <p>在 Co-Pilot 模式中保留最终控制权，防止未确认交易被静默执行。</p>
        </div>
      </div>
    </section>

    <section class="band modes-band">
      <div class="band-head">
        <h2>One system, two operating modes</h2>
        <p>同一个任务状态机，切换审批策略即可支持 Pilot 与 Co-Pilot。</p>
      </div>
      <div class="mode-rows">
        <div class="mode-row">
          <div>
            <div class="mode-name">Pilot Mode</div>
            <p class="mode-copy">Auto-approve policy（今天不演示真实执行，仅展示概念映射）</p>
          </div>
          <ul>
            <li>适合受控账户或阈值内策略</li>
            <li>仍然保留审计日志与任务记录</li>
            <li>可配置高风险交易强制人工审批</li>
          </ul>
        </div>

        <div class="mode-row active">
          <div>
            <div class="mode-name">Co-Pilot Mode (Demo)</div>
            <p class="mode-copy">Human approval required before execution</p>
          </div>
          <ul>
            <li>NOFA 先给建议与理由</li>
            <li>OpenClaw 推送建议给人类</li>
            <li>Yes / No 决策回传 NOFA 再执行（mock）</li>
          </ul>
        </div>
      </div>
    </section>

    <section ref="demoRef" class="band demo-band">
      <div class="band-head">
        <h2>Interactive demo (today)</h2>
        <p>模拟完整链路：API key onboarding → NOFA suggestion → Human approval → Mock execution result.</p>
      </div>

      <el-alert type="warning" :closable="false" show-icon class="demo-alert">
        <template #title>Demo only / No live trading / No real exchange request</template>
        所有 API Key 仅保存在本页内存态；不会发起真实 Binance 下单或验签。
      </el-alert>

      <div class="demo-layout">
        <div class="demo-column">
          <div class="panel">
            <div class="panel-title">1. Connect account (mock)</div>
            <p class="panel-desc">用户通过 OpenClaw 提交交易所 API，NOFA 返回 account_id 与 masked key。</p>
            <el-form label-width="96px" class="demo-form">
              <el-form-item label="Mode">
                <el-radio-group v-model="mode">
                  <el-radio-button label="copilot">Co-Pilot</el-radio-button>
                  <el-radio-button label="pilot" disabled>Pilot</el-radio-button>
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
              <el-form-item label="Secret">
                <el-input v-model="apiSecret" type="password" show-password placeholder="Enter API secret (mock only)" />
              </el-form-item>
              <div class="form-actions">
                <el-button type="warning" :loading="submittingAccount" @click="submitAccount">Submit API Key</el-button>
                <el-button @click="resetDemo">Reset Demo</el-button>
              </div>
            </el-form>

            <div v-if="accountConnected" class="status-card success">
              <div class="status-title">OpenClaw connected to NOFA account (mock)</div>
              <div class="kv"><span>Account ID</span><code>{{ accountId }}</code></div>
              <div class="kv"><span>Status</span><el-tag type="success">connected_mock</el-tag></div>
              <div class="kv"><span>Masked Key</span><code>{{ maskedKey }}</code></div>
              <div class="kv"><span>Permissions</span><code>trade, read (mock)</code></div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-title">2. API integration preview</div>
            <p class="panel-desc">OpenClaw 一下接入 NOFA 的最小接口面。</p>
            <ul class="endpoint-list">
              <li><code>POST /api/nofa/openclaw/accounts</code></li>
              <li><code>POST /api/nofa/openclaw/suggestions</code></li>
              <li><code>POST /api/nofa/openclaw/approvals</code></li>
              <li><code>GET /api/nofa/openclaw/tasks/{task_id}</code></li>
            </ul>
          </div>
        </div>

        <div class="demo-column wide">
          <div class="panel">
            <div class="panel-toprow">
              <div>
                <div class="panel-title">3. NOFA suggestion + human yes/no</div>
                <p class="panel-desc">模拟 OpenClaw 以 Slack / Telegram 风格卡片推送交易建议。</p>
              </div>
              <div class="panel-actions">
                <el-button
                  type="warning"
                  :disabled="!accountConnected || !!task"
                  :loading="generatingSuggestion"
                  @click="generateSuggestion"
                >
                  Generate Suggestion
                </el-button>
                <el-button text @click="showSampleCurl = !showSampleCurl">Toggle curl</el-button>
              </div>
            </div>

            <pre v-if="showSampleCurl" class="curl-block"><code>{{ sampleCurl }}</code></pre>

            <div v-if="task" class="push-card">
              <div class="push-head">
                <div>
                  <div class="push-title">NOFA Trading Opportunity</div>
                  <div class="push-sub">Task {{ task.task_id }} · OpenClaw push (mock)</div>
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

              <div v-if="task.state === 'pending_approval'" class="approval-actions">
                <el-button type="success" :loading="approving" @click="approve('yes')">Yes / Approve</el-button>
                <el-button type="danger" plain :loading="approving" @click="approve('no')">No / Cancel</el-button>
              </div>

              <div v-if="task.approval" class="status-card">
                <div class="status-title">Human decision captured</div>
                <div class="kv">
                  <span>Decision</span>
                  <strong>{{ task.approval.decision.toUpperCase() }}</strong>
                </div>
                <div class="kv">
                  <span>Channel</span>
                  <span>{{ task.approval.channel }}</span>
                </div>
                <div class="kv">
                  <span>Time</span>
                  <span>{{ task.approval.decided_at }}</span>
                </div>
              </div>

              <div v-if="task.execution_result" class="status-card">
                <div class="status-title">4. Mock execution result</div>
                <p>{{ task.execution_result.message }}</p>
                <div v-if="task.execution_result.mock_order_id" class="kv">
                  <span>Mock Order ID</span>
                  <code>{{ task.execution_result.mock_order_id }}</code>
                </div>
              </div>
            </div>

            <el-empty v-else description="Submit account first, then generate a NOFA suggestion" />
          </div>

          <div class="panel">
            <div class="panel-title">State machine + audit timeline</div>
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
      </div>
    </section>

    <section ref="docsRef" class="band docs-band">
      <div class="band-head">
        <h2>Docs for OpenClaw integration</h2>
        <p>今天 demo 先把接口和 Skill contract 定义清楚，后续再接真实 webhook / exchange testnet。</p>
      </div>
      <div class="docs-grid">
        <div class="panel">
          <div class="panel-title">Docs files</div>
          <div class="doc-item">
            <code>/Users/bowenwang/NOF2 /TradingAgents-CN/docs/integration/NOFA_OPENCLAW_AGENT_NATIVE_DEMO.md</code>
          </div>
          <div class="doc-item">
            <code>/Users/bowenwang/NOF2 /TradingAgents-CN/docs/api/NOFA_OPENCLAW_TRADING_OPENAPI.md</code>
          </div>
          <p class="muted">Landing route: <code>/nofa-agent-native</code></p>
        </div>

        <div class="panel">
          <div class="panel-title">Safety defaults (documented)</div>
          <ul class="plain-list">
            <li>Timeout defaults to cancel</li>
            <li>Idempotency by <code>suggestion_id</code></li>
            <li>Credential masking in UI</li>
            <li>HMAC signature headers reserved for production</li>
            <li>Auditability for every decision and execution result</li>
          </ul>
        </div>
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
  --bg: #0a0a0b;
  --panel: #101012;
  --panel-soft: rgba(16, 16, 18, 0.9);
  --line: rgba(255, 255, 255, 0.1);
  --line-strong: rgba(245, 173, 34, 0.35);
  --text: #f6f3ea;
  --muted: #b6b0a1;
  --muted-2: #908a7d;
  --accent: #f5ad22;
  --green: #43d37a;
  --red: #ff6d6d;
  position: relative;
  min-height: 100vh;
  padding: 20px;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 0%, rgba(245, 173, 34, 0.16), transparent 38%),
    radial-gradient(circle at 90% 10%, rgba(255, 255, 255, 0.06), transparent 30%),
    #090909;
}

.noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.55;
}

.hero-shell,
.band {
  position: relative;
  z-index: 1;
  max-width: 1240px;
  margin: 0 auto;
}

.hero-shell {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(20, 20, 22, 0.95), rgba(10, 10, 11, 0.98));
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

.topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-pill {
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  background: rgba(245, 173, 34, 0.08);
  color: #ffd67c;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 7px 12px;
  font-weight: 700;
}

.hero-links {
  display: flex;
  gap: 8px;
}

.hero-links button {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: transparent;
  color: var(--text);
  border-radius: 999px;
  padding: 7px 12px;
  cursor: pointer;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
  padding-top: 16px;
}

.hero-copy {
  padding: 10px 8px 8px 4px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #cfc7b3;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 11px;
}

h1 {
  margin: 0;
  font-size: clamp(34px, 4vw, 56px);
  line-height: 0.98;
  letter-spacing: -0.03em;
  color: #f8f5ed;
}

.hero-sub {
  margin: 16px 0 0;
  max-width: 640px;
  color: var(--muted);
  line-height: 1.55;
  font-size: 15px;
}

.hero-cta {
  margin-top: 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-proof {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.proof-item {
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 10px;
}

.proof-k {
  display: block;
  color: var(--muted-2);
  font-size: 11px;
  margin-bottom: 4px;
}

.proof-item strong {
  font-size: 13px;
  line-height: 1.35;
  color: #f7f1df;
}

.hero-aside {
  display: grid;
  gap: 12px;
}

.mini-card,
.panel,
.feature-card,
.mode-row {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--panel-soft);
  border-radius: 14px;
}

.mini-card {
  padding: 14px;
}

.mini-title {
  font-weight: 700;
  color: #fbe9b7;
  margin-bottom: 8px;
}

.metrics-card ul {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
  line-height: 1.45;
}

.metrics-card li + li {
  margin-top: 6px;
}

.message-card {
  background: linear-gradient(180deg, rgba(20, 17, 10, 0.6), rgba(13, 13, 14, 0.95));
  border-color: rgba(245, 173, 34, 0.2);
}

.message-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  color: #d7d0c0;
  font-size: 12px;
}

.badge-live {
  border: 1px solid rgba(245, 173, 34, 0.35);
  color: #ffd67c;
  padding: 3px 8px;
  border-radius: 999px;
}

.message-title {
  margin-top: 10px;
  font-weight: 700;
  color: #fff3cf;
}

.message-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}

.message-grid > div {
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  padding: 8px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: #bfb7a5;
  font-size: 12px;
}

.message-grid strong {
  color: #fff;
}

.buy {
  color: var(--green);
}

.sell {
  color: var(--red);
}

.message-note {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.message-buttons {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.message-buttons button {
  border-radius: 10px;
  padding: 9px 12px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 700;
}

.btn-primary {
  background: var(--accent);
  color: #17120a;
}

.btn-secondary {
  background: transparent;
  color: #f0dcc0;
  border-color: rgba(255, 255, 255, 0.14) !important;
}

.band {
  margin-top: 18px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 18px;
  background: rgba(12, 12, 13, 0.92);
  padding: 18px;
}

.band-head h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.band-head p {
  margin: 8px 0 0;
  color: var(--muted);
  max-width: 820px;
  line-height: 1.55;
}

.feature-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.feature-card {
  padding: 14px;
}

.feature-card h3 {
  margin: 0 0 6px;
  color: #f8e9bf;
  font-size: 16px;
}

.feature-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.5;
}

.mode-rows {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

.mode-row {
  padding: 14px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.mode-row.active {
  border-color: rgba(245, 173, 34, 0.28);
  box-shadow: inset 0 0 0 1px rgba(245, 173, 34, 0.08);
}

.mode-name {
  font-weight: 700;
  color: #fff0c1;
}

.mode-copy {
  margin: 6px 0 0;
  color: var(--muted);
}

.mode-row ul {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}

.mode-row li + li {
  margin-top: 5px;
}

.demo-band {
  scroll-margin-top: 20px;
}

.demo-alert {
  margin-top: 12px;
}

.demo-layout {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 12px;
}

.demo-column {
  display: grid;
  gap: 12px;
  align-content: start;
}

.demo-column.wide {
  grid-template-rows: auto auto;
}

.panel {
  padding: 14px;
}

.panel-title {
  font-weight: 700;
  color: #f8e9bf;
}

.panel-desc {
  margin: 6px 0 0;
  color: var(--muted);
  line-height: 1.45;
  font-size: 13px;
}

.panel-toprow {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.demo-form {
  margin-top: 12px;
}

.form-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-card {
  margin-top: 12px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  padding: 10px;
}

.status-card.success {
  border-color: rgba(67, 211, 122, 0.25);
  background: rgba(67, 211, 122, 0.03);
}

.status-title {
  font-weight: 700;
  color: #e7f7cf;
  margin-bottom: 8px;
}

.kv {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  color: var(--muted);
  font-size: 13px;
  margin-top: 6px;
}

.kv code {
  word-break: break-all;
}

.endpoint-list {
  margin: 10px 0 0;
  padding-left: 18px;
}

.endpoint-list li + li {
  margin-top: 6px;
}

.curl-block {
  margin: 10px 0 0;
  background: #0b0b0d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
  color: #d4d0c6;
  font-size: 12px;
  overflow-x: auto;
}

.push-card {
  margin-top: 12px;
  border: 1px solid rgba(245, 173, 34, 0.22);
  background: linear-gradient(180deg, rgba(19, 16, 11, 0.55), rgba(13, 13, 14, 0.95));
  border-radius: 12px;
  padding: 12px;
}

.push-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.push-title {
  font-weight: 700;
  color: #fff3cb;
}

.push-sub {
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
}

.suggestion-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.suggestion-grid > div {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 8px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  background: rgba(255, 255, 255, 0.02);
  color: #bfb7a5;
  font-size: 12px;
}

.suggestion-grid strong {
  color: #fff;
}

.reason-box {
  margin-top: 10px;
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #d9d3c8;
}

.reason-box.subtle {
  color: var(--muted-2);
  font-size: 12px;
}

.approval-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.state-strip {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.state-pill {
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--muted-2);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
}

.state-pill.active {
  border-color: rgba(245, 173, 34, 0.35);
  background: rgba(245, 173, 34, 0.09);
  color: #ffd98c;
}

.timeline {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 360px;
  overflow: auto;
}

.timeline-item {
  display: grid;
  grid-template-columns: 12px 1fr;
  gap: 10px;
}

.timeline-dot {
  width: 8px;
  height: 8px;
  margin-top: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 12px rgba(245, 173, 34, 0.45);
}

.timeline-content {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.015);
  padding: 9px 10px;
}

.tl-meta {
  color: var(--muted-2);
  font-size: 11px;
}

.tl-title {
  margin-top: 3px;
  color: #f5e4b6;
  font-weight: 600;
}

.tl-summary {
  margin-top: 4px;
  color: #d5d0c4;
  font-size: 13px;
}

.docs-band {
  scroll-margin-top: 20px;
}

.docs-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.doc-item + .doc-item {
  margin-top: 8px;
}

.plain-list {
  margin: 10px 0 0;
  padding-left: 18px;
  color: var(--muted);
}

.plain-list li + li {
  margin-top: 6px;
}

.muted {
  color: var(--muted);
}

code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
}

@media (max-width: 1180px) {
  .hero-grid,
  .demo-layout {
    grid-template-columns: 1fr;
  }

  .hero-proof,
  .feature-grid,
  .docs-grid,
  .mode-row {
    grid-template-columns: 1fr;
  }

  .suggestion-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .nofa-agent-native {
    padding: 12px;
  }

  .topline {
    flex-direction: column;
    align-items: flex-start;
  }

  .panel-toprow {
    flex-direction: column;
  }

  .suggestion-grid,
  .message-grid {
    grid-template-columns: 1fr;
  }

  .hero-links {
    width: 100%;
  }

  .hero-links button {
    flex: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
</style>
