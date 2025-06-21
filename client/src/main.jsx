import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { HashRouter } from "react-router";
import Index from "./index.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <div className="font-lato">
      <HashRouter>
        <Index />
      </HashRouter>
    </div>
  </StrictMode>
);
