// A custom React hook: keeps all planner state + logic out of the UI components.
// useState stores values that, when changed, make React re-render the screen.
import { useState } from "react";
import { reviewPlan, startPlan } from "../api";

export function usePlanner() {
  const [result, setResult] = useState(null);     // last finished answer from the server
  const [plan, setPlan] = useState(null);         // supervisor's decision {agents, reasoning}
  const [done, setDone] = useState([]);           // agents finished in the current run
  const [revisions, setRevisions] = useState([]); // feedback the user has sent (HITL history)
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handles every streamed event from the server.
  function onEvent(e) {
    if (e.type === "step") {
      setDone((prev) => [...prev, e.node]);
      if (e.node === "supervisor") setPlan({ agents: e.agents, reasoning: e.reasoning });
    } else if (e.type === "result") {
      setResult(e);
      setPlan({ agents: e.agents, reasoning: e.reasoning });
    } else if (e.type === "error") {
      throw new Error(e.message);
    }
  }

  // Returns true if the request finished without errors.
  async function run(request) {
    setError("");
    setDone([]);
    setLoading(true);
    try {
      await request();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }

  return {
    result, plan, done, revisions, loading, error, setError,
    start: (message) => {
      setResult(null);
      setPlan(null);
      setRevisions([]);
      return run(() => startPlan(message, onEvent));
    },
    review: async (approved, feedback) => {
      const ok = await run(() => reviewPlan(result.thread_id, approved, feedback, onEvent));
      if (ok && !approved) setRevisions((prev) => [...prev, feedback]);
    },
  };
}
