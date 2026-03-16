from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

from telegram.ext import Application
from bot import setup_handlers, bot_stats

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB (optional — bot works without it, stats just won't persist)
mongo_url = os.environ.get("MONGO_URL")
db = None
mongo_client = None
if mongo_url:
    mongo_client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get("DB_NAME", "casper_bot")
    db = mongo_client[db_name]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Bot state
bot_application = None
bot_start_time = None
bot_running = False

# ── Lifecycle ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global bot_application, bot_start_time, bot_running

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.warning("No TELEGRAM_BOT_TOKEN set. Bot will NOT start.")
        return

    try:
        bot_application = Application.builder().token(token).build()
        setup_handlers(bot_application)
        await bot_application.initialize()
        await bot_application.start()
        await bot_application.updater.start_polling(drop_pending_updates=True)
        bot_start_time = datetime.now(timezone.utc)
        bot_running = True
        logging.info("Telegram bot started successfully!")

        # Restore saved stats from MongoDB (if available)
        if db is not None:
            try:
                saved = await db.bot_stats.find_one({"id": "global"}, {"_id": 0})
                if saved:
                    for k, v in saved.items():
                        if k == "id":
                            continue
                        if k == "groups_seen":
                            bot_stats["groups_seen"] = set(v)
                        elif k in bot_stats:
                            bot_stats[k] = v
                logging.info("Stats restored from MongoDB.")
            except Exception as e:
                logging.warning(f"Could not restore stats from MongoDB: {e}")
    except Exception as e:
        logging.error(f"Failed to start Telegram bot: {e}")
        bot_running = False


@app.on_event("shutdown")
async def shutdown():
    global bot_application, bot_running

    # Persist stats to MongoDB (if available)
    if db is not None:
        try:
            stats_doc = {k: v for k, v in bot_stats.items() if k != "groups_seen"}
            stats_doc["groups_seen"] = list(bot_stats["groups_seen"])
            stats_doc["id"] = "global"
            await db.bot_stats.update_one(
                {"id": "global"}, {"$set": stats_doc}, upsert=True
            )
        except Exception:
            pass

    if bot_application:
        try:
            await bot_application.updater.stop()
            await bot_application.stop()
            await bot_application.shutdown()
        except Exception:
            pass
        bot_running = False

    if mongo_client:
        mongo_client.close()


# ── API routes ──────────────────────────────────────────────────
@api_router.get("/")
async def root():
    return {"message": "Casper Moderation Bot API"}


@api_router.get("/health")
async def health_check():
    """Health check for Railway / deployment monitoring."""
    return {
        "status": "healthy",
        "bot_running": bot_running,
        "uptime_seconds": int(
            (datetime.now(timezone.utc) - bot_start_time).total_seconds()
        )
        if bot_start_time
        else 0,
        "mongo_connected": db is not None,
    }


@api_router.get("/bot/status")
async def get_bot_status():
    uptime_seconds = 0
    if bot_start_time and bot_running:
        uptime_seconds = int(
            (datetime.now(timezone.utc) - bot_start_time).total_seconds()
        )
    return {
        "status": "online" if bot_running else "offline",
        "uptime_seconds": uptime_seconds,
        "started_at": bot_start_time.isoformat() if bot_start_time else None,
    }


@api_router.get("/bot/stats")
async def get_bot_stats():
    return {
        "total_commands": bot_stats["total_commands"],
        "mute_count": bot_stats["mute_count"],
        "unmute_count": bot_stats["unmute_count"],
        "kick_count": bot_stats["kick_count"],
        "ban_count": bot_stats["ban_count"],
        "promote_count": bot_stats["promote_count"],
        "demote_count": bot_stats["demote_count"],
        "fun_count": bot_stats["fun_count"],
        "groups_count": len(bot_stats["groups_seen"]),
    }


@api_router.get("/bot/commands")
async def get_bot_commands():
    return {
        "mute": [
            {"cmd": "/shutup", "desc": "Shut your stinking mouth", "duration": "custom"},
            {"cmd": "/shush", "desc": "Stop Yappin", "duration": "custom"},
            {"cmd": "/ftg", "desc": "Ferme ta gueule big", "duration": "custom"},
            {"cmd": "/bec", "desc": "Aie bec!", "duration": "custom"},
            {"cmd": "/stopbarking", "desc": "Stop barking, Bitch", "duration": "custom"},
            {"cmd": "/artdejapper", "desc": "Arrete d'aboyer pti chiwawa", "duration": "custom"},
            {"cmd": "/sybau", "desc": "Shut your bitch AHHHH up", "duration": "custom"},
            {"cmd": "/goofy", "desc": "You're gay, can't talk faggot", "duration": "custom"},
            {"cmd": "/keh", "desc": "Ferme ta jgole senti ptite sharmouta", "duration": "custom"},
            {"cmd": "/vio", "desc": "PERMANENT mute", "duration": "permanent"},
        ],
        "unmute": [
            {"cmd": "/talk", "desc": "Talk respectfully n*gga"},
            {"cmd": "/parle", "desc": "Parle bien bruv"},
        ],
        "kick": [
            {"cmd": "/sort", "desc": "Trace ta route bouzin senti"},
            {"cmd": "/getout", "desc": "Go take a bath"},
            {"cmd": "/decawlis", "desc": "Ta yeule pu la marde"},
        ],
        "ban": [
            {"cmd": "/ntm", "desc": "Vazi niquer ta marrain"},
            {"cmd": "/bouge", "desc": "Ayo bouge tu parle trop"},
            {"cmd": "/ciao", "desc": "Ciao per sempre"},
        ],
        "admin": [
            {"cmd": "/levelup", "desc": "Promote to Casper's VIP"},
            {"cmd": "/debout", "desc": "Promote to Casper's VIP"},
            {"cmd": "/assistoi", "desc": "Demote (mauvais chien)"},
            {"cmd": "/leveldown", "desc": "Remove VIP status"},
        ],
        "fun": [
            {"cmd": "/pussy", "desc": "You're acting scared"},
            {"cmd": "/shifta", "desc": "Go do your shift"},
            {"cmd": "/cap", "desc": "Stop the cap / T'es un mytho"},
            {"cmd": "/mgd", "desc": "MTL Groups Destroyed"},
            {"cmd": "/fu", "desc": "..."},
            {"cmd": "/gay", "desc": "You're a faggot"},
        ],
        "owner": [
            {"cmd": "/papa /pere /boss /patron /chef /owner /roi /king", "desc": "Mention the owner"},
        ],
        "help": [
            {"cmd": "/help", "desc": "Show command list"},
        ],
    }


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
