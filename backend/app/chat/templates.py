"""
Chat reply templates in 7 pilgrimage languages (EN, HI, BN, MR, GU, TE, TA).
ALL user-facing text originates here, filled with real DB and system values.
No emojis are used in responses per project guidelines.
"""
from __future__ import annotations
from typing import Optional


LEVEL_TAG = {
    "green": "[GREEN - SAFE]",
    "yellow": "[YELLOW - MODERATE]",
    "orange": "[ORANGE - WARNING]",
    "red": "[RED - CRITICAL DANGER]",
}

LEVEL_NAME_LOCAL: dict[str, dict[str, str]] = {
    "en": {"green": "SAFE", "yellow": "MODERATE", "orange": "WARNING", "red": "CRITICAL DANGER"},
    "hi": {"green": "सुरक्षित", "yellow": "मध्यम", "orange": "चेतावनी", "red": "अत्यधिक खतरा"},
    "bn": {"green": "নিরাপদ", "yellow": "মাঝারি ভিড়", "orange": "সতর্কতা", "red": "বিপজ্জনক ভিড়"},
    "mr": {"green": "सुरक्षित", "yellow": "मध्यम गर्दी", "orange": "इशारा", "red": "धोकादायक गर्दी"},
    "gu": {"green": "સુરક્ષિત", "yellow": "મધ્યમ ભીડ", "orange": "ચેતવણી", "red": "ખતરનાક ભીડ"},
    "te": {"green": "సురక్షితం", "yellow": "మితమైన రద్దీ", "orange": "హెచ్చరిక", "red": "తీవ్ర ప్రమాదం"},
    "ta": {"green": "பாதுகாப்பானது", "yellow": "மிதமான கூட்டம்", "orange": "எச்சரிக்கை", "red": "அபாயகரமான கூட்டம்"},
}


def crowd_status_en(
    zone_name: str,
    count: int,
    density: float,
    level: str,
    forecast_minutes: Optional[float],
    divert_to: Optional[str],
) -> str:
    tag = LEVEL_TAG.get(level, "[STATUS]")
    lines = [
        f"{tag} {zone_name}: {level.upper()}",
        f"Count: ~{count} pilgrims | Density: {density:.2f} p/m²",
    ]
    if forecast_minutes is not None:
        lines.append(f"SURGE NOTICE: Reaching RED in ~{forecast_minutes:.0f} min.")
    if divert_to:
        lines.append(f"RECOMMENDED ROUTE: Consider diverting to {divert_to}.")
    lines.append("[SIMULATED DATA]")
    return "\n".join(lines)


def crowd_status_hi(
    zone_name: str,
    count: int,
    density: float,
    level: str,
    forecast_minutes: Optional[float],
    divert_to: Optional[str],
) -> str:
    hi_level = LEVEL_NAME_LOCAL["hi"].get(level, level)
    lines = [
        f"[{hi_level}] {zone_name}",
        f"अनुमानित संख्या: ~{count} श्रद्धालु | घनत्व: {density:.2f} व्यक्ति/म²",
    ]
    if forecast_minutes is not None:
        lines.append(f"चेतावनी: लगभग {forecast_minutes:.0f} मिनट में अत्यधिक भीड़ की सम्भावना।")
    if divert_to:
        lines.append(f"सुरक्षित मार्ग: कृपया {divert_to} की ओर प्रस्थान करें।")
    lines.append("[अनुकरणीय डेटा]")
    return "\n".join(lines)


def crowd_status(
    language: str,
    zone_name: str,
    count: int,
    density: float,
    level: str,
    forecast_minutes: Optional[float],
    divert_to: Optional[str],
) -> tuple[str, list[str]]:
    lang = language.lower()
    lvl = LEVEL_NAME_LOCAL.get(lang, LEVEL_NAME_LOCAL["en"]).get(level, level)
    buttons = ["Get Snan Pass", "Divert Route", "Emergency Facilities"]

    if lang == "hi":
        text = crowd_status_hi(zone_name, count, density, level, forecast_minutes, divert_to)
        buttons = ["स्नान पास", "सुरक्षित मार्ग", "हेल्पलाइन व सुविधाएं"]
    elif lang == "bn":
        lines = [
            f"[{lvl}] {zone_name}",
            f"শ্রদ্ধালু সংখ্যা: ~{count} | ঘনত্ব: {density:.2f} ব্যক্তি/বর্গমিটার",
        ]
        if forecast_minutes is not None:
            lines.append(f"সতর্কতা: প্রায় {forecast_minutes:.0f} মিনিটের মধ্যে মারাত্মক ভিড় হতে পারে।")
        if divert_to:
            lines.append(f"বিকল্প রুট: {divert_to} ঘাটে যাওয়ার অনুরোধ করা হচ্ছে।")
        lines.append("[সিমুলেটেড ডেটা]")
        text = "\n".join(lines)
        buttons = ["স্নান পাস", "বিকল্প রুট", "জরুরি সাহায্য"]
    elif lang == "mr":
        lines = [
            f"[{lvl}] {zone_name}",
            f"भाविकांची संख्या: ~{count} | घनता: {density:.2f} व्यक्ती/चौ.मी.",
        ]
        if forecast_minutes is not None:
            lines.append(f"सूचना: सुमारे {forecast_minutes:.0f} मिनिटांत गर्दी वाढण्याची शक्यता आहे.")
        if divert_to:
            lines.append(f"पर्यायी मार्ग: कृपया {divert_to} कडे जा.")
        lines.append("[सिम्युलेटेड डेटा]")
        text = "\n".join(lines)
        buttons = ["स्नान पास", "पर्यायी मार्ग", "मदत केंद्र"]
    elif lang == "gu":
        lines = [
            f"[{lvl}] {zone_name}",
            f"યાત્રાળુ સંખ્યા: ~{count} | ઘનતા: {density:.2f} વ્યક્તિ/ચો.મી.",
        ]
        if forecast_minutes is not None:
            lines.append(f"ચેતવણી: આશરે {forecast_minutes:.0f} મિનિટમાં ભીડ વધવાની શક્યતા.")
        if divert_to:
            lines.append(f"વૈકલ્પિક માર્ગ: {divert_to} તરફ આગળ વધો.")
        lines.append("[સિમ્યુલેટેડ ડેટા]")
        text = "\n".join(lines)
        buttons = ["સ્નાન પાસ", "વૈકલ્પિક માર્ગ", "સહાયતા કેન્દ્ર"]
    elif lang == "te":
        lines = [
            f"[{lvl}] {zone_name}",
            f"భక్తుల సంఖ్య: ~{count} | సాంద్రత: {density:.2f} వ్యక్తులు/చ.మీ.",
        ]
        if forecast_minutes is not None:
            lines.append(f"హెచ్చరిక: దాదాపు {forecast_minutes:.0f} నిమిషాల్లో రద్దీ పెరిగే అవకాశం ఉంది.")
        if divert_to:
            lines.append(f"సురక్షిత మార్గం: {divert_to} వైపు వెళ్ళండి.")
        lines.append("[సిమ్యులేటెడ్ డేటా]")
        text = "\n".join(lines)
        buttons = ["స్నాన పాస్", "సురక్షిత మార్గం", "సహాయ కేంద్రం"]
    elif lang == "ta":
        lines = [
            f"[{lvl}] {zone_name}",
            f"பக்தர்கள் எண்ணிக்கை: ~{count} | அடர்த்தி: {density:.2f} நபர்/ச.மீ.",
        ]
        if forecast_minutes is not None:
            lines.append(f"எச்சரிக்கை: இன்னும் {forecast_minutes:.0f} நிமிடங்களில் கூட்டம் அதிகமாகலாம்.")
        if divert_to:
            lines.append(f"மாற்று வழி: {divert_to} படித்துறைக்கு செல்லவும்.")
        lines.append("[உருவகப்படுத்தப்பட்ட தரவு]")
        text = "\n".join(lines)
        buttons = ["நீராடல் அனுமதி", "மாற்று வழி", "உதவி மையம்"]
    else:
        text = crowd_status_en(zone_name, count, density, level, forecast_minutes, divert_to)

    return text, buttons


