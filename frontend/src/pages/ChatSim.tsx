/**
 * ChatSim : web-based chat simulator for KumbhRaksha.
 * Supports 7 Indian languages (EN, HI, BN, MR, GU, TE, TA),
 * ticket/pass generation, facility assistance, and crowd diversion.
 */
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { SimBadge } from "../components/SimBadge";

interface Message {
  id: string;
  role: "user" | "bot";
  text: string;
  buttons?: string[];
  timestamp: Date;
}

const LANGUAGES = [
  { code: "en", label: "EN", name: "English" },
  { code: "hi", label: "HI", name: "हिन्दी" },
  { code: "bn", label: "BN", name: "বাংলা" },
  { code: "mr", label: "MR", name: "मराठी" },
  { code: "gu", label: "GU", name: "ગુજરાતી" },
  { code: "te", label: "TE", name: "తెలుగు" },
  { code: "ta", label: "TA", name: "தமிழ்" },
];

const QUICK_REPLIES_BY_LANG: Record<string, string[]> = {
  en: [
    "🌐 Open Live Dashboard",
    "How is the crowd at Har Ki Pauri?",
    "Book Free Snan Pass",
    "Where is nearest water and doctor?",
    "Safe Divert Route",
    "Emergency Help / SOS",
  ],
  hi: [
    "🌐 लाइव डैशबोर्ड व मैप देखें",
    "हर की पौड़ी पर कितनी भीड़ है?",
    "स्नान ई-पास बुक करें",
    "पानी व डॉक्टर कहाँ है?",
    "सुरक्षित रास्ता बताएं",
    "मदद / आपातकाल",
  ],
  bn: [
    "🌐 লাইভ ড্যাশবোর্ড ও ম্যাপ",
    "হর কি পৌড়ীতে ভিড় কেমন?",
    "স্নান ই-পাস বুক করুন",
    "পানীয় জল ও ডাক্তার কোথায়?",
    "বিকল্প রুট",
    "জরুরি সাহায্য",
  ],
  mr: [
    "🌐 थेट डॅशबोर्ड व नकाशा",
    "हर की पौरीवर गर्दी कशी आहे?",
    "स्नान ई-पास बुक करा",
    "पाणी व दवाखाना कुठे आहे?",
    "पर्यायी मार्ग",
    "मदत / आपत्कालीन",
  ],
  gu: [
    "🌐 લાઈવ ડેશબોર્ડ અને નકશો",
    "હર કી પૌરી પર ભીડ કેવી છે?",
    "સ્નાન ઇ-પાસ બુક કરો",
    "પાણી અને ડૉક્ટર ક્યાં છે?",
    "વૈકલ્પિક માર્ગ",
    "મદદ / કટોકટી",
  ],
  te: [
    "🌐 లైవ్ డాష్‌బోర్డ్ & మ్యాప్",
    "హర్ కీ పౌరీ వద్ద రద్దీ ఎలా ఉంది?",
    "స్నాన ఈ-పాస్ బుక్ చేసుకోండి",
    "మంచినీరు మరియు వైద్య కేంద్రం ఎక్కడ ఉంది?",
    "సురక్షిత ప్రత్యామ్నాయ మార్గం",
    "అత్యవసర సహాయం",
  ],
  ta: [
    "🌐 நேரலை டாஷ்போர்டு",
    "ஹர் கி பௌரியில் கூட்டம் எப்படி இருக்கிறது?",
    "நீராடல் இ-பாஸ் பதிவு செய்யவும்",
    "குடிநீர் மற்றும் மருத்துவர் எங்கே?",
    "பாதுகாப்பான மாற்று வழி",
    "அவசர உதவி",
  ],
};

