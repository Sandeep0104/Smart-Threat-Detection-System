import { useState } from 'react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '🛡️' },
  { id: 'upload', label: 'Upload Logs', icon: '📂' },
  { id: 'chat', label: 'Chat with Logs', icon: '💬' },
  { id: 'reports', label: 'Reports', icon: '📄' },
];

export default function Sidebar({ activeView, onViewChange, hasAnalysis }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`fixed left-0 top-0 h-screen bg-cyber-surface/95 backdrop-blur-xl 
                  border-r border-cyber-border flex flex-col z-50
                  transition-all duration-300 ease-in-out
                  ${collapsed ? 'w-[72px]' : 'w-[240px]'}`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-6 border-b border-cyber-border">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyber-cyan to-emerald-500
                        flex items-center justify-center text-xl flex-shrink-0
                        shadow-cyber animate-pulse-slow">
          🛡️
        </div>
        {!collapsed && (
          <div className="animate-fade-in">
            <h1 className="text-sm font-bold gradient-text leading-tight">AI Security</h1>
            <p className="text-[10px] text-cyber-text-muted font-medium">ANALYST</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = activeView === item.id;
          const isDisabled = !hasAnalysis && (item.id === 'chat' || item.id === 'reports');

          return (
            <button
              key={item.id}
              onClick={() => !isDisabled && onViewChange(item.id)}
              disabled={isDisabled}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium
                         transition-all duration-200 group relative
                         ${isActive
                  ? 'bg-cyber-cyan/10 text-cyber-cyan border border-cyber-cyan/20 shadow-cyber'
                  : isDisabled
                    ? 'text-cyber-text-muted/40 cursor-not-allowed'
                    : 'text-cyber-text-dim hover:bg-cyber-hover hover:text-cyber-text'
                }`}
            >
              {/* Active indicator glow */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-8 
                              bg-cyber-cyan rounded-r-full shadow-[0_0_10px_rgba(0,212,255,0.5)]" />
              )}

              <span className="text-lg flex-shrink-0">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}

              {/* Tooltip when collapsed */}
              {collapsed && (
                <div className="absolute left-full ml-3 px-3 py-1.5 rounded-lg bg-cyber-card 
                              border border-cyber-border text-xs text-cyber-text whitespace-nowrap
                              opacity-0 pointer-events-none group-hover:opacity-100
                              transition-opacity duration-200 shadow-lg z-50">
                  {item.label}
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Status indicator */}
      <div className="px-3 pb-3">
        <div className={`glass-card p-3 ${collapsed ? 'text-center' : ''}`}>
          {!collapsed ? (
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${hasAnalysis ? 'bg-cyber-emerald animate-pulse' : 'bg-cyber-text-muted'}`} />
              <span className="text-xs text-cyber-text-muted">
                {hasAnalysis ? 'Analysis Active' : 'No Data'}
              </span>
            </div>
          ) : (
            <div className={`w-2 h-2 rounded-full mx-auto ${hasAnalysis ? 'bg-cyber-emerald animate-pulse' : 'bg-cyber-text-muted'}`} />
          )}
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="px-3 pb-4 text-cyber-text-muted hover:text-cyber-cyan transition-colors"
      >
        <div className={`w-full flex items-center justify-center py-2 rounded-lg
                        border border-cyber-border hover:border-cyber-cyan/30 
                        transition-all duration-200`}>
          <span className={`text-sm transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}>
            ◀
          </span>
        </div>
      </button>
    </aside>
  );
}
