"""Tests for chat intent classification (M4)."""
import pytest
from app.chat.intent import classify_keywords

def test_crowd_status_en():
    assert classify_keywords("how is the crowd at ghat") == "crowd_status"

def test_crowd_status_hi():
    assert classify_keywords("घाट पर भीड़ कैसी है") == "crowd_status"

def test_divert():
    assert classify_keywords("where should I go to avoid crowd") == "divert"

def test_lost():
    assert classify_keywords("I lost my child near the ghat") == "lost_person"

def test_sos():
    from app.sos import is_sos
    assert is_sos("help") is True
    assert is_sos("बचाओ") is True
    assert is_sos("hello world") is False

def test_menu_fallback():
    assert classify_keywords("xyzzy") == "menu"

def test_ticket():
    assert classify_keywords("book snan pass for ghat") == "ticket"
    assert classify_keywords("स्नान पास चाहिए") == "ticket"

def test_facilities():
    assert classify_keywords("where is the nearest medical doctor and toilet") == "facilities"
    assert classify_keywords("पानी और शौचालय कहाँ है") == "facilities"

def test_language_switch():
    assert classify_keywords("switch language to hindi") == "language_switch"
    assert classify_keywords("বাংলা language") == "language_switch"


def test_zone_matching():
    from app.chat.intent import find_matching_zone_id
    assert find_matching_zone_id("How is the crowd at Har Ki Pauri?") == "har-ki-pauri"
    assert find_matching_zone_id("हर की पौड़ी पर कितनी भीड़ है?") == "har-ki-pauri"
    assert find_matching_zone_id("subhash ghat crowd") == "subhash-ghat"
    assert find_matching_zone_id("random text") is None


def test_sos_transliterated_and_regional():
    from app.sos import is_sos
    assert is_sos("bachao") is True
    assert is_sos("madad") is True
    assert is_sos("emergency!") is True
    assert is_sos("Emergency Help / SOS") is True
    assert is_sos("জরুরি সাহায্য") is True
    assert is_sos("मदत / आपत्कालीन") is True
    assert is_sos("મદદ / કટોકટી") is True
    assert is_sos("அவசர உதவி") is True


def test_website():
    assert classify_keywords("open live dashboard") == "website"
    assert classify_keywords("show live map & website") == "website"
    assert classify_keywords("वेबसाइट दिखाएं") == "website"
    assert classify_keywords("लाइव डैशबोर्ड खोलें") == "website"
    assert classify_keywords("লাইভ ড্যাশবোর্ড") == "website"



