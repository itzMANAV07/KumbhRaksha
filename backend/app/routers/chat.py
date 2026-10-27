"""POST /chat — Chat endpoint."""
import random
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Zone
from app.schemas import ChatRequest, ChatResponse
from app.chat import intent as intent_module
from app.chat import templates
from app.sim import engine as sim_engine
from app.sos import is_sos

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory session state (chat_id -> dict)
_sessions: dict[str, dict] = {}

LANG_DETECT_MAP = {
    "hindi": "hi", "हिंदी": "hi", "हिन्दी": "hi",
    "bengali": "bn", "bangla": "bn", "বাংলা": "bn",
    "marathi": "mr", "मराठी": "mr",
    "gujarati": "gu", "ગુજરાતી": "gu",
    "telugu": "te", "తెలుగు": "te",
    "tamil": "ta", "தமிழ்": "ta",
    "english": "en", "angrezi": "en",
}


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    session = _sessions.setdefault(req.chat_id, {"language": req.language or "en", "lite": False})
    
    # Check if request has an explicit language set
    language = req.language or session.get("language", "en")
    
    # Check if the user text explicitly requests a language switch
    lower_text = req.text.lower().strip()
    for trigger, lang_code in LANG_DETECT_MAP.items():
        if trigger in lower_text and ("switch" in lower_text or "change" in lower_text or "language" in lower_text or "bhasha" in lower_text or lower_text == trigger):
            language = lang_code
            break

    session["language"] = language
    lite_mode = session.get("lite", False) or req.text.strip() == "/lite"

    if req.text.strip() == "/lite":
        session["lite"] = True
        reply = "Lite mode on. Ultra-short plain text responses only."
        return ChatResponse(text=templates.lite(reply) if lite_mode else reply)

    # SOS check FIRST — no LLM
    if is_sos(req.text):
        if req.lat is not None and req.lon is not None:
            from app.routers.sos import _handle_sos
            return await _handle_sos(req.chat_id, req.lat, req.lon, language, lite_mode, db)
        else:
            msg_text, _ = templates.menu(language)
            reply = "[SOS DETECTED] Send your GPS coordinates or location pin to dispatch the nearest emergency unit.\n\n" + msg_text
            if lite_mode:
                reply = templates.lite("SOS: Send GPS location for emergency response.")
            return ChatResponse(text=reply)

    # Intent classification
    detected_intent = await intent_module.classify(req.text, language)

    buttons: list[str] | None = None

    if detected_intent == "language_switch":
        reply, buttons = templates.language_switched(language)

    elif detected_intent == "website":
        from app.config import settings
        reply, buttons = templates.website_reply(language, dashboard_url=settings.dashboard_url)

    elif detected_intent == "ticket":
        # Find safest zone for Snan pass allocation
        states = list(sim_engine.zone_state.values())
        safe_zone_name = "Subhash Ghat"
        if states:
            safest_state = min(states, key=lambda s: s.density)
            result = await db.execute(select(Zone).where(Zone.id == safest_state.zone_id))
            z = result.scalar_one_or_none()
            if z:
                safe_zone_name = z.name

        pass_code = f"KR-SNAN-2027-{random.randint(1000, 9999)}"
        reply, buttons = templates.ticket_reply(language, zone_name=safe_zone_name, pass_code=pass_code)

    elif detected_intent == "facilities":
        reply, buttons = templates.facilities_reply(language)

    elif detected_intent == "divert":
        # Find highest-risk zone and recommended safe alternative
        states = list(sim_engine.zone_state.values())
        curr_name = "Har Ki Pauri"
        target_name = "Subhash Ghat"
        if states:
            matched_zid = intent_module.find_matching_zone_id(req.text)
            worst = None
            if matched_zid:
                for s in states:
                    if s.zone_id == matched_zid:
                        worst = s
                        break
            if not worst:
                worst = max(states, key=lambda s: s.density)

            res1 = await db.execute(select(Zone).where(Zone.id == worst.zone_id))
            z1 = res1.scalar_one_or_none()
            if z1:
                curr_name = z1.name
            if worst.divert_to:
                res2 = await db.execute(select(Zone).where(Zone.id == worst.divert_to))
                z2 = res2.scalar_one_or_none()
                if z2:
                    target_name = z2.name
            else:
                best = min(states, key=lambda s: s.density)
                res3 = await db.execute(select(Zone).where(Zone.id == best.zone_id))
                z3 = res3.scalar_one_or_none()
                if z3:
                    target_name = z3.name

        reply, buttons = templates.divert_reply(language, target_zone=target_name, current_zone=curr_name)

    elif detected_intent == "lost_person":
        reply, buttons = templates.lost_person_reply(language)

    elif detected_intent == "found_person":
        reply, buttons = templates.found_person_reply(language)

    elif detected_intent == "subscribe":
        reply = templates.subscription_consent_en("Har Ki Pauri")
        buttons = ["YES", "STOP", "Menu"]

    elif detected_intent == "unsubscribe":
        reply = templates.subscription_confirmed_en("Har Ki Pauri")
        buttons = ["Menu"]

    elif detected_intent == "crowd_status":
        states = list(sim_engine.zone_state.values())
        if not states:
            reply = "No zone telemetry available yet." if language == "en" else "डेटा उपलब्ध नहीं है।"
            return ChatResponse(text=reply)

        # Match specific zone if mentioned in text, else pick highest density
        matched_zid = intent_module.find_matching_zone_id(req.text)
        state = None
        if matched_zid:
            for s in states:
                if s.zone_id == matched_zid:
                    state = s
                    break
        if not state:
            state = max(states, key=lambda s: s.density)

        result = await db.execute(select(Zone).where(Zone.id == state.zone_id))
        zone = result.scalar_one_or_none()
        zone_name = zone.name if zone else state.zone_id

        reply, buttons = templates.crowd_status(
            language,
            zone_name,
            state.count,
            state.density,
            state.level,
            state.forecast_minutes,
            state.divert_to,
        )

    else:
        # Default: show comprehensive menu
        reply, buttons = templates.menu(language)

    if lite_mode:
        reply = templates.lite(reply)
        buttons = None

    return ChatResponse(text=reply, buttons=buttons)
