import os
import re
import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

# Owner configuration
OWNER_ID = 7109454163
OWNER_USERNAME = "casperthe6ix"

# ── State tracking ──────────────────────────────────────────────
last_speaker = {}                       # chat_id -> user_id
user_cache = {}                         # username_lower -> (user_id, first_name)
user_messages_store = defaultdict(list)  # (chat_id, user_id) -> [messages]

# ── Stats ───────────────────────────────────────────────────────
bot_stats = {
    "total_commands": 0,
    "mute_count": 0,
    "unmute_count": 0,
    "kick_count": 0,
    "ban_count": 0,
    "promote_count": 0,
    "demote_count": 0,
    "fun_count": 0,
    "groups_seen": set(),
}

# ── Owner protection messages ───────────────────────────────────
MUTE_PROTECTION = {
    "en": "You don't tell your dad to be quiet. \U0001f92b",
    "fr": "Tu ne dis pas \u00e0 ton p\u00e8re de se taire. \U0001f92b",
    "es": "No le dices a tu padre que se calle. \U0001f92b",
    "ar": "\u0644\u0627 \u062a\u0642\u0644 \u0644\u0623\u0628\u064a\u0643 \u0623\u0646 \u064a\u0635\u0645\u062a. \U0001f92b",
    "de": "Du sagst deinem Vater nicht, er soll still sein. \U0001f92b",
    "pt": "Voc\u00ea n\u00e3o manda seu pai calar a boca. \U0001f92b",
    "ru": "\u0422\u044b \u043d\u0435 \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0448\u044c \u0441\u0432\u043e\u0435\u043c\u0443 \u043e\u0442\u0446\u0443 \u043c\u043e\u043b\u0447\u0430\u0442\u044c. \U0001f92b",
    "tr": "Babana sus diyemezsin. \U0001f92b",
    "it": "Non dici a tuo padre di stare zitto. \U0001f92b",
    "zh-cn": "\u4f60\u4e0d\u80fd\u53eb\u4f60\u7238\u95ed\u5634\u3002\U0001f92b",
    "ja": "\u304a\u524d\u306f\u7236\u89aa\u306b\u9ed9\u308c\u3068\u306f\u8a00\u3048\u306a\u3044\u3002\U0001f92b",
    "ko": "\uc544\ubc84\uc9c0\ud55c\ud14c \uc870\uc6a9\ud788 \ud558\ub77c\uace0 \ud558\uc9c0 \ub9c8. \U0001f92b",
    "hi": "\u0924\u0942 \u0905\u092a\u0928\u0947 \u092c\u093e\u092a \u0915\u094b \u091a\u0941\u092a \u0930\u0939\u0928\u0947 \u0928\u0939\u0940\u0902 \u0915\u0939\u0924\u093e\u0964 \U0001f92b",
}

