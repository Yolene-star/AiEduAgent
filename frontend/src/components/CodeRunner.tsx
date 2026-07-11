"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type Props = {
  sessionId: string | null;
};

export function CodeRunner({ sessionId }: Props) {
  const [code, setCode] = useState("print('hello classifier')");
  const [result, setResult] = useState("提交代码后查看运行结果。");
  const [busy, setBusy] = useState(false);

  async function runCode() {
    if (!sessionId) {
      setResult("请先选择学段并开始学习。");
      return;
    }
    setBusy(true);
    try {
      const response = await api.runCode(sessionId, code);
      setResult(`${response.feedback} 输出：${response.output || "无"} 沙箱：${response.sandbox}`);
    } catch {
      setResult("代码服务暂不可用，请稍后重试。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="code-runner" aria-label="在线编程">
      <h2>Python 小实验</h2>
      <textarea
        aria-label="Python代码"
        value={code}
        onChange={(event) => setCode(event.target.value)}
      />
      <button type="button" disabled={busy} onClick={runCode}>
        运行代码
      </button>
      <p>{result}</p>
    </section>
  );
}
