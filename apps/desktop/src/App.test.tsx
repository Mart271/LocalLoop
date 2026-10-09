import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const invoke = vi.fn<(command: string, args: { request: { nonce: string } }) => Promise<unknown>>();
vi.mock("@tauri-apps/api/core", () => ({
  invoke: (command: string, args: { request: { nonce: string } }) => invoke(command, args),
}));

import { App } from "./App";
import { call, isIpcError } from "./ipc";

const echo = (_command: string, args: { request: { nonce: string } }) =>
  Promise.resolve({ nonce: args.request.nonce, coreVersion: "0.1.0" });

describe("App", () => {
  beforeEach(() => {
    invoke.mockReset();
  });

  it("shows the core version after a successful ping", async () => {
    invoke.mockImplementation(echo);
    render(<App />);
    expect(await screen.findByText("Connected (version 0.1.0)")).toBeInTheDocument();
    expect(invoke).toHaveBeenCalledWith("ping", { request: { nonce: expect.any(String) as string } });
  });

  it("reports a failure in plain language and lets the user retry", async () => {
    invoke.mockRejectedValueOnce({ code: "invalid_argument", message: "The request was not accepted." });
    render(<App />);
    expect(await screen.findByText("The request was not accepted.")).toBeInTheDocument();
    invoke.mockImplementation(echo);
    await userEvent.click(screen.getByRole("button", { name: "Check again" }));
    expect(await screen.findByText("Connected (version 0.1.0)")).toBeInTheDocument();
  });

  it("does not trust a response to a different request", async () => {
    invoke.mockResolvedValue({ nonce: "someone-else", coreVersion: "0.1.0" });
    render(<App />);
    expect(await screen.findByText("The core answered, but not to this request.")).toBeInTheDocument();
  });
});

describe("ipc", () => {
  it("maps unknown rejection values to a safe message", async () => {
    invoke.mockRejectedValueOnce(new Error("boom <script>"));
    const result = await call("ping", { nonce: "abc" });
    expect(result).toEqual({
      ok: false,
      error: { code: "invalid_argument", message: "LocalLoop could not complete the request. Nothing was changed." },
    });
  });

  it("recognises only well-formed IPC errors", () => {
    expect(isIpcError({ code: "invalid_argument", message: "x" })).toBe(true);
    expect(isIpcError({ code: "other", message: "x" })).toBe(false);
    expect(isIpcError("invalid_argument")).toBe(false);
    expect(isIpcError(null)).toBe(false);
  });
});
