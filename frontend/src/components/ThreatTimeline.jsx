import ThreatCard from './ThreatCard';

export default function ThreatTimeline({ threats }) {
  if (!threats?.length) return null;

  return (
    <div className="space-y-4 animate-slide-up">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-cyber-text flex items-center gap-2">
          <span className="text-xl">🎯</span>
          Detected Threats
          <span className="text-xs font-normal text-cyber-text-muted bg-cyber-surface 
                         px-2 py-0.5 rounded-full border border-cyber-border">
            {threats.length}
          </span>
        </h2>
      </div>

      {/* Severity summary */}
      <div className="flex items-center gap-3 flex-wrap">
        {['critical', 'high', 'medium', 'low'].map(sev => {
          const count = threats.filter(t => t.severity === sev).length;
          if (count === 0) return null;
          const colors = {
            critical: 'bg-red-500/10 text-red-400 border-red-500/20',
            high: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
            medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
            low: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
          };
          return (
            <span key={sev} className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full 
                                       text-xs font-semibold border ${colors[sev]}`}>
              {count} {sev.toUpperCase()}
            </span>
          );
        })}
      </div>

      {/* Threat cards */}
      <div className="space-y-3">
        {threats.map((threat, index) => (
          <ThreatCard key={index} threat={threat} index={index} />
        ))}
      </div>
    </div>
  );
}
