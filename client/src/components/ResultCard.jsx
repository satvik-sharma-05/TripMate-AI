// Renders the plan (Markdown from the AI) with Copy and PDF buttons.
import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown"; // turns Markdown text into HTML elements safely
import remarkGfm from "remark-gfm";    // adds tables (GitHub-style Markdown)

// Tells react-markdown to render every link so it opens in a new tab.
// rel="noopener noreferrer" stops the new page from controlling this one (security).
const NewTabLink = ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />;

export default function ResultCard({ result, revisions }) {
  const cardRef = useRef(null); // direct handles to DOM elements
  const pdfRef = useRef(null);
  const [copied, setCopied] = useState(false);
  const isDraft = result.status === "needs_review";
  const lastFeedback = revisions.at(-1);

  // useEffect runs after render: whenever a new answer arrives, scroll to its top.
  useEffect(() => {
    cardRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [result.answer]);

  const title = !isDraft ? "Your final travel plan"
    : revisions.length ? `Revised draft (version ${revisions.length + 1})` : "Draft itinerary";

  async function copy() {
    await navigator.clipboard.writeText(result.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  async function downloadPdf() {
    const html2pdf = (await import("html2pdf.js")).default; // loaded only when clicked
    html2pdf().set({ margin: 0.5, filename: "travel-plan.pdf", jsPDF: { unit: "in", format: "a4" } })
      .from(pdfRef.current).save();
  }

  return (
    <section className="panel" ref={cardRef} style={{ scrollMarginTop: 88 }}>
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          <p>Reference: {result.thread_id.slice(0, 8)}</p>
        </div>
        <div className="chips">
          <span className={`badge ${isDraft ? "badge-draft" : "badge-ok"}`}>
            {isDraft ? "Awaiting review" : "Approved"}
          </span>
          <button className="btn btn-outline btn-sm" onClick={copy}>{copied ? "Copied" : "Copy"}</button>
          <button className="btn btn-outline btn-sm" onClick={downloadPdf}>Download PDF</button>
        </div>
      </div>
      {isDraft && lastFeedback && (
        <div className="notice">Updated with your feedback: “{lastFeedback}”</div>
      )}
      <div ref={pdfRef} className="markdown">
        <Markdown remarkPlugins={[remarkGfm]} components={{ a: NewTabLink }}>{result.answer}</Markdown>
      </div>
    </section>
  );
}
