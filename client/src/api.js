// All calls to the backend live here, so components never deal with fetch details.
const BASE = import.meta.env.VITE_API_URL || "";

// POST, then read the Server-Sent Events stream: one `data: {...}` line per event.
// onEvent is called for every event: {type: "step" | "result" | "error", ...}
async function stream(path, body, onEvent) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    // Validation errors come back as normal JSON, not a stream.
    const data = await res.json();
    const detail = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
    throw new Error(detail || "Request failed");
  }

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    const events = buffer.split("\n\n"); // events are separated by a blank line
    buffer = events.pop();               // keep any half-received event for next time
    for (const e of events) {
      if (e.startsWith("data: ")) onEvent(JSON.parse(e.slice(6)));
    }
  }
}

export const startPlan = (message, onEvent) => stream("/api/plan", { message }, onEvent);
export const reviewPlan = (threadId, approved, feedback, onEvent) =>
  stream(`/api/plan/${threadId}/review`, { approved, feedback }, onEvent);
