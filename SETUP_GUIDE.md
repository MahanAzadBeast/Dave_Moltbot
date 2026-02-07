# Moltbot (Moltworker) Setup Guide

This guide will walk you through deploying Moltbot on Cloudflare Workers step by step.

## Prerequisites

Before starting, ensure you have:

- **Cloudflare Workers Paid Plan** ($5/month) - Required for Sandbox containers
- **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com/)
- **Node.js & npm** installed on your machine
- **Cloudflare Account** with billing enabled

## 📋 Step-by-Step Setup

### Step 1: Project Setup (Already Complete ✅)

The project has been cloned and dependencies are installed. You're in the `moltworker` directory.

### Step 2: Authenticate with Cloudflare

First, log in to your Cloudflare account using Wrangler:

```bash
npx wrangler login
```

This will open your browser to authenticate. Follow the prompts to authorize Wrangler.

### Step 3: Configure Required Secrets

#### 3.1 Set Anthropic API Key

Get your API key from [Anthropic Console](https://console.anthropic.com/):

```bash
npx wrangler secret put ANTHROPIC_API_KEY
```

When prompted, paste your Anthropic API key (starts with `sk-ant-`).

#### 3.2 Set Gateway Token

The gateway token has been pre-generated for you. Set it using this command:

```bash
echo 865ca953944a8c0944d4f96c34bb60e1 | npx wrangler secret put MOLTBOT_GATEWAY_TOKEN
```

**⚠️ IMPORTANT:** Save this token somewhere safe! You'll need it to access your Control UI:

```
Token: 865ca953944a8c0944d4f96c34bb60e1
```

### Step 4: Deploy to Cloudflare Workers

Now deploy your Moltbot instance:

```bash
npm run deploy
```

This will:
1. Build the frontend UI with Vite
2. Build the worker code
3. Create the Docker container
4. Deploy to Cloudflare Workers

**Note:** The first deployment may take 2-3 minutes to build the container.

### Step 5: Get Your Worker URL

After deployment completes, Wrangler will output your worker URL. It will look like:

```
Published moltbot-sandbox (X.XX sec)
  https://moltbot-sandbox.YOUR-SUBDOMAIN.workers.dev
```

**Save this URL!** You'll need it for the next steps.

### Step 6: Verify Deployment

Test that your worker is running by opening this URL in your browser (replace with your actual worker URL and token):

```
https://moltbot-sandbox.YOUR-SUBDOMAIN.workers.dev/?token=865ca953944a8c0944d4f96c34bb60e1
```

**Expected behavior:**
- First request may take 1-2 minutes (cold start)
- You should see a loading screen while the container starts
- Once loaded, you'll see the Control UI

**⚠️ You won't be able to use the Control UI fully until you complete Step 7 (Cloudflare Access) and pair a device.**

### Step 7: Configure Cloudflare Access (Required for Admin UI)

To manage devices and use the admin features, you MUST set up Cloudflare Access:

#### 7.1 Enable Cloudflare Access

1. Go to [Workers & Pages Dashboard](https://dash.cloudflare.com/)
2. Click on your worker (e.g., `moltbot-sandbox`)
3. Go to **Settings** > **Domains & Routes**
4. In the `workers.dev` row, click the three dots menu (`...`)
5. Click **Enable Cloudflare Access**
6. Click **Manage Cloudflare Access** to configure access:
   - Add your email address to the allow list
   - Or configure other identity providers (Google, GitHub, etc.)
7. **IMPORTANT:** Copy the **Application Audience (AUD)** tag - you'll need it next

#### 7.2 Set Access Secrets

Set your Cloudflare Access configuration:

```bash
# Set your team domain (e.g., "myteam.cloudflareaccess.com")
npx wrangler secret put CF_ACCESS_TEAM_DOMAIN
# When prompted, enter: your-team.cloudflareaccess.com

# Set the Application Audience tag you copied above
npx wrangler secret put CF_ACCESS_AUD
# When prompted, paste the AUD tag
```

To find your team domain:
- Go to [Zero Trust Dashboard](https://one.dash.cloudflare.com/)
- Navigate to **Settings** > **Custom Pages**
- Your team domain is the subdomain before `.cloudflareaccess.com`

#### 7.3 Redeploy

After setting the Access secrets, redeploy:

```bash
npm run deploy
```

### Step 8: Access the Admin UI and Pair Devices

1. Visit the admin UI at: `https://your-worker.workers.dev/_admin/`
2. You'll be prompted to authenticate via Cloudflare Access
3. After authentication, you'll see the Device Pairing interface
4. Open your Control UI in a new browser tab: `https://your-worker.workers.dev/?token=865ca953944a8c0944d4f96c34bb60e1`
5. The device will appear as "pending" in the admin UI
6. Click **"Approve"** or **"Approve All"** to pair the device
7. Your Control UI will now be fully functional!

## 🚀 Optional: Enable R2 Storage (Recommended)

By default, all data (paired devices, conversation history) is lost when the container restarts. To persist data:

### Step 1: Create R2 API Token

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) > **R2** > **Overview**
2. Click **Manage R2 API Tokens**
3. Create a new token:
   - Name: "Moltbot R2 Access"
   - Permissions: **Object Read & Write**
   - Bucket: Select `moltbot-data` (created automatically on first deploy)
4. Save the **Access Key ID** and **Secret Access Key**

### Step 2: Set R2 Secrets

```bash
# Set R2 Access Key ID
npx wrangler secret put R2_ACCESS_KEY_ID
# When prompted, paste your Access Key ID

# Set R2 Secret Access Key
npx wrangler secret put R2_SECRET_ACCESS_KEY
# When prompted, paste your Secret Access Key

# Set your Cloudflare Account ID
npx wrangler secret put CF_ACCOUNT_ID
# When prompted, paste your Account ID
```

**To find your Account ID:**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Click the three dots menu next to your account name
3. Select **"Copy Account ID"**

### Step 3: Redeploy

```bash
npm run deploy
```

After deployment, visit `/_admin/` and you should see "Last backup: [timestamp]" with a "Backup Now" button.

## 📱 Optional: Add Chat Channels

### Telegram

1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Set the secret:

```bash
npx wrangler secret put TELEGRAM_BOT_TOKEN
```

4. Redeploy: `npm run deploy`

### Discord

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Get your bot token
3. Set the secret:

```bash
npx wrangler secret put DISCORD_BOT_TOKEN
```

4. Redeploy: `npm run deploy`

### Slack

1. Create a bot in the [Slack API Dashboard](https://api.slack.com/apps)
2. Get your bot and app tokens
3. Set the secrets:

```bash
npx wrangler secret put SLACK_BOT_TOKEN
npx wrangler secret put SLACK_APP_TOKEN
```

4. Redeploy: `npm run deploy`

## 🔧 Optional: Enable Browser Automation (CDP)

To enable browser automation capabilities:

```bash
# Generate a secure secret
npx wrangler secret put CDP_SECRET
# Enter a random secure string

# Set your worker URL
npx wrangler secret put WORKER_URL
# Enter: https://your-worker.workers.dev
```

Redeploy: `npm run deploy`

## 🐛 Troubleshooting

### Container takes too long to start
- First request takes 1-2 minutes (cold start)
- Subsequent requests are much faster
- Consider keeping `SANDBOX_SLEEP_AFTER=never` (default)

### Can't access Admin UI
- Ensure `CF_ACCESS_TEAM_DOMAIN` and `CF_ACCESS_AUD` are set correctly
- Check that Cloudflare Access is enabled on your worker
- Verify you're authenticated in the Cloudflare Access portal

### Device pairing not working
- Wait 10-15 seconds for device list to load in admin UI
- Refresh the page if devices don't appear
- Check that both Control UI and Admin UI are open simultaneously

### R2 storage not working
- Ensure all three secrets are set: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `CF_ACCOUNT_ID`
- R2 mounting only works in production, not with `wrangler dev`
- Check that the `moltbot-data` bucket exists in your R2 dashboard

### Gateway fails to start
- Check secrets are set correctly: `npx wrangler secret list`
- View live logs: `npx wrangler tail`
- Ensure you're on the Workers Paid plan

## 📚 Useful Commands

```bash
# View all configured secrets
npx wrangler secret list

# View live logs from your worker
npx wrangler tail

# Delete a secret
npx wrangler secret delete SECRET_NAME

# Local development (limited functionality)
npm run dev

# Run tests
npm test

# Type checking
npm run typecheck
```

## 🔐 Security Best Practices

1. **Never commit secrets** - The `.env` file is gitignored
2. **Use Cloudflare Access** - Always enable it for production
3. **Keep gateway token secret** - Don't share it publicly
4. **Enable device pairing** - Require explicit approval for new devices
5. **Rotate tokens regularly** - Especially if they might be compromised

## 📖 Additional Resources

- [OpenClaw Documentation](https://docs.openclaw.ai/)
- [Cloudflare Sandbox Docs](https://developers.cloudflare.com/sandbox/)
- [Cloudflare Access Docs](https://developers.cloudflare.com/cloudflare-one/policies/access/)
- [Wrangler CLI Docs](https://developers.cloudflare.com/workers/wrangler/)

## ✅ Next Steps

After completing this setup:

1. ✅ Test your Control UI with a simple message
2. ✅ Pair additional devices (mobile browsers, other computers)
3. ✅ Configure R2 storage for persistence
4. ✅ Optionally add chat channels (Telegram, Discord, Slack)
5. ✅ Explore the built-in skills in `/root/clawd/skills/`
6. ✅ Read the [OpenClaw documentation](https://docs.openclaw.ai/) to learn advanced features

---

**Need help?** Check the troubleshooting section or review the [project README](./README.md).
