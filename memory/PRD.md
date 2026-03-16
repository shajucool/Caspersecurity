# Casper Moderation Bot - PRD

## Problem Statement
Build a Telegram moderation bot with 30+ commands (mute, unmute, kick, ban, admin, fun, owner mention, help) with owner protection for @casperthe6ix (ID: 7109454163). Auto-detect target language, per-group last speaker tracking, custom mute durations. Minimal web status dashboard. Deployable on Railway/Fly.io.

## Architecture
- **Backend**: FastAPI + python-telegram-bot v22.6 (async polling)
- **Frontend**: React + Tailwind + shadcn/ui (terminal-themed status page)
- **Database**: MongoDB (stats persistence)
- **Bot Token**: Stored in .env

## Core Requirements
- Owner immune to all punishments
- Target detection: reply > @mention > last speaker
- Language auto-detection via langdetect
- Custom mute durations (m, h, d, w, mo, y)
- /vio = permanent mute
- /help sends DM in groups, inline in private

## What's Been Implemented (2026-03-16)
- All 30+ command handlers (mute x10, unmute x2, kick x3, ban x3, promote x2, demote x2, fun x6, owner x8, help)
- Owner protection with multilingual messages (13 languages)
- Per-group last speaker tracking + user cache
- Language detection via langdetect
- FastAPI status API (/api/bot/status, /api/bot/stats, /api/bot/commands)
- Terminal-aesthetic React dashboard (dark theme, JetBrains Mono, neon green accent)
- Deployment files (Dockerfile, railway.toml, fly.toml)
- Stats persistence in MongoDB

## User Personas
- **Owner** (@casperthe6ix): Full control, immune to all punishments
- **Group Members**: Use commands, subject to moderation

## Railway Deployment Readiness (2026-03-16)
- MongoDB made optional (bot works without it, stats just don't persist)
- /api/health endpoint added for Railway health checks
- Dockerfile uses $PORT env var (Railway sets this)
- .dockerignore excludes .env from Docker image
- Slim requirements.deploy.txt (9 packages vs 126 in full freeze)
- railway.toml with healthcheck config
- DEPLOY.md with step-by-step Railway instructions
- No hardcoded values — all config via environment variables

## Vercel Conversion (2026-03-16)
- Complete Python→Node.js port: Telegraf + Vercel serverless
- Webhook-based (no polling) — Vercel compatible
- All 38 commands preserved with identical behavior
- MongoDB for stateful tracking (last speaker, user cache, language detection)
- Zero-dependency language detection (regex-based, 13 languages)
- Files: /app/vercel-bot/api/bot.js, api/set-webhook.js, package.json, vercel.json

## Prioritized Backlog
- P0: Complete (all commands + Railway + Vercel deploy)
- P1: Admin-only command restriction option
- P2: Web dashboard with logs/history
