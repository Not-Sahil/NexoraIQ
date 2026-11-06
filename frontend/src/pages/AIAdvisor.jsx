import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Bot,
  Send,
  Sparkles,
  CheckCircle2,
  AlertOctagon,
  ArrowRight,
  HelpCircle,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';

const SUGGESTED_QUERIES = [
  "Why did my profit decrease this month?",
  "Which products or catalog lines should I prioritize?",
  "Which customer accounts are currently at risk of churning?",
  "What is my expected revenue over the next 30 days?",
  "Where are we spending inefficiently across marketing?"
];

export default function AIAdvisor() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your NexoraIQ Business Decision Advisor. I analyze your uploaded datasets, walk-forward forecasts, unit economics, and anomaly models to provide evidence-backed recommendations. Ask me any strategic business question below.'
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingRecs, setLoadingRecs] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchRecs = async () => {
      setLoadingRecs(true);
      try {
        const url = activeDataset
          ? `/advisor/recommendations?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/advisor/recommendations?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setRecommendations(res.data.recommendations || []);
      } catch (err) {
        console.error('Error fetching recommendations:', err);
      } finally {
        setLoadingRecs(false);
      }
    };
    fetchRecs();
  }, [activeWorkspace, activeDataset]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputQuery;
    if (!query.trim() || sending) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setSending(true);

    try {
      const res = await api.post(`/advisor/chat?workspace_id=${activeWorkspace?.id}`, {
        query: query,
        dataset_id: activeDataset?.id
      });
      const assistantMsg = {
        role: 'assistant',
        content: res.data.answer,
        dataPoints: res.data.data_points,
        confidence: res.data.confidence
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error retrieving analytical metrics: ${err.response?.data?.detail || err.message}`
      }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Bot className="w-7 h-7 text-cyan-400" />
          Grounded AI Business Decision Advisor
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Evidence-backed reasoning engine synthesizing predictive forecasts, margin compression, and customer churn
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Interactive Chat Assistant (7 cols) */}
        <div className="lg:col-span-7 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-col h-[650px] shadow-sm">
          {/* Chat Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60 rounded-t-xl">
            <div className="flex items-center gap-2.5">
              <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-xs font-semibold text-white">Tool-Grounded Context Active</span>
            </div>
            <span className="text-[11px] font-mono text-slate-500">Hallucination-Protected</span>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                    isUser
                      ? 'bg-brand-600 text-white rounded-br-none shadow-md'
                      : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none shadow-sm'
                  }`}>
                    <p>{msg.content}</p>
                    {msg.confidence && (
                      <span className="block mt-2 text-[10px] text-brand-300 font-semibold uppercase tracking-wider">
                        &bull; Grounded Confidence: {msg.confidence}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
            {sending && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-slate-950 border border-slate-800 px-4 py-3 text-xs text-slate-400 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span>Querying analytical engines and computing ground-truth metrics...</span>
                </div>
              </div>
            )}
          </div>

          {/* Suggested Prompts */}
          <div className="px-4 py-2 border-t border-slate-800/60 bg-slate-950/40 flex items-center gap-2 overflow-x-auto">
            <span className="text-[10px] text-slate-500 uppercase font-semibold shrink-0">Suggestions:</span>
            {SUGGESTED_QUERIES.slice(0, 3).map((q, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(q)}
                className="text-[11px] text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700/50 whitespace-nowrap transition-colors"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Chat Input */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
            className="p-3 border-t border-slate-800 bg-slate-950/80 rounded-b-xl flex items-center gap-2"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask a strategic decision question (e.g. Why did my profit decrease?)..."
              className="flex-1 rounded-lg bg-slate-900 border border-slate-800 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || sending}
              className="p-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Strategic Prioritized Recommendations Feed (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Prioritized Action Feed ({recommendations.length})
            </h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Evidence-Backed
            </span>
          </div>

          {loadingRecs ? (
            <LoadingSpinner message="Generating root-cause recommendations..." />
          ) : recommendations.length > 0 ? (
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-1">
              {recommendations.map((rec, idx) => {
                const isCritical = rec.priority === 'critical';
                const isHigh = rec.priority === 'high';
                return (
                  <div
                    key={idx}
                    className="p-5 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-slate-700 transition-all space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        isCritical
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : isHigh
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                      }`}>
                        {rec.priority} Priority &bull; {rec.category}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400 font-semibold">
                        {(rec.confidence_score * 100).toFixed(0)}% Conf
                      </span>
                    </div>

                    <h3 className="text-xs font-bold text-white leading-snug">
                      {rec.problem_statement}
                    </h3>

                    <div className="text-[11px] text-slate-300 space-y-1.5 bg-slate-950/60 p-3 rounded-lg border border-slate-800/60">
                      <p><strong className="text-slate-400">Evidence:</strong> {rec.supporting_evidence}</p>
                      <p><strong className="text-slate-400">Root Cause:</strong> {rec.possible_root_cause}</p>
                    </div>

                    <div className="pt-2 text-xs">
                      <p className="font-semibold text-brand-300 flex items-start gap-1.5">
                        <ArrowRight className="w-3.5 h-3.5 mt-0.5 shrink-0 text-brand-400" />
                        <span>Action: {rec.recommended_action}</span>
                      </p>
                      <p className="text-[11px] text-emerald-400 mt-1 font-medium pl-5">
                        Impact: {rec.expected_business_impact}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800">
              <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-medium">No pressing strategic risks detected across active datasets.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