KICK_FUN_PROTECTION = {
    "en": "Gay Goyim! how dare you use this command on the owner. clown ahh nigga \U0001f921",
    "fr": "Gay Goyim! comment oses-tu utiliser cette commande sur le propri\u00e9taire. clown ahh nigga \U0001f921",
    "es": "Gay Goyim! c\u00f3mo te atreves a usar este comando contra el due\u00f1o. payaso ahh nigga \U0001f921",
    "ar": "Gay Goyim! \u0643\u064a\u0641 \u062a\u062c\u0631\u0624 \u0639\u0644\u0649 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 \u0647\u0630\u0627 \u0627\u0644\u0623\u0645\u0631 \u0636\u062f \u0627\u0644\u0645\u0627\u0644\u0643. \u0645\u0647\u0631\u062c ahh nigga \U0001f921",
    "de": "Gay Goyim! wie wagst du es, diesen Befehl gegen den Besitzer zu verwenden. Clown ahh nigga \U0001f921",
    "pt": "Gay Goyim! como voc\u00ea ousa usar esse comando no dono. palha\u00e7o ahh nigga \U0001f921",
    "ru": "Gay Goyim! \u043a\u0430\u043a \u0442\u044b \u0441\u043c\u0435\u0435\u0448\u044c \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u044d\u0442\u0443 \u043a\u043e\u043c\u0430\u043d\u0434\u0443 \u043f\u0440\u043e\u0442\u0438\u0432 \u0432\u043b\u0430\u0434\u0435\u043b\u044c\u0446\u0430. \u043a\u043b\u043e\u0443\u043d ahh nigga \U0001f921",
    "tr": "Gay Goyim! bu komutu sahibine kar\u015f\u0131 kullanmaya nas\u0131l c\u00fcret edersin. palyaco ahh nigga \U0001f921",
    "it": "Gay Goyim! come osi usare questo comando contro il proprietario. pagliaccio ahh nigga \U0001f921",
    "zh-cn": "Gay Goyim! \u4f60\u600e\u4e48\u6562\u5bf9\u4e3b\u4eba\u4f7f\u7528\u8fd9\u4e2a\u547d\u4ee4\u3002\u5c0f\u4e11 ahh nigga \U0001f921",
    "ja": "Gay Goyim! \u30aa\u30fc\u30ca\u30fc\u306b\u3053\u306e\u30b3\u30de\u30f3\u30c9\u3092\u4f7f\u3046\u3068\u306f\u4f55\u4e8b\u3060\u3002\u30d4\u30a8\u30ed ahh nigga \U0001f921",
    "ko": "Gay Goyim! \uac10\ud788 \uc8fc\uc778\uc5d0\uac8c \uc774 \uba85\ub839\uc744 \uc0ac\uc6a9\ud558\ub2e4\ub2c8. \uad11\ub300 ahh nigga \U0001f921",
    "hi": "Gay Goyim! \u092e\u093e\u0932\u093f\u0915 \u092a\u0930 \u0907\u0938 \u0915\u092e\u093e\u0902\u0921 \u0915\u093e \u0907\u0938\u094d\u0924\u0947\u092e\u093e\u0932 \u0915\u0930\u0928\u0947 \u0915\u0940 \u0939\u093f\u092e\u094d\u092e\u0924 \u0915\u0948\u0938\u0947 \u0939\u0941\u0908\u0964 \u091c\u094b\u0915\u0930 ahh nigga \U0001f921",
}

# ── Command replies ─────────────────────────────────────────────
MUTE_REPLIES = {
    "shutup": "Shut your stinking mouth. \U0001f910",
    "shush": "Stop Yappin. \U0001f92b",
    "ftg": "Ferme ta gueule big. \U0001f910",
    "bec": "Aie bec! \U0001f636",
    "stopbarking": "Stop barking, Bitch. \U0001f415",
    "artdejapper": "Arr\u00eate d'aboyer pti chiwawa. \U0001f436",
    "sybau": "shut your bitch AHHHH up. \U0001f92c",
    "goofy": "you're gay, you can't talk faggot. \U0001f921",
    "keh": "Ferme ta jgole senti ptite sharmouta. \U0001f922",
    "vio": "enfant de viole detected, geule closed. \U0001f512",
}

UNMUTE_REPLIES = {
    "talk": "talk respectfully n*gga \U0001f5e3\ufe0f",
    "parle": "parle bien bruv \U0001f5e3\ufe0f",
}

KICK_REPLIES = {
    "sort": "trace ta route bouzin senti. \U0001f6aa",
    "getout": "go take a bath \U0001f6c1",
    "decawlis": "ta yeule pu la marde, va te brosser les dents. \U0001faa5",
}

BAN_REPLIES = {
    "ntm": "vazi niquer ta marrain \U0001f480",
    "bouge": "ayo bouge tu parle trop pti wanna be. \U0001f44b",
    "ciao": "Ciao per sempre. \U0001fae1",
}

PROMOTE_REPLIES = {
    "levelup": "You are now Casper's VIP member. Protection added. \U0001f451",
    "debout": "You are now Casper's VIP member. Protection added. \U0001f451",
}

DEMOTE_REPLIES = {
    "assistoi": "mauvais chien, reste assis. pas de bonbon pr toi. \U0001f415",
    "leveldown": "You are no longer Casper's VIP Member \U0001f4c9",
}

FUN_REPLIES = {
    "pussy": "You're acting scared. \U0001f631",
    "shifta": "Go do your shift. \u23f0",
    "mgd": "MTL Groups Destroyed Send His Tiny Rat Dick To Transgenders \U0001f480",
    "fu": "put a fat bbc in your ass \U0001f351",
    "gay": "You're a faggot \U0001f3f3\ufe0f\u200d\U0001f308",
}