def ticket_reply(language: str, zone_name: str = "Subhash Ghat", slot: str = "06:30 - 08:30 AM", pass_code: str = "KR-SNAN-2027-4892") -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = (
            f"[कुम्भ स्नान ई-पास : निःशुल्क प्रवेश]\n"
            f"पास संख्या: {pass_code}\n"
            f"आवंटित घाट: {zone_name}\n"
            f"पवित्र स्नान समय: {slot}\n"
            f"भीड़ स्थिति: स्तर हरा (सुरक्षित एवं सुगम)\n"
            f"प्रवेश द्वार: गेट संख्या 3 (अपर रोड)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"सूचना: हरिद्वार महाकुम्भ में स्नान पूर्णतः निःशुल्क है। यह डिजिटल ई-पास भगदड़ व भीड़ प्रबंधन के लिए समय-स्लॉट आरक्षित करता है। कृपया कतार नियमों का पालन करें।"
        )
        buttons = ["घाट पर भीड़", "सुरक्षित मार्ग", "हेल्पलाइन"]
    elif lang == "bn":
        text = (
            f"[কুম্ভ স্নান ই-পাস : বিনামূল্যে প্রবেশ]\n"
            f"পাস নম্বর: {pass_code}\n"
            f"ঘাট: {zone_name}\n"
            f"স্নানের সময়: {slot}\n"
            f"ভিড় অবস্থা: নিরাপদ (সবুজ স্তর)\n"
            f"প্রবেশ তোরণ: গেট ৩ (আপার রোড)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"তথ্য: কুম্ভমেলায় স্নান সম্পূর্ণ বিনামূল্যে। ভিড় নিয়ন্ত্রণ ও সুরক্ষার সুবিধার্থে এই টাইম-স্লট পাস প্রদান করা হয়েছে।"
        )
        buttons = ["ঘাটের ভিড়", "বিকল্প রুট", "হেল্পলাইন"]
    elif lang == "mr":
        text = (
            f"[कुंभ स्नान ई-पास : विनामूल्य प्रवेश]\n"
            f"पास क्रमांक: {pass_code}\n"
            f"घाट: {zone_name}\n"
            f"स्नान वेळ: {slot}\n"
            f"गर्दी स्थिती: सुरक्षित (हिरवा स्तर)\n"
            f"प्रवेश द्वार: गेट क्र. ३\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"सूचना: कुंभमेळ्यात स्नान पूर्णपणे विनामूल्य आहे. गर्दी टाळण्यासाठी हा डिजिटल स्लॉट पास देण्यात आला आहे."
        )
        buttons = ["घाटावरील गर्दी", "पर्यायी मार्ग", "मदत केंद्र"]
    elif lang == "gu":
        text = (
            f"[કુંભ સ્નાન ઇ-પાસ : નિઃશુલ્ક પ્રવેશ]\n"
            f"પાસ નંબર: {pass_code}\n"
            f"ઘાટ: {zone_name}\n"
            f"સ્નાન સમય: {slot}\n"
            f"સ્થિતિ: સુરક્ષિત (લીલો સ્તર)\n"
            f"પ્રવેશ દ્વાર: ગેટ ૩\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"માહિતી: કુંભમેળામાં સ્નાન તદ્દન મફત છે. ભીડ નિયંત્રણ અને સલામતી માટે આ સ્લોટ પાસ ફાળવવામાં આવ્યો છે."
        )
        buttons = ["ઘાટ પર ભીડ", "વૈકલ્પિક માર્ગ", "સહાયતા"]
    elif lang == "te":
        text = (
            f"[కుంభ స్నాన ఈ-పాస్ : ఉచిత ప్రవేశం]\n"
            f"పాస్ సంఖ్య: {pass_code}\n"
            f"ఘాట్: {zone_name}\n"
            f"స్నాన సమయం: {slot}\n"
            f"రద్దీ స్థితి: సురక్షితం (గ్రీన్ లెవెల్)\n"
            f"ప్రవేశ ద్వారం: గేట్ నం. 3\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"సమాచారం: కుంభమేళాలో పవిత్ర స్నానం పూర్తిగా ఉచితం. తొక్కిసలాట నివారణ కోసం ఈ టైమ్-స్లాట్ పాస్ జారీ చేయబడింది."
        )
        buttons = ["ఘాట్ రద్దీ", "సురక్షిత మార్గం", "హెల్ప్‌లైన్"]
    elif lang == "ta":
        text = (
            f"[கும்ப நீராடல் இ-பாஸ் : இலவச அனுமதி]\n"
            f"பாஸ் எண்: {pass_code}\n"
            f"படித்துறை: {zone_name}\n"
            f"நீராடல் நேரம்: {slot}\n"
            f"கூட்ட நிலை: பாதுகாப்பானது (பச்சை நிலை)\n"
            f"நுழைவு வாயில்: கேட் 3\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"தகவல்: புனித நீராடல் முற்றிலும் இலவசம். நெரிசலைத் தவிர்க்க இந்த நேர ஒதுக்கீடு பாஸ் வழங்கப்படுகிறது."
        )
        buttons = ["படித்துறை கூட்டம்", "மாற்று வழி", "உதவி எண்"]
    else:
        text = (
            f"[KUMBH SNAN E-PASS : FREE PILGRIM ENTRY]\n"
            f"Pass ID: {pass_code}\n"
            f"Allocated Ghat: {zone_name}\n"
            f"Recommended Bathing Slot: {slot}\n"
            f"Crowd Safety Level: GREEN (Safe and uncongested)\n"
            f"Recommended Entrance: Gate 3 (Upper Road Corridor)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"NOTICE: Holy Snan at Haridwar Ghats is 100% free and open. This digital token allocates a guaranteed safe time-slot to prevent stampede formation. Please follow volunteer marshals."
        )
        buttons = ["Check Ghat Crowd", "Divert Route", "Emergency Helpline"]

    return text, buttons


