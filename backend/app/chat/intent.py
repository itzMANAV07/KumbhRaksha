"""
Intent classification: keyword rules first, optional Gemini fallback.
Implements AGENTS.md Section 4 (LLM is optional) and Section 12 Rule 4.
SOS keywords are detected BEFORE this module is called (see router).
"""
from __future__ import annotations
import logging
import os
from typing import Optional

from app.schemas import LLMIntentResponse

logger = logging.getLogger(__name__)

# Keyword rules
# Priority-ordered rule list: higher-priority intents are listed first.
# When a message matches multiple intents the first match wins.
RULES_ORDERED: list[tuple[str, list[str], list[str]]] = [
    # intent, EN keywords, Multilingual keywords (HI, BN, MR, GU, TE, TA)
    (
        "language_switch",
        ["change language", "switch language", "select language", "bhasha", "english", "hindi", "bengali", "marathi", "gujarati", "telugu", "tamil", "language"],
        [
            "भाषा बदलो", "भाषा बदलें", "भाषा बदला", "हिंदी", "हिन्दी", "अंग्रेजी",
            "বাংলা", "মরাঠী", "मराठी", "ગુજરાતી", "ભાષા બદલો", "తెలుగు", "భాష మార్చండి",
            "தமிழ்", "மொழி மாற்றவும்", "மொழி", "ভাষা"
        ],
    ),
    (
        "website",
        [
            "website", "site", "dashboard", "portal", "live map", "web link", "web app",
            "open website", "open map", "open dashboard", "live dashboard", "map link", "link",
            "view dashboard", "view map", "live map & website", "open live dashboard"
        ],
        [
            "वेबसाइट", "डैशबोर्ड", "पोर्टल", "नक्शा", "मैप", "साइट", "वेब लिंक", "लाइव मैप",
            "लाइव डैशबोर्ड", "वेबसाइट खोलें", "नक्शा देखें", "डैशबोर्ड देखें", "वेब", "लाइव पोर्टल",
            "ওয়েবসাইট", "ড্যাশবোর্ড", "ম্যাপ", "পোর্টাল", "ওয়েব", "ওয়েবসাইট খুলুন", "লাইভ ড্যাশবোর্ড",
            "वेबसाईट", "डॅशबोर्ड", "नकाशा", "पोर्टल", "थेट डॅशबोर्ड",
            "વેબસાઇટ", "ડેશબોર્ડ", "નકશો", "પોર્ટલ", "લાઈવ ડેશબોર્ડ",
            "వెబ్‌సైట్", "డాష్‌బోర్డ్", "మ్యాప్", "పోర్టల్", "లైవ్ డాష్‌బోర్డ్",
            "வலைத்தளம்", "டாஷ்போர்டு", "வரைபடம்", "வலைப்பக்கம்", "நேரலை டாஷ்போர்டு"
        ],
    ),
    (
        "ticket",
        ["ticket", "pass", "snan pass", "epass", "e-pass", "booking", "slot", "darshan", "entry token", "bath pass", "get snan pass", "book free snan pass"],
        [
            "टिकट", "पास", "स्नान पास", "स्नान ई-पास", "ई-पास", "बुकिंग", "टोकन", "दर्शन", "स्नान ई-पास प्राप्त करें", "स्नान ई-पास बुक करें",
            "টিকিট", "পাস", "স্নান পাস", "স্নান ই-পাস", "বিনামূল্যে স্নান পাস", "স্নান ই-পাস বুক করুন",
            "तिकीट", "स्नान ई-पास", "मोफत स्नान ई-पास", "स्नान ई-पास बुक करा",
            "ટિકિટ", "સ્નાન ઇ-પાસ", "મફત સ્નાન ઇ-પાસ", "સ્નાન ઇ-પાસ બુક કરો",
            "టికెట్", "స్నాన ఈ-పాస్", "ఉచిత స్నాన ఈ-పాస్", "స్నాన ఈ-పాస్ బుక్ చేసుకోండి",
            "டிக்கெட்", "நீராடல் பாஸ்", "இலவச நீராடல் பாஸ்", "நீராடல் இ-பாஸ் பதிவு செய்யவும்", "இ-பாஸ்", "நீராடல்"
        ],
    ),
    (
        "facilities",
        [
            "facility", "facilities", "toilet", "washroom", "restroom", "water", "drinking", "medical",
            "doctor", "hospital", "dispensary", "police", "food", "langar", "prasad", "tent", "ashram",
            "stay", "dharamsala", "problem", "complaint", "helpline", "station", "bus", "train", "shauchalay", "paani"
        ],
        [
            "सुविधा", "सुविधाएं", "शौचालय", "पानी", "जल", "डॉक्टर", "दवा", "अस्पताल", "पुलिस", "भोजन", "लंगर", "प्रसाद",
            "आश्रम", "धर्मशाला", "रुकना", "समस्या", "शिकायत", "हेल्पलाइन", "स्टेशन", "बस", "ट्रेन", "चिकित्सा", "पेयजल",
            "টয়লেট", "জল", "ডাক্তার", "সমস্যা", "চিকিৎসা", "পানীয় জল",
            "पाणी", "दवाखाना", "वैद्यकीय",
            "પાણી", "પ્રશ્ન", "તબીબી", "દવા",
            "వైద్య", "నీరు", "సౌకర్యాలు", "వైద్య కేంద్రం",
            "மருத்துவ", "மருத்துவர்", "தண்ணீர்", "குடிநீர்", "வசதிகள்"
        ],
    ),
    (
        "lost_person",
        ["lost", "missing", "child", "separated", "khoya", "lost person", "gumshuda"],
        ["खोया", "गुम", "बच्चा", "बिछड़", "लापता", "हारিয়ে", "হারানো", "हरवला", "ખોવાઈ", "పోయిన", "காணவில்லை"],
    ),
    (
        "found_person",
        ["found", "wandering", "mila", "found child", "found person"],
        ["मिला", "व्यक्ति", "भटक", "बच्चा मिला", "খুঁজে", "सापडला", "મળ્યો", "దొరికిన", "கிடைத்தார்"],
    ),
    (
        "divert",
        ["go", "route", "avoid", "alternate", "move", "rasta", "detour", "direction", "corridor", "safe divert", "divert route", "safe divert route"],
        [
            "जाएं", "रास्ता", "बचें", "मार्ग", "निकास", "सुरक्षित वैकल्पिक मार्ग", "वैकल्पिक मार्ग", "सुरक्षित रास्ता बताएं",
            "পথ", "রুট", "বিকল্প", "বিকল্প নিরাপদ রুট", "বিকল্প রুট",
            "रस्ता", "मार्ग", "पर्यायी सुरक्षित मार्ग", "पर्यायी मार्ग",
            "રસ્તો", "વૈકલ્પિક સુરક્ષિત રસ્તો", "વૈકલ્પિક માર્ગ", "વૈકલ્પિક", "માર્ગ",
            "దారి", "సురక్షిత ప్రత్యామ్నాయం", "సురక్షిత ప్రత్యామ్నాయ మార్గం", "ప్రత్యామ్నాయ", "మార్గం",
            "பாதை", "மாற்றுப் பாதை", "பாதுகாப்பான மாற்று வழி", "மாற்று வழி", "வழி", "மாற்று"
        ],
    ),
    (
        "crowd_status",
        ["crowd", "density", "safe", "zone", "ghat", "bheed", "level", "rush", "status", "people", "crowd status"],
        [
            "भीड़", "घाट", "सुरक्षित", "स्तर", "हालत", "भीड़ स्थिति", "घाटों पर भीड़ स्थिति",
            "ভিড়", "ঘাট", "ঘাটের ভিড়",
            "गर्दी", "घाटावर", "घाटावरील गर्दी",
            "ભીડ", "ઘાટ", "ઘાટ પર ભીડ",
            "రద్దీ", "ఘాట్", "ఘాట్ రద్దీ",
            "கூட்டம்", "படித்துறை", "படித்துறை கூட்டம்"
        ],
    ),
    (
        "subscribe",
        ["alert", "notify", "subscribe", "notification", "updates"],
        ["सूचना", "अलर्ट", "सब्सक्राइब", "अपडेट"],
    ),
    (
        "unsubscribe",
        ["unsubscribe", "stop alerts", "off", "cancel alerts", "stop"],
        ["बंद", "रोको", "अनसब्सक्राइब"],
    ),
]

