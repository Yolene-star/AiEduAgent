"use client";

import { useMemo, useState } from "react";

type Props = {
  text: string;
};

export function SpeechButton({ text }: Props) {
  const [status, setStatus] = useState("待播放");
  const supported = useMemo(
    () => typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window,
    []
  );

  function speak() {
    if (!supported) {
      setStatus("当前浏览器不支持语音播放");
      return;
    }
    if (!text.trim()) {
      setStatus("没有可播放文本");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "zh-CN";
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.onstart = () => setStatus("播放中");
    utterance.onend = () => setStatus("播放完成");
    utterance.onerror = () => setStatus("播放失败，已保留文字内容");
    window.speechSynthesis.speak(utterance);
  }

  function stop() {
    if (supported) {
      window.speechSynthesis.cancel();
    }
    setStatus("已停止");
  }

  return (
    <div className="speech-tools" aria-label="语音播放">
      <button type="button" onClick={speak}>
        播放语音
      </button>
      <button type="button" onClick={stop}>
        停止
      </button>
      <span>{status}</span>
    </div>
  );
}
