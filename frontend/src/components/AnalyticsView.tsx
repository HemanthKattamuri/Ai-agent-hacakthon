import React from 'react';
import { 
  Flame, 
  Sparkles, 
  Calendar, 
  Award, 
  CheckCircle2, 
  Sword,
  Clock
} from 'lucide-react';
import type { AnalyticsData, CharacterStats } from '../types';

interface AnalyticsViewProps {
  analytics: AnalyticsData;
  character: CharacterStats;
}

const HEATMAP_COLORS = [
  'bg-slate-900 border-slate-800 text-slate-600',
  'bg-cyan-950/60 border-cyan-800/80 text-cyan-400',
  'bg-cyan-700/70 border-cyan-600 text-cyan-200',
  'bg-cyan-500 border-cyan-400 text-slate-950 font-bold',
  'bg-indigo-500 border-indigo-400 text-white font-bold',
];

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  analytics,
  character
}) => {
  return (
    <div className="space-y-6">
      
      {/* Top Metrics Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Consecutive Streak</span>
            <Flame className="w-4 h-4 text-orange-400 fill-orange-400/30" />
          </div>
          <div className="text-2xl font-black text-amber-400">
            {character.streak_count} <span className="text-xs font-semibold text-slate-400">Days</span>
          </div>
          <p className="text-[10px] text-slate-500">+{(character.streak_count - 1) * 3}% XP Boost Active</p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Quests Cleared</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">
            {character.tasks_completed_count}
          </div>
          <p className="text-[10px] text-slate-500">Total Lifecycle Completions</p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Boss DMG</span>
            <Sword className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400">
            {character.boss_damage_dealt} <span className="text-xs font-semibold text-slate-400">HP</span>
          </div>
          <p className="text-[10px] text-slate-500">Dealt across all raid encounters</p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Current Level</span>
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400">
            LVL {character.level}
          </div>
          <p className="text-[10px] text-slate-500">{character.current_xp} / {character.next_level_xp} XP to next level</p>
        </div>

      </div>

      {/* 30-Day Activity Heatmap Matrix */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Calendar className="w-4 h-4 text-cyan-400" />
            30-Day Productivity & Habit Matrix
          </h3>
          <span className="text-[11px] text-slate-400">
            Daily consistency tracker
          </span>
        </div>

        {/* Heat Grid */}
        <div className="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-15 gap-2">
          {analytics.activity_matrix.map((day) => {
            const colorClass = HEATMAP_COLORS[Math.min(HEATMAP_COLORS.length - 1, day.level)];
            return (
              <div
                key={day.date}
                className={`p-2 rounded-xl border flex flex-col items-center justify-center text-center transition-transform hover:scale-105 select-none ${colorClass}`}
                title={`${day.date}: ${day.completed_tasks} Quests completed`}
              >
                <span className="text-[9px] uppercase opacity-75">{day.day}</span>
                <span className="text-xs font-bold">{day.completed_tasks}</span>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-end gap-2 text-[10px] text-slate-400 pt-2 border-t border-slate-800">
          <span>Less Active</span>
          {HEATMAP_COLORS.map((c, i) => (
            <span key={i} className={`w-3.5 h-3.5 rounded-sm border ${c}`} />
          ))}
          <span>More Active</span>
        </div>
      </div>

      {/* Attribute Breakdown & Recent Activity Log */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Attribute XP Distribution (LG: 5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-purple-400" />
            Completed Quests by Attribute
          </h3>

          <div className="space-y-3 pt-2">
            {analytics.attribute_breakdown.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No completed quests yet. Finish tasks to view distribution.</p>
            ) : (
              analytics.attribute_breakdown.map((item) => (
                <div key={item.attribute_tag} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="capitalize text-slate-200">{item.attribute_tag}</span>
                    <span className="text-cyan-400">{item.count} Quests ({item.total_xp} XP)</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500"
                      style={{
                        width: `${Math.min(100, Math.round((item.count / Math.max(1, character.tasks_completed_count)) * 100))}%`
                      }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Real-time Activity Timeline (LG: 7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" />
            Recent Chronicle Logs
          </h3>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {analytics.recent_logs.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No activity recorded yet.</p>
            ) : (
              analytics.recent_logs.map((log) => (
                <div
                  key={log.id}
                  className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" />
                    <span className="text-slate-300 font-medium">{log.message}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