# Keep the dict form for any legacy callers
RULES: dict[str, tuple[list[str], list[str]]] = {
    intent: (en_kws, hi_kws)
    for intent, en_kws, hi_kws in RULES_ORDERED
}

MENU_TRIGGERS = {
    "hi", "hello", "start", "/start", "help", "/help", "menu", "/menu", "main menu", "namaste", "नमस्ते", "शुरू", "हेलो",
    "নমস্কার", "नमस्कार", "નમસ્તે", "నమస్కారం", "வணக்கம்"
}


def classify_keywords(text: str) -> str:
    """Return intent name via keyword matching. Falls back to 'menu'.

    Priority: lost_person / found_person / divert take precedence over
    crowd_status when there is keyword overlap.
    """
    lower = text.lower()

    for intent, en_kws, hi_kws in RULES_ORDERED:
        all_kws = [k.lower() for k in en_kws + hi_kws]
        if any(k in lower for k in all_kws):
            return intent

    words = set(lower.split())
    if words & MENU_TRIGGERS:
        return "menu"
    return "menu"


async def classify(text: str, language: str = "en") -> str:
    """
    Classify intent. Keyword rules first; Gemini fallback if API key present.
    Returns intent name string.
    """
    # Keyword rules first
    intent = classify_keywords(text)
    if intent != "menu":
        return intent

    # Try Gemini if key is set
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return intent

    try:
        import asyncio
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Strip digits from user text before LLM call (AGENTS.md Rule 18)
        import re
        sanitized = re.sub(r"\d+", "", text)

        prompt = (
            "Classify this pilgrim message into one of these intents: "
            "website, ticket, facilities, crowd_status, divert, lost_person, found_person, language_switch, subscribe, "
            "unsubscribe, sos, menu.\n"
            f"Message: {sanitized!r}\n"
            f"Language hint: {language}\n"
            'Respond ONLY with valid JSON like: {"intent": "crowd_status", "zone_id": null, "language": "en"}'
        )

        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: model.generate_content(prompt)
            ),
            timeout=3.0,
        )
        raw = response.text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = LLMIntentResponse.model_validate_json(raw)
        logger.info(f"Gemini intent: {parsed.intent}")
        return parsed.intent

    except Exception as exc:
        logger.warning(f"Gemini fallback triggered: {exc}")
        return "menu"


