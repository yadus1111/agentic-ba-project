"use client";
import { useState } from "react";
import BusinessAnalysisForm from "./components/BusinessAnalysisForm";
import ReportViewer from "./components/ReportViewer";

export default function Home() {
  const [generatedReport, setGeneratedReport] = useState<string>('');

  const handleReportGenerated = (report: string) => {
    setGeneratedReport(report);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            BA Agentic AI Dashboard
          </h1>
          <p className="text-xl text-gray-600">
            Generate comprehensive business analysis reports with AI-powered insights
          </p>
        </div>

        {!generatedReport ? (
          <BusinessAnalysisForm onReportGenerated={handleReportGenerated} />
        ) : (
          <div className="space-y-6">
            <div className="text-center">
              <button
                onClick={() => setGeneratedReport('')}
                className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Generate New Report
              </button>
            </div>
            <ReportViewer report={generatedReport} />
          </div>
        )}
      </div>
    </div>
  );
}
