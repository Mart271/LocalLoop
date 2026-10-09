import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import "@fontsource-variable/dm-sans";
import "./styles/global.css";
import { App } from "./App";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("LocalLoop UI root element is missing.");
}
createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
