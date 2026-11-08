// Free hosting (Render) puts the server to sleep when nobody uses it.
// We ping it on page load; if it's slow, we tell the user why instead of leaving them guessing.
import { useEffect, useState } from "react";
import { ping } from "../api";

export default function ServerStatus() {
  const [status, setStatus] = useState("checking"); // checking | waking | ready

  useEffect(() => {
    const slow = setTimeout(() => setStatus("waking"), 2000); // no answer in 2s = asleep
    ping().catch(() => {}).finally(() => {
      clearTimeout(slow);
      setStatus((s) => (s === "waking" ? "ready" : "hidden"));
    });
    return () => clearTimeout(slow);
  }, []);

  if (status === "waking") return (
    <div className="notice">
      ⏳ Waking up the server. This demo runs on free hosting, which sleeps when idle,
      so the first load can take up to a minute. You can start typing meanwhile.
    </div>
  );
  if (status === "ready") return <div className="notice notice-ok">✅ Server is awake. You're good to go!</div>;
  return null;
}
