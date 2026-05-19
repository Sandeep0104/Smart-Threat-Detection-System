export default function AnalysisSummary({ analysis }) {
  if (!analysis) return null;

  const riskScore = analysis.risk_score || 0;
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (riskScore / 100) * circumference;
  const riskColor = riskScore >= 75 ? '#ef4444' : riskScore >= 50 ? '#f59e0b' : riskScore >= 25 ? '#eab308' : '#10b981';

  // Extract top attacking IPs from threats
  const ipCounts = {};
  analysis.threats?.forEach(t => {
    if (t.source_ip) {
      ipCounts[t.source_ip] = (ipCounts[t.source_ip] || 0) + t.count;
    }
  });
  const topIPs = Object.entries(ipCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="space-y-4 animate-slide-up">
      <h2 className="text-lg font-bold text-cyber-text flex items-center gap-2">
        <span className="text-xl">🤖</span>
        AI Analysis
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Risk Score Gauge */}
        <div className="glass-card p-6 flex flex-col items-center justify-center">
          <p className="text-xs text-cyber-text-muted uppercase tracking-wider font-medium mb-4">
            Risk Score
          </p>
          <div className="relative w-32 h-32">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" fill="none" stroke="#1e2a42" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="54" fill="none"
                stroke={riskColor}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                className="transition-all duration-1000 ease-out"
                style={{ filter: `drop-shadow(0 0 6px ${riskColor}50)` }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-cyber-text">{riskScore}</span>
              <span className="text-[10px] text-cyber-text-muted">/100</span>
            </div>
          </div>
          <span className="mt-3 text-xs font-bold uppercase tracking-wider"
            style={{ color: riskColor }}>
            {riskScore >= 75 ? 'CRITICAL' : riskScore >= 50 ? 'HIGH' : riskScore >= 25 ? 'MEDIUM' : 'LOW'}
          </span>
        </div>

        {/* AI Summary */}
        <div className="glass-card p-6 lg:col-span-2 overflow-y-auto max-h-80">
          <p className="text-xs text-cyber-text-muted uppercase tracking-wider font-medium mb-3">
            AI Summary
          </p>
          <div className="prose-sm text-cyber-text-dim text-sm leading-relaxed space-y-2">
            {analysis.ai_summary?.split('\n').filter(Boolean).map((line, i) => {
              // Simple markdown-like rendering
              let text = line.trim();
              if (text.startsWith('##')) {
                return <h4 key={i} className="text-sm font-bold text-cyber-text mt-3">{text.replace(/^#+\s*/, '')}</h4>;
              }
              if (text.startsWith('- ') || text.startsWith('* ')) {
                return <p key={i} className="text-xs text-cyber-text-dim pl-3 flex gap-2">
                  <span className="text-cyber-cyan">•</span>
                  <span>{text.slice(2)}</span>
                </p>;
              }
              if (text.startsWith('>')) {
                return <div key={i} className="bg-cyber-surface/50 border-l-2 border-cyber-cyan/30 px-3 py-2 text-xs text-cyber-text-muted italic rounded-r">
                  {text.slice(1).trim()}
                </div>;
              }
              return <p key={i} className="text-xs text-cyber-text-dim">{text}</p>;
            })}
          </div>
        </div>
      </div>

      {/* Bottom row: Top IPs + Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top Attacking IPs */}
        {topIPs.length > 0 && (
          <div className="glass-card p-5">
            <h3 className="text-xs font-bold text-cyber-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
              🌐 Top Attacking IPs
            </h3>
            <div className="space-y-2">
              {topIPs.map(([ip, count], i) => {
                const maxCount = topIPs[0][1];
                const width = (count / maxCount) * 100;
                return (
                  <div key={ip} className="flex items-center gap-3 group">
                    <span className="text-[10px] text-cyber-text-muted w-4">{i + 1}</span>
                    <code className="text-xs font-mono text-cyber-text-dim min-w-[120px]">{ip}</code>
                    <div className="flex-1 h-2 bg-cyber-border/50 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-red-500 to-amber-500 
                                  transition-all duration-700 ease-out"
                        style={{ width: `${width}%`, transitionDelay: `${i * 100}ms` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-cyber-text-dim w-10 text-right">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {analysis.recommendations?.length > 0 && (
          <div className="glass-card p-5">
            <h3 className="text-xs font-bold text-cyber-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
              ✅ Recommendations
            </h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {analysis.recommendations.map((rec, i) => (
                <div key={i} className="flex gap-2 text-xs text-cyber-text-dim leading-relaxed">
                  <span className="text-cyber-emerald flex-shrink-0 mt-0.5">→</span>
                  <span>{rec.replace(/^[🔴🟠🟡\s•\-*]+/, '')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
