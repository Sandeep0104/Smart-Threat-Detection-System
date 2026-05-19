import { useEffect, useState } from 'react';

function AnimatedNumber({ value, duration = 600 }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value === 0) { setDisplay(0); return; }
    const start = performance.now();
    const startVal = display;

    function animate(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(startVal + (value - startVal) * eased));
      if (progress < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  }, [value]);

  return <span>{display}</span>;
}

const stats = [
  {
    key: 'total_lines',
    label: 'Total Events',
    icon: '📊',
    gradient: 'from-blue-500 to-cyan-500',
    glow: 'shadow-[0_0_20px_rgba(59,130,246,0.15)]',
  },
  {
    key: 'threats',
    label: 'Threats Found',
    icon: '⚠️',
    gradient: 'from-red-500 to-amber-500',
    glow: 'shadow-[0_0_20px_rgba(239,68,68,0.15)]',
  },
  {
    key: 'risk_score',
    label: 'Risk Score',
    icon: '🎯',
    gradient: 'from-amber-500 to-orange-500',
    glow: 'shadow-[0_0_20px_rgba(245,158,11,0.15)]',
    suffix: '/100',
  },
  {
    key: 'unique_ips',
    label: 'Unique IPs',
    icon: '🌐',
    gradient: 'from-emerald-500 to-teal-500',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.15)]',
  },
];

export default function StatsBar({ analysis }) {
  if (!analysis) return null;

  const values = {
    total_lines: analysis.stats?.total_lines || 0,
    threats: analysis.threats?.length || 0,
    risk_score: analysis.risk_score || 0,
    unique_ips: analysis.stats?.unique_ips || 0,
  };

  const riskLevel = values.risk_score >= 75 ? 'CRITICAL' : values.risk_score >= 50 ? 'HIGH' : values.risk_score >= 25 ? 'MEDIUM' : 'LOW';
  const riskColor = values.risk_score >= 75 ? 'text-red-400' : values.risk_score >= 50 ? 'text-amber-400' : values.risk_score >= 25 ? 'text-yellow-400' : 'text-emerald-400';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      {stats.map((stat, index) => (
        <div
          key={stat.key}
          className={`glass-card-hover p-5 relative overflow-hidden group ${stat.glow}`}
          style={{ animationDelay: `${index * 100}ms` }}
        >
          {/* Background gradient accent */}
          <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${stat.gradient} 
                          opacity-5 rounded-full -translate-y-8 translate-x-8
                          group-hover:opacity-10 transition-opacity duration-500`} />

          <div className="flex items-start justify-between relative z-10">
            <div>
              <p className="text-cyber-text-muted text-xs font-medium uppercase tracking-wider mb-1">
                {stat.label}
              </p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-cyber-text">
                  <AnimatedNumber value={values[stat.key]} />
                </span>
                {stat.suffix && (
                  <span className="text-sm text-cyber-text-muted">{stat.suffix}</span>
                )}
              </div>
              {stat.key === 'risk_score' && (
                <span className={`text-xs font-bold ${riskColor} mt-1 inline-block`}>
                  {riskLevel}
                </span>
              )}
            </div>
            <span className="text-2xl opacity-80">{stat.icon}</span>
          </div>

          {/* Risk score bar */}
          {stat.key === 'risk_score' && (
            <div className="mt-3 w-full h-1.5 bg-cyber-border rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r ${stat.gradient}`}
                style={{ width: `${values.risk_score}%` }}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