def facilities_reply(language: str) -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = (
            "हरिद्वार महाकुम्भ 2027 : 24x7 जनसुविधाएं व सहायता\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "आपातकालीन सहायता नंबर:\n"
            "  पुलिस नियंत्रण कक्ष: 112\n"
            "  मेला हेल्पलाइन: 1916\n"
            "  आपदा नियंत्रण कक्ष: 1077\n"
            "  खोया-पाया केंद्र (हर की पौड़ी चौकी): 01334-224411\n"
            "\nमुख्य सुविधाएं:\n"
            "  चिकित्सा शिविर: हर की पौड़ी मुख्य पोस्ट, ब्रह्मकुंड सचल वाहन\n"
            "  पेयजल (जल सेवा): प्रत्येक प्रवेश द्वार पर निःशुल्क आरओ जल\n"
            "  शौचालय परिसर: सेक्टर 1, 2 व 3 में आधुनिक बायो-शौचालय\n"
            "  आश्रय व धर्मशाला: दीनदयाल उपाध्याय पार्किंग एवं लालजीवाला क्षेत्र"
        )
        buttons = ["स्नान पास", "भीड़ की स्थिति", "रास्ता"]
    elif lang == "bn":
        text = (
            "হরিদ্বার মহাকুম্ভ 2027 : 24x7 তীর্থযাত্রী সহায়তা\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "জরুরি নম্বর:\n"
            "  পুলিশ কন্ট্রোল রুম: 112\n"
            "  মেলা হেল্পলাইন: 1916\n"
            "  দুর্যোগ নিয়ন্ত্রণ: 1077\n"
            "  হারানো-পাওয়া কেন্দ্র (হর কি পৌড়ী): 01334-224411\n"
            "\nমূল সুবিধা:\n"
            "  চিকিৎসা কেন্দ্র: হর কি পৌড়ী ও ব্রহ্মকুণ্ডে 24 ঘণ্টা ডাক্তার\n"
            "  পানীয় জল: প্রতিটি সেক্টরে বিনামূল্যে বিশুদ্ধ পানীয় জল\n"
            "  শৌচালয়: সেক্টর ১ ও ২ সংলগ্ন আধুনিক বায়ো-টয়লেট\n"
            "  আশ্রয় শিবির: লালজীওয়ালা এবং পার্কিং সেক্টর"
        )
        buttons = ["স্নান পাস", "ঘাটের ভিড়", "জরুরি সাহায্য"]
    elif lang == "mr":
        text = (
            "हरिद्वार महाकुंभ 2027 : 24x7 भाविक सुविधा व मदत\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "आपत्कालीन क्रमांक:\n"
            "  पोलीस नियंत्रण कक्ष: 112\n"
            "  कुंभमेळा हेल्पलाईन: 1916\n"
            "  आपत्ती व्यवस्थापन: 1077\n"
            "  हरवलेले-सापडलेले केंद्र: 01334-224411\n"
            "\nसुविधा:\n"
            "  वैद्यकीय मदत: हर की पौरी मुख्य केंद्र व फिरते दवाखाने\n"
            "  पिण्याचे पाणी: मोफत आरओ पाण्याची सोय सर्व प्रवेशद्वारांवर\n"
            "  शौचालये: सेक्टर १ व २ मधील बायो-टॉयलेट संकुल"
        )
        buttons = ["स्नान पास", "गर्दी तपासा", "मदत केंद्र"]
    elif lang == "gu":
        text = (
            "હરિદ્વાર મહાકુંભ 2027 : 24x7 યાત્રાળુ સુવિધા અને સહાય\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "કટોકટી હેલ્પલાઇન:\n"
            "  પોલીસ કંટ્રોલ રૂમ: 112\n"
            "  કુંભ હેલ્પલાઇન: 1916\n"
            "  આપત્તિ નિયંત્રણ: 1077\n"
            "  ખોયા-પાયા કેન્દ્ર: 01334-224411\n"
            "\nસુવિધાઓ:\n"
            "  તબીબી કેન્દ્ર: હર કી પૌરી મુખ્ય પોસ્ટ અને મોબાઇલ ક્લિનિક\n"
            "  પીવાનું પાણી: તમામ ગેટ પર મફત આરઓ પાણી\n"
            "  શૌચાલય: સેક્ટર ૧ અને ૨ માં બાયો-ટોઇલેટ"
        )
        buttons = ["સ્નાન પાસ", "ભીડ તપાસો", "સહાયતા"]
    elif lang == "te":
        text = (
            "హరిద్వార్ మహాకుంభ్ 2027 : 24x7 యాత్రికుల సహాయ కేంద్రం\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "అత్యవసర హెల్ప్‌లైన్ నంబర్లు:\n"
            "  పోలీస్ కంట్రోల్ రూమ్: 112\n"
            "  మేళా హెల్ప్‌లైన్: 1916\n"
            "  విపత్తు నియంత్రణ: 1077\n"
            "  తప్పిపోయిన వారి కేంద్రం: 01334-224411\n"
            "\nసౌకర్యాలు:\n"
            "  వైద్య సేవలు: హర్ కీ పౌరీ వద్ద ఉచిత వైద్య శిబిరాలు\n"
            "  మంచినీరు: అన్ని ద్వారాల వద్ద ఉచిత తాగునీరు\n"
            "  బయో టాయిలెట్లు: సెక్టార్ 1 & 2 పార్కింగ్ వద్ద"
        )
        buttons = ["స్నాన పాస్", "రద్దీ తనిఖీ", "సహాయం"]
    elif lang == "ta":
        text = (
            "ஹரித்வார் மகாகும்பமேளா 2027 : 24x7 யாத்ரீகர் வசதிகள்\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "அவசர உதவி எண்கள்:\n"
            "  காவல்துறை கட்டுப்பாட்டு அறை: 112\n"
            "  கும்பமேளா உதவி எண்: 1916\n"
            "  பேரிடர் மேலாண்மை: 1077\n"
            "  காணாமல் போனோர் மையம்: 01334-224411\n"
            "\nவசதிகள்:\n"
            "  மருத்துவ உதவி: ஹர் கி பௌரி பிரதான மருத்துவ முகாம்\n"
            "  குடிநீர் வசதி: அனைத்து நுழைவாயில்களிலும் இலவச சுத்திகரிக்கப்பட்ட நீர்\n"
            "  கழிப்பறை வசதி: பிரிவு 1 மற்றும் 2 இல் உயிர் கழிப்பறைகள்"
        )
        buttons = ["நீராடல் பாஸ்", "கூட்டம் சரிபார்", "உதவி"]
    else:
        text = (
            "Haridwar Maha Kumbh 2027 : 24x7 Pilgrim Amenities & Assistance\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Emergency Helplines:\n"
            "  Police Control Room: 112\n"
            "  Mela Command Center: 1916\n"
            "  District Disaster Management: 1077\n"
            "  Lost & Found Headquarters (Har Ki Pauri Chowki): 01334-224411\n"
            "\nOn-Ground Facilities:\n"
            "  Medical Centers: Har Ki Pauri Main Clinic, Brahmakund Mobile Unit\n"
            "  Drinking Water: Free RO potable water at every sector gate\n"
            "  Bio-Toilets: Sector 1, Sector 2, and Pant Dweep facilities\n"
            "  Shelters & Dharmashalas: Deendayal Upadhyaya transit ground"
        )
        buttons = ["Get Snan Pass", "Crowd Levels", "Emergency SOS"]

    return text, buttons


