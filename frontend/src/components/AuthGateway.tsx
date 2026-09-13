import React, { useState } from 'react';
import { 
  Shield, 
  Sparkles, 
  Zap, 
  Flame, 
  User as UserIcon, 
  Lock, 
  Mail, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  Sword, 
  Cpu, 
  Crown,
  AlertCircle
} from 'lucide-react';
import { AnimatedLogo } from './AnimatedLogo';
import { sound } from '../soundEngine';
import type { User, CharacterStats } from '../types';

interface AuthGatewayProps {
  onAuthSuccess: (token: string, user: User, character: CharacterStats) => void;
  onDemoLogin: (persona: string) => Promise<void>;
  onLogin: (data: { email: string; password: string }) => Promise<void>;
  onSignup: (data: { username: string; email: string; password: string; class_name: string; title?: string }) => Promise<void>;
  isLoading: boolean;
  error?: string | null;
  clearError: () => void;
}

const CHARACTER_CLASSES = [
  {
    id: 'Code Mage',
    name: 'Code Mage',
    icon: Cpu,
    statBonus: '+15% Intellect XP',
    desc: 'Master of algorithms, architecture, and intense problem solving.',
    gradient: 'from-cyan-500 to-blue-600',
    border: 'border-cyan-500/50'
  },
  {
    id: 'Iron Warrior',
    name: 'Iron Warrior',
    icon: Sword,
    statBonus: '+15% Strength XP',
    desc: 'Titan of physical discipline, workouts, and relentless grit.',
    gradient: 'from-rose-500 to-amber-600',
    border: 'border-rose-500/50'
  },
  {
    id: 'Cyber Rogue',
    name: 'Cyber Rogue',
    icon: Zap,
    statBonus: '+15% Agility XP',
    desc: 'Sub-second task speedrunner who demolishes backlogs with agility.',
    gradient: 'from-emerald-500 to-teal-600',
    border: 'border-emerald-500/50'
  },
  {
    id: 'Paladin Scholar',
    name: 'Paladin Scholar',
    icon: Shield,
    statBonus: '+15% Vitality XP',
    desc: 'Guardian of health, hydration, mindfulness, and unbroken streaks.',
    gradient: 'from-purple-500 to-indigo-600',
    border: 'border-purple-500/50'
  }
];

const DEMO_PERSONAS = [
  {
    id: 'code_mage',
    name: 'Alex Chen',
    role: 'Lead AI Ops Architect',
    className: 'Code Mage',
    level: 4,
    streak: 7,
    avatar: '👨‍💻',
    bgGlow: 'hover:border-cyan-400/80 hover:shadow-cyan-500/20'
  },
  {
    id: 'paladin',
    name: 'Sarah Lin',
    role: 'Resolution Champion',
    className: 'Paladin Scholar',
    level: 3,
    streak: 5,
    avatar: '👩‍💼',
    bgGlow: 'hover:border-amber-400/80 hover:shadow-amber-500/20'
  },
  {
    id: 'cyber_rogue',
    name: 'Marcus Vance',
    role: 'Speedrunner of Tasks',
    className: 'Cyber Rogue',
    level: 5,
    streak: 12,
    avatar: '🥷',
    bgGlow: 'hover:border-emerald-400/80 hover:shadow-emerald-500/20'
  }
];

