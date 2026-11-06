import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function KPICard({
  title,
  value,
  change,
  trend = 'up',
  subtitle,
  icon: Icon,
  badgeText
}) {
  const isPositive = trend === 'up';
  const isNeutral = trend === 'neutral';

  return (
    <div className="relative overflow-hidden rounded-xl bg-slate-900/70 border border-slate-800/80 p-5 shadow-sm hover:border-slate-700/80 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">
          {title}
        </span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-slate-800/80 border border-slate-700/50 flex items-center justify-center text-brand-400">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <h3 className="text-2xl font-bold tracking-tight text-white">
          {value}
        </h3>
        {badgeText && (
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
            {badgeText}
          </span>
        )}
      </div>

      {(change !== undefined || subtitle) && (
        <div className="mt-3 flex items-center gap-1.5 text-xs">
          {change !== undefined && (
            <span className={`inline-flex items-center font-medium ${
              isNeutral ? 'text-slate-400' : isPositive ? 'text-emerald-400' : 'text-rose-400'
            }`}>
              {isNeutral ? (
                <Minus className="w-3.5 h-3.5 mr-0.5" />
              ) : isPositive ? (
                <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
              ) : (
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
              )}
              {change > 0 ? `+${change}%` : `${change}%`}
            </span>
          )}
          {subtitle && (
            <span className="text-slate-400 text-[11px]">
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

