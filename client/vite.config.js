// Vite = the dev server + build tool. It serves React instantly during development
// and bundles everything into static files (dist/) for production.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // In dev, forward /api calls to the FastAPI backend so there are no CORS issues.
  server: { proxy: { "/api": "http://localhost:8000" } },
});
