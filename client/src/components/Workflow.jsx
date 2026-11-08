// Shows the supervisor's decision: guardrail result and which agents it chose.
const LABELS = { flight_agent: "Flight", hotel_agent: "Hotel", weather_agent: "Weather", budget_agent: "Budget" };

export default function Workflow({ plan, blocked }) {
  const agents = blocked ? [] : [...plan.agents.map((a) => LABELS[a]), "Itinerary"];

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <span className="eyebrow">Supervisor</span>
          <h2>Execution plan</h2>
        </div>
        <span className={`badge ${blocked ? "badge-blocked" : "badge-ok"}`}>
          {blocked ? "Blocked by guardrail" : "Guardrail passed"}
        </span>
      </div>
      <p className="reasoning">{plan.reasoning}</p>
      <div className="chips">
        {agents.map((a) => <span key={a} className="chip chip-static">{a} agent</span>)}
      </div>
    </section>
  );
}