const WELCOME_MESSAGES: Record<string, string> = {
  en: "Namaste! Welcome to KumbhRaksha Safety Assistant for Haridwar Maha Kumbh 2027.\n\nI can help you check ghat crowd levels, issue free Snan Time-Slot E-Passes, guide you through safe alternate routes, and find 24x7 medical or water facilities.\n\nSelect a quick service below or type your question.",
  hi: "नमस्ते! हरिद्वार महाकुम्भ 2027 सुरक्षा सहायक में आपका स्वागत है।\n\nमैं आपको घाटों पर भीड़ की स्थिति, निःशुल्क स्नान ई-पास, सुरक्षित वैकल्पिक रास्ते और 24x7 पेयजल व चिकित्सा सहायता प्रदान कर सकता हूँ।\n\nकृपया नीचे दिए गए विकल्प चुनें या अपना प्रश्न लिखें।",
  bn: "নমস্কার! হরিদ্বার মহাকুম্ভ 2027 সুরক্ষা সহায়ক-এ আপনাকে স্বাগতম।\n\nআমি আপনাকে ঘাটের ভিড়ের অবস্থা, বিনামূল্যে স্নান ই-পাস, নিরাপদ বিকল্প রুট এবং ২৪x৭ চিকিৎসা ও পানীয় জলের কেন্দ্র সম্পর্কে তথ্য দিতে পারি।",
  mr: "नमस्कार! हरिद्वार महाकुंभ 2027 सुरक्षा सहाय्यकामध्ये आपले स्वागत आहे.\n\nमी आपल्याला घाटावरील गर्दी, मोफत स्नान ई-पास, सुरक्षित पर्यायी मार्ग आणि 24x7 वैद्यकीय व पिण्याच्या पाण्याची माहिती देऊ शकतो.",
  gu: "નમસ્તે! હરિદ્વાર મહાકુંભ 2027 સુરક્ષા સહાયકમાં આપનું સ્વાગત છે.\n\nહું તમને ઘાટ પર ભીડની સ્થિતિ, મફત સ્નાન ઇ-પાસ, સુરક્ષિત વૈકલ્પિક માર્ગો અને તબીબી સુવિધાઓ વિશે માર્ગદર્શન આપી શકું છું.",
  te: "నమస్కారం! హరిద్వార్ మహాకుంభ్ 2027 భద్రతా సహాయకుడికి స్వాగతం.\n\nనేను మీకు ఘాట్ రద్దీ వివరాలు, ఉచిత స్నాన ఈ-పాస్, సురక్షిత ప్రత్యామ్నాయ మార్గాలు మరియు 24x7 వైద్య సదుపాయాల సమాచారాన్ని అందించగలను.",
  ta: "வணக்கம்! ஹரித்வார் மகாகும்பமேளா 2027 பாதுகாப்பு உதவியாளருக்கு உங்களை வரவேற்கிறோம்.\n\nபடித்துறை கூட்டம், இலவச நீராடல் இ-பாஸ், பாதுகாப்பான மாற்று வழிகள் மற்றும் 24x7 மருத்துவ வசதிகள் குறித்து நான் உதவ முடியும்.",
};

