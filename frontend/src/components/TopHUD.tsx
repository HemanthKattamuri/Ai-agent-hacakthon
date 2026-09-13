import React, { useState } from 'react';
import { 
  Flame, 
  Coins, 
  Gem, 
  Volume2, 
  VolumeX, 
  Palette, 
  LogOut, 
  RotateCcw, 
  Sparkles, 
  ChevronDown,
  Heart,
  Zap,
  Sword,
  User as UserIcon
} from 'lucide-react';
import { AnimatedLogo } from './AnimatedLogo';
import { sound } from '../soundEngine';
import type { User, CharacterStats } from '../types';

interface TopHUDProps {
  user: User;
  character: CharacterStats;
  currentTheme: string;
  onThemeChange: (theme: string) => void;
  onLogout: () => void;
  onResetDemo: () => void;
  isResetting: boolean;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const TopHUD: React.FC<TopHUDProps> = ({
  user,
  character,
  currentTheme,
  onThemeChange,
  onLogout,
  onResetDemo,
  isResetting,
  activeTab,
  setActiveTab
}) => {
  const [muted, setMuted] = useState<boolean>(() => sound.isMuted());
  const [showProfileMenu, setShowProfileMenu] = useState<boolean>(false);
  const [showThemeMenu, setShowThemeMenu] = useState<boolean>(false);

  const handleToggleMute = () => {
    const isNowMuted = sound.toggleMute();
    setMuted(isNowMuted);
    if (!isNowMuted) sound.playButtonTick();
  };

  const xpPercent = Math.min(100, Math.round((character.current_xp / Math.max(1, character.next_level_xp)) * 100));
  const hpPercent = Math.min(100, Math.round((character.hp / Math.max(1, character.max_hp)) * 100));
  const mpPercent = Math.min(100, Math.round((character.mp / Math.max(1, character.max_mp)) * 100));

  const themes = [
    { id: 'cyberpunk', name: 'Cyberpunk Neon', color: 'bg-cyan-500' },
    { id: 'fantasy', name: 'Obsidian Fantasy', color: 'bg-purple-600' },
    { id: 'solar', name: 'Solar Radiant', color: 'bg-amber-500' },
    { id: 'void', name: 'Midnight Void', color: 'bg-slate-700' }
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <AnimatedLogo size="sm" showText={true} />
          </div>

          <div className="hidden md:flex items-center gap-4 flex-1 max-w-lg px-2">
            <div className="flex flex-col items-center justify-center min-w-[50px] px-2 py-1 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-extrabold shadow-md shadow-cyan-500/20">
              <span className="text-[10px] uppercase font-bold text-cyan-200">LVL</span>
              <span className="text-sm leading-none">{character.level}</span>
            </div>

            <div className="flex-1 space-y-1.5">
              <div className="space-y-0.5">
                <div className="flex justify-between text-[10px] font-semibold text-slate-300">
                  <span className="flex items-center gap-1 text-cyan-400">
                    <Sparkles className="w-2.5 h-2.5" /> XP
                  </span>
                  <span>{character.current_xp} / {character.next_level_xp} ({xpPercent}%)</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 border border-slate-800 overflow-hidden relative">
                  <div 
                    className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-indigo-500 to-fuchsia-500 transition-all duration-500 ease-out"
                    style={{ width: `${xpPercent}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-0.5">
                  <div className="flex justify-between text-[9px] font-bold text-rose-400">
                    <span className="flex items-center gap-0.5"><Heart className="w-2.5 h-2.5 fill-rose-500" /> HP</span>
                    <span>{character.hp}/{character.max_hp}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                    <div className="h-full bg-rose-500 transition-all duration-300" style={{ width: `${hpPercent}%` }} />
                  </div>
                </div>

                <div className="space-y-0.5">
                  <div className="flex justify-between text-[9px] font-bold text-indigo-400">
                    <span className="flex items-center gap-0.5"><Zap className="w-2.5 h-2.5 fill-indigo-500" /> FOCUS</span>
                    <span>{character.mp}/{character.max_mp}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                    <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${mpPercent}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3">
            <div 
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-orange-500/10 border border-orange-500/30 text-amber-300 font-bold text-xs"
              title={`${character.streak_count} Consecutive Active Days (+${Math.min(50, (character.streak_count - 1) * 3)}% XP bonus)`}
            >
              <Flame className="w-4 h-4 text-orange-400 fill-orange-400/40 animate-bounce" />
              <span>{character.streak_count}d</span>
            </div>

            <div 
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 font-bold text-xs"
              title="Gold Coins: Earn by completing quests to buy armory gear"
            >
              <Coins className="w-4 h-4 text-amber-400" />
              <span>{character.gold}</span>
            </div>

            <div 
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold text-xs"
              title="Soul Gems: Rare loot drops for legendary items"
            >
              <Gem className="w-3.5 h-3.5 text-cyan-400" />
              <span>{character.gems}</span>
            </div>

            <button
              onClick={handleToggleMute}
              className="p-2 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 transition-colors cursor-pointer"
              title={muted ? 'Unmute RPG Sound Effects (M)' : 'Mute Sound Effects (M)'}
              aria-label="Toggle Audio"
            >
              {muted ? <VolumeX className="w-4 h-4 text-slate-500" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
            </button>

            <div className="relative">
              <button
                onClick={() => { setShowThemeMenu(!showThemeMenu); setShowProfileMenu(false); }}
                className="p-2 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 transition-colors cursor-pointer"
                title="Change Theme Skin"
                aria-label="Theme selector"
              >
                <Palette className="w-4 h-4 text-purple-400" />
              </button>

              {showThemeMenu && (
                <div className="absolute right-0 mt-2 w-48 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 animate-fadeIn">
                  <div className="text-[10px] font-bold text-slate-400 px-2 py-1 uppercase tracking-wider">
                    Select Realm Theme
                  </div>
                  {themes.map((th) => (
                    <button
                      key={th.id}
                      onClick={() => {
                        onThemeChange(th.id);
                        setShowThemeMenu(false);
                        sound.playButtonTick();
                      }}
                      className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                        currentTheme === th.id ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40' : 'text-slate-300 hover:bg-slate-800'
                      }`}
                    >
                      <span className={`w-3 h-3 rounded-full ${th.color}`} />
                      <span>{th.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="relative">
              <button
                onClick={() => { setShowProfileMenu(!showProfileMenu); setShowThemeMenu(false); }}
                className="flex items-center gap-2 pl-2 pr-2.5 py-1.5 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-slate-700 transition-all cursor-pointer"
              >
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-inner">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="hidden sm:block text-left">
                  <div className="text-xs font-bold text-slate-200 leading-tight truncate max-w-[100px]">
                    {user.username}
                  </div>
                  <div className="text-[10px] text-cyan-400 font-medium leading-none">
                    {user.class_name}
                  </div>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-60 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-3 z-50 animate-fadeIn">
                  <div className="pb-2 mb-2 border-b border-slate-800">
                    <p className="text-xs font-bold text-white">{user.username}</p>
                    <p className="text-[11px] text-slate-400">{user.email}</p>
                    <span className="inline-block mt-1 px-1.5 py-0.5 text-[10px] font-bold rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                      {user.title}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <button
                      onClick={() => {
                        onResetDemo();
                        setShowProfileMenu(false);
                      }}
                      disabled={isResetting}
                      className="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-rose-300 hover:bg-rose-500/10 transition-colors cursor-pointer"
                    >
                      <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
                      <span>Reset Demo Database</span>
                    </button>

                    <button
                      onClick={() => {
                        onLogout();
                        setShowProfileMenu(false);
                      }}
                      className="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-colors cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Sign Out / Switch Hero</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 overflow-x-auto py-2 border-t border-slate-800/40 no-scrollbar">
          {[
            { id: 'quests', label: 'Quest Board', icon: Sword, shortcut: '1' },
            { id: 'character', label: 'Character Sheet', icon: UserIcon, shortcut: '2' },
            { id: 'boss', label: 'Boss Arena', icon: Flame, shortcut: '3' },
            { id: 'shop', label: 'Armory Shop', icon: Coins, shortcut: '4' },
            { id: 'analytics', label: 'Streak Matrix', icon: Sparkles, shortcut: '5' }
          ].map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  sound.playButtonTick();
                }}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-600/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
                <span className="hidden sm:inline-block text-[9px] px-1 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50">
                  {item.shortcut}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