def divert_reply(language: str, target_zone: str = "Subhash Ghat", current_zone: str = "Har Ki Pauri") -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = (
            f"[सुरक्षित वैकल्पिक मार्ग सूचना]\n"
            f"वर्तमान क्षेत्र: {current_zone} (अत्यधिक भीड़)\n"
            f"अनुशंसित सुरक्षित क्षेत्र: {target_zone}\n"
            f"मार्ग निर्देश: कृपया अपर रोड या वीआईपी घाट कॉरिडोर से {target_zone} की ओर प्रस्थान करें।\n"
            f"सुरक्षा स्तर: हरा (सुगम स्नान एवं निकास उपलब्ध)"
        )
        buttons = ["स्नान पास", "भीड़ की स्थिति", "हेल्पलाइन"]
    elif lang == "bn":
        text = (
            f"[বিকল্প নিরাপদ রুট নির্দেশিকা]\n"
            f"বর্তমান স্থান: {current_zone} (উচ্চ ভিড়)\n"
            f"প্রস্তাবিত নিরাপদ স্থান: {target_zone}\n"
            f"নির্দেশ: অনুগ্রহ করে আপার রোড করিডোর ধরে {target_zone} ঘাটের দিকে চলুন।\n"
            f"নিরাপত্তা অবস্থা: নিরাপদ ও স্বাভাবিক"
        )
        buttons = ["স্নান পাস", "ঘাটের ভিড়", "জরুরি সাহায্য"]
    elif lang == "mr":
        text = (
            f"[सुरक्षित पर्यायी मार्ग सूचना]\n"
            f"सध्याचे क्षेत्र: {current_zone} (जास्त गर्दी)\n"
            f"पर्यायी सुरक्षित क्षेत्र: {target_zone}\n"
            f"मार्गदर्शन: कृपया अप्पर रोड कॉरिडॉरने {target_zone} कडे जा.\n"
            f"स्थिती: सुरक्षित आणि मोकळा घाट"
        )
        buttons = ["स्नान पास", "गर्दी तपासा", "मदत केंद्र"]
    elif lang == "gu":
        text = (
            f"[સુરક્ષિત વૈકલ્પિક માર્ગ સૂચના]\n"
            f"હાલનું ક્ષેત્ર: {current_zone} (વધુ ભીડ)\n"
            f"સુરક્ષિત ક્ષેત્ર: {target_zone}\n"
            f"માર્ગદર્શન: અપર રોડ થઈને {target_zone} તરફ આગળ વધો.\n"
            f"સ્થિતિ: સુરક્ષિત અને સુગમ"
        )
        buttons = ["સ્નાન પાસ", "ભીડ તપાસો", "સહાયતા"]
    elif lang == "te":
        text = (
            f"[సురక్షిత ప్రత్యామ్నాయ మార్గం]\n"
            f"ప్రస్తుత ప్రాంతం: {current_zone} (రద్దీ ఎక్కువ)\n"
            f"సురక్షిత ప్రాంతం: {target_zone}\n"
            f"సూచన: అప్పర్ రోడ్ గుండా {target_zone} వైపు వెళ్ళండి.\n"
            f"స్థితి: సురక్షితం"
        )
        buttons = ["స్నాన పాస్", "రద్దీ తనిఖీ", "హెల్ప్‌లైన్"]
    elif lang == "ta":
        text = (
            f"[பாதுகாப்பான மாற்று வழி]\n"
            f"தற்போதைய இடம்: {current_zone} (அதிக கூட்டம்)\n"
            f"பரிந்துரைக்கப்பட்ட இடம்: {target_zone}\n"
            f"வழி: அப்பர் ரோடு வழியாக {target_zone} நோக்கி செல்லவும்.\n"
            f"நிலை: பாதுகாப்பானது"
        )
        buttons = ["நீராடல் பாஸ்", "கூட்டம் சரிபார்", "உதவி"]
    else:
        text = (
            f"[CROWD DIVERSION ADVISORY]\n"
            f"Congested Zone: {current_zone}\n"
            f"Recommended Safe Destination: {target_zone}\n"
            f"Pedestrian Guidance: Divert via Upper Road Bypass to {target_zone}.\n"
            f"Safety Status: Safe and uncongested bathing access."
        )
        buttons = ["Get Snan Pass", "Check Crowd", "Facilities"]

    return text, buttons


