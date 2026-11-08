// Live progress: one row per agent, updated as the server streams each step.
const LABELS = {
  supervisor: "Supervisor: checking request and choosing agents",
  flight_agent: "Flight agent: researching flights",
  hotel_agent: "Hotel agent: finding places to stay",
  weather_agent: "Weather agent: checking weather",
  budget_agent: "Budget agent: estimating costs",
  itinerary_agent: "Itinerary agent: writing the plan",
  human_review: "Recording your review",
  final_agent: "Final agent: polishing the plan",
};

// Which agents this run will use, in display order.
function expectedSteps(plan, isReview) {
  if (isReview) return ["human_review", "itinerary_agent", "final_agent"];
  const research = plan ? plan.agents : [];
  return ["supervisor", ...research, "itinerary_agent"];
}

export default function Progress({ plan, done, isReview }) {
  // On review we don't know yet if it's approve (final) or revise (itinerary),
  // so only show steps that actually ran, plus a "working" row.
  const steps = isReview ? done : expectedSteps(plan, false);
  const current = steps.find((s) => !done.includes(s));

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <span className="eyebrow">Live progress</span>
          <h2>Agents at work</h2>
          <p>Flight, hotel and weather agents run in parallel.</p>
        </div>
      </div>
      <ul className="steps">
        {steps.map((s) => (
          <li key={s} className={done.includes(s) ? "step done" : s === current ? "step active" : "step"}>
            <span className="step-dot" />
            {LABELS[s] || s}
          </li>
        ))}
        {isReview && <li className="step active"><span className="step-dot" />Working on it…</li>}
      </ul>
    </section>
  );
}
