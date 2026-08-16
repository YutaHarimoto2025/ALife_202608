/** React appのentry point。Appを #root にmountし、共通styleを読み込む。 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./_App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
