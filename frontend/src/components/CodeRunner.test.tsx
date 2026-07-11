import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CodeRunner } from "./CodeRunner";

vi.mock("@/lib/api", () => ({
  api: {
    runCode: () =>
      Promise.resolve({
        status: "ok",
        output: "hello",
        feedback: "代码运行成功。",
        sandbox: "mock-judge0"
      })
  }
}));

describe("CodeRunner", () => {
  it("runs code through backend API", async () => {
    render(<CodeRunner sessionId="session-1" />);
    fireEvent.click(screen.getByText("运行代码"));
    await waitFor(() => expect(screen.getByText(/代码运行成功/)).toBeInTheDocument());
    expect(screen.getByLabelText("Python代码")).toBeInTheDocument();
  });
});
