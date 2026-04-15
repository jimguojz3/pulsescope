'use client';

import { useState } from 'react';
import { Search, AlertTriangle, AlertCircle, Activity, Ship, Factory, TrendingUp, Loader2 } from 'lucide-react';

interface Report {
  company: string;
  event: string;
  event_date?: string;
  risk_level: string;
  reasoning: string;
  impact_chain: string[];
  suggested_metrics: string[];
}

function cn(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ');
}

function RiskBadge({ level }: { level: string }) {
  const map: Record<string, { text: string; cls: string; icon: React.ReactNode }> = {
    高: { text: '高风险', cls: 'bg-red-500/10 text-red-400 border-red-500/30', icon: <AlertTriangle className="w-4 h-4" /> },
    中: { text: '中风险', cls: 'bg-amber-500/10 text-amber-400 border-amber-500/30', icon: <AlertCircle className="w-4 h-4" /> },
    低: { text: '低风险', cls: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', icon: <Activity className="w-4 h-4" /> },
  };
  const conf = map[level] || map['低'];
  return (
    <span className={cn('inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border', conf.cls)}>
      {conf.icon}
      {conf.text}
    </span>
  );
}

export default function Home() {
  const [company, setCompany] = useState('万华化学');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState('');

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    setReports([]);
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: company, days_back: days }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || '分析失败');
      } else {
        setReports(data.reports || []);
      }
    } catch (err) {
      setError('网络错误，请确保后端服务已启动 (python src/pulsescope/api/main.py)');
    } finally {
      setLoading(false);
    }
  }

  const high = reports.filter(r => r.risk_level === '高').length;
  const med = reports.filter(r => r.risk_level === '中').length;
  const low = reports.filter(r => r.risk_level === '低').length;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-indigo-400" />
            PulseScope
          </h1>
          <p className="text-slate-400 mt-2">供应链风险情报引擎 — 监控新闻、事件推理、定制化风险报告</p>
        </header>

        <form onSubmit={handleAnalyze} className="bg-slate-900/60 border border-slate-700/60 rounded-2xl p-5 mb-8 backdrop-blur">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-slate-300 mb-1.5">企业名称</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                  placeholder="例如：万华化学"
                />
              </div>
            </div>
            <div className="w-full md:w-40">
              <label className="block text-sm font-medium text-slate-300 mb-1.5">时间范围（天）</label>
              <input
                type="number"
                min={1}
                max={30}
                value={days}
                onChange={e => setDays(Number(e.target.value))}
                className="w-full px-3 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full md:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/60 text-white text-sm font-semibold rounded-lg transition"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? '分析中...' : '生成风险报告'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-200 text-sm">
            {error}
          </div>
        )}

        {reports.length > 0 && (
          <section className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 rounded-lg bg-red-500/10 text-red-400"><AlertTriangle className="w-5 h-5" /></div>
                <div>
                  <div className="text-2xl font-bold text-white">{high}</div>
                  <div className="text-xs text-slate-400">高风险事件</div>
                </div>
              </div>
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400"><AlertCircle className="w-5 h-5" /></div>
                <div>
                  <div className="text-2xl font-bold text-white">{med}</div>
                  <div className="text-xs text-slate-400">中风险事件</div>
                </div>
              </div>
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4 flex items-center gap-4">
                <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400"><Activity className="w-5 h-5" /></div>
                <div>
                  <div className="text-2xl font-bold text-white">{low}</div>
                  <div className="text-xs text-slate-400">低风险事件</div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {reports.map((r, idx) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-700/60 rounded-2xl p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <h3 className="text-lg font-semibold text-white">{r.event}</h3>
                    <RiskBadge level={r.risk_level} />
                  </div>

                  <div className="mb-5">
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1.5">推理</div>
                    <p className="text-slate-300 text-sm leading-relaxed">{r.reasoning}</p>
                  </div>

                  <div className="mb-5">
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">影响链</div>
                    <div className="relative pl-4 border-l-2 border-slate-700 space-y-4">
                      {r.impact_chain.map((step, i) => (
                        <div key={i} className="relative">
                          <span className="absolute -left-[21px] top-0.5 w-4 h-4 rounded-full bg-slate-800 border border-slate-600 text-[10px] text-slate-300 flex items-center justify-center">
                            {i + 1}
                          </span>
                          <p className="text-slate-300 text-sm">{step}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">关键监测指标</div>
                    <div className="flex flex-wrap gap-2">
                      {r.suggested_metrics.map((m, i) => (
                        <span key={i} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-950 border border-slate-700 text-slate-300 text-xs">
                          {m.includes('航') || m.includes('运') ? <Ship className="w-3 h-3" /> : m.includes('产') || m.includes('装置') ? <Factory className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {!loading && reports.length === 0 && !error && (
          <div className="text-center py-16 text-slate-500 text-sm">
            输入企业名称并点击“生成风险报告”查看结果
          </div>
        )}
      </div>
    </main>
  );
}