ZONE_KEYWORDS: dict[str, str] = {
    "har ki pauri": "har-ki-pauri",
    "har-ki-pauri": "har-ki-pauri",
    "हर की पौड़ी": "har-ki-pauri",
    "हर की पैड़ी": "har-ki-pauri",
    "হর কি পৌড়ী": "har-ki-pauri",
    "হর কি পৌড়ীতে": "har-ki-pauri",
    "हर की पौरी": "har-ki-pauri",
    "હર કી પૌરી": "har-ki-pauri",
    "హర్ కీ పౌరీ": "har-ki-pauri",
    "ஹர் கி பௌரி": "har-ki-pauri",
    "brahmakund": "brahmakund",
    "ब्रह्मकुंड": "brahmakund",
    "ganga ghat": "ganga-ghat-upper",
    "ganga-ghat-upper": "ganga-ghat-upper",
    "गंगा घाट": "ganga-ghat-upper",
    "subhash": "subhash-ghat",
    "subhash-ghat": "subhash-ghat",
    "सुभाष घाट": "subhash-ghat",
    "malviya": "malviya-ghat",
    "malviya-ghat": "malviya-ghat",
    "मालवीय घाट": "malviya-ghat",
    "bilkeshwar": "bilkeshwar-road",
    "bilkeshwar-road": "bilkeshwar-road",
    "बिल्केश्वर": "bilkeshwar-road",
}


def find_matching_zone_id(text: str) -> Optional[str]:
    """Find a zone_id mentioned in text, matching English or Indian language names."""
    lower = text.lower()
    for kw, zid in ZONE_KEYWORDS.items():
        if kw in lower:
            return zid
    return None