CAP_REPLIES = {
    "en": "Stop the cap. \U0001f9e2",
    "fr": "T'es un mytho. \U0001f9e2",
}

OWNER_COMMANDS = ["papa", "pere", "boss", "patron", "chef", "owner", "roi", "king"]


# ── Helpers ─────────────────────────────────────────────────────
def detect_user_language(chat_id: int, user_id: int) -> str:
    msgs = user_messages_store.get((chat_id, user_id), [])
    if not msgs:
        return "en"
    combined = " ".join(msgs[-5:])
    try:
        lang = detect(combined)
        return lang
    except LangDetectException:
        return "en"


def parse_duration(text: str):
    match = re.match(r"(\d+)(mo|m|h|d|w|y)", text.lower())
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    mapping = {
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
        "w": timedelta(weeks=value),
        "mo": timedelta(days=value * 30),
        "y": timedelta(days=value * 365),
    }
    return mapping.get(unit)


def parse_command_args(args: list):
    username = None
    duration_str = None
    for arg in args:
        if arg.startswith("@"):
            username = arg.lstrip("@").lower()
        elif re.match(r"\d+(mo|m|h|d|w|y)", arg.lower()):
            duration_str = arg
    return username, duration_str


async def resolve_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = update.effective_chat.id

    # 1. Reply
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    # 2. @username in args
    username, _ = parse_command_args(context.args or [])
    if username:
        # Check if it's the owner username
        if username == OWNER_USERNAME.lower():
            try:
                member = await context.bot.get_chat_member(chat_id, OWNER_ID)
                return member.user
            except Exception:
                pass
        if username in user_cache:
            uid, _ = user_cache[username]
            try:
                member = await context.bot.get_chat_member(chat_id, uid)
                return member.user
            except Exception:
                pass

    # 3. Last speaker
    if chat_id in last_speaker:
        uid = last_speaker[chat_id]
        if uid != update.effective_user.id:
            try:
                member = await context.bot.get_chat_member(chat_id, uid)
                return member.user
            except Exception:
                pass

    return None


def is_owner(user) -> bool:
    return user.id == OWNER_ID


def get_cmd(update: Update) -> str:
    return update.effective_message.text.split()[0].lstrip("/").split("@")[0].lower()


FULL_MUTE = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_manage_topics=False,
)

FULL_UNMUTE = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
    can_manage_topics=True,
)


# ── Message tracker ─────────────────────────────────────────────
async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user:
        return
    if not update.effective_chat or update.effective_chat.type == "private":
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.effective_message.text or ""

    # Update last speaker only for non-command messages
    if not text.startswith("/"):
        last_speaker[chat_id] = user.id

    # Cache user info
    if user.username:
        user_cache[user.username.lower()] = (user.id, user.first_name)

    # Track text for language detection
    if text and not text.startswith("/"):
        key = (chat_id, user.id)
        user_messages_store[key].append(text)
        if len(user_messages_store[key]) > 10:
            user_messages_store[key] = user_messages_store[key][-10:]

    # Track group
    bot_stats["groups_seen"].add(chat_id)


# ── Command handlers ────────────────────────────────────────────
async def mute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["mute_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text(
            "Couldn't find a target. Reply to someone, tag them, or let someone speak first. \U0001f3af"
        )
        return

    # Owner protection
    if is_owner(target):
        lang = detect_user_language(update.effective_chat.id, update.effective_user.id)
        msg = MUTE_PROTECTION.get(lang, MUTE_PROTECTION["en"])
        await update.effective_message.reply_text(msg)
        return

    # Parse duration
    _, duration_str = parse_command_args(context.args or [])
    if cmd == "vio":
        until_date = datetime.now(timezone.utc) + timedelta(days=400)
    elif duration_str:
        delta = parse_duration(duration_str)
        until_date = datetime.now(timezone.utc) + (delta if delta else timedelta(hours=1))
    else:
        until_date = datetime.now(timezone.utc) + timedelta(hours=1)

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=FULL_MUTE,
            until_date=until_date,
        )
        reply = MUTE_REPLIES.get(cmd, "Muted. \U0001f910")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't mute. Make sure I'm admin with restrict permissions! \u26a0\ufe0f"
        )


