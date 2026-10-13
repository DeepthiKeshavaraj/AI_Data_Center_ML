import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Brain,
  HelpCircle,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Send,
  RotateCcw,
  ShieldAlert,
  Info,
  ChevronRight,
  Lightbulb,
  Key,
} from 'lucide-react';
import {
  requestExplanation,
  fetchExplanationStatus,
  ExplanationResponse,
  ExplanationStatusResponse,
} from '../api_ai';

interface AiExplanationPanelProps {
  module: 'security' | 'workload' | 'cluster' | 'thermal' | 'benchmarks';
  context: Record<string, any> | null;
  isContextReady: boolean;
  contextDescription: string;
  suggestedQuestions?: string[];
}

export const AiExplanationPanel: React.FC<AiExplanationPanelProps> = ({
  module,
  context,
  isContextReady,
  contextDescription,
  suggestedQuestions = [],
}) => {
  const [question, setQuestion] = useState<string>('');
  const [detailLevel, setDetailLevel] = useState<'concise' | 'detailed'>('concise');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ExplanationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<ExplanationStatusResponse | null>(null);

  const checkStatus = () => {
    fetchExplanationStatus()
      .then((res) => setStatus(res))
      .catch(() => setStatus(null));
  };

  useEffect(() => {
    checkStatus();
    const onFocus = () => checkStatus();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, []);

  const handleExplain = async (customQuestion?: string) => {
    if (!context || !isContextReady) return;

    setLoading(true);
    setError(null);
    try {
      const q = customQuestion !== undefined ? customQuestion : question;
      const res = await requestExplanation({
        module,
        context,
        question: q.trim() ? q.trim() : undefined,
        detail_level: detailLevel,
      });
      setResult(res);
      setStatus((prev) => (prev ? { ...prev, configured: true } : prev));
    } catch (err: any) {
      setError(err?.message || 'Failed to generate AI explanation.');
      checkStatus();
    } finally {
      setLoading(false);
    }
  };

  const handleSelectQuestion = (q: string) => {
    setQuestion(q);
    handleExplain(q);
  };

  return (
    <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md space-y-4">
      {/* Panel Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white m-0 flex items-center gap-1.5">
              <span>Generative AI Explanation</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono">
                {status?.model || 'gpt-4o-mini'}
              </span>
            </h4>
            <p className="text-[11px] text-slate-400 m-0">{contextDescription}</p>
          </div>
        </div>

        {/* Model status pill */}
        <div className="flex items-center space-x-2">
          {status && !status.configured ? (
            <button
              type="button"
              onClick={checkStatus}
              className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1 hover:bg-amber-500/20 transition cursor-pointer"
              title="Click to recheck API key"
            >
              <Key className="w-3 h-3" />
              API Key Not Set
              <RotateCcw className="w-2.5 h-2.5 ml-0.5 opacity-70" />
            </button>
          ) : (
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {status?.provider || 'AI'} Active
            </span>
          )}

          {/* Detail Level Toggle */}
          <div className="flex rounded bg-slate-950 p-0.5 border border-slate-800 text-[10px]">
            <button
              type="button"
              onClick={() => setDetailLevel('concise')}
              className={`px-2 py-0.5 rounded transition ${
                detailLevel === 'concise' ? 'bg-cyan-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              Concise
            </button>
            <button
              type="button"
              onClick={() => setDetailLevel('detailed')}
              className={`px-2 py-0.5 rounded transition ${
                detailLevel === 'detailed' ? 'bg-cyan-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              Detailed
            </button>
          </div>
        </div>
      </div>

      {/* Unconfigured Alert */}
      {status && !status.configured && (
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-xs text-amber-200 flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="flex items-start space-x-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1.5">
              <div className="font-semibold text-amber-100 flex items-center gap-2">
                <span>Generative AI Key Required</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-mono">
                  Gemini / OpenAI Supported
                </span>
              </div>
              <p className="text-[11px] text-slate-300 m-0 leading-relaxed">
                To activate real Generative AI explanations, add your key to <code className="bg-slate-950 px-1 py-0.5 rounded text-cyan-300 font-mono">backend/.env</code>:
              </p>
              <div className="text-[11px] font-mono bg-slate-950/80 p-2 rounded border border-slate-800 text-slate-300 space-y-1">
                <div className="text-emerald-400 font-semibold"># Free Google Gemini (Recommended):</div>
                <div>GEMINI_API_KEY=AIzaSy...</div>
                <div className="text-slate-500 text-[10px]">Get free key instantly at: <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-cyan-400 underline">aistudio.google.com</a></div>
                <div className="text-slate-400 pt-1 font-semibold"># Or OpenAI:</div>
                <div>OPENAI_API_KEY=sk-...</div>
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={checkStatus}
            className="self-start sm:self-center shrink-0 px-3 py-1.5 text-[11px] font-medium rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/30 flex items-center gap-1.5 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Recheck Key
          </button>
        </div>
      )}

      {/* Suggested Quick Questions */}
      {suggestedQuestions.length > 0 && isContextReady && (
        <div className="space-y-1.5">
          <div className="text-[11px] text-slate-400 flex items-center gap-1">
            <Lightbulb className="w-3 h-3 text-cyan-400" />
            <span>Suggested Operator Inquiries:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                disabled={loading || !isContextReady}
                onClick={() => handleSelectQuestion(q)}
                className="text-[10px] px-2.5 py-1 rounded-full bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 hover:border-slate-700 transition cursor-pointer text-left disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* User Question Input & Trigger Button */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading || !isContextReady}
            placeholder={
              isContextReady
                ? 'Optional: Ask a specific question about this result...'
                : 'Run prediction or evaluation above first to provide context...'
            }
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 disabled:opacity-50"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleExplain();
              }
            }}
          />

          <button
            type="button"
            disabled={loading || !isContextReady}
            onClick={() => handleExplain()}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs transition cursor-pointer flex items-center space-x-1.5 shrink-0 shadow-lg shadow-cyan-950/40 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Analyzing with AI...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Explain with AI</span>
              </>
            )}
          </button>
        </div>

        {!isContextReady && (
          <p className="text-[10px] text-slate-500 m-0 italic">
            * Please execute a model prediction or allocation above to supply genuine operational context to the AI explanation engine.
          </p>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-start space-x-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <div className="font-semibold text-red-200">Explanation Request Failed</div>
            <p className="text-[11px] text-red-300/80 m-0 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Rendered AI Explanation Result */}
      {result && (
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/90 space-y-4 text-xs">
          {/* Main Narrative */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-cyan-400">
              <span className="flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5" />
                Technical Analysis & Contextual Interpretation
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                {result.provider} • {result.model}
              </span>
            </div>
            <p className="text-xs text-slate-200 leading-relaxed m-0 bg-slate-900/60 p-3 rounded-lg border border-slate-850">
              {result.explanation}
            </p>
          </div>

          {/* Key Findings */}
          {result.key_findings && result.key_findings.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-300 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                <span>Key Grounded Findings:</span>
              </div>
              <ul className="space-y-1 pl-4 list-disc text-slate-300 text-[11px] leading-relaxed m-0">
                {result.key_findings.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Actionable Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="space-y-1.5 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
              <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Actionable Operator Recommendations:</span>
              </div>
              <ul className="space-y-1 pl-4 list-disc text-emerald-200/90 text-[11px] leading-relaxed m-0">
                {result.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Technical Limitations */}
          {result.limitations && result.limitations.length > 0 && (
            <div className="space-y-1.5 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
              <div className="text-[11px] font-semibold text-amber-400 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" />
                <span>Limitations & Data Scope:</span>
              </div>
              <ul className="space-y-1 pl-4 list-disc text-amber-200/90 text-[11px] leading-relaxed m-0">
                {result.limitations.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Footer details */}
          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
            <span>
              {result.prompt_tokens && result.completion_tokens
                ? `Processed ${result.prompt_tokens + result.completion_tokens} tokens`
                : 'Grounded against live telemetry'}
            </span>
            <button
              type="button"
              onClick={() => {
                setResult(null);
                setQuestion('');
              }}
              className="text-slate-400 hover:text-cyan-400 transition cursor-pointer flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset Explanation</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
