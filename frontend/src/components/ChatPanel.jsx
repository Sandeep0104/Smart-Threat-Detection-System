import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, clearChatHistory } from '../utils/api';

const suggestedQuestions = [
  "Why was this IP blocked?",
  "Show me all failed login attempts",
  "What are the most critical threats?",
  "Which IPs are most suspicious?",
  "What should I do to secure my server?",
  "Explain the brute-force attack",
];

export default function ChatPanel({ analysisId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (text) => {
    const message = text || input.trim();
    if (!message || !analysisId) return;

    setInput('');
    setError(null);
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setIsTyping(true);

    try {
      const response = await sendChatMessage(analysisId, message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response,
        sources: response.sources,
      }]);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message}. Please make sure Ollama is running.`,
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClear = async () => {
    try {
      await clearChatHistory(analysisId);
      setMessages([]);
    } catch (err) { /* ignore */ }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!analysisId) {
    return (
      <div className="glass-card p-10 text-center animate-fade-in">
        <span className="text-5xl mb-4 block">💬</span>
        <h3 className="text-lg font-semibold text-cyber-text mb-2">Chat with your Logs</h3>
        <p className="text-sm text-cyber-text-muted">
          Upload and analyze logs first, then ask questions about your security data.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] min-h-[500px] animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-cyber-text flex items-center gap-2">
          <span className="text-xl">💬</span>
          Chat with Logs
        </h2>
        {messages.length > 0 && (
          <button
            onClick={handleClear}
            className="text-xs text-cyber-text-muted hover:text-cyber-red transition-colors
                     px-3 py-1.5 rounded-lg border border-cyber-border hover:border-red-500/30"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 glass-card overflow-y-auto p-4 space-y-4 mb-4">
        {messages.length === 0 && !isTyping && (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="text-4xl mb-4 animate-pulse-slow">🤖</div>
            <p className="text-sm text-cyber-text-dim mb-6">
              Ask me anything about your security logs
            </p>

            {/* Suggested questions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg">
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="text-xs text-left text-cyber-text-dim bg-cyber-surface/80 
                           border border-cyber-border rounded-lg px-3 py-2.5
                           hover:border-cyber-cyan/30 hover:text-cyber-cyan
                           transition-all duration-200"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 animate-fade-in ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyber-cyan to-emerald-500 
                            flex items-center justify-center text-sm flex-shrink-0 shadow-cyber">
                🤖
              </div>
            )}

            <div
              className={`max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed
                         ${msg.role === 'user'
                  ? 'bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-text'
                  : 'bg-cyber-surface border border-cyber-border text-cyber-text-dim'
                }`}
            >
              {/* Simple markdown rendering */}
              {msg.content.split('\n').map((line, j) => {
                let text = line;
                if (text.startsWith('```')) return null;
                if (text.startsWith('**') && text.endsWith('**')) {
                  return <p key={j} className="font-bold text-cyber-text text-xs mt-2 mb-1">
                    {text.replace(/\*\*/g, '')}
                  </p>;
                }
                if (text.startsWith('- ') || text.startsWith('* ')) {
                  return <p key={j} className="text-xs pl-2 flex gap-1.5">
                    <span className="text-cyber-cyan">•</span>
                    <span>{text.slice(2)}</span>
                  </p>;
                }
                if (!text.trim()) return <br key={j} />;
                return <p key={j} className="text-xs">{text}</p>;
              })}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-cyber-surface border border-cyber-border
                            flex items-center justify-center text-sm flex-shrink-0">
                👤
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-3 animate-fade-in">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyber-cyan to-emerald-500 
                          flex items-center justify-center text-sm flex-shrink-0">
              🤖
            </div>
            <div className="bg-cyber-surface border border-cyber-border rounded-xl px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-typing" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-typing" style={{ animationDelay: '200ms' }} />
                <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-typing" style={{ animationDelay: '400ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your logs... (e.g., 'Why was this IP blocked?')"
          disabled={isTyping}
          className="cyber-input flex-1"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || isTyping}
          className="cyber-button-primary px-5"
        >
          {isTyping ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
