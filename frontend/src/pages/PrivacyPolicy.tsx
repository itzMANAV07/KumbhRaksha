/**
 * PrivacyPolicy : KumbhRaksha privacy policy page.
 */
export function PrivacyPolicy() {
  return (
    <div className="legal-page">
      <div className="legal-page__inner">
        <h1 className="legal-page__title">Privacy Policy</h1>
        <p className="legal-page__meta">Last updated: 26 October 2026</p>

        <section className="legal-section">
          <h2>1. Overview</h2>
          <p>
            KumbhRaksha is a crowd safety demonstration system built for Kumbh Mela 2027. This
            policy explains what data is collected, how it is used, and how it is protected.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Data We Collect</h2>
          <p>
            KumbhRaksha collects only the minimum information necessary to operate the
            lost-and-found and SOS systems:
          </p>
          <ul>
            <li>
              <strong>Lost and found reports:</strong> Age (approximate), clothing colour and
              garment type, last-seen zone, and an optional name. No photographs, fingerprints,
              facial data, or government ID are collected.
            </li>
            <li>
              <strong>Chat sessions:</strong> Messages sent through the web chat simulator or
              Telegram bot are processed to generate a safety response. Messages are not stored
              beyond the current session unless explicitly required for an SOS incident record.
            </li>
            <li>
              <strong>SOS incidents:</strong> If a user submits an SOS request with GPS
              coordinates, those coordinates and the incident status are stored until the
              incident is resolved.
            </li>
            <li>
              <strong>Telegram subscriptions:</strong> If a user explicitly consents to zone
              alerts, their Telegram chat ID and preferred zone are stored to deliver alerts.
              This data is never shared with third parties and is deleted after the Mela window.
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>3. No Biometric Data</h2>
          <p>
            KumbhRaksha does not collect, process, or store any biometric data. The
            lost-and-found system uses text descriptors only (age, clothing colour, garment type,
            zone, and time). No face recognition or photograph matching is performed at any stage.
          </p>
        </section>

        <section className="legal-section">
          <h2>4. All Data Is Simulated During the Demo Phase</h2>
          <p>
            During the demonstration and evaluation period, all crowd density, zone counts, and
            incident data displayed on the dashboard are simulated. No real pilgrim data is
            collected or processed. The SIMULATED DATA badge is displayed at all times when
            simulated data is active.
          </p>
        </section>

        <section className="legal-section">
          <h2>5. Data Retention</h2>
          <p>
            All personal data associated with lost-and-found reports, SOS incidents, and
            Telegram subscriptions is automatically deleted by a scheduled purge job after the
            conclusion of the Mela event window. Data is not retained for any purpose beyond
            the operation of the system during the event.
          </p>
        </section>

        <section className="legal-section">
          <h2>6. Consent</h2>
          <p>
            No personal data is stored without explicit consent. Telegram alert subscriptions
            require an explicit affirmative reply ("yes" or "haan") before any data is saved.
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Third-Party Services</h2>
          <p>
            KumbhRaksha uses OpenStreetMap tiles via Leaflet for mapping. No user data is
            sent to mapping providers. The optional Gemini language model is used only to
            parse non-SOS chat messages; digits are stripped from all text before any model
            call, and the system functions fully without an active API key.
          </p>
        </section>

        <section className="legal-section">
          <h2>8. Contact</h2>
          <p>
            Questions regarding this policy can be directed to the project team. Contact
            details will be published when a custom domain and production deployment are
            finalised.
          </p>
        </section>
      </div>
    </div>
  );
}
