"use client";
import { useState, useEffect } from 'react';
import Mermaid from './Mermaid';

interface ReportViewerProps {
  report: string;
}

export default function ReportViewer({ report }: ReportViewerProps) {
  const [sections, setSections] = useState<Array<{ type: 'text' | 'mermaid', content: string }>>([]);

  useEffect(() => {
    if (!report) return;

    // Parse the report and extract sections
    const lines = report.split('\n');
    const parsedSections: Array<{ type: 'text' | 'mermaid', content: string }> = [];
    let currentSection = '';
    let inMermaidBlock = false;
    let mermaidContent = '';

    for (const line of lines) {
      if (line.trim().startsWith('```mermaid')) {
        // Save any accumulated text
        if (currentSection.trim()) {
          parsedSections.push({ type: 'text', content: currentSection.trim() });
          currentSection = '';
        }
        inMermaidBlock = true;
        mermaidContent = '';
        continue;
      }

      if (line.trim() === '```' && inMermaidBlock) {
        inMermaidBlock = false;
        if (mermaidContent.trim()) {
          parsedSections.push({ type: 'mermaid', content: mermaidContent.trim() });
        }
        continue;
      }

      if (inMermaidBlock) {
        mermaidContent += line + '\n';
      } else {
        currentSection += line + '\n';
      }
    }

    // Add any remaining text
    if (currentSection.trim()) {
      parsedSections.push({ type: 'text', content: currentSection.trim() });
    }

    setSections(parsedSections);
  }, [report]);

  const renderMarkdown = (text: string) => {
    // Simple markdown rendering
    return text
      .replace(/^### (.*$)/gim, '<h3 class="text-xl font-semibold mt-6 mb-3">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-bold mt-8 mb-4 text-blue-600">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold mt-8 mb-6 text-gray-800">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  if (!report) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="prose prose-lg max-w-none">
        {sections.map((section, index) => (
          <div key={index} className="mb-6">
            {section.type === 'mermaid' ? (
              <div className="my-6 p-4 bg-gray-50 rounded-lg">
                <Mermaid chart={section.content} />
              </div>
            ) : (
              <div 
                className="text-gray-700 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(section.content) }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 