import { useEffect, useState } from "react";
import { call } from "./ipc";

type Connection =
  { state: "checking" } | { state: "connected"; coreVersion: string } | { state: "failed"; message: string };

/** Asks the core for a ping and checks that the answer belongs to this request. */
async function checkCore(): Promise<Connection> {
  const nonce = crypto.randomUUID();
  const result = await call("ping", { nonce });
  if (result.ok && result.value.nonce === nonce) {
    return { state: "connected", coreVersion: result.value.coreVersion };
  }
  return {
    state: "failed",
    message: result.ok ? "The core answered, but not to this request." : result.error.message,
  };
}

export function App() {
  const [connection, setConnection] = useState<Connection>({ state: "checking" });

  useEffect(() => {
    let active = true;
    void checkCore().then((next) => {
      if (active) setConnection(next);
    });
    return () => {
      active = false;
    };
  }, []);

  const recheck = () => {
    setConnection({ state: "checking" });
    void checkCore().then(setConnection);
  };

  return (
    <main className="page">
      <h1>LocalLoop</h1>
      <p className="lead">Offline workflow automation that runs entirely on this computer.</p>

      <section className="panel" aria-labelledby="status-heading">
        <h2 id="status-heading">System status</h2>
        <p className="label">LocalLoop core</p>
        <p className="metric" role="status" aria-live="polite">
          {connection.state === "checking" && "Checking connection…"}
          {connection.state === "connected" && (
            <span className="status-ok">Connected (version {connection.coreVersion})</span>
          )}
          {connection.state === "failed" && <span className="status-error">{connection.message}</span>}
        </p>
        <button type="button" onClick={recheck} disabled={connection.state === "checking"}>
          Check again
        </button>
      </section>

      <section className="panel" aria-labelledby="build-heading">
        <h2 id="build-heading">What this build includes</h2>
        <p>
          This is the foundation build. It does not read, move, or change any of your files yet. Workflows, runs,
          approvals, and the review queue arrive in later milestones.
        </p>
      </section>
    </main>
  );
}