export const AuthGateway: React.FC<AuthGatewayProps> = ({
  onDemoLogin,
  onLogin,
  onSignup,
  isLoading,
  error,
  clearError
}) => {
  const [tab, setTab] = useState<'login' | 'signup' | 'demo'>('login');
  const [showPassword, setShowPassword] = useState<boolean>(false);

  // Sign In Form State
  const [loginEmail, setLoginEmail] = useState<string>('alex.chen@questflow.io');
  const [loginPassword, setLoginPassword] = useState<string>('password123');

  // Sign Up Form State
  const [signupUsername, setSignupUsername] = useState<string>('');
  const [signupEmail, setSignupEmail] = useState<string>('');
  const [signupPassword, setSignupPassword] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<string>('Code Mage');

  // Password Strength Calculation
  const calculateStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length >= 6) score += 1;
    if (pwd.length >= 10) score += 1;
    if (/[0-9]/.test(pwd)) score += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
    return score;
  };

  const passwordStrength = calculateStrength(signupPassword);
  const strengthLabels = ['Too Weak', 'Weak', 'Good', 'Strong', 'Legendary'];
  const strengthColors = ['bg-slate-700', 'bg-rose-500', 'bg-amber-500', 'bg-cyan-500', 'bg-emerald-500'];

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    sound.playButtonTick();
    await onLogin({ email: loginEmail, password: loginPassword });
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    sound.playButtonTick();
    await onSignup({
      username: signupUsername,
      email: signupEmail,
      password: signupPassword,
      class_name: selectedClass,
      title: 'Novice Adventurer'
    });
  };

  const handlePersonaClick = async (personaId: string) => {
    sound.playQuestComplete();
    await onDemoLogin(personaId);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-slate-950 text-white overflow-hidden selection:bg-cyan-500 selection:text-slate-950">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-indigo-600/20 blur-[120px] animate-pulse" />
        <div className="absolute top-1/3 -right-40 w-96 h-96 rounded-full bg-cyan-600/20 blur-[140px] animate-pulse delay-700" />
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 rounded-full bg-fuchsia-600/20 blur-[130px] animate-pulse delay-1000" />
        
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, #fff 1px, transparent 0)`,
            backgroundSize: '32px 32px'
          }}
        />
      </div>

      <div className="relative z-10 w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-900/80 backdrop-blur-2xl shadow-2xl shadow-cyan-950/40 overflow-hidden">
        
        <div className="lg:col-span-5 p-6 sm:p-8 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800/80 bg-gradient-to-b from-slate-900/90 via-indigo-950/30 to-slate-950/90">
          <div>
            <div className="mb-6 flex items-center justify-center sm:justify-start">
              <AnimatedLogo 
                size="lg" 
                subtitle="RPG Task & Habit Progression Engine" 
              />
            </div>

            <p className="text-slate-300 text-sm leading-relaxed mb-6">
              Transform everyday tasks, habits, and coding sprints into an epic RPG quest. Level up 5 core attributes, defeat procrastination bosses, and forge legendary streaks.
            </p>

            <div className="space-y-3">
              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">Non-Linear XP Progression</h4>
                  <p className="text-[11px] text-slate-400">Exponential leveling curve with attribute scaling</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">Habit Streaks & Multipliers</h4>
                  <p className="text-[11px] text-slate-400">+3% bonus XP/Gold per consecutive active day</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                  <Crown className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">Virtual Armory & Boss Arena</h4>
                  <p className="text-[11px] text-slate-400">Equip gear to deal damage to raid monsters</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Shield className="w-3.5 h-3.5 text-emerald-400" /> PBKDF2 Encrypted
            </span>
            <span className="flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> 100% Client + API Sync
            </span>
          </div>
        </div>

        <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div className="flex items-center p-1 rounded-xl bg-slate-950/60 border border-slate-800 mb-6">
              <button
                type="button"
                onClick={() => { setTab('login'); clearError(); sound.playButtonTick(); }}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  tab === 'login'
                    ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setTab('signup'); clearError(); sound.playButtonTick(); }}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  tab === 'signup'
                    ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Character
              </button>
              <button
                type="button"
                onClick={() => { setTab('demo'); clearError(); sound.playButtonTick(); }}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  tab === 'demo'
                    ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                1-Click Demo
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 animate-shake">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {tab === 'login' && (
              <form onSubmit={handleLoginSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Adventurer Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
                    <input
                      type="email"
                      required
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="alex.chen@questflow.io"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700/70 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Master Password
                    </label>
                    <span className="text-[11px] text-cyan-400 hover:underline cursor-pointer">
                      Demo Mode Ready
                    </span>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700/70 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-200 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded border-slate-700 text-cyan-500 focus:ring-0 bg-slate-950" />
                    <span>Remember this station</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full mt-2 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 via-indigo-600 to-fuchsia-600 hover:opacity-95 text-white shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Enter QuestFlow Station</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            )}

            {tab === 'signup' && (
              <form onSubmit={handleSignupSubmit} className="space-y-3.5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Hero Username
                    </label>
                    <div className="relative">
                      <UserIcon className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                      <input
                        type="text"
                        required
                        value={signupUsername}
                        onChange={(e) => setSignupUsername(e.target.value)}
                        placeholder="CyberKnight99"
                        className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950/60 border border-slate-700/70 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                      <input
                        type="email"
                        required
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        placeholder="you@domain.com"
                        className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950/60 border border-slate-700/70 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Select Starter RPG Class
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {CHARACTER_CLASSES.map((cls) => {
                      const Icon = cls.icon;
                      const isSelected = selectedClass === cls.id;
                      return (
                        <div
                          key={cls.id}
                          onClick={() => { setSelectedClass(cls.id); sound.playButtonTick(); }}
                          className={`p-2 rounded-xl border transition-all cursor-pointer ${
                            isSelected
                              ? `bg-gradient-to-br ${cls.gradient} text-white ${cls.border} shadow-md`
                              : 'bg-slate-950/40 border-slate-800 text-slate-300 hover:border-slate-700'
                          }`}
                        >
                          <div className="flex items-center gap-1.5 font-bold text-xs">
                            <Icon className="w-3.5 h-3.5" />
                            <span>{cls.name}</span>
                          </div>
                          <p className={`text-[10px] mt-0.5 ${isSelected ? 'text-white/90' : 'text-cyan-400 font-medium'}`}>
                            {cls.statBonus}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Master Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      placeholder="Min 6 characters"
                      className="w-full pl-9 pr-9 py-2 rounded-xl bg-slate-950/60 border border-slate-700/70 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-200 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  {signupPassword && (
                    <div className="mt-1.5 space-y-1">
                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span>Security Rating:</span>
                        <span className="font-bold text-cyan-400">{strengthLabels[passwordStrength]}</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden flex gap-1">
                        {[1, 2, 3, 4].map((step) => (
                          <div
                            key={step}
                            className={`h-full flex-1 rounded-full transition-all duration-300 ${
                              passwordStrength >= step ? strengthColors[passwordStrength] : 'bg-slate-800'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-cyan-500 via-indigo-600 to-fuchsia-600 hover:opacity-95 text-white shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Forge Character & Start Quest</span>
                    </>
                  )}
                </button>
              </form>
            )}

            {tab === 'demo' && (
              <div className="space-y-3">
                <p className="text-xs text-slate-400 mb-2">
                  Select a pre-configured adventurer to instantly test all game systems:
                </p>

                <div className="space-y-2.5">
                  {DEMO_PERSONAS.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => handlePersonaClick(p.id)}
                      className={`p-3 rounded-xl border border-slate-800 bg-slate-950/60 hover:bg-slate-800/50 transition-all cursor-pointer flex items-center justify-between shadow-sm ${p.bgGlow}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center text-xl shadow-inner">
                          {p.avatar}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-xs font-bold text-white">{p.name}</h4>
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                              Lvl {p.level} {p.className}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">{p.role}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1 text-xs font-bold text-amber-400">
                          <Flame className="w-3.5 h-3.5 text-orange-400 fill-orange-400/30 animate-pulse" />
                          {p.streak}d
                        </span>
                        <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/40">
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-slate-800/80 text-center">
            <p className="text-[11px] text-slate-500">
              QuestFlow Autonomous RPG Life Progression Engine • Fully Responsive & Keyboard Accessible
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
