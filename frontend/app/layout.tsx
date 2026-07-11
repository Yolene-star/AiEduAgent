import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "AiEduAgent",
  description: "K12 AI teaching assistant"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
