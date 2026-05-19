import { useState } from 'react';
import StatsBar from './StatsBar';
import LogUpload from './LogUpload';
import ThreatTimeline from './ThreatTimeline';
import AnalysisSummary from './AnalysisSummary';
import ChatPanel from './ChatPanel';
import { generateReport, getReportDownloadUrl } from '../utils/api';

export default function Dashboard({ activeView, analysis, onAnalysisComplete }) {
  const [isLoading, setIsLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [companyName, setCompanyName] = useState('Your Company');

  const handleGenerateReport = async () => {
    if (!analysis) return;
    setReportLoading(true);
    try {
      const result = await generateReport(analysis.analysis_id, companyName);
      // Trigger download
      const downloadUrl = getReportDownloadUrl(result.report_id);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert('Failed to generate report: ' + err.message);
    } finally {
      setReportLoading(false);
    }
  };

  // Upload view
  if (activeView === 'upload') {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-cyber-text mb-1">Upload & Analyze Logs</h1>
          <p className="text-sm text-cyber-text-muted">
            Upload your server logs or try a sample to see AI-powered security analysis in action.
          </p>
        </div>
        <LogUpload
          onAnalysisComplete={onAnalysisComplete}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
      </div>
    );
  }

  // Chat view
  if (activeView === 'chat') {
    return (
      <div className="max-w-4xl mx-auto">
        <ChatPanel analysisId={analysis?.analysis_id} />
      </div>
    );
  }

  // Reports view
  if (activeView === 'reports') {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-cyber-text mb-1">Generate Incident Report</h1>
          <p className="text-sm text-cyber-text-muted">
            Create a professional PDF incident report from your analysis results.
          </p>
        </div>

        {analysis ? (
          <div className="glass-card p-8 space-y-6 animate-slide-up">
            {/* Report preview */}
            <div className="bg-cyber-surface/50 rounded-xl p-6 border border-cyber-border">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-red-500 to-amber-500 
                              flex items-center justify-center text-2xl shadow-glow-amber">
                  📄
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-cyber-text">Security Incident Report</h3>
                  <p className="text-xs text-cyber-text-muted mt-1">
                    File: {analysis.filename} • {analysis.threats?.length || 0} threats •
                    Risk Score: {analysis.risk_score}/100
                  </p>
                  <p className="text-xs text-cyber-text-muted mt-0.5">
                    Analyzed: {new Date(analysis.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Report includes */}
            <div>
              <h4 className="text-xs font-bold text-cyber-text-muted uppercase tracking-wider mb-3">
                Report Includes
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  '📊 Executive Summary',
                  '🎯 Risk Score Analysis',
                  '⚠️ Threat Breakdown Table',
                  '🔍 Detailed Findings',
                  '🔧 Recommendations',
                  '📋 Evidence Samples',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-cyber-text-dim 
                                        bg-cyber-bg/50 rounded-lg px-3 py-2 border border-cyber-border/50">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            {/* Company name input */}
            <div>
              <label className="text-xs font-medium text-cyber-text-muted block mb-2">
                Company Name (for report header)
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="cyber-input"
                placeholder="Your Company Name"
              />
            </div>

            {/* Generate button */}
            <button
              onClick={handleGenerateReport}
              disabled={reportLoading}
              className="cyber-button-primary w-full py-4 text-base flex items-center justify-center gap-2"
            >
              {reportLoading ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Generating PDF...
                </>
              ) : (
                <>
                  📥 Generate & Download PDF Report
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="glass-card p-10 text-center animate-fade-in">
            <span className="text-5xl mb-4 block">📄</span>
            <h3 className="text-lg font-semibold text-cyber-text mb-2">No Analysis Data</h3>
            <p className="text-sm text-cyber-text-muted">
              Upload and analyze logs first to generate an incident report.
            </p>
          </div>
        )}
      </div>
    );
  }

  // Dashboard (default)
  return (
    <div className="space-y-6">
      {!analysis ? (
        <div className="max-w-3xl mx-auto">
          {/* Welcome state */}
          <div className="glass-card p-10 text-center mb-8 relative overflow-hidden">
            {/* Background effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyber-cyan/5 to-emerald-500/5" />
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyber-cyan/30 to-transparent" />

            <div className="relative z-10">
              <div className="text-6xl mb-4 animate-pulse-slow">🛡️</div>
              <h1 className="text-2xl font-bold gradient-text mb-2">
                AI Security Analyst
              </h1>
              <p className="text-sm text-cyber-text-muted max-w-md mx-auto mb-6">
                Upload your server logs to get AI-powered threat detection, plain-English explanations,
                and actionable security recommendations.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-3">
                {[
                  { icon: '📂', label: 'Upload Logs' },
                  { icon: '🔍', label: 'Detect Threats' },
                  { icon: '🤖', label: 'AI Analysis' },
                  { icon: '💬', label: 'Chat with Data' },
                  { icon: '📄', label: 'PDF Reports' },
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-1.5 text-xs text-cyber-text-dim
                                        bg-cyber-surface px-3 py-1.5 rounded-full border border-cyber-border">
                    <span>{feat.icon}</span>
                    <span>{feat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <LogUpload
            onAnalysisComplete={onAnalysisComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        </div>
      ) : (
        <>
          {/* Analysis header */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 className="text-xl font-bold text-cyber-text">Security Analysis</h1>
              <p className="text-xs text-cyber-text-muted">
                File: <span className="text-cyber-cyan">{analysis.filename}</span>
                {' • '}Format: {analysis.stats?.log_format}
                {' • '}{new Date(analysis.timestamp).toLocaleString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleGenerateReport}
                disabled={reportLoading}
                className="cyber-button-secondary text-xs flex items-center gap-1.5"
              >
                📄 {reportLoading ? 'Generating...' : 'Export PDF'}
              </button>
            </div>
          </div>

          {/* Stats */}
          <StatsBar analysis={analysis} />

          {/* AI Summary */}
          <AnalysisSummary analysis={analysis} />

          {/* Threats */}
          <ThreatTimeline threats={analysis.threats} />
        </>
      )}
    </div>
  );
}
