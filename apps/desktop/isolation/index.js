// Tauri isolation hook: every IPC message from the UI passes through here before it reaches the
// core. Messages for commands outside LocalLoop's allowlist are dropped. The core enforces the
// same allowlist with capabilities; this is a second, independent layer (NFR-014, T-17).
"use strict";
(function () {
  var ALLOWED = Object.freeze(["ping"]);
  window.__TAURI_ISOLATION_HOOK__ = function (payload) {
    if (!payload || typeof payload.cmd !== "string" || ALLOWED.indexOf(payload.cmd) === -1) {
      throw new Error("LocalLoop blocked a command that is not on the allowlist.");
    }
    return payload;
  };
})();
