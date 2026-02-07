# Moltbot Quick Reference

## 🔗 Your URLs

**Control UI (Main Interface):**
```
https://moltbot-sandbox.mahanazad19.workers.dev/?token=802f0514b3654d9d603f637b4847f8c5
```

**Admin UI:**
```
https://moltbot-sandbox.mahanazad19.workers.dev/_admin/
```

**Dashboard:**
```
https://dash.cloudflare.com/ → Workers & Pages → moltbot-sandbox
```

---

## 🔑 Your Tokens

**Gateway Token (Current):**
```
802f0514b3654d9d603f637b4847f8c5
```

**Old Token (INVALID - Do not use):**
```
865ca953944a8c0944d4f96c34bb60e1
```

---

## 🔐 Security Status

| Item | Status |
|------|--------|
| DEV_MODE | ✅ Disabled (Secure) |
| Gateway Token | ✅ Rotated (Secure) |
| Anthropic API Key | ❌ Needs rotation |
| Cloudflare API Token | ❌ Needs rotation |
| Device Pairing | ✅ Enabled |
| R2 Storage | ❌ Not configured |

---

## ⚡ Quick Commands

**View secrets:**
```bash
npx wrangler secret list --name moltbot-sandbox
```

**View live logs:**
```bash
npx wrangler tail --name moltbot-sandbox
```

**Set a secret:**
```bash
npx wrangler secret put SECRET_NAME --name moltbot-sandbox
```

**Deploy changes:**
```bash
npm run deploy
```

---

## 🚨 Important Action Items

1. **Rotate Anthropic API Key** (Do within 24h)
   - Go to: https://console.anthropic.com/settings/keys
   - Delete old key, create new one
   - Update with: `npx wrangler secret put ANTHROPIC_API_KEY --name moltbot-sandbox`

2. **Rotate Cloudflare API Token** (Do within 24h)
   - Go to: https://dash.cloudflare.com/profile/api-tokens
   - Delete old token, create new one

3. **Enable R2 Storage** (Recommended)
   - See `SETUP_GUIDE.md` for instructions
   - Provides data persistence and backup

---

## 📞 Support Resources

- **Setup Guide:** `SETUP_GUIDE.md`
- **Security Status:** `SECURITY_FIXES.md`
- **Deployment Checklist:** `CHECKLIST.md`
- **Original README:** `README.md`

---

**Last Updated:** 2026-02-01
