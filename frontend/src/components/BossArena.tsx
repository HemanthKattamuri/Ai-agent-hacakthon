import React, { useState } from 'react';
import { 
  Flame, 
  Sword, 
  Sparkles, 
  Coins, 
  Gem, 
  Swords,
  Heart
} from 'lucide-react';
import { sound } from '../soundEngine';
import type { BossRaid, CharacterStats } from '../types';

interface BossArenaProps {
  boss: BossRaid;
  character: CharacterStats;
  onRefreshBoss?: () => Promise<void>;
}

export const BossArena: React.FC<BossArenaProps> = ({
  boss,
  character
}) => {
  const [isAttacking, setIsAttacking] = useState<boolean>(false);
  const [combatEffects, setCombatEffects] = useState<Array<{ id: number; damage: number; x: number; y: number }>>([]);

  const hpPercent = Math.min(100, Math.max(0, Math.round((boss.current_hp / Math.max(1, boss.max_hp)) * 100)));
  const isDefeated = !!boss.is_defeated || boss.current_hp <= 0;

  const triggerSpecialStrike = () => {
    if (character.mp < 20) {
      alert("Need at least 20 Focus MP to execute Overclock Strike! Complete tasks to restore Focus.");
      return;
    }
    sound.playBossSlash();
    setIsAttacking(true);

    const dmg = 250 + Math.floor(Math.random() * 150);
    const newEff = {
      id: Date.now(),
      damage: dmg,
      x: 40 + Math.random() * 20,
      y: 30 + Math.random() * 30
    };
    setCombatEffects((prev) => [...prev, newEff]);

    setTimeout(() => {
      setCombatEffects((prev) => prev.filter((e) => e.id !== newEff.id));
      setIsAttacking(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between p-4 rounded-2xl bg-rose-950/20 border border-rose-900/40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <Swords className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Daily Procrastination Dungeon Raid</h3>
            <p className="text-xs text-slate-400">
              Every quest completed in your journal strikes the monster with weapon attack damage.
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-rose-300 font-bold">
          <Flame className="w-4 h-4 text-orange-400 animate-pulse" />
          <span>Active Raid Season 1</span>
        </div>
      </div>

      <div className="relative rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl p-6 sm:p-8 overflow-hidden">
        <div className="absolute top-0 right-0 -m-12 w-96 h-96 rounded-full bg-rose-600/10 blur-[100px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 -m-12 w-96 h-96 rounded-full bg-indigo-600/10 blur-[100px] pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between gap-8">
          <div className="flex flex-col items-center text-center">
            <div className={`relative w-36 h-36 sm:w-44 sm:h-44 rounded-3xl bg-gradient-to-br from-rose-950/80 via-slate-900 to-indigo-950/80 border-2 border-rose-500/40 flex items-center justify-center text-6xl shadow-2xl shadow-rose-950/50 select-none transition-transform duration-300 ${
              isAttacking ? 'scale-95 translate-x-1 translate-y-1' : 'hover:scale-105'
            }`}>
              <span className={isDefeated ? 'grayscale opacity-50' : 'animate-pulse'}>
                {isDefeated ? '💀' : '👹'}
              </span>

              {combatEffects.map((eff) => (
                <div
                  key={eff.id}
                  className="absolute font-black text-rose-400 text-2xl drop-shadow-[0_0_8px_rgba(244,63,94,0.8)] animate-bounce"
                  style={{ top: `${eff.y}%`, left: `${eff.x}%` }}
                >
                  -{eff.damage} HP!
                </div>
              ))}

              {isDefeated && (
                <div className="absolute inset-0 rounded-3xl bg-black/60 backdrop-blur-xs flex items-center justify-center">
                  <span className="px-3 py-1 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-black text-sm uppercase tracking-wider">
                    DEFEATED!
                  </span>
                </div>
              )}
            </div>

            <div className="mt-3">
              <h2 className="text-lg font-black text-white">{boss.name}</h2>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">
                {isDefeated ? 'Raid Victorious' : 'Tier 1 World Boss'}
              </span>
            </div>
          </div>

          <div className="flex-1 w-full max-w-xl space-y-4">
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              {boss.description}
            </p>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="flex items-center gap-1.5 text-rose-400">
                  <Heart className="w-4 h-4 fill-rose-500" /> Monster Health Gauge
                </span>
                <span className="text-slate-200">
                  {boss.current_hp} / {boss.max_hp} HP ({hpPercent}%)
                </span>
              </div>

              <div className="w-full h-4 rounded-full bg-slate-950 border border-slate-800 overflow-hidden relative shadow-inner">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    hpPercent > 50
                      ? 'bg-gradient-to-r from-rose-500 to-orange-500'
                      : (hpPercent > 20 ? 'bg-gradient-to-r from-orange-500 to-amber-500' : 'bg-rose-600 animate-pulse')
                  }`}
                  style={{ width: `${hpPercent}%` }}
                />
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                Bounty Rewards upon Defeat:
              </div>
              <div className="flex flex-wrap items-center gap-3 text-xs font-bold">
                <span className="flex items-center gap-1 text-cyan-400">
                  <Sparkles className="w-3.5 h-3.5" /> +{boss.reward_xp} XP
                </span>
                <span className="flex items-center gap-1 text-amber-400">
                  <Coins className="w-3.5 h-3.5" /> +{boss.reward_gold} Gold
                </span>
                <span className="flex items-center gap-1 text-purple-400">
                  <Gem className="w-3.5 h-3.5" /> +{boss.reward_gems} Soul Gems
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={triggerSpecialStrike}
                disabled={isDefeated || isAttacking}
                className="flex-1 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-rose-600 via-orange-600 to-amber-600 hover:opacity-95 text-white shadow-lg shadow-rose-600/25 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
              >
                <Sword className="w-4 h-4" />
                <span>Overclock Focus Strike (-20 Focus MP)</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
