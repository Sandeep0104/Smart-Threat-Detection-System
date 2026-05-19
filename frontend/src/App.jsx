import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import { healthCheck } from './utils/api';

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [analysis, setAnalysis] = useState(null);
  const [backendStatus, setBackendStatus] = useState(null);

  useEffect(() => {
    // Check backend connectivity
    healthCheck()
      .then(data => setBackendStatus(data))
      .catch(() => setBackendStatus({ status: 'offline' }));
  }, []);

  const handleAnalysisComplete = (result) => {
    setAnalysis(result);
    setActiveView('dashboard');
  };

  return (
    <div className="min-h-screen bg-cyber-bg">
      {/* Ambient background effects */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyber-cyan/3 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-500/3 rounded-full blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/2 rounded-full blur-[150px]" />
      </div>

      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        hasAnalysis={!!analysis}
      />

      {/* Main Content */}
      <main className="ml-[240px] min-h-screen relative z-10">
        {/* Top bar */}
        <header className="sticky top-0 z-40 backdrop-blur-xl bg-cyber-bg/80 border-b border-cyber-border/50">
          <div className="px-8 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-cyber-text capitalize">
                {activeView === 'dashboard' ? (analysis ? 'Security Dashboard' : 'Welcome') : activeView.replace(/_/g, ' ')}
              </h2>
            </div>

            <div className="flex items-center gap-4">
              {/* Backend status */}
              <div className="flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${
                  backendStatus?.status === 'healthy' 
                    ? 'bg-cyber-emerald animate-pulse' 
                    : backendStatus?.status === 'offline' 
                      ? 'bg-cyber-red' 
                      : 'bg-cyber-amber animate-pulse'
                }`} />
                <span className="text-cyber-text-muted">
                  {backendStatus?.status === 'healthy' ? 'Backend Connected' : 
                   backendStatus?.status === 'offline' ? 'Backend Offline' : 'Checking...'}
                </span>
              </div>

              {/* Ollama status */}
              {backendStatus?.ollama && (
                <div className="flex items-center gap-2 text-xs">
                  <div className={`w-2 h-2 rounded-full ${
                    backendStatus.ollama.includes('connected') 
                      ? 'bg-cyber-emerald' 
                      : 'bg-cyber-amber'
                  }`} />
                  <span className="text-cyber-text-muted">
                    Ollama: {backendStatus.ollama.includes('connected') ? '✓' : 'Not Running'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="p-8">
          {backendStatus?.status === 'offline' && (
            <div className="mb-6 glass-card border-amber-500/30 bg-amber-500/5 p-4 animate-slide-up">
              <div className="flex items-start gap-3">
                <span className="text-amber-400 text-lg">⚠️</span>
                <div>
                  <p className="text-amber-400 font-medium text-sm">Backend Not Running</p>
                  <p className="text-amber-300/70 text-xs mt-1">
                    Start the backend server with: <code className="bg-cyber-bg px-2 py-0.5 rounded font-mono">
                    cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload</code>
                  </p>
                </div>
              </div>
            </div>
          )}

          <Dashboard
            activeView={activeView}
            analysis={analysis}
            onAnalysisComplete={handleAnalysisComplete}
          />
        </div>
      </main>
    </div>
  );
}
