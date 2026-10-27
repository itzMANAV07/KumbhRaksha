"""
Telegram long-polling adapter (M7).
Rules from AGENTS.md:
- Rule 19: Long-polling ONLY. No webhook, no setWebhook, no public IP.
- Rule 5: SOS keywords handled BEFORE any LLM call.
- Rule 18: No LLM in lost-and-found or SOS flows; strip digits before LLM.
- Rule 6: Lite mode <= 200 chars, plain text, no buttons.
- Rule 3: Consent before subscription.
- Rule 20: No face recognition / biometrics.

Run as a background asyncio task started in FastAPI lifespan.
"""
from __future__ import annotations

import asyncio
import logging
import os
import random
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ── In-memory session state (chat_id -> dict) ─────────────────────────────────
_tg_sessions: dict[str, dict] = {}

LANG_DETECT_MAP = {
    "hindi": "hi", "हिंदी": "hi", "हिन्दी": "hi",
    "bengali": "bn", "bangla": "bn", "বাংলা": "bn",
    "marathi": "mr", "मराठी": "mr",
    "gujarati": "gu", "ગુજરાતી": "gu",
    "telugu": "te", "తెలుగు": "te",
    "tamil": "ta", "தமிழ்": "ta",
    "english": "en", "angrezi": "en",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "bn": "বাংলা (Bengali)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
    "te": "తెలుగు (Telugu)",
    "ta": "தமிழ் (Tamil)",
}


def _get_session(chat_id: str) -> dict:
    return _tg_sessions.setdefault(chat_id, {
        "language": "en",
        "lite": False,
        "consent_pending": None,
    })


