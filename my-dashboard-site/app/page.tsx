import Image from "next/image";
import styles from "./page.module.css";
import Mermaid from "./components/Mermaid";

export default function Home() {
  const mermaidCode = `
    graph TD;
      A[Start] --> B{Is it working?};
      B -- Yes --> C[Celebrate!];
      B -- No --> D[Debug];
      D --> B;
  `;
  return (
    <div style={{ padding: 40 }}>
      <h1>My Dashboard with Mermaid</h1>
      <p>This is a live Mermaid diagram rendered in Next.js!</p>
      <Mermaid chart={mermaidCode} />
    </div>
  );
}
