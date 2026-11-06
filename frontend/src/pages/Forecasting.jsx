import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  BrainCircuit,
  Play,
  Calendar,
  CheckCircle2,
  TrendingUp,
  Award,
  Layers,
  Sparkles
} from 'lucide-react';
import {
  ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';

export default function Forecasting() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [forecastData, setForecastData] = useState(null);
  const [horizon, setHorizon] = useState(30);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchLatest = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/forecasting/latest?workspace_id=${activeWorkspace.id}`);
        if (res.data && res.data.best_model_name) {
          setForecastData(res.data);
        }
      } catch (err) {
        console.error('Error fetching latest forecast:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLatest();
  }, [activeWorkspace]);

  const handleRunForecast = async () => {
    if (!activeDataset) return;
    setRunning(true);
    try {
      const res = await api.post('/forecasting/run', {
        dataset_id: activeDataset.id,
        forecast_horizon: parseInt(horizon)
      });
      setForecastData(res.data);
    } catch (err) {
      alert(`Forecast run failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading forecasting engine and model benchmarks..." />;
  if (!activeDataset) return <EmptyState title="No Active Dataset" description="Select a dataset in the top navigation to run predictive forecasts." />;

  // Prepare chart series merging historical tail and future predictions
  const chartSeries = [];
  if (forecastData?.history_tail) {
    forecastData.history_tail.forEach(item => {
      chartSeries.push({
        date: item.date,
        actual: item.actual,
        forecast: null,
        lower: null,
        upper: null
      });
    });
  }

  if (forecastData?.future_forecast) {
    forecastData.future_forecast.forEach(item => {
      chartSeries.push({
        date: item.date,
        actual: null,
        forecast: item.predicted_value,
        lower: item.lower_bound,
        upper: item.upper_bound,
        ciRange: [item.lower_bound, item.upper_bound]
      });
    });
  }

  const valMetrics = forecastData?.validation_metrics || {};
  const testMetrics = forecastData?.test_metrics || {};

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Predictive Revenue & Demand Forecasting
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Multi-model chronological walk-forward cross-validation on <span className="text-brand-400 font-semibold">{activeDataset.name}</span>
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>Horizon:</span>
            <select
              value={horizon}
              onChange={(e) => setHorizon(e.target.value)}
              className="bg-transparent font-semibold text-white focus:outline-none cursor-pointer"
            >
              <option value={14} className="bg-slate-900">14 Days</option>
              <option value={30} className="bg-slate-900">30 Days</option>
              <option value={60} className="bg-slate-900">60 Days</option>
              <option value={90} className="bg-slate-900">90 Days</option>
            </select>
          </div>

          <button
            onClick={handleRunForecast}
            disabled={running}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-brand-600/20 transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{running ? 'Evaluating Models...' : 'Run Walk-Forward Forecast'}</span>
          </button>
        </div>
      </div>

      {forecastData ? (
        <>
          {/* Winner Model Banner & Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              title="Selected Best Model"
              value={forecastData.best_model_name}
              subtitle="Lowest Out-of-Sample RMSE"
              badgeText="Winner"
              icon={Award}
            />
            <KPICard
              title="Validation MAPE"
              value={`${valMetrics.mape || 0}%`}
              subtitle="Mean Absolute Percentage Error"
              trend={valMetrics.mape < 10 ? 'up' : 'down'}
              icon={TrendingUp}
            />
            <KPICard
              title="Validation RMSE"
              value={`$${(valMetrics.rmse || 0).toLocaleString()}`}
              subtitle={`MAE: $${(valMetrics.mae || 0).toLocaleString()}`}
              trend="neutral"
              icon={BrainCircuit}
            />
            <KPICard
              title="Model R² Score"
              value={`${valMetrics.r2 || 0}`}
              subtitle="Explained Variance"
              trend={valMetrics.r2 > 0.75 ? 'up' : 'neutral'}
              icon={Sparkles}
            />
          </div>

          {/* Interactive Chart with Prediction Envelope */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
              <div>
                <h2 className="text-base font-semibold text-white">Historical Actuals vs Forward Projections</h2>
                <p className="text-xs text-slate-400">Includes 95% Confidence Interval bounds computed from validation residuals</p>
              </div>
              <div className="flex items-center gap-4 text-xs font-medium">
                <span className="flex items-center gap-1.5 text-brand-400">
                  <span className="w-3 h-0.5 bg-brand-400 rounded" /> Historical Actuals
                </span>
                <span className="flex items-center gap-1.5 text-cyan-300">
                  <span className="w-3 h-0.5 bg-cyan-300 rounded border-dashed" /> Forecast Projection
                </span>
                <span className="flex items-center gap-1.5 text-slate-400">
                  <span className="w-3 h-3 bg-cyan-500/10 border border-cyan-500/30 rounded" /> 95% Confidence Envelope
                </span>
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartSeries}>
                  <defs>
                    <linearGradient id="ciGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38a9f8" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#38a9f8" stopOpacity={0.02}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    formatter={(val) => val ? [`$${Number(val).toLocaleString()}`, ''] : ['-', '']}
                  />
                  {/* Confidence bounds */}
                  <Area type="monotone" dataKey="upper" stroke="none" fill="url(#ciGradient)" name="Upper Bound" />
                  <Area type="monotone" dataKey="lower" stroke="none" fill="#090d16" fillOpacity={1} name="Lower Bound" />
                  {/* Historical Line */}
                  <Line type="monotone" dataKey="actual" stroke="#0e8ce9" strokeWidth={2.5} dot={false} name="Actual Revenue" />
                  {/* Forecast Line */}
                  <Line type="monotone" dataKey="forecast" stroke="#38bdf8" strokeWidth={2.5} strokeDasharray="4 4" dot={false} name="Forecast Revenue" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Comparison Matrix Table */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-semibold text-white">Full Model Benchmark Matrix</h2>
                <p className="text-xs text-slate-400">Strict chronological out-of-sample evaluation across all candidate algorithms</p>
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Model Architecture</th>
                    <th className="px-4 py-3 font-semibold text-right">Val MAE</th>
                    <th className="px-4 py-3 font-semibold text-right">Val RMSE</th>
                    <th className="px-4 py-3 font-semibold text-right">Val MAPE %</th>
                    <th className="px-4 py-3 font-semibold text-right">Val sMAPE %</th>
                    <th className="px-4 py-3 font-semibold text-right">R² Score</th>
                    <th className="px-4 py-3 font-semibold text-center">Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
                  {forecastData.model_comparison?.map((m, idx) => {
                    const isWinner = m.model_name === forecastData.best_model_name;
                    return (
                      <tr key={idx} className={`hover:bg-slate-800/30 transition-colors ${isWinner ? 'bg-brand-500/5' : ''}`}>
                        <td className="px-4 py-3 font-semibold text-white flex items-center gap-2">
                          {isWinner && <Award className="w-4 h-4 text-brand-400" />}
                          {m.model_name}
                        </td>
                        <td className="px-4 py-3 text-right font-mono">${m.val_mae?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-right font-mono font-bold text-white">${m.val_rmse?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-right font-mono">{m.val_mape}%</td>
                        <td className="px-4 py-3 text-right font-mono">{m.val_smape}%</td>
                        <td className="px-4 py-3 text-right font-mono">{m.val_r2}</td>
                        <td className="px-4 py-3 text-center">
                          {isWinner ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-brand-500/20 text-brand-300 border border-brand-500/30">
                              Selected Winner
                            </span>
                          ) : (
                            <span className="text-[11px] text-slate-500">Benchmark</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <EmptyState
          title="No Forecast Models Trained Yet"
          description="Click 'Run Walk-Forward Forecast' above to benchmark ML algorithms against naive baselines."
        />
      )}
    </div>
  );
}

