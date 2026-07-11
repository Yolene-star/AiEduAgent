"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Analytics = {
  total_sessions: number;
  weak_knowledge_points: string[];
  note: string;
};

export function TeacherDashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [status, setStatus] = useState("加载中");

  useEffect(() => {
    api
      .teacherAnalytics()
      .then((data) => {
        setAnalytics(data);
        setStatus("已连接");
      })
      .catch(() => setStatus("教师端数据暂不可用"));
  }, []);

  return (
    <main className="teacher-shell">
      <header className="topbar">
        <div className="brand">
          <strong>教师工作台</strong>
          <span>课程、资源与学情分析</span>
        </div>
        <div className={status === "已连接" ? "status ok" : "status warn"}>{status}</div>
      </header>

      <section className="teacher-grid">
        <article className="panel">
          <h2>学情概览</h2>
          <div className="metric">
            <span>学习会话数</span>
            <strong>{analytics?.total_sessions ?? "--"}</strong>
          </div>
          <div className="metric">
            <span>薄弱知识点</span>
            <strong>
              {analytics?.weak_knowledge_points.length
                ? analytics.weak_knowledge_points.join("、")
                : "暂无数据"}
            </strong>
          </div>
        </article>

        <article className="panel">
          <h2>资源管理</h2>
          <p>下一步接入资源上传、审核状态和 Dify 知识库同步。</p>
          <button type="button">新增资源</button>
        </article>

        <article className="panel">
          <h2>课程调整建议</h2>
          <p>{analytics?.note ?? "等待学情数据生成建议。"}</p>
        </article>
      </section>
    </main>
  );
}
