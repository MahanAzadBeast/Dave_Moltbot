# Moltbot Deployment Checklist

Use this checklist to track your deployment progress.

## 🔐 Initial Authentication & Setup

- [ ] **Authenticate with Cloudflare**
  ```bash
  npx wrangler login
  ```

## 🔑 Required Secrets Configuration

- [ ] **Anthropic API Key Set**
  ```bash
  npx wrangler secret put ANTHROPIC_API_KEY
  ```
  - Get from: https://console.anthropic.com/

- [ ] **Gateway Token Set**
  ```bash
  echo 865ca953944a8c0944d4f96c34bb60e1 | npx wrangler secret put MOLTBOT_GATEWAY_TOKEN
  ```
  - **Token to save:** `865ca953944a8c0944d4f96c34bb60e1`

## 🚀 Initial Deployment

- [ ] **Deployment Complete**
  ```bash
  npm run deploy
  ```
  - Note your worker URL: `https://moltbot-sandbox.YOUR-SUBDOMAIN.workers.dev`

- [ ] **Verify Deployment Works**
  - Visit: `https://your-worker.workers.dev/?token=865ca953944a8c0944d4f96c34bb60e1`
  - Wait 1-2 minutes for cold start
  - Confirm loading screen appears

## 🔒 Cloudflare Access Configuration

- [ ] **Enable Cloudflare Access**
  - Workers Dashboard > Your Worker > Settings > Domains & Routes
  - Click `...` menu on workers.dev row
  - Click "Enable Cloudflare Access"

- [ ] **Configure Access Policy**
  - Add your email to allow list
  - Copy the Application Audience (AUD) tag

- [ ] **Set Access Secrets**
  ```bash
  npx wrangler secret put CF_ACCESS_TEAM_DOMAIN
  npx wrangler secret put CF_ACCESS_AUD
  ```
  - Find team domain at: Zero Trust Dashboard > Settings > Custom Pages

- [ ] **Redeploy After Access Configuration**
  ```bash
  npm run deploy
  ```

## 🔗 Device Pairing

- [ ] **Access Admin UI**
  - Visit: `https://your-worker.workers.dev/_admin/`
  - Authenticate via Cloudflare Access

- [ ] **Pair First Device**
  - Open Control UI: `https://your-worker.workers.dev/?token=865ca953944a8c0944d4f96c34bb60e1`
  - Device appears as "pending" in Admin UI
  - Click "Approve" or "Approve All"
  - Control UI is now functional

## 💾 Optional: R2 Storage (Recommended)

- [ ] **Create R2 API Token**
  - Cloudflare Dashboard > R2 > Manage R2 API Tokens
  - Create token with Object Read & Write permissions
  - Select `moltbot-data` bucket
  - Save Access Key ID and Secret Access Key

- [ ] **Set R2 Secrets**
  ```bash
  npx wrangler secret put R2_ACCESS_KEY_ID
  npx wrangler secret put R2_SECRET_ACCESS_KEY
  npx wrangler secret put CF_ACCOUNT_ID
  ```

- [ ] **Verify R2 Working**
  - Visit `/_admin/` after redeploying
  - Should see "Last backup: [timestamp]"

## 📱 Optional: Chat Channels

### Telegram (Optional)

- [ ] **Configure Telegram Bot**
  ```bash
  npx wrangler secret put TELEGRAM_BOT_TOKEN
  npm run deploy
  ```

### Discord (Optional)

- [ ] **Configure Discord Bot**
  ```bash
  npx wrangler secret put DISCORD_BOT_TOKEN
  npm run deploy
  ```

### Slack (Optional)

- [ ] **Configure Slack Bot**
  ```bash
  npx wrangler secret put SLACK_BOT_TOKEN
  npx wrangler secret put SLACK_APP_TOKEN
  npm run deploy
  ```

## 🌐 Optional: Browser Automation

- [ ] **Configure CDP (Chrome DevTools Protocol)**
  ```bash
  npx wrangler secret put CDP_SECRET
  npx wrangler secret put WORKER_URL
  npm run deploy
  ```

## ✅ Final Verification

- [ ] **Test Control UI**
  - Send a test message
  - Verify Claude responds

- [ ] **Test Admin UI**
  - View paired devices
  - Check R2 backup status (if configured)

- [ ] **Security Check**
  - Gateway token kept secret ✓
  - Cloudflare Access enabled ✓
  - Device pairing active ✓

---

## 📋 Quick Reference

**Your Worker URL:** `https://moltbot-sandbox.YOUR-SUBDOMAIN.workers.dev`

**Your Gateway Token:** `865ca953944a8c0944d4f96c34bb60e1`

**Control UI:** `https://your-worker.workers.dev/?token=865ca953944a8c0944d4f96c34bb60e1`

**Admin UI:** `https://your-worker.workers.dev/_admin/`

---

## 🔧 Useful Commands

```bash
# View configured secrets
npx wrangler secret list

# View live logs
npx wrangler tail

# Redeploy
npm run deploy

# Delete a secret
npx wrangler secret delete SECRET_NAME
```

---

**Status:** All setup steps completed! 🎉

For detailed instructions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)
