// The planner page: form -> live progress -> draft -> human review (repeatable) -> final.
import { usePlanner } from "../hooks/usePlanner";
import PlannerForm from "../components/PlannerForm";
import Progress from "../components/Progress";
import Workflow from "../components/Workflow";
import ResultCard from "../components/ResultCard";
import ReviewPanel from "../components/ReviewPanel";

export default function Plan() {
  const { result, plan, done, revisions, loading, error, setError, start, review } = usePlanner();
  const isReview = loading && !!result; // loading after a draft exists = processing a review

  return (
    <>
      <section className="page-header">
        <div className="container">
          <span className="eyebrow">Planner</span>
          <h1>Plan a trip</h1>
          <p>Describe where you want to go. Review the draft and revise it as many times as you like.</p>
        </div>
      </section>

      <div className="container plan-layout">
        <PlannerForm loading={loading} onSubmit={start} />
        {plan && <Workflow plan={plan} blocked={result?.status === "blocked"} />}
        {loading && !isReview && <Progress plan={plan} done={done} isReview={false} />}
        {result && result.status !== "blocked" && <ResultCard result={result} revisions={revisions} />}

        {/* Review area: shows progress in the same place you clicked, so you see it working */}
        {isReview && <Progress plan={plan} done={done} isReview />}
        {!loading && result?.status === "needs_review" && (
          <ReviewPanel key={result.answer} loading={loading} onReview={review} onError={setError} />
        )}
        {error && <div className="alert">{error}</div>}
      </div>
    </>
  );
}
