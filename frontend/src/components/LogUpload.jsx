import { useState, useCallback } from 'react';
import { uploadLog, analyzeSample } from '../utils/api';

export default function LogUpload({ onAnalysisComplete, isLoading, setIsLoading }) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');

  const samples = [
    { id: 'auth',      name: 'SSH Auth Log',      desc: 'Brute-force attacks & failed logins',               icon: '🔐', color: 'from-red-500 to-amber-500'    },
    { id: 'syslog',    name: 'System Log',         desc: 'Firewall blocks & port scanning',                   icon: '🖥️', color: 'from-blue-500 to-cyan-500'    },
    { id: 'access',    name: 'Apache Access Log',  desc: 'SQL injection & web attacks',                       icon: '🌐', color: 'from-purple-500 to-pink-500'   },
    { id: 'nginx',     name: 'Nginx Web Log',      desc: 'XSS, SQLi & directory traversal',                  icon: '⚡', color: 'from-green-500 to-emerald-500' },
    { id: 'ssh_heavy', name: 'Heavy Brute Force',  desc: 'Multi-source SSH attack from 4 IPs',               icon: '💥', color: 'from-rose-600 to-red-500'      },
    { id: 'mixed',     name: 'Mixed Attack Log',   desc: 'SSH + SQLi + XSS + privilege escalation',          icon: '🎯', color: 'from-orange-500 to-amber-600'  },
  ];

  const processFile = useCallback(async (file) => {
    setError(null);
    setIsLoading(true);
    setProgress(0);

    try {
      // Validate
      if (file.size > 50 * 1024 * 1024) {
        throw new Error('File too large. Maximum size: 50MB');
      }

      setStatus('Uploading log file...');
      setProgress(20);

      await new Promise(r => setTimeout(r, 300));
      setStatus('Parsing log entries...');
      setProgress(40);

      const result = await uploadLog(file);

      setStatus('Detecting threats...');
      setProgress(70);

      await new Promise(r => setTimeout(r, 300));
      setStatus('Running AI analysis...');
      setProgress(90);

      await new Promise(r => setTimeout(r, 200));
      setProgress(100);
      setStatus('Analysis complete!');

      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
      setTimeout(() => { setProgress(0); setStatus(''); }, 1500);
    }
  }, [onAnalysisComplete, setIsLoading]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const files = e.dataTransfer?.files;
    if (files?.length) processFile(files[0]);
  }, [processFile]);

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  const handleSample = async (sampleId) => {
    setError(null);
    setIsLoading(true);
    setProgress(0);

    try {
      setStatus('Loading sample log...');
      setProgress(30);

      const result = await analyzeSample(sampleId);

      setStatus('Analysis complete!');
      setProgress(100);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
      setTimeout(() => { setProgress(0); setStatus(''); }, 1500);
    }
  };

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Upload zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        className={`glass-card p-10 text-center cursor-pointer group
                   transition-all duration-300 relative overflow-hidden
                   ${dragActive
            ? 'border-cyber-cyan shadow-cyber-lg scale-[1.01]'
            : 'border-dashed border-2 border-cyber-border hover:border-cyber-cyan/40'
          }
                   ${isLoading ? 'pointer-events-none' : ''}`}
        onClick={() => !isLoading && document.getElementById('file-input').click()}
      >
        {/* Scan line animation when processing */}
        {isLoading && (
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyber-cyan to-transparent animate-scan-line" />
          </div>
        )}

        <input
          type="file"
          id="file-input"
          accept=".log,.txt"
          onChange={handleFileInput}
          className="hidden"
        />

        {isLoading ? (
          <div className="space-y-4">
            <div className="text-4xl animate-pulse-slow">🔍</div>
            <p className="text-cyber-cyan font-semibold">{status}</p>

            {/* Progress bar */}
            <div className="max-w-xs mx-auto">
              <div className="w-full h-2 bg-cyber-border rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyber-cyan to-emerald-500 
                            transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-cyber-text-muted mt-2">{progress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-5xl mb-2 group-hover:scale-110 transition-transform duration-300">
              {dragActive ? '📥' : '📂'}
            </div>
            <h3 className="text-lg font-semibold text-cyber-text">
              {dragActive ? 'Drop your log file here' : 'Upload Server Logs'}
            </h3>
            <p className="text-sm text-cyber-text-muted">
              Drag & drop your log file, or <span className="text-cyber-cyan underline">browse</span>
            </p>
            <p className="text-xs text-cyber-text-muted">
              Supports: auth.log, syslog, Apache access.log (.log, .txt) • Max 50MB
            </p>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="glass-card border-red-500/30 bg-red-500/5 p-4 animate-slide-up">
          <div className="flex items-start gap-3">
            <span className="text-red-400 text-lg">⚠️</span>
            <div>
              <p className="text-red-400 font-medium text-sm">Upload Error</p>
              <p className="text-red-300/80 text-xs mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sample logs section */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-px flex-1 bg-cyber-border" />
          <span className="text-xs text-cyber-text-muted uppercase tracking-wider font-medium">
            Or try a sample log
          </span>
          <div className="h-px flex-1 bg-cyber-border" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {samples.map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleSample(sample.id)}
              disabled={isLoading}
              className="glass-card-hover p-5 text-left group disabled:opacity-50"
            >
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${sample.color} 
                               flex items-center justify-center text-lg
                               group-hover:shadow-lg transition-shadow duration-300`}>
                  {sample.icon}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-cyber-text group-hover:text-cyber-cyan transition-colors">
                    {sample.name}
                  </h4>
                  <p className="text-xs text-cyber-text-muted mt-0.5">{sample.desc}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
