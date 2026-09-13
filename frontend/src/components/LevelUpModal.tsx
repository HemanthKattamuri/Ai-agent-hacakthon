import React, { useEffect } from 'react';
import { Sparkles, Crown, ArrowUpRight, X, Shield, Sword } from 'lucide-react';
import { sound } from '../soundEngine';

interface LevelUpModalProps {
  isOpen: boolean;
  newLevel: number;
  attributeIncreased?: string;
  statGain?: number;
  onClose: () => void;
}

export const LevelUpModal: React.FC<LevelUpModalProps> = ({
  isOpen,
  newLevel,
  attributeIncreased,
  statGain = 1,
  onClose
}) => {
  useEffect(() => {
    if (isOpen) {
      sound.playLevelUpFanfare();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl animate-fadeIn">
      <div className="relative w-full max-w-md rounded-3xl bg-gradient-to-b from-slate-900 via-indigo-950/80 to-slate-950 border-2 border-cyan-500/60 shadow-2xl shadow-cyan-500/40 p-6 sm:p-8 text-center overflow-hidden">
        
        {/* Animated Background Rays & Glow */}
        <div className="absolute inset-0 -m-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-500/30 via-indigo-600/20 to-transparent blur-2xl animate-pulse pointer-events-none" />

        {/* Floating Particles */}
        <div className="absolute top-4 left-6 text-amber-400 animate-bounce">✨</div>
        <div className="absolute top-8 right-8 text-cyan-300 animate-pulse delay-300">🌟</div>
        <div className="absolute bottom-6 left-8 text-fuchsia-400 animate-bounce delay-700">⚡</div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Level Emblem */}
        <div className="relative z-10 flex flex-col items-center">
          <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-fuchsia-500 p-1 shadow-2xl shadow-cyan-500/50 animate-bounce">
            <div className="w-full h-full rounded-2xl bg-slate-950 flex flex-col items-center justify-center text-white">
              <Crown className="w-8 h-8 text-amber-400 mb-0.5" />
              <span className="text-[10px] font-black uppercase tracking-widest text-cyan-300">LEVEL</span>
              <span className="text-2xl sm:text-3xl font-black leading-none">{newLevel}</span>
            </div>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight mt-4 bg-gradient-to-r from-white via-cyan-200 to-indigo-300 bg-clip-text text-transparent">
            LEVEL UP REACHED!
          </h2>
          <p className="text-xs text-slate-300 mt-1 max-w-xs">
            Your discipline has ascended to a new realm tier! Character attributes and combat capacity have evolved.
          </p>

          {/* Stat Boost Highlights */}
          <div className="w-full mt-5 space-y-2 bg-slate-950/70 p-4 rounded-2xl border border-slate-800 text-left">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Stat Points Earned:
            </div>
            
            {attributeIncreased && (
              <div className="flex items-center justify-between text-xs font-bold text-cyan-300 p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                <span className="capitalize flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  +{statGain} {attributeIncreased} Stat Mastery
                </span>
                <span className="text-[10px] bg-cyan-500/20 px-2 py-0.5 rounded text-cyan-200">ASCENDED</span>
              </div>
            )}

            <div className="flex items-center justify-between text-xs font-semibold text-slate-300 p-2 rounded-xl bg-slate-900 border border-slate-800">
              <span className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-purple-400" />
                Max HP & MP Restored to 100%
              </span>
              <span className="text-[10px] text-emerald-400 font-bold">RECHARGED</span>
            </div>

            <div className="flex items-center justify-between text-xs font-semibold text-slate-300 p-2 rounded-xl bg-slate-900 border border-slate-800">
              <span className="flex items-center gap-1.5">
                <Sword className="w-3.5 h-3.5 text-rose-400" />
                New Armory Gear Unlocked
              </span>
              <span className="text-[10px] text-amber-400 font-bold">TIER {newLevel}</span>
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={() => {
              sound.playQuestComplete();
              onClose();
            }}
            className="w-full mt-6 py-3 rounded-2xl font-bold text-sm bg-gradient-to-r from-cyan-500 via-indigo-600 to-fuchsia-600 hover:opacity-95 text-white shadow-xl shadow-cyan-500/30 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <span>Claim Ascendancy & Continue Quest</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