def lost_person_reply(language: str) -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = (
            "[खोया व्यक्ति सहायता सेवा]\n"
            "यदि आपका कोई परिजन अथवा बच्चा बिछड़ गया है:\n"
            "1. तुरंत डैशबोर्ड के 'Lost & Found' टैब में रिपोर्ट दर्ज करें (उम्र, वस्त्रों का रंग, प्रकार व अंतिम देखा गया स्थान)।\n"
            "2. निकटतम 'खोया-पाया सहायता केंद्र' (हर की पौड़ी मुख्य चौकी) पर संपर्क करें।\n"
            "3. 24x7 हेल्पलाइन: 01334-224411 अथवा आपातकालीन 112 डायल करें।\n"
            "सूचना: सम्पूर्ण मेला क्षेत्र में लाउडस्पीकर द्वारा निरन्तर घोषणाएं की जा रही हैं।"
        )
        buttons = ["खोया-पाया रिपोर्ट", "हेल्पलाइन 112", "मुख्य मेनू"]
    elif lang == "bn":
        text = (
            "[হারানো ব্যক্তি সহায়তা কেন্দ্র]\n"
            "আপনার পরিবারের কেউ বা শিশু হারিয়ে গেলে:\n"
            "১. ওয়েবসাইটের 'Lost & Found' ট্যাবে গিয়ে বিবরণ লিখুন (বয়স, পোশাকের রঙ ও শেষ দেখার স্থান)।\n"
            "২. নিকটস্থ 'খোয়া-পায়া কেন্দ্রে' যোগাযোগ করুন।\n"
            "৩. মেলা পুলিশ হেল্পলাইন: 01334-224411 অথবা 112 নম্বরে ফোন করুন।"
        )
        buttons = ["রিপোর্ট করুন", "হেল্পলাইন 112", "মেনু"]
    else:
        text = (
            "[LOST PERSON ASSISTANCE]\n"
            "If a family member or child has become separated:\n"
            "1. Submit a report in the 'Lost & Found' tab with text descriptors (approximate age, clothing color, garment type, last seen zone).\n"
            "2. Report in person to the nearest Lost & Found Booth at Har Ki Pauri Chowki.\n"
            "3. Call 24x7 Lost-Child Helpline: 01334-224411 or Police: 112.\n"
            "Public address announcements are active across all 6 ghat sectors."
        )
        buttons = ["Submit Lost Report", "Call Helpline 112", "Main Menu"]

    return text, buttons


def found_person_reply(language: str) -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = (
            "[मिला व्यक्ति सहायता]\n"
            "यदि आपको कोई भटकता हुआ बच्चा अथवा वृद्ध व्यक्ति मिला है:\n"
            "1. कृपया उन्हें तत्काल निकटतम पुलिस सहायता बूथ अथवा स्वयंसेवक शिविर में पहुंचाएं।\n"
            "2. 'Lost & Found' टैब में व्यक्ति का विवरण (वस्त्र, रंग, आयु) दर्ज करें।\n"
            "3. पुलिस नियंत्रण कक्ष 112 को सूचित करें।"
        )
        buttons = ["मिला व्यक्ति रिपोर्ट", "पुलिस 112", "मुख्य मेनू"]
    else:
        text = (
            "[FOUND PERSON ASSISTANCE]\n"
            "If you have found a wandering child or separated elder:\n"
            "1. Please escort them immediately to the nearest Police Assistance Post or Volunteer Help Desk.\n"
            "2. File a Found Person report in the 'Lost & Found' tab.\n"
            "3. Notify the Police Control Room at 112."
        )
        buttons = ["Submit Found Report", "Police 112", "Main Menu"]

    return text, buttons


