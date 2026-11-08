// About page: the architecture, explained simply.
import { Fragment } from "react";

const FLOW = ["Supervisor + Guardrail", "Flight", "Hotel", "Weather", "Budget",
              "Itinerary draft", "Human review", "Final plan"];

const STACK = [
  ["LangGraph", "Runs the agents as a graph and pauses for human approval."],
  ["LangChain + Groq", "Calls the GPT-OSS 120B open-weight model, hosted on Groq."],
  ["MCP", "Standard protocol that connects agents to tools (Tavily search, weather server)."],
  ["FastAPI", "Python backend that exposes the planner as an API."],
  ["PostgreSQL", "Saves paused plans so they can be resumed later."],
  ["React + Vite", "This frontend."],
];

export default function About() {
  return (
    <>
      <section className="page-header">
        <div className="container">
          <span className="eyebrow">About</span>
          <h1>How TripMate AI works</h1>
          <p>
            A supervisor agent breaks your request into tasks, specialist agents research them,
            and you approve the result. Each agent does one job, which keeps the system easy to
            understand and extend.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Workflow</span>
            <h2>The agent pipeline</h2>
            <p>The supervisor runs only the specialists your request needs.</p>
          </div>
          <div className="flow">
            {FLOW.map((step, i) => (
              <Fragment key={step}>
                <span className="flow-step">{step}</span>
                {i < FLOW.length - 1 && <span className="flow-arrow">→</span>}
              </Fragment>
            ))}
          </div>
        </div>
      </section>

      <section className="section section-alt">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Technology</span>
            <h2>Tech stack</h2>
          </div>
          <table className="table">
            <thead><tr><th>Technology</th><th>Role</th></tr></thead>
            <tbody>
              {STACK.map(([name, role]) => <tr key={name}><td>{name}</td><td>{role}</td></tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