def _build_keyboard(language: str, lite_mode: bool = False):
    """Build a language-specific ReplyKeyboardMarkup for Telegram."""
    if lite_mode:
        from telegram import ReplyKeyboardRemove
        return ReplyKeyboardRemove()

    from telegram import ReplyKeyboardMarkup, KeyboardButton

    if language == "hi":
        return ReplyKeyboardMarkup(
            [
                ["घाटों पर भीड़ स्थिति", "स्नान ई-पास प्राप्त करें"],
                ["चिकित्सा व पेयजल सुविधाएं", "सुरक्षित वैकल्पिक मार्ग"],
                ["🌐 लाइव डैशबोर्ड व मैप", "भाषा बदलें (Language)"],
                [KeyboardButton("आपातकाल SOS (लोकेशन भेजें)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    elif language == "bn":
        return ReplyKeyboardMarkup(
            [
                ["ঘাটের ভিড় অবস্থা", "বিনামূল্যে স্নান পাস"],
                ["চিকিৎসা ও পানীয় জল", "বিকল্প নিরাপদ রুট"],
                ["🌐 লাইভ ড্যাশবোর্ড ও ম্যাপ", "ভাষা পরিবর্তন (Language)"],
                [KeyboardButton("জরুরি SOS (লোকেশন পাঠান)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    elif language == "mr":
        return ReplyKeyboardMarkup(
            [
                ["घाटावरील गर्दी स्थिती", "मोफत स्नान ई-पास"],
                ["वैद्यकीय व पाणी सुविधा", "पर्यायी सुरक्षित मार्ग"],
                ["🌐 थेट डॅशबोर्ड व नकाशा", "भाषा बदला (Language)"],
                [KeyboardButton("आपत्कालीन SOS (लोकेशन पाठवा)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    elif language == "gu":
        return ReplyKeyboardMarkup(
            [
                ["ઘાટ પર ભીડ તપાસો", "મફત સ્નાન ઇ-પાસ"],
                ["તબીબી અને પાણી સુવિધા", "વૈકલ્પિક સુરક્ષિત રસ્તો"],
                ["🌐 લાઈવ ડેશબોર્ડ અને નકશો", "ભાષા બદલો (Language)"],
                [KeyboardButton("કટોકટી SOS (લોકેશન મોકલો)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    elif language == "te":
        return ReplyKeyboardMarkup(
            [
                ["ఘాట్ రద్దీ వివరాలు", "ఉచిత స్నాన ఈ-పాస్"],
                ["వైద్యం & మంచినీరు", "సురక్షిత ప్రత్యామ్నాయం"],
                ["🌐 లైవ్ డాష్‌బోర్డ్ & మ్యాప్", "భాష మార్చండి (Language)"],
                [KeyboardButton("అత్యవసర SOS (లొకేషన్ షేర్ చేయండి)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    elif language == "ta":
        return ReplyKeyboardMarkup(
            [
                ["படித்துறை கூட்டம்", "இலவச நீராடல் பாஸ்"],
                ["மருத்துவம் & குடிநீர்", "மாற்றுப் பாதை"],
                ["🌐 நேரலை டாஷ்போர்டு", "மொழி மாற்றவும் (Language)"],
                [KeyboardButton("அவசர உதவி SOS (இருப்பிடம்)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )
    else:  # Default: English
        return ReplyKeyboardMarkup(
            [
                ["Ghat Crowd Status", "Get Snan Pass"],
                ["Facilities & Medical", "Safe Divert Route"],
                ["🌐 Live Map & Dashboard", "Change Language"],
                [KeyboardButton("Emergency SOS (Send Location)", request_location=True)],
            ],
            resize_keyboard=True,
            is_persistent=True,
        )


def _build_lang_keyboard():
    """Keyboard for selecting language."""
    from telegram import ReplyKeyboardMarkup
    return ReplyKeyboardMarkup(
        [
            ["English", "हिन्दी (Hindi)"],
            ["বাংলা (Bengali)", "मराठी (Marathi)"],
            ["ગુજરાતી (Gujarati)", "తెలుగు (Telugu)"],
            ["தமிழ் (Tamil)", "Main Menu"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# ── Main polling loop ─────────────────────────────────────────────────────────

async def run_polling() -> None:
    """Long-polling loop. Runs forever until cancelled."""
    from app.config import settings
    token = os.getenv("TELEGRAM_BOT_TOKEN") or settings.telegram_bot_token
    if not token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN not set — Telegram adapter disabled. "
            "Use the web ChatSim at /chat as fallback."
        )
        return

    try:
        from telegram import Update
        from telegram.ext import (
            Application,
            CommandHandler,
            MessageHandler,
            filters,
            ContextTypes,
        )
    except ImportError:
        logger.warning("python-telegram-bot not installed; Telegram adapter disabled.")
        return

    app = Application.builder().token(token).build()

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _send(
        update: Update,
        text: str,
        language: str = "en",
        lite_mode: bool = False,
        custom_keyboard=None,
    ) -> None:
        """Send a reply, respecting lite mode (no buttons, plain text)."""
        if not update.message and not update.effective_message:
            return
        target = update.message or update.effective_message

        reply_markup = None
        if not lite_mode:
            reply_markup = custom_keyboard or _build_keyboard(language, lite_mode=False)

        try:
            await target.reply_text(text, reply_markup=reply_markup)
        except Exception as exc:
            logger.error(f"Telegram send error: {exc}")

    async def _process_sos(chat_id: str, lat: float, lon: float, language: str, lite_mode: bool) -> str:
        """Create incident in DB, emit SSE, and return nearest facility details."""
        from app.database import AsyncSessionLocal
        from app.routers.sos import _handle_sos

        try:
            async with AsyncSessionLocal() as db_session:
                resp = await _handle_sos(chat_id, lat, lon, language, lite_mode, db_session)
                return resp.text
        except Exception as exc:
            logger.error(f"Error handling Telegram SOS in DB: {exc}")
            # Fallback haversine without DB
            import json, pathlib
            from app.sos import find_nearest_facility, haversine_km
            from app.chat import templates

            fac_path = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "facilities.json"
            facilities = []
            if fac_path.exists():
                raw = json.loads(fac_path.read_text(encoding="utf-8"))
                facilities = raw.get("facilities", [])
            nearest = find_nearest_facility(lat, lon, facilities)
            if nearest:
                dist = haversine_km(lat, lon, nearest["lat"], nearest["lon"])
                maps_link = f"https://maps.google.com/?q={nearest['lat']},{nearest['lon']}"
                if language == "hi":
                    return templates.sos_reply_hi(nearest["name"], dist, maps_link)
                return templates.sos_reply_en(nearest["name"], dist, maps_link)
            return "Emergency SOS registered. Police (112) and Medical (108) units alerted."

    # ── Unified Core Handler ─────────────────────────────────────────────────

    async def _handle_incoming(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        override_text: Optional[str] = None,
    ) -> None:
        """Process any incoming message: text, command, location pin."""
        if not update.effective_chat:
            return

        chat_id = str(update.effective_chat.id)
        session = _get_session(chat_id)
        msg = update.message or update.effective_message
        if not msg and not override_text:
            return

        text = ""
        lat: Optional[float] = None
        lon: Optional[float] = None

        if override_text:
            text = override_text.strip()
        elif msg and msg.text:
            text = msg.text.strip()
        elif msg and msg.location:
            lat = msg.location.latitude
            lon = msg.location.longitude
            text = f"sos {lat},{lon}"

        if not text and lat is None:
            return

        # Normalize slash commands if sent as text
        if text.startswith("/"):
            parts = text.split()
            cmd = parts[0].lower()
            if cmd in {"/start", "/menu", "/help"}:
                text = "menu"
            elif cmd in {"/website", "/dashboard", "/map", "/portal", "/app", "/site"}:
                text = "website"
            elif cmd in {"/ticket", "/pass", "/snan"}:
                text = "ticket"
            elif cmd == "/facilities":
                text = "facilities"
            elif cmd == "/divert":
                text = "divert"
            elif cmd == "/crowd":
                text = "crowd"
            elif cmd == "/sos":
                text = "sos"

        logger.info(f"Telegram incoming from chat={chat_id} user={update.effective_user.username if update.effective_user else 'unknown'}: {text!r}")

        from app.chat.intent import classify_keywords, find_matching_zone_id
        from app.chat import templates
        from app.sos import is_sos

        lite_mode: bool = session.get("lite", False) or text == "/lite"

        if text == "/lite":
            session["lite"] = True
            reply = "Lite mode on. Short replies only."
            await _send(update, reply, lite_mode=True)
            return

        language: str = session.get("language", "en")
        lower_text = text.lower()

        # Check if user picked a language option from the language keyboard
        LANG_PICK_MAP = {
            "english": "en",
            "हिन्दी (hindi)": "hi",
            "hindi": "hi",
            "বাংলা (bengali)": "bn",
            "bengali": "bn",
            "मराठी (marathi)": "mr",
            "marathi": "mr",
            "ગુજરાતી (gujarati)": "gu",
            "gujarati": "gu",
            "తెలుగు (telugu)": "te",
            "telugu": "te",
            "தமிழ் (tamil)": "ta",
            "tamil": "ta",
        }
        for pick_str, code in LANG_PICK_MAP.items():
            if lower_text == pick_str or (pick_str in lower_text and ("language" in lower_text or "switch" in lower_text or "(" in lower_text)):
                language = code
                session["language"] = language
                reply, _ = templates.language_switched(language)
                await _send(update, reply, language=language, lite_mode=lite_mode)
                return

        if lower_text == "/hi":
            language = "hi"
            session["language"] = language
            reply, _ = templates.language_switched(language)
            await _send(update, reply, language=language, lite_mode=lite_mode)
            return
        elif lower_text == "/en":
            language = "en"
            session["language"] = language
            reply, _ = templates.language_switched(language)
            await _send(update, reply, language=language, lite_mode=lite_mode)
            return

        # Check for explicit language switch request
        if (
            "change language" in lower_text
            or "switch language" in lower_text
            or "select language" in lower_text
            or "भाषा बदलें" in lower_text
            or "भाषा बदला" in lower_text
            or "ભાષા બદલો" in lower_text
            or "భాష మార్చండి" in lower_text
            or "மொழி மாற்றவும்" in lower_text
            or "ভাষা পরিবর্তন" in lower_text
            or text == "Language / भाषा"
        ):
            msg_text = "Select your preferred language / अपनी भाषा चुनें:"
            await _send(update, msg_text, language=language, lite_mode=lite_mode, custom_keyboard=_build_lang_keyboard())
            return

        # ── SOS — handled synchronously, no LLM ───────────────────────────
        if is_sos(text) or lat is not None:
            # Check if lat/lon in text (e.g. "sos 29.93,78.01")
            if lat is None or lon is None:
                coord_match = re.search(r"(\d{2}\.\d+)[,\s]+(\d{2}\.\d+)", text)
                if coord_match:
                    lat = float(coord_match.group(1))
                    lon = float(coord_match.group(2))

            if lat is not None and lon is not None:
                reply = await _process_sos(chat_id, lat, lon, language, lite_mode)
            else:
                reply = (
                    "[SOS EMERGENCY DETECTED]\n"
                    "Tap the 'Emergency SOS (Send Location)' button below or attach your GPS Location pin "
                    "so rapid response teams can navigate directly to you.\n"
                    "Helplines: Police 112 | Ambulance 108"
                )
                if language == "hi":
                    reply = (
                        "[आपातकाल सूचना प्राप्त]\n"
                        "कृपया नीचे दिए गए 'आपातकाल SOS (लोकेशन भेजें)' बटन पर टैप करें या अपना GPS लोकेशन पिन भेजें "
                        "ताकि बचाव दल तत्काल आप तक पहुँच सके।\n"
                        "हेल्पलाइन: पुलिस 112 | एम्बुलेंस 108"
                    )
            if lite_mode:
                reply = templates.lite(reply)
            await _send(update, reply, language=language, lite_mode=lite_mode)
            return

        # ── Consent check ─────────────────────────────────────────────────
        consent_zone = session.get("consent_pending")
        if consent_zone:
            if text.lower() in {"yes", "haan", "हाँ", "ha"}:
                session["consent_pending"] = None
                reply = templates.subscription_confirmed_en(consent_zone)
            else:
                session["consent_pending"] = None
                reply = "Subscription cancelled." if language == "en" else "सदस्यता रद्द।"
            if lite_mode:
                reply = templates.lite(reply)
            await _send(update, reply, language=language, lite_mode=lite_mode)
            return

        # ── Intent classification ──────────────────────────────────────────
        intent = classify_keywords(text)

        if intent == "language_switch":
            msg_text = "Select your preferred language / अपनी भाषा चुनें:"
            await _send(update, msg_text, language=language, lite_mode=lite_mode, custom_keyboard=_build_lang_keyboard())
            return

        elif intent == "website":
            from app.config import settings
            dash_url = settings.dashboard_url
            if dash_url and not dash_url.startswith(("http://", "https://")):
                dash_url = f"https://{dash_url}"
            reply, _ = templates.website_reply(language, dashboard_url=dash_url)
            inline_kb = None
            if not lite_mode:
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                btn_title = "🌐 Open Live Safety Dashboard ↗"
                if language == "hi":
                    btn_title = "🌐 लाइव डैशबोर्ड व मैप खोलें ↗"
                elif language == "bn":
                    btn_title = "🌐 লাইভ ড্যাশবোর্ড খুলুন ↗"
                elif language == "mr":
                    btn_title = "🌐 थेट डॅशबोर्ड उघडा ↗"
                elif language == "gu":
                    btn_title = "🌐 લાઈવ ડેશબોર્ડ ખોલો ↗"
                elif language == "te":
                    btn_title = "🌐 లైవ్ డాష్‌బోర్డ్ తెరవండి ↗"
                elif language == "ta":
                    btn_title = "🌐 நேரலை டாஷ்போர்டு திறக்க ↗"

                inline_kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=btn_title, url=dash_url)]
                ])
            await _send(update, reply, language=language, lite_mode=lite_mode, custom_keyboard=inline_kb)
            return

        elif intent == "ticket":
            from app.sim import engine as sim_engine
            safe_name = "Subhash Ghat"
            if sim_engine.zone_state:
                safest = min(sim_engine.zone_state.values(), key=lambda s: s.density)
                safe_name = safest.zone_id.replace("-", " ").title()
            pass_code = f"KR-SNAN-2027-{random.randint(1000, 9999)}"
            reply, _ = templates.ticket_reply(language, zone_name=safe_name, pass_code=pass_code)

        elif intent == "facilities":
            reply, _ = templates.facilities_reply(language)

        elif intent == "crowd_status":
            from app.sim import engine as sim_engine
            states = list(sim_engine.zone_state.values())
            if not states:
                reply = "No zone telemetry available yet." if language == "en" else "डेटा उपलब्ध नहीं है।"
            else:
                matched_zid = find_matching_zone_id(text)
                matched_state = None
                if matched_zid:
                    for st in states:
                        if st.zone_id == matched_zid:
                            matched_state = st
                            break
                if not matched_state:
                    for st in states:
                        clean_zid = st.zone_id.replace("-", " ").lower()
                        if clean_zid in lower_text or st.zone_id in lower_text:
                            matched_state = st
                            break
                if not matched_state:
                    matched_state = max(states, key=lambda s: s.density)

                zone_title = matched_state.zone_id.replace("-", " ").title()
                reply, _ = templates.crowd_status(
                    language,
                    zone_title,
                    matched_state.count,
                    matched_state.density,
                    matched_state.level,
                    matched_state.forecast_minutes,
                    matched_state.divert_to,
                )

        elif intent == "divert":
            from app.sim import engine as sim_engine
            states = list(sim_engine.zone_state.values())
            curr_name = "Har Ki Pauri"
            target_name = "Subhash Ghat"
            if states:
                matched_zid = find_matching_zone_id(text)
                worst = None
                if matched_zid:
                    for st in states:
                        if st.zone_id == matched_zid:
                            worst = st
                            break
                if not worst:
                    worst = max(states, key=lambda s: s.density)

                curr_name = worst.zone_id.replace("-", " ").title()
                if worst.divert_to:
                    target_name = worst.divert_to.replace("-", " ").title()
                else:
                    best = min(states, key=lambda s: s.density)
                    target_name = best.zone_id.replace("-", " ").title()

            reply, _ = templates.divert_reply(language, target_zone=target_name, current_zone=curr_name)

        elif intent == "lost_person":
            reply, _ = templates.lost_person_reply(language)

        elif intent == "found_person":
            reply, _ = templates.found_person_reply(language)

        elif intent == "subscribe":
            from app.sim import engine as sim_engine
            if sim_engine.zone_state:
                worst = max(sim_engine.zone_state.values(), key=lambda s: s.density)
                session["consent_pending"] = worst.zone_id
                reply = templates.subscription_consent_en(worst.zone_id.replace("-", " ").title())
            else:
                reply = "No zones loaded yet."

        elif intent == "unsubscribe":
            reply = "Unsubscribed from all alerts." if language == "en" else "सभी अलर्ट से हटाया गया।"

        else:
            # menu / unknown / start
            reply, _ = templates.menu(language)

        if lite_mode:
            reply = templates.lite(reply)

        await _send(update, reply, language=language, lite_mode=lite_mode)

    # ── Command-specific wrappers ─────────────────────────────────────────────

    async def _start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="start")

    async def _help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="menu")

    async def _ticket_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="ticket")

    async def _facilities_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="facilities")

    async def _divert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="divert")

    async def _crowd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="crowd")

    async def _sos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="sos")

    async def _website_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_incoming(update, context, override_text="website")

    async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Telegram error in handler: {context.error}", exc_info=context.error)

    # ── Register handlers ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", _start_cmd))
    app.add_handler(CommandHandler("help", _help_cmd))
    app.add_handler(CommandHandler("menu", _help_cmd))
    app.add_handler(CommandHandler("ticket", _ticket_cmd))
    app.add_handler(CommandHandler("pass", _ticket_cmd))
    app.add_handler(CommandHandler("snan", _ticket_cmd))
    app.add_handler(CommandHandler("facilities", _facilities_cmd))
    app.add_handler(CommandHandler("divert", _divert_cmd))
    app.add_handler(CommandHandler("crowd", _crowd_cmd))
    app.add_handler(CommandHandler("sos", _sos_cmd))
    app.add_handler(CommandHandler("website", _website_cmd))
    app.add_handler(CommandHandler("dashboard", _website_cmd))
    app.add_handler(CommandHandler("map", _website_cmd))
    app.add_handler(CommandHandler("portal", _website_cmd))
    app.add_handler(CommandHandler("app", _website_cmd))

    # Location handler
    app.add_handler(MessageHandler(filters.LOCATION, _handle_incoming))

    # All text / generic messages
    app.add_handler(MessageHandler(filters.ALL, _handle_incoming))

    # Global error handler
    app.add_error_handler(_error_handler)

    logger.info("Telegram long-polling adapter starting...")
    try:
        await app.initialize()
        await app.start()
        # Drop pending updates = False so any messages queued while offline are processed
        await app.updater.start_polling(
            drop_pending_updates=False,
        )
        # Block until cancelled
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Telegram adapter stopping...")
    except Exception as exc:
        logger.error(f"Telegram polling error: {exc}", exc_info=True)
    finally:
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except Exception as exc:
            logger.warning(f"Telegram shutdown error: {exc}")