async def unmute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["unmute_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=FULL_UNMUTE,
        )
        reply = UNMUTE_REPLIES.get(cmd, "Unmuted. \U0001f5e3\ufe0f")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Unmute failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't unmute. Am I admin? \u26a0\ufe0f"
        )


async def kick_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["kick_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    if is_owner(target):
        lang = detect_user_language(update.effective_chat.id, update.effective_user.id)
        msg = KICK_FUN_PROTECTION.get(lang, KICK_FUN_PROTECTION["en"])
        await update.effective_message.reply_text(msg)
        return

    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id, user_id=target.id
        )
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id, user_id=target.id
        )
        reply = KICK_REPLIES.get(cmd, "Kicked. \U0001f6aa")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Kick failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't kick. Am I admin? \u26a0\ufe0f"
        )


async def ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["ban_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    if is_owner(target):
        lang = detect_user_language(update.effective_chat.id, update.effective_user.id)
        msg = KICK_FUN_PROTECTION.get(lang, KICK_FUN_PROTECTION["en"])
        await update.effective_message.reply_text(msg)
        return

    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id, user_id=target.id
        )
        reply = BAN_REPLIES.get(cmd, "Banned. \U0001f528")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Ban failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't ban. Am I admin? \u26a0\ufe0f"
        )


async def promote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["promote_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        try:
            await context.bot.set_chat_administrator_custom_title(
                chat_id=update.effective_chat.id,
                user_id=target.id,
                custom_title="Casper's VIP",
            )
        except Exception:
            pass
        reply = PROMOTE_REPLIES.get(cmd, "Promoted. \U0001f451")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Promote failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't promote. Am I admin with promote rights? \u26a0\ufe0f"
        )


