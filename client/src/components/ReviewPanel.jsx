// Human-in-the-loop: approve the draft or send feedback to revise it.
import { useState } from "react";

export default function ReviewPanel({ loading, onReview, onError }) {
  const [feedback, setFeedback] = useState("");

  function revise() {
    if (!feedback.trim()) return onError("Please describe the changes you want.");
    onReview(false, feedback.trim());
  }

  return (
    <section className="panel review">
      <div className="panel-head">
        <div>
          <span className="eyebrow">Human in the loop</span>
          <h2>Review the draft</h2>
          <p>Approve it as is, or describe changes and the plan will be revised.</p>
        </div>
      </div>
      <textarea
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
        placeholder="e.g. Use cheaper hotels and add a free day in Kyoto"
      />
      <div className="review-actions">
        <button className="btn btn-primary" disabled={loading} onClick={() => onReview(true, "")}>
          Approve and finalise
        </button>
        <button className="btn btn-outline" disabled={loading} onClick={revise}>
          Revise with feedback
        </button>
      </div>
    </section>
  );
}
