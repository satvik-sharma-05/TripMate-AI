export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <span>© {new Date().getFullYear()} TripMate AI</span>
        <span>React · FastAPI · LangGraph · MCP · Groq</span>
      </div>
    </footer>
  );
}