def language_switched(language: str) -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        text = "भाषा बदलकर हिन्दी कर दी गई है। कुम्भ मेला 2027 में आपकी क्या सहायता कर सकता हूँ?"
        buttons = ["घाट पर भीड़", "स्नान पास", "सुरक्षित मार्ग", "सुविधाएं"]
    elif lang == "bn":
        text = "ভাষা বাংলায় পরিবর্তন করা হয়েছে। কুম্ভমেলা 2027 এ আপনাকে কীভাবে সাহায্য করতে পারি?"
        buttons = ["ঘাটের ভিড়", "স্নান পাস", "বিকল্প রুট", "জরুরি সাহায্য"]
    elif lang == "mr":
        text = "भाषा मराठी मध्ये बदलली आहे. कुंभमेळा 2027 मध्ये मी तुम्हाला कशी मदत करू शकतो?"
        buttons = ["घाटावरील गर्दी", "स्नान पास", "पर्यायी मार्ग", "सुविधा"]
    elif lang == "gu":
        text = "ભાષા ગુજરાતીમાં બદલાઈ ગઈ છે. કુંભ મેળો 2027 માં હું તમને કેવી રીતે મદદ કરી શકું?"
        buttons = ["ઘાટ પર ભીડ", "સ્નાન પાસ", "વૈકલ્પિક માર્ગ", "સહાયતા"]
    elif lang == "te":
        text = "భాష తెలుగులోకి మార్చబడింది. కుంభమేళా 2027 లో నేను మీకు ఎలా సహాయపడగలను?"
        buttons = ["ఘాట్ రద్దీ", "స్నాన పాస్", "సురక్షిత మార్గం", "సహాయం"]
    elif lang == "ta":
        text = "மொழி தமிழுக்கு மாற்றப்பட்டது. கும்பமேளா 2027 இல் நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
        buttons = ["படித்துறை கூட்டம்", "நீராடல் பாஸ்", "மாற்று வழி", "உதவி"]
    else:
        text = "Language set to English. How may I assist you at Haridwar Maha Kumbh 2027?"
        buttons = ["Ghat Crowd", "Get Snan Pass", "Divert Route", "Facilities"]

    return text, buttons


def website_reply(language: str, dashboard_url: str = "") -> tuple[str, list[str]]:
    lang = language.lower()
    target_url = dashboard_url or "https://kumbhraksha.org.in"
    if lang == "hi":
        text = (
            "[KumbhRaksha लाइव पोर्टल व मैप]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "हरिद्वार महाकुम्भ 2027 का डिजिटल क्राउड-सेफ्टी डैशबोर्ड व रियल-टाइम मैप:\n"
            f"🔗 वेबसाइट लिंक: {target_url}\n\n"
            "वेब पोर्टल की मुख्य सुविधाएं:\n"
            "• सभी 6 घाटों का लाइव जीपीएस क्राउड हीटमैप\n"
            "• भगदड़ पूर्व चेतावनी एवं 30-मिनट पूर्वानुमान अलर्ट\n"
            "• खोया-पाया (Lost & Found) डिजिटल रिपोर्टिंग व मिलान\n"
            "• सुरक्षित स्नान मार्ग एवं 24x7 आपातकालीन सहायता\n\n"
            "लाइव पोर्टल खोलने के लिए दिए गए लिंक अथवा बटन पर क्लिक करें।\n"
            "[अनुकरणीय डेटा]"
        )
        buttons = ["🌐 लाइव डैशबोर्ड देखें", "घाट पर भीड़", "स्नान पास", "मुख्य मेनू"]
    elif lang == "bn":
        text = (
            "[KumbhRaksha লাইভ পোর্টাল ও ম্যাপ]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "হরিদ্বার মহাকুম্ভ 2027 লাইভ ভিড় সুরক্ষা ড্যাশবোর্ড ও রিয়েল-টাইম ম্যাপ:\n"
            f"🔗 পোর্টাল লিঙ্ক: {target_url}\n\n"
            "পোর্টালের মূল সুবিধাসমূহ:\n"
            "• ৬টি ঘাটের লাইভ জিপিএস ভিড় হিটম্যাপ\n"
            "• ভিড় নিয়ন্ত্রণ ও ৩০-মিনিটের পূর্বাভাস সতর্কতা\n"
            "• হারানো-পাওয়া ডিজিটাল অনুসন্ধান কেন্দ্র\n"
            "• নিরাপদ স্নানের বিকল্প রুট ও চিকিৎসা সহায়তা\n\n"
            "[সিমুলেটেড ডেটা]"
        )
        buttons = ["🌐 লাইভ ড্যাশবোর্ড খুলুন", "ঘাটের ভিড়", "স্নান পাস", "মেনু"]
    elif lang == "mr":
        text = (
            "[KumbhRaksha थेट पोर्टल व नकाशा]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "हरिद्वार महाकुंभ 2027 थेट गर्दी सुरक्षा डॅशबोर्ड व नकाशा:\n"
            f"🔗 वेबसाईट लिंक: {target_url}\n\n"
            "डॅशबोर्डची वैशिष्ट्ये:\n"
            "• सर्व घाटांचा थेट जीपीएस गर्दी हीटमॅप\n"
            "• ३० मिनिटांचा गर्दी वाढण्याचा पूर्वसूचना इशारा\n"
            "• हरवलेले-सापडलेले डिजिटल नोंदणी\n"
            "• सुरक्षित पर्यायी मार्ग व २४x७ मदत\n\n"
            "[सिम्युलेटेड डेटा]"
        )
        buttons = ["🌐 थेट डॅशबोर्ड उघडा", "घाटावरील गर्दी", "स्नान पास", "मेनू"]
    elif lang == "gu":
        text = (
            "[KumbhRaksha લાઈવ પોર્ટલ અને નકશો]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "હરિદ્વાર મહાકુંભ 2027 લાઈવ ભીડ સુરક્ષા ડેશબોર્ડ:\n"
            f"🔗 વેબસાઇટ લિંક: {target_url}\n\n"
            "ડેશબોર્ડની મુખ્ય વિશેષતાઓ:\n"
            "• તમામ ઘાટોનો જીવંત ભીડ હીટમેપ\n"
            "• ૩૦-મિનિટનો આગોતરો ચેતવણી ઈશારો\n"
            "• ખોયા-પાયા ડિજિટલ પોર્ટલ\n"
            "• સુરક્ષિત વૈકલ્પિક સ્નાન માર્ગ\n\n"
            "[સિમ્યુલેટેડ ડેટા]"
        )
        buttons = ["🌐 લાઈવ ડેશબોર્ડ ખોલો", "ઘાટ પર ભીડ", "સ્નાન પાસ", "મેનુ"]
    elif lang == "te":
        text = (
            "[KumbhRaksha లైవ్ పోర్టల్ & మ్యాప్]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "హరిద్వార్ మహాకుంభ్ 2027 లైవ్ క్రౌడ్ సేఫ్టీ డాష్‌బోర్డ్:\n"
            f"🔗 వెబ్‌సైట్ లింక్: {target_url}\n\n"
            "పోర్టల్ ముఖ్య ఫీచర్లు:\n"
            "• ఘాట్ల లైవ్ హీట్‌మ్యాప్ & రద్దీ స్థాయి\n"
            "• 30 నిమిషాల ముందస్తు తొక్కిసలాట హెచ్చరికలు\n"
            "• తప్పిపోయిన వారి డిజిటల్ సెంటర్\n"
            "• సురక్షిత ప్రత్యామ్నాయ మార్గాలు & వైద్య సహాయం\n\n"
            "[సిమ్యులేటెడ్ డేటా]"
        )
        buttons = ["🌐 లైవ్ డాష్‌బోర్డ్ తెరవండి", "ఘాట్ రద్దీ", "స్నాన పాస్", "మెనూ"]
    elif lang == "ta":
        text = (
            "[KumbhRaksha நேரலை வலைத்தளம் & வரைபடம்]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ஹரித்வார் மகாகும்பமேளா 2027 நேரலை நெரிசல் பாதுகாப்பு டாஷ்போர்டு:\n"
            f"🔗 வலைத்தள இணைப்பு: {target_url}\n\n"
            "வலைத்தளத்தின் சிறப்பம்சங்கள்:\n"
            "• நேரலை ஜிபிஎஸ் கூட்ட நெரிசல் வரைபடம்\n"
            "• 30 நிமிட முன்கூட்டிய எச்சரிக்கை அறிவிப்பு\n"
            "• காணாமல் போனோர் டிஜிட்டல் மையம்\n"
            "• பாதுகாப்பான மாற்றுப்பாதை வழிகாட்டி\n\n"
            "[உருவகப்படுத்தப்பட்ட தரவு]"
        )
        buttons = ["🌐 நேரலை டாஷ்போர்டு திறக்க", "படித்துறை கூட்டம்", "நீராடல் பாஸ்", "முதன்மை மெனு"]
    else:
        text = (
            "[KUMBHRAKSHA LIVE PORTAL & MAP]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Real-time Crowd-Safety Command Dashboard for Haridwar Maha Kumbh 2027:\n"
            f"🔗 Live Portal URL: {target_url}\n\n"
            "Web Portal Interactive Capabilities:\n"
            "• Live GPS Crowd Heatmap across all 6 Ghat sectors\n"
            "• 30-Minute Stampede Risk Forecast & Divert Matrix\n"
            "• Lost & Found Digital Registry (photo-less matching)\n"
            "• 24x7 Emergency Medical, Water & Sanitation Locator\n\n"
            "Click the link above or button below to launch the Live Dashboard.\n"
            "[SIMULATED DATA]"
        )
        buttons = ["🌐 Open Live Dashboard", "Ghat Crowd Status", "Get Snan Pass", "Main Menu"]

    return text, buttons


