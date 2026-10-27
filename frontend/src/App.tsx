import { useState } from "react";
import { BrowserRouter, NavLink, Route, Routes, Link } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { LostFound } from "./pages/LostFound";
import { ChatSim } from "./pages/ChatSim";
import { PrivacyPolicy } from "./pages/PrivacyPolicy";
import { TermsAndConditions } from "./pages/TermsAndConditions";
import "./App.css";

function Nav() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="app-nav" aria-label="Main navigation">
      {/* Logo / Brand */}
      <Link to="/" className="app-nav__brand" aria-label="KumbhRaksha home">
        <svg className="app-nav__brand-logo" viewBox="0 0 32 32" fill="none" aria-hidden="true">
          <path d="M16 3 L28 9 L28 21 C28 27 22 30 16 31 C10 30 4 27 4 21 L4 9 Z" fill="#e87c00"/>
          <rect x="14.5" y="10" width="3" height="11" rx="1" fill="white"/>
          <rect x="10" y="10" width="2.5" height="6" rx="1" fill="white"/>
          <rect x="19.5" y="10" width="2.5" height="6" rx="1" fill="white"/>
          <rect x="10" y="14.5" width="12" height="1.5" rx="0.75" fill="white"/>
          <rect x="14.5" y="21" width="3" height="2.5" rx="1" fill="white"/>
        </svg>
        <span className="app-nav__brand-name">
          Kumbh<span className="app-nav__brand-accent">Raksha</span>
        </span>
      </Link>

      {/* Desktop nav links */}
      <div className="app-nav__links">
        <NavLink
          id="nav-dashboard"
          to="/"
          end
          className={({ isActive }) =>
            `app-nav__link ${isActive ? "app-nav__link--active" : ""}`
          }
        >
          Dashboard
        </NavLink>
        <NavLink
          id="nav-lost-found"
          to="/lost-found"
          className={({ isActive }) =>
            `app-nav__link ${isActive ? "app-nav__link--active" : ""}`
          }
        >
          Lost &amp; Found
        </NavLink>
        <NavLink
          id="nav-chat"
          to="/chat"
          className={({ isActive }) =>
            `app-nav__link ${isActive ? "app-nav__link--active" : ""}`
          }
        >
          Chat Simulator
        </NavLink>
      </div>

      {/* Mobile hamburger */}
      <button
        className="app-nav__hamburger"
        aria-label="Toggle navigation menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((o) => !o)}
      >
        <span />
        <span />
        <span />
      </button>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div className="app-nav__mobile-menu" onClick={() => setMenuOpen(false)}>
          <NavLink id="nav-dashboard-m" to="/" end className="app-nav__mobile-link">
            Dashboard
          </NavLink>
          <NavLink id="nav-lost-found-m" to="/lost-found" className="app-nav__mobile-link">
            Lost &amp; Found
          </NavLink>
          <NavLink id="nav-chat-m" to="/chat" className="app-nav__mobile-link">
            Chat Simulator
          </NavLink>
        </div>
      )}
    </nav>
  );
}

function Footer() {
  return (
    <footer className="app-footer">
      <div className="app-footer__inner">
        <div className="app-footer__brand-block">
          <span className="app-footer__brand">KumbhRaksha: Crowd Safety System for Kumbh Mela</span>
          <span className="app-footer__domain">kumbhraksha.org.in</span>
        </div>
        <nav className="app-footer__links" aria-label="Legal">
          <Link to="/privacy-policy" className="app-footer__link">Privacy Policy</Link>
          <Link to="/terms" className="app-footer__link">Terms &amp; Conditions</Link>
        </nav>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Nav />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/lost-found" element={<LostFound />} />
            <Route path="/chat" element={<ChatSim />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsAndConditions />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
