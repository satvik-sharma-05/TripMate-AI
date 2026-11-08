// Landing page: what the product does and a call to action.
import { Link } from "react-router-dom";

const FEATURES = [
  ["Supervisor agent", "Reads your request and decides which specialists are needed."],
  ["Built-in guardrail", "Politely declines anything that is not about travel."],
  ["Live research", "Searches the web for flights and hotels and checks real weather."],
  ["You stay in control", "Review the draft and approve it or request changes."],
];

const STEPS = [
  ["Describe your trip", "Destination, dates, budget and preferences, in plain words."],
  ["Agents research", "Flight, hotel, weather and budget agents collect the details."],
  ["Review the draft", "Read the itinerary and approve or ask for revisions."],
  ["Get the final plan", "A clean day-by-day plan you can copy or save as PDF."],
];

// Reusable grid of numbered cards (used by both sections below).
function CardGrid({ items, numbered }) {
  return (
    <div className="grid">
      {items.map(([title, text], i) => (
        <div className="card" key={title}>
          <div className="card-index">{numbered ? i + 1 : `0${i + 1}`}</div>
          <h3>{title}</h3>
          <p>{text}</p>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="container">
          <span className="eyebrow">Multi-agent travel planning</span>
          <h1>Plan complete trips with a team of AI agents.</h1>
          <p>
            TripMate AI coordinates specialist agents for flights, hotels, weather and budget,
            then lets you review the plan before it is finalised.
          </p>
          <div className="hero-actions">
            <Link to="/plan" className="btn btn-light">Start planning</Link>
            <Link to="/about" className="btn btn-ghost-light">How it works</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Features</span>
            <h2>Built like a real travel desk</h2>
          </div>
          <CardGrid items={FEATURES} />
        </div>
      </section>

      <section className="section section-alt">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">How it works</span>
            <h2>From idea to itinerary in four steps</h2>
          </div>
          <CardGrid items={STEPS} numbered />
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="cta">
            <div>
              <h2>Ready for your next trip?</h2>
              <p>Describe it in one sentence and get a reviewed plan.</p>
            </div>
            <Link to="/plan" className="btn btn-light">Plan a trip</Link>
          </div>
        </div>
      </section>
    </>
  );
}
