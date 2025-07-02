"use client";
import { useEffect, useRef } from "react";
import mermaid from "mermaid";

export default function Mermaid({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      // Generate a unique id for each diagram
      const id = "mermaid-" + Math.random().toString(36).substr(2, 9);
      ref.current.id = id;
      try {
        mermaid.initialize({ startOnLoad: false });
        mermaid.render(id, chart).then((result: any) => {
          if (ref.current) ref.current.innerHTML = result.svg;
        });
      } catch (e: any) {
        if (ref.current) ref.current.innerHTML = `<pre style='color:red'>${e.message}</pre>`;
      }
    }
  }, [chart]);

  return <div ref={ref} />;
} 