import React from 'react';
import { 
  Shield, 
  Sparkles, 
  Brain, 
  Dumbbell, 
  Zap, 
  Heart, 
  MessageSquare, 
  Award, 
  Flame, 
  Sword, 
  Crown,
  CheckCircle2,
  Layers
} from 'lucide-react';
import { sound } from '../soundEngine';
import type { User, CharacterStats, InventoryItem } from '../types';

interface CharacterSheetProps {
  user: User;
  stats: CharacterStats;
  equippedItems: InventoryItem[];
  gearBonuses: Record<string, number>;
  totalStats: Record<string, number>;
  radarData: Array<{ attribute: string; value: number; base: number; gear: number }>;
  onEquipItem: (id: string, equip: boolean) => Promise<void>;
}

const STAT_CONFIG: Record<string, { label: string; icon: any; color: string; bg: string; desc: string }> = {
  intellect: { label: 'Intellect', icon: Brain, color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/30', desc: 'Accelerates coding speed, problem-solving, and logic mastery' },
  strength: { label: 'Strength', icon: Dumbbell, color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/30', desc: 'Increases physical endurance, workout energy, and raw willpower' },
  agility: { label: 'Agility', icon: Zap, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', desc: 'Speeds up daily task completion rate and backlog sprint clearing' },
  vitality: { label: 'Vitality', icon: Heart, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/30', desc: 'Boosts max HP, sleep quality, hydration, and stress resistance' },
  charisma: { label: 'Charisma', icon: MessageSquare, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30', desc: 'Enhances communication clarity, networking, and leadership presence' },
};

export const CharacterSheet: React.FC<CharacterSheetProps> = ({
  user,
  stats,
  equippedItems,
  gearBonuses,
  totalStats,
  radarData,
  onEquipItem
}) => {
  const slots: Array<{ type: string; label: string; icon: any }> = [
    { type: 'weapon', label: 'Main Weapon', icon: Sword },
    { type: 'helmet', label: 'Neural Visor / Crown', icon: Crown },
    { type: 'armor', label: 'Body Armor / Robe', icon: Shield },
    { type: 'pet', label: 'Familiar Pet', icon: Sparkles },
    { type: 'aura', label: 'Cosmetic Aura', icon: Flame },
  ];

  const radius = 80;
  const center = 110;
  const numPoints = 5;

  const getCoordinates = (index: number, value: number) => {
    const angle = (Math.PI * 2 / numPoints) * index - Math.PI / 2;
    const r = (value / 100) * radius;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y };
  };

  const polygonPoints = radarData
    .map((d, i) => {
      const pt = getCoordinates(i, Math.max(15, d.value));
      return `${pt.x},${pt.y}`;
    })
    .join(' ');

  return (
    <div className="space-y-6">
      <div className="relative rounded-3xl p-6 bg-gradient-to-r from-slate-900/90 via-indigo-950/40 to-slate-900/90 border border-slate-800 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 -m-8 w-64 h-64 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-center gap-6">
          <div className="relative">
            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-fuchsia-600 p-1 shadow-xl shadow-cyan-500/20">
              <div className="w-full h-full rounded-xl bg-slate-950 flex flex-col items-center justify-center text-4xl select-none">
                {user.class_name === 'Code Mage' ? '🧙‍♂️' : (
                  user.class_name === 'Iron Warrior' ? '⚔️' : (
                    user.class_name === 'Paladin Scholar' ? '🛡️' : '🥷'
                  )
                )}
              </div>
            </div>
            <div className="absolute -bottom-2 -right-2 px-2 py-0.5 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 text-[10px] font-black text-white shadow">
              LVL {stats.level}
            </div>
          </div>

          <div className="text-center md:text-left flex-1">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
              <h2 className="text-2xl font-black text-white tracking-tight">
                {user.username}
              </h2>
              <span className="px-2 py-0.5 rounded-lg text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                {user.class_name}
              </span>
              <span className="px-2 py-0.5 rounded-lg text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {user.title}
              </span>
            </div>

            <p className="text-xs text-slate-400 mt-1.5 max-w-xl">
              Equipped with neural-focus runes and battle-forged habits. Every task completed bolsters your core RPG stats and deals direct damage to procrastination monsters.
            </p>

            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 mt-3 text-xs">
              <div className="flex items-center gap-1.5 text-slate-300">
                <Flame className="w-4 h-4 text-orange-400 fill-orange-400/30" />
                <span>Streak: <strong className="text-amber-400">{stats.streak_count} Days</strong></span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Quests Completed: <strong className="text-emerald-400">{stats.tasks_completed_count}</strong></span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-300">
                <Sword className="w-4 h-4 text-rose-400" />
                <span>Boss DMG: <strong className="text-rose-400">{stats.boss_damage_dealt} HP</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Equipped Battle Gear
            </h3>
            <span className="text-[11px] text-slate-400">
              {equippedItems.length} / {slots.length} Slots Active
            </span>
          </div>

          <div className="space-y-3">
            {slots.map((slot) => {
              const equipped = equippedItems.find((item) => item.item_type === slot.type);
              const SlotIcon = slot.icon;

              return (
                <div
                  key={slot.type}
                  className={`p-3 rounded-2xl border transition-all ${
                    equipped
                      ? 'bg-slate-900/80 border-slate-700/80 hover:border-slate-600 shadow-md'
                      : 'bg-slate-950/40 border-slate-800/60 border-dashed'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        equipped ? 'bg-gradient-to-tr from-cyan-600/30 to-indigo-600/30 text-cyan-300 border border-cyan-500/40' : 'bg-slate-900 text-slate-600'
                      }`}>
                        <SlotIcon className="w-5 h-5" />
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs font-bold text-white">
                            {equipped ? equipped.item_name : `Empty ${slot.label}`}
                          </h4>
                          {equipped && (
                            <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                              {equipped.rarity}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {equipped ? equipped.description : `Visit the Armory Shop to acquire ${slot.label.toLowerCase()}`}
                        </p>
                      </div>
                    </div>

                    {equipped && (
                      <button
                        onClick={() => {
                          sound.playEquipItem();
                          onEquipItem(equipped.id, false);
                        }}
                        className="px-2.5 py-1 rounded-lg text-[10px] font-bold text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors cursor-pointer"
                        title="Unequip Gear"
                      >
                        Unequip
                      </button>
                    )}
                  </div>

                  {equipped && equipped.stat_bonus && Object.keys(equipped.stat_bonus).length > 0 && (
                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-slate-800/60 flex-wrap">
                      {Object.entries(equipped.stat_bonus).map(([k, v]) => (
                        <span key={k} className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                          +{v} {k.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Award className="w-4 h-4 text-purple-400" />
              5-Attribute Pentagon & Mastery
            </h3>
            <span className="text-[11px] text-cyan-400 font-semibold">
              Total Stat Points: {Object.values(totalStats).reduce((a, b) => a + b, 0)}
            </span>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5">
            <div className="flex justify-center items-center py-1">
              <svg width="220" height="220" className="overflow-visible select-none">
                <defs>
                  <linearGradient id="radarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.6" />
                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.4" />
                  </linearGradient>
                </defs>

                {[0.25, 0.5, 0.75, 1.0].map((ringScale) => {
                  const ringPoints = Array.from({ length: 5 })
                    .map((_, i) => {
                      const pt = getCoordinates(i, ringScale * 100);
                      return `${pt.x},${pt.y}`;
                    })
                    .join(' ');
                  return (
                    <polygon
                      key={ringScale}
                      points={ringPoints}
                      fill="none"
                      stroke="#334155"
                      strokeWidth="1"
                      strokeDasharray={ringScale === 1.0 ? '0' : '3 3'}
                    />
                  );
                })}

                {Array.from({ length: 5 }).map((_, i) => {
                  const pt = getCoordinates(i, 100);
                  return (
                    <line
                      key={i}
                      x1={center}
                      y1={center}
                      x2={pt.x}
                      y2={pt.y}
                      stroke="#334155"
                      strokeWidth="1"
                    />
                  );
                })}

                <polygon
                  points={polygonPoints}
                  fill="url(#radarGrad)"
                  stroke="#06b6d4"
                  strokeWidth="2.5"
                  className="transition-all duration-500 ease-out drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]"
                />

                {radarData.map((d, i) => {
                  const pt = getCoordinates(i, Math.max(15, d.value));
                  const labelPt = getCoordinates(i, 122);
                  return (
                    <g key={d.attribute}>
                      <circle
                        cx={pt.x}
                        cy={pt.y}
                        r="4"
                        fill="#ffffff"
                        stroke="#06b6d4"
                        strokeWidth="2"
                      />
                      <text
                        x={labelPt.x}
                        y={labelPt.y}
                        textAnchor="middle"
                        dominantBaseline="central"
                        className="text-[10px] font-bold fill-slate-300"
                      >
                        {d.attribute} ({d.value})
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="space-y-2.5 pt-2 border-t border-slate-800">
              {Object.entries(STAT_CONFIG).map(([key, cfg]) => {
                const Icon = cfg.icon;
                const baseVal = (stats as any)[key] || 10;
                const gearVal = (gearBonuses as any)[key] || 0;
                const totalVal = baseVal + gearVal;
                const progressPct = Math.min(100, Math.round((totalVal / 100) * 100));

                return (
                  <div key={key} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-slate-200">
                        <Icon className={`w-3.5 h-3.5 ${cfg.color}`} />
                        <span>{cfg.label}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 font-semibold">
                        <span className="text-white font-bold">{totalVal}</span>
                        {gearVal > 0 && <span className="text-cyan-400 ml-1">(+{gearVal} Gear)</span>}
                      </div>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-950 border border-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-500`}
                        style={{ width: `${progressPct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