async def demote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["demote_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    if is_owner(target):
        lang = detect_user_language(update.effective_chat.id, update.effective_user.id)
        msg = KICK_FUN_PROTECTION.get(lang, KICK_FUN_PROTECTION["en"])
        await update.effective_message.reply_text(msg)
        return

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        reply = DEMOTE_REPLIES.get(cmd, "Demoted. \U0001f4c9")
        name = target.first_name or target.username or "User"
        await update.effective_message.reply_text(f"{name}, {reply}")
    except Exception as e:
        logger.error(f"Demote failed: {e}")
        await update.effective_message.reply_text(
            "Couldn't demote. Am I admin? \u26a0\ufe0f"
        )


async def owner_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_stats["total_commands"] += 1
    await update.effective_message.reply_text(
        f"The owner, The boss, Our leader is @{OWNER_USERNAME} \U0001f451\U0001f525"
    )


async def fun_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    cmd = get_cmd(update)
    bot_stats["total_commands"] += 1
    bot_stats["fun_count"] += 1

    target = await resolve_target(update, context)
    if not target:
        await update.effective_message.reply_text("Couldn't find a target. \U0001f3af")
        return

    # Owner protection for fun commands
    if is_owner(target):
        lang = detect_user_language(update.effective_chat.id, update.effective_user.id)
        msg = KICK_FUN_PROTECTION.get(lang, KICK_FUN_PROTECTION["en"])
        await update.effective_message.reply_text(msg)
        return

    name = target.first_name or target.username or "User"

    if cmd == "cap":
        lang = detect_user_language(update.effective_chat.id, target.id)
        reply = CAP_REPLIES.get("fr" if lang == "fr" else "en", CAP_REPLIES["en"])
    else:
        reply = FUN_REPLIES.get(cmd, "lol \U0001f602")

    await update.effective_message.reply_text(f"{name}, {reply}")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_stats["total_commands"] += 1
    help_text = (
        "<b>\U0001f916 CASPER MOD BOT \u2014 COMMANDS</b>\n\n"
        "<b>\U0001f910 MUTE COMMANDS</b> <i>(default 1h, add time: 10m, 2h, 3d, 1w, 2mo, 1y)</i>\n"
        "/shutup \u2014 Shut your stinking mouth\n"
        "/shush \u2014 Stop Yappin\n"
        "/ftg \u2014 Ferme ta gueule big\n"
        "/bec \u2014 Aie bec!\n"
        "/stopbarking \u2014 Stop barking, Bitch\n"
        "/artdejapper \u2014 Arr\u00eate d'aboyer pti chiwawa\n"
        "/sybau \u2014 Shut your bitch AHHHH up\n"
        "/goofy \u2014 You're gay, can't talk faggot\n"
        "/keh \u2014 Ferme ta jgole senti ptite sharmouta\n"
        "/vio \u2014 <b>PERMANENT</b> mute\n\n"
        "<b>\U0001f5e3\ufe0f UNMUTE COMMANDS</b>\n"
        "/talk \u2014 Talk respectfully n*gga\n"
        "/parle \u2014 Parle bien bruv\n\n"
        "<b>\U0001f6aa KICK COMMANDS</b>\n"
        "/sort \u2014 Trace ta route bouzin senti\n"
        "/getout \u2014 Go take a bath\n"
        "/decawlis \u2014 Ta yeule pu la marde\n\n"
        "<b>\U0001f528 BAN COMMANDS</b>\n"
        "/ntm \u2014 Vazi niquer ta marrain\n"
        "/bouge \u2014 Ayo bouge tu parle trop\n"
        "/ciao \u2014 Ciao per sempre\n\n"
        "<b>\U0001f451 ADMIN COMMANDS</b>\n"
        "/levelup \u2014 Promote to Casper's VIP\n"
        "/debout \u2014 Promote to Casper's VIP\n"
        "/assistoi \u2014 Demote (mauvais chien)\n"
        "/leveldown \u2014 Remove VIP status\n\n"
        "<b>\U0001f602 FUN COMMANDS</b> <i>(no punishment)</i>\n"
        "/pussy \u2014 You're acting scared\n"
        "/shifta \u2014 Go do your shift\n"
        "/cap \u2014 Stop the cap / T'es un mytho\n"
        "/mgd \u2014 MTL Groups Destroyed\n"
        "/fu \u2014 ...\n"
        "/gay \u2014 You're a faggot\n\n"
        "<b>\U0001f525 OWNER MENTION</b>\n"
        "/papa /pere /boss /patron /chef /owner /roi /king\n\n"
        "<b>\u2753 HELP</b>\n"
        "/help \u2014 Show this list\n\n"
        "<i>Target: reply to a message, tag @username, or bot uses the last speaker.</i>"
    )

    if update.effective_chat.type != "private":
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=help_text,
                parse_mode="HTML",
            )
            await update.effective_message.reply_text(
                "Check your DMs! \U0001f4ec"
            )
        except Exception:
            bot_me = await context.bot.get_me()
            await update.effective_message.reply_text(
                f"Start a chat with me first: @{bot_me.username} then try /help again \U0001f4ac"
            )
    else:
        await update.effective_message.reply_text(help_text, parse_mode="HTML")


# ── Error handler ───────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)


# ── Setup ───────────────────────────────────────────────────────
def setup_handlers(application: Application):
    # Mute
    for cmd in MUTE_REPLIES:
        application.add_handler(CommandHandler(cmd, mute_handler))

    # Unmute
    for cmd in UNMUTE_REPLIES:
        application.add_handler(CommandHandler(cmd, unmute_handler))

    # Kick
    for cmd in KICK_REPLIES:
        application.add_handler(CommandHandler(cmd, kick_handler))

    # Ban
    for cmd in BAN_REPLIES:
        application.add_handler(CommandHandler(cmd, ban_handler))

    # Promote
    for cmd in PROMOTE_REPLIES:
        application.add_handler(CommandHandler(cmd, promote_handler))

    # Demote
    for cmd in DEMOTE_REPLIES:
        application.add_handler(CommandHandler(cmd, demote_handler))

    # Owner mention
    for cmd in OWNER_COMMANDS:
        application.add_handler(CommandHandler(cmd, owner_handler))

    # Fun
    for cmd in FUN_REPLIES:
        application.add_handler(CommandHandler(cmd, fun_handler))
    application.add_handler(CommandHandler("cap", fun_handler))

    # Help
    application.add_handler(CommandHandler("help", help_handler))

    # Message tracker (group 1 so it runs alongside command handlers)
    application.add_handler(
        MessageHandler(filters.ALL, track_message), group=1
    )

    # Error handler
    application.add_error_handler(error_handler)