export function ChatSim() {
  const navigate = useNavigate();
  const [lang, setLang] = useState<string>("en");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "bot",
      text: WELCOME_MESSAGES["en"],
      buttons: ["🌐 Open Live Dashboard", "How is the crowd at Har Ki Pauri?", "Book Free Snan Pass", "Nearest Medical Post & Water"],
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const chatId = useRef(`web-chat-${Date.now()}`);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleButtonClick = (btnText: string) => {
    const lower = btnText.toLowerCase();
    if (
      btnText.startsWith("🌐") ||
      lower.includes("dashboard") ||
      lower.includes("लाइव डैशबोर्ड") ||
      lower.includes("ড্যাশবোর্ড") ||
      lower.includes("डॅशबोर्ड") ||
      lower.includes("ડેશબોર્ડ") ||
      lower.includes("డాష్‌బోర్డ్") ||
      lower.includes("டாஷ்போர்டு") ||
      lower.includes("live map") ||
      lower.includes("open website")
    ) {
      navigate("/");
      return;
    }
    send(btnText);
  };

  const send = async (text: string, overrideLang?: string) => {
    if (!text.trim() || sending) return;

    const currentLang = overrideLang || lang;
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      const res = await api.sendChat({
        chat_id: chatId.current,
        text,
        language: currentLang,
      });

      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        role: "bot",
        text: res.text,
        buttons: res.buttons,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "bot",
          text: "Could not reach server. Please check the backend is running.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setSending(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  };

  const handleLanguageSwitch = (newLang: string) => {
    if (newLang === lang) return;
    setLang(newLang);
    // Send a message to inform the backend and receive active language confirmation
    const langObj = LANGUAGES.find((l) => l.code === newLang);
    const switchPrompt = `Switch language to ${langObj?.name || newLang}`;
    send(switchPrompt, newLang);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  const activeQuickReplies = QUICK_REPLIES_BY_LANG[lang] || QUICK_REPLIES_BY_LANG["en"];

  return (
    <div className="chat-sim">
      <div className="chat-sim__header">
        <div>
          <h1 className="page-title">Pilgrim Safety Chat Assistant</h1>
          <p className="page-subtitle">Interactive 24x7 Multilingual Safety &amp; E-Pass Portal (Kumbh 2027)</p>
        </div>
        <div className="chat-sim__header-right">
          <SimBadge />
          <div className="lang-toggle-bar" role="group" aria-label="Select Language">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                id={`lang-${l.code}-btn`}
                className={`lang-toggle__btn ${lang === l.code ? "lang-toggle__btn--active" : ""}`}
                onClick={() => handleLanguageSwitch(l.code)}
                type="button"
                title={l.name}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="chat-sim__window">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`chat-msg chat-msg--${m.role}`}
          >
            <div className="chat-msg__bubble">
              <p className="chat-msg__text" style={{ whiteSpace: "pre-wrap" }}>{m.text}</p>
              {m.role === "bot" && (m.text.includes("LIVE PORTAL") || m.text.includes("लाइव पोर्टल") || m.text.includes("Live Portal URL") || m.text.includes("वेबसाइट लिंक")) && (
                <div style={{ marginTop: "10px", marginBottom: "4px" }}>
                  <button
                    type="button"
                    className="btn btn--primary"
                    style={{ fontSize: "0.85rem", padding: "6px 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                    onClick={() => navigate("/")}
                  >
                    <span>🗺️</span>
                    <span>{lang === "hi" ? "लाइव मैप व डैशबोर्ड खोलें" : "Open Live Map & Dashboard"}</span>
                  </button>
                </div>
              )}
              {m.buttons && m.buttons.length > 0 && (
                <div className="chat-msg__btns">
                  {m.buttons.map((b) => (
                    <button
                      key={b}
                      className="chat-msg__btn"
                      onClick={() => handleButtonClick(b)}
                      type="button"
                    >
                      {b}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <span className="chat-msg__time">
              {m.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
          </div>
        ))}
        {sending && (
          <div className="chat-msg chat-msg--bot">
            <div className="chat-msg__bubble chat-msg__bubble--typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick replies */}
      <div className="chat-sim__quick-replies">
        {activeQuickReplies.map((q) => (
          <button
            key={q}
            className="quick-reply"
            onClick={() => send(q)}
            disabled={sending}
            type="button"
          >
            {q}
          </button>
        ))}
      </div>

      <form className="chat-sim__input-row" onSubmit={handleSubmit}>
        <input
          id="chat-input"
          type="text"
          className="chat-sim__input"
          placeholder={
            lang === "hi"
              ? "संदेश लिखें (उदा. हर की पौड़ी पर भीड़, स्नान पास, पानी)..."
              : lang === "bn"
              ? "বার্তা লিখুন (যেমন স্নান পাস, ভিড়, পানীয় জল)..."
              : "Type a message (e.g. check crowd, book snan pass, nearest water)..."
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
          autoComplete="off"
        />
        <button
          id="chat-send-btn"
          type="submit"
          className="btn btn--primary chat-sim__send"
          disabled={sending || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
