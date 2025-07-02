"use client";
import { useState } from 'react';

interface BusinessAnalysisFormProps {
  onReportGenerated: (report: string) => void;
}

export default function BusinessAnalysisForm({ onReportGenerated }: BusinessAnalysisFormProps) {
  const [businessProblem, setBusinessProblem] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/ba-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ businessProblem }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate report');
      }

      onReportGenerated(data.report);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Business Analysis Report Generator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="businessProblem" className="block text-sm font-medium text-gray-700 mb-2">
            Business Problem/Objective
          </label>
          <textarea
            id="businessProblem"
            value={businessProblem}
            onChange={(e) => setBusinessProblem(e.target.value)}
            placeholder="Describe your business problem or objective here..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={6}
            required
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !businessProblem.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Generating Report...' : 'Generate Business Analysis Report'}
        </button>
      </form>
    </div>
  );
} 