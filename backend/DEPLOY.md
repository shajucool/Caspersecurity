# Casper Moderation Bot — Railway Deployment Guide

## Quick Deploy to Railway

### 1. Push to GitHub
Push the `/backend` folder to a GitHub repo.

### 2. Create Railway Project
- Go to [railway.app](https://railway.app)
- Click **New Project → Deploy from GitHub repo**
- Select your repo
- Railway auto-detects the Dockerfile

### 3. Set Environment Variables
In Railway dashboard → your service → **Variables**, add:

| Variable | Required | Value |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | YES | Your bot token from @BotFather |
| `MONGO_URL` | NO | MongoDB connection string (e.g. `mongodb+srv://user:pass@cluster.mongodb.net`) |
| `DB_NAME` | NO | Database name (default: `casper_bot`) |
| `CORS_ORIGINS` | NO | Allowed origins (default: `*`) |

> **MongoDB is optional.** Without it the bot works perfectly — stats just won't persist across restarts. To add MongoDB:
> - Railway: Add a **MongoDB** plugin from the dashboard
> - Or use [MongoDB Atlas](https://www.mongodb.com/atlas) free tier

### 4. Deploy
Railway auto-deploys on push. The bot starts polling Telegram immediately.

### 5. Verify
- Check logs in Railway dashboard for `Telegram bot started successfully!`
- Visit `https://your-app.up.railway.app/api/health` — should return:
  ```json
  {"status": "healthy", "bot_running": true, ...}
  ```

---

## Quick Deploy to Fly.io

```bash
cd backend
fly launch          # creates app
fly secrets set TELEGRAM_BOT_TOKEN=your_token_here
fly secrets set MONGO_URL=mongodb+srv://...
fly deploy
```

---

## Important Notes

- **Only one instance** can run at a time (Telegram polling conflict). Don't run locally while Railway is active.
- The bot needs **admin permissions** in Telegram groups to mute/kick/ban/promote.
- Health check endpoint: `GET /api/health`
- Status page API: `GET /api/bot/status`

## File Structure
```
backend/
├── server.py              # FastAPI app + bot lifecycle
├── bot.py                 # All Telegram command handlers
├── requirements.deploy.txt # Slim deps for Docker
├── Dockerfile             # Production build
├── railway.toml           # Railway config
├── fly.toml               # Fly.io config (alternative)
├── Procfile               # Fallback start command
└── .dockerignore          # Excludes .env from image
```