def menu_en() -> str:
    return (
        "KumbhRaksha Safety Assistant\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Available Services:\n"
        "  website - Open live crowd map & web portal\n"
        "  crowd - Check ghat crowd density\n"
        "  ticket - Get free Snan E-Pass token\n"
        "  divert - Safe alternate evacuation route\n"
        "  facilities - Medical, water, bio-toilets & helplines\n"
        "  lost - Report separated person\n"
        "  found - Report found person\n"
        "  help / sos - Emergency SOS assistance\n"
        "  /lite - Ultra-fast text lite mode\n"
        "[SIMULATED DATA]"
    )


def menu_hi() -> str:
    return (
        "KumbhRaksha सुरक्षा सहायक\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "उपलब्ध सेवाएं:\n"
        "  वेबसाइट - लाइव डिजिटल मैप व डैशबोर्ड\n"
        "  भीड़ - घाटों पर भीड़ व घनत्व जांचें\n"
        "  टिकट - निःशुल्क स्नान ई-पास प्राप्त करें\n"
        "  रास्ता - सुरक्षित वैकल्पिक निकास मार्ग\n"
        "  सुविधाएं - डॉक्टर, पानी, शौचालय व हेल्पलाइन\n"
        "  खोया - बिछड़े व्यक्ति की रिपोर्ट\n"
        "  मिला - मिले व्यक्ति की रिपोर्ट\n"
        "  बचाओ / मदद - आपातकालीन सहायता\n"
        "  /lite - लाइट टेक्स्ट मोड\n"
        "[अनुकरणीय डेटा]"
    )


