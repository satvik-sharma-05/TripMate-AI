// The request box, a guide to what details to include, and example prompts.
import { useState } from "react";

// What the agents need for a good plan. "required" ones are asked for clearly.
const DETAILS = [
  ["Starting city", "Where you travel from, e.g. Patiala", true],
  ["Dates", "When you leave, e.g. 26 November", true],
  ["Trip length", "Number of days, e.g. 3 days / 2 nights", true],
  ["Budget", "Total amount, e.g. ₹60,000", true],
  ["Travellers", "Who is going, e.g. 4 adults", true],
  ["Destination", "Optional: leave it out and we suggest one", false],
  ["Interests", "Optional: beaches, food, temples, adventure…", false],
];

const TEMPLATE = `From:
Destination (optional):
Dates:
Trip length:
Budget:
Travellers:
Interests (optional): `;

const EXAMPLES = {
  "Japan, 7 days": "From Delhi to Japan, 10-16 March 2027, 7 days, budget ₹2,00,000, 2 adults, interested in food and temples.",
  "Goa family trip": "From Mumbai to Goa, 20-23 December, 4 days, budget ₹60,000, 2 adults and 2 kids, beaches and seafood.",
  "Suggest a destination": "From Patiala, 26 November, 3 days / 2 nights, budget ₹60,000-70,000, 4 adults (family).",
  "Weather in Tokyo": "What is the weather like in Tokyo this week?",
};

export default function PlannerForm({ loading, onSubmit }) {
  const [message, setMessage] = useState("");

  function submit(e) {
    e.preventDefault(); // stop the browser from reloading the page
    if (message.trim()) onSubmit(message.trim());
  }

  return (
    <form className="panel" onSubmit={submit}>
      <div className="panel-head">
        <div>
          <h2>Your trip request</h2>
          <p>Write it in your own words. The more of these details you include, the better the plan.</p>
        </div>
        <button type="button" className="btn btn-outline btn-sm" onClick={() => setMessage(TEMPLATE)}>
          Use template
        </button>
      </div>

      <ul className="details">
        {DETAILS.map(([name, hint, required]) => (
          <li key={name} className={required ? "" : "optional"}>
            <strong>{name}</strong>
            <span>{hint}</span>
          </li>
        ))}
      </ul>

      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => e.ctrlKey && e.key === "Enter" && submit(e)}
        placeholder="e.g. From Patiala, 26 November, 3 days / 2 nights, budget ₹60,000, 4 adults. Suggest a destination."
      />
      <div className="form-row">
        <div className="chips">
          {Object.entries(EXAMPLES).map(([label, text]) => (
            <button key={label} type="button" className="chip" onClick={() => setMessage(text)}>
              {label}
            </button>
          ))}
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? <><span className="spinner" /> Working…</> : "Generate draft"}
        </button>
      </div>
    </form>
  );
}
