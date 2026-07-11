"use client";

import { useEffect, useState } from "react";
import { AnimationResponse } from "@/lib/api";

type Props = {
  animation: AnimationResponse | null;
  currentStep: number;
  onStepChange: (step: number) => void;
};

export function ClassificationAnimation({ animation, currentStep, onStepChange }: Props) {
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    if (!animation || !playing) return;
    const timer = window.setInterval(() => {
      onStepChange((currentStep + 1) % animation.steps.length);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [animation, currentStep, onStepChange, playing]);

  if (!animation) {
    return null;
  }

  const step = animation.steps[currentStep] ?? animation.steps[0];

  return (
    <section className="animation-panel" aria-label="分类与特征动画">
      <div className="animation-stage">
        <div className="object-card">
          <span className="object-dot" />
          <strong>{step.category}</strong>
          <div className="feature-tags">
            {step.highlighted_features.map((feature) => (
              <span key={feature}>{feature}</span>
            ))}
          </div>
        </div>
      </div>
      <div>
        <h2>{step.title}</h2>
        <p className="step-progress">
          第 {currentStep + 1} / {animation.steps.length} 步
        </p>
        <p>{step.narration}</p>
        <div className="animation-controls">
          <button onClick={() => onStepChange(Math.max(0, currentStep - 1))}>上一步</button>
          <button onClick={() => onStepChange((currentStep + 1) % animation.steps.length)}>下一步</button>
          <button onClick={() => setPlaying((value) => !value)}>{playing ? "暂停" : "播放"}</button>
          <button onClick={() => onStepChange(0)}>重播</button>
        </div>
      </div>
    </section>
  );
}