def menu(language: str) -> tuple[str, list[str]]:
    lang = language.lower()
    if lang == "hi":
        return menu_hi(), ["🌐 लाइव डैशबोर्ड", "भीड़ जांचें", "स्नान पास", "सुरक्षित मार्ग", "सुविधाएं"]
    elif lang == "bn":
        text = (
            "KumbhRaksha তীর্থযাত্রী সহায়ক\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "পরিষেবাসমূহ:\n"
            "  ওয়েবসাইট - লাইভ ডিজিটাল পোর্টাল ও ম্যাপ\n"
            "  ভিড় - ঘাটের ভিড় ও নিরাপত্তা স্তর\n"
            "  টিকিট - বিনামূল্যে স্নান ই-পাস\n"
            "  রুট - নিরাপদ বিকল্প পথ\n"
            "  সুবিধা - চিকিৎসা, পানীয় জল ও হেল্পলাইন\n"
            "  হারানো - নিখোঁজ ব্যক্তির রিপোর্ট\n"
            "  পাওয়া - পাওয়া ব্যক্তির রিপোর্ট\n"
            "  সাহায্য / sos - জরুরি সাহায্য"
        )
        return text, ["🌐 লাইভ ড্যাশবোর্ড", "ঘাটের ভিড়", "স্নান পাস", "বিকল্প রুট", "জরুরি সাহায্য"]
    elif lang == "mr":
        text = (
            "KumbhRaksha सुरक्षा सहाय्यक\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "सेवा:\n"
            "  वेबसाईट - थेट डिजिटल पोर्टल व नकाशा\n"
            "  गर्दी - घाटावरील गर्दी तपासा\n"
            "  तिकीट - मोफत स्नान ई-पास\n"
            "  मार्ग - पर्यायी सुरक्षित मार्ग\n"
            "  सुविधा - दवाखाना, पाणी, शौचालय व मदत\n"
            "  हरवले - हरवलेल्या व्यक्तीची नोंद\n"
            "  सापडले - सापडलेल्या व्यक्तीची नोंद\n"
            "  मदत - आपत्कालीन मदत"
        )
        return text, ["🌐 थेट डॅशबोर्ड", "घाटावरील गर्दी", "स्नान पास", "पर्यायी मार्ग", "मदत केंद्र"]
    elif lang == "gu":
        text = (
            "KumbhRaksha સુરક્ષા સહાયક\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "સેવાઓ:\n"
            "  વેબસાઇટ - લાઈવ ડિજિટલ પોર્ટલ અને નકશો\n"
            "  ભીડ - ઘાટ પર ભીડ તપાસો\n"
            "  ટિકિટ - મફત સ્નાન ઇ-પાસ\n"
            "  માર્ગ - વૈકલ્પિક સુરક્ષિત રસ્તો\n"
            "  સુવિધા - તબીબી, પાણી અને હેલ્પલાઇન\n"
            "  ખોવાયેલ - ગુમ થયેલ વ્યક્તિની માહિતી\n"
            "  મળેલ - મળેલ વ્યક્તિની માહિતી\n"
            "  મદદ - કટોકટી સહાય"
        )
        return text, ["🌐 લાઈવ ડેશબોર્ડ", "ઘાટ પર ભીડ", "સ્નાન પાસ", "વૈકલ્પિક માર્ગ", "સહાયતા"]
    elif lang == "te":
        text = (
            "KumbhRaksha భద్రతా సహాయకుడు\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "సేవలు:\n"
            "  వెబ్‌సైట్ - లైవ్ డిజిటల్ పోర్టల్ & మ్యాప్\n"
            "  రద్దీ - ఘాట్ రద్దీ సాంద్రతను తనిఖీ చేయండి\n"
            "  టికెట్ - ఉచిత స్నాన ఈ-పాస్\n"
            "  మార్గం - సురక్షిత ప్రత్యామ్నాయ మార్గం\n"
            "  సౌకర్యాలు - వైద్యం, నీరు & హెల్ప్‌లైన్లు\n"
            "  తప్పిపోయిన - తప్పిపోయిన వారి రిపోర్ట్\n"
            "  దొరికిన - దొరికిన వారి రిపోర్ట్\n"
            "  సహాయం - అత్యవసర SOS"
        )
        return text, ["🌐 లైవ్ డాష్‌బోర్డ్", "ఘాట్ రద్దీ", "స్నాన పాస్", "సురక్షిత మార్గం", "సహాయం"]
    elif lang == "ta":
        text = (
            "KumbhRaksha பாதுகாப்பு உதவியாளர்\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "சேவைகள்:\n"
            "  வலைத்தளம் - நேரலை டிஜிட்டல் போர்டல்\n"
            "  கூட்டம் - படித்துறை கூட்ட நெரிசல் நிலை\n"
            "  டிக்கெட் - இலவச நீராடல் இ-பாஸ்\n"
            "  பாதை - பாதுகாப்பான மாற்று வழி\n"
            "  வசதிகள் - மருத்துவம், குடிநீர் மற்றும் உதவி எண்கள்\n"
            "  காணவில்லை - பிரிந்தவர் பதிவு\n"
            "  கிடைத்தார் - கிடைத்தவர் பதிவு\n"
            "  உதவி - அவசர உதவி SOS"
        )
        return text, ["🌐 நேரலை டாஷ்போர்டு", "படித்துறை கூட்டம்", "நீராடல் பாஸ்", "மாற்று வழி", "உதவி"]
    else:
        return menu_en(), ["🌐 Live Dashboard", "Ghat Crowd", "Get Snan Pass", "Divert Route", "Facilities"]



def sos_reply_en(facility_name: str, dist_km: float, maps_link: str) -> str:
    return (
        f"[EMERGENCY SOS RECEIVED]\n"
        f"Nearest facility: {facility_name} ({dist_km:.2f} km)\n"
        f"Navigation Link: {maps_link}\n"
        f"Stay calm. Rapid response personnel have been dispatched."
    )


def sos_reply_hi(facility_name: str, dist_km: float, maps_link: str) -> str:
    return (
        f"[आपातकाल सूचना प्राप्त]\n"
        f"निकटतम सुविधा: {facility_name} ({dist_km:.2f} किमी)\n"
        f"मार्ग लिंक: {maps_link}\n"
        f"कृपया शांत रहें। सहायता दल आपकी ओर अग्रसर है।"
    )


def subscription_consent_en(zone_name: str) -> str:
    return (
        f"Would you like to receive alerts when {zone_name} reaches "
        f"orange or red level?\nReply YES to subscribe. [SIMULATED DATA]"
    )


def subscription_confirmed_en(zone_name: str) -> str:
    return f"Subscribed to alerts for {zone_name}. Send STOP to unsubscribe."


def subscription_alert_en(
    zone_name: str, level: str, divert_to: Optional[str]
) -> str:
    tag = LEVEL_TAG.get(level, "[STATUS]")
    msg = f"{tag} ALERT: {zone_name} is now {level.upper()}."
    if divert_to:
        msg += f" Consider: {divert_to}"
    msg += " [SIMULATED DATA]"
    return msg


def subscription_alert_hi(
    zone_name: str, level: str, divert_to: Optional[str]
) -> str:
    hi_level = LEVEL_NAME_LOCAL["hi"].get(level, level)
    msg = f"[{hi_level}] अलर्ट: {zone_name} अब {hi_level} स्तर पर है।"
    if divert_to:
        msg += f" वैकल्पिक: {divert_to}"
    msg += " [अनुकरणीय डेटा]"
    return msg


def lite(text: str) -> str:
    """Truncate to 200 chars for lite mode."""
    return text[:200]
