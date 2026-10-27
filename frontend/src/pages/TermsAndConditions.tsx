/**
 * TermsAndConditions : KumbhRaksha terms and conditions page.
 */
export function TermsAndConditions() {
  return (
    <div className="legal-page">
      <div className="legal-page__inner">
        <h1 className="legal-page__title">Terms and Conditions</h1>
        <p className="legal-page__meta">Last updated: 26 October 2026</p>

        <section className="legal-section">
          <h2>1. System Purpose and Agreement</h2>
          <p>
            KumbhRaksha is an intelligent crowd-safety and flow-management system designed for the
            Kumbh Mela 2027 pilgrimage in Haridwar. By accessing or using the KumbhRaksha web
            dashboard, mobile portal, Telegram interface, or public safety endpoints, you agree to
            be bound by these terms.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Demonstration and Simulated Data Notice</h2>
          <p>
            During pre-event demonstration and testing phases, all crowd metrics, zone density
            ratings, and simulated incidents displayed on this dashboard represent simulated data
            generated for operational validation. The SIMULATED DATA badge is prominently displayed
            to indicate active simulation states.
          </p>
        </section>

        <section className="legal-section">
          <h2>3. Crowd Routing and Advisory Notices</h2>
          <p>
            Zone density levels (green, yellow, orange, red) and diversion route recommendations
            are advisory safety notifications derived from area capacity calculations. In the event
            of an on-site emergency or police-directed crowd control measure, on-ground police and
            magisterial directives supersede all automated recommendations.
          </p>
        </section>

        <section className="legal-section">
          <h2>4. Emergency SOS Path</h2>
          <p>
            The emergency SOS system identifies nearest verified medical, police, or disaster
            management posts using validated geospatial records from the Haridwar administration.
            SOS keywords (help, sos, bachao, madad) are processed synchronously through deterministic
            logic. Users in life-threatening distress must simultaneously contact local emergency
            responders or dial 112.
          </p>
        </section>

        <section className="legal-section">
          <h2>5. Lost and Found Person System Rules</h2>
          <p>
            In compliance with strict data protection and anti-surveillance protocols:
          </p>
          <ul>
            <li>No biometric, facial recognition, or photo matching is used.</li>
            <li>Reports use textual descriptors only: age range, garment type, clothing colour, and zone.</li>
            <li>All personal identifiers and report records are systematically purged following the conclusion of the Mela window.</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>6. Telegram Alert Subscriptions and User Consent</h2>
          <p>
            Proactive zone alerts require explicit affirmative consent ("yes" or "haan") before
            storing any communication handle. Users may terminate alerts at any time by issuing
            the "stop" or "unsubscribe" command.
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Acceptable Use</h2>
          <p>
            Users shall not submit fraudulent SOS alarms, flood the SMS or webhook endpoints with
            spurious traffic, or attempt to disrupt safety telemetry pipelines. Misuse of emergency
            channels may be reported to relevant authorities under applicable telecommunications
            regulations.
          </p>
        </section>

        <section className="legal-section">
          <h2>8. Contact and Jurisdiction</h2>
          <p>
            Operational inquiries regarding KumbhRaksha protocols may be addressed through the
            official deployment administration portal at kumbhraksha.org.in.
          </p>
        </section>
      </div>
    </div>
  );
}
