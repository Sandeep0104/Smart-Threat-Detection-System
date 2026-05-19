const severityConfig = {
  critical: { label: 'CRITICAL', classes: 'severity-critical', icon: '🔴', border: 'border-l-red-500' },
  high: { label: 'HIGH', classes: 'severity-high', icon: '🟠', border: 'border-l-amber-500' },
  medium: { label: 'MEDIUM', classes: 'severity-medium', icon: '🟡', border: 'border-l-yellow-500' },
  low: { label: 'LOW', classes: 'severity-low', icon: '🟢', border: 'border-l-emerald-500' },
  info: { label: 'INFO', classes: 'severity-info', icon: '🔵', border: 'border-l-blue-500' },
};

const threatIcons = {
  brute_force: '🔓',
  user_enumeration: '👤',
  port_scan: '🔍',
  sql_injection: '💉',
  directory_traversal: '📁',
  unusual_hour_access: '🌙',
  privilege_escalation: '⬆️',
  high_firewall_activity: '🛡️',
};

import { useState } from 'react';

export default function ThreatCard({ threat, index }) {
  const [expanded, setExpanded] = useState(false);
  const sev = severityConfig[threat.severity] || severityConfig.info;
  const icon = threatIcons[threat.threat_type] || '⚠️';

  return (
    <div
      className={`glass-card-hover border-l-4 ${sev.border} overflow-hidden
                 animate-slide-up cursor-pointer`}
      style={{ animationDelay: `${index * 80}ms` }}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1">
            <span className="text-2xl">{icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-sm font-bold text-cyber-text">
                  {threat.threat_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </h3>
                <span className={sev.classes}>{sev.label}</span>
              </div>

              <div className="flex items-center gap-4 mt-2 text-xs text-cyber-text-muted">
                {threat.source_ip && (
                  <span className="flex items-center gap-1">
                    <span className="text-cyber-cyan">IP:</span>
                    <code className="font-mono text-cyber-text-dim bg-cyber-surface px-1.5 py-0.5 rounded">
                      {threat.source_ip}
                    </code>
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <span className="text-cyber-cyan">Count:</span>
                  <span className="font-bold text-cyber-text">{threat.count}</span>
                </span>
                {threat.first_seen && (
                  <span className="hidden sm:inline">
                    <span className="text-cyber-cyan">Time:</span> {threat.first_seen}
                  </span>
                )}
              </div>
            </div>
          </div>

          <button className={`text-cyber-text-muted transition-transform duration-200 text-xs
                            ${expanded ? 'rotate-180' : ''}`}>
            ▼
          </button>
        </div>

        {/* Description */}
        <p className="text-xs text-cyber-text-dim mt-3 leading-relaxed">
          {threat.description}
        </p>

        {/* Expanded content */}
        {expanded && (
          <div className="mt-4 space-y-3 animate-fade-in">
            {/* Recommendation */}
            {threat.recommendation && (
              <div className="bg-cyber-surface/80 rounded-lg p-4 border border-cyber-border">
                <h4 className="text-xs font-bold text-cyber-emerald uppercase tracking-wider mb-2">
                  🔧 Recommended Actions
                </h4>
                <div className="space-y-1.5">
                  {threat.recommendation.split('\n').filter(Boolean).map((line, i) => (
                    <p key={i} className="text-xs text-cyber-text-dim leading-relaxed font-mono">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence */}
            {threat.evidence?.length > 0 && (
              <div className="bg-cyber-bg/80 rounded-lg p-4 border border-cyber-border">
                <h4 className="text-xs font-bold text-cyber-amber uppercase tracking-wider mb-2">
                  📋 Evidence
                </h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {threat.evidence.map((line, i) => (
                    <code key={i} className="block text-[10px] text-cyber-text-muted font-mono 
                                           leading-relaxed break-all">
                      {line}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
