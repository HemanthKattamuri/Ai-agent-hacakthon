import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

interface AnimatedLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  interactive?: boolean;
  subtitle?: string;
  onClick?: () => void;
}

export const AnimatedLogo: React.FC<AnimatedLogoProps> = ({
  size = 'md',
  showText = true,
  interactive = true,
  subtitle,
  onClick
}) => {
  const [tilt, setTilt] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState<boolean>(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 28; // -14 to +14 deg
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -28;
    setTilt({ x, y });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setIsHovered(false);
  };

  const sizeDimensions = {
    sm: { box: 'w-8 h-8', svg: 32, text: 'text-base', sub: 'text-[10px]' },
    md: { box: 'w-12 h-12', svg: 48, text: 'text-xl', sub: 'text-xs' },
    lg: { box: 'w-20 h-20', svg: 80, text: 'text-3xl', sub: 'text-sm' },
    xl: { box: 'w-28 h-28', svg: 112, text: 'text-4xl', sub: 'text-base' },
  }[size];

  return (
    <div 
      className={`inline-flex items-center gap-3.5 select-none ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      style={{ perspective: 1000 }}
    >
      {/* 3D-Tilt Container */}
      <div 
        className={`relative ${sizeDimensions.box} flex items-center justify-center transition-transform duration-200 ease-out`}
        style={{
          transform: `rotateY(${tilt.x}deg) rotateX(${tilt.y}deg) scale(${isHovered ? 1.08 : 1})`,
          transformStyle: 'preserve-3d'
        }}
      >
        {/* Ambient Pulsing Glow Aura */}
        <div className="absolute inset-0 -m-3 rounded-full bg-gradient-to-tr from-cyan-500/40 via-indigo-600/40 to-fuchsia-500/40 blur-xl animate-pulse pointer-events-none" />

        {/* Animated Multi-Layer SVG Glyph */}
        <svg 
          viewBox="0 0 100 100" 
          className="w-full h-full drop-shadow-[0_0_15px_rgba(99,102,241,0.6)]"
        >
          <defs>
            <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="50%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#d946ef" />
            </linearGradient>

            <linearGradient id="ringGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#818cf8" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#c084fc" stopOpacity="0.9" />
            </linearGradient>

            <radialGradient id="neuralAura" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.8" />
              <stop offset="60%" stopColor="#6366f1" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
            </radialGradient>

            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="glow" />
              <feComposite in="SourceGraphic" in2="glow" operator="over" />
            </filter>
          </defs>

          {/* Outer Orbital Ring with Counter-Clockwise Dash Rotation */}
          <circle
            cx="50"
            cy="50"
            r="44"
            fill="none"
            stroke="url(#ringGrad1)"
            strokeWidth="1.8"
            strokeDasharray="8 6 18 6"
            className="origin-center animate-[spin_16s_linear_infinite]"
          />

          {/* Inner Orbital Fast Ring with Clockwise Rotation */}
          <circle
            cx="50"
            cy="50"
            r="35"
            fill="none"
            stroke="url(#coreGrad)"
            strokeWidth="2.2"
            strokeDasharray="14 10 24 10"
            className="origin-center animate-[spin_8s_linear_infinite_reverse]"
          />

          {/* Glowing Energy Orbit Nodes */}
          <g className="origin-center animate-[spin_6s_linear_infinite]">
            <circle cx="50" cy="6" r="3.5" fill="#38bdf8" filter="url(#glowFilter)" />
            <circle cx="50" cy="94" r="3.5" fill="#e879f9" filter="url(#glowFilter)" />
          </g>
          <g className="origin-center animate-[spin_10s_linear_infinite_reverse]">
            <circle cx="15" cy="50" r="2.8" fill="#facc15" filter="url(#glowFilter)" />
            <circle cx="85" cy="50" r="2.8" fill="#4ade80" filter="url(#glowFilter)" />
          </g>

          {/* Inner Neural Core Diamond Hexagon */}
          <polygon
            points="50,22 74,36 74,64 50,78 26,64 26,36"
            fill="url(#neuralAura)"
            stroke="url(#coreGrad)"
            strokeWidth="2.5"
            className="origin-center animate-pulse"
          />

          {/* Center RPG Energy Core Rune (Stylized Sword & Crystal Spark) */}
          <path
            d="M50 30 L55 45 L68 50 L55 55 L50 70 L45 55 L32 50 L45 45 Z"
            fill="url(#coreGrad)"
            className="drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]"
          />

          {/* Central Heart Particle */}
          <circle cx="50" cy="50" r="4" fill="#ffffff" filter="url(#glowFilter)" />
        </svg>

        {/* Dynamic Micro-Sparkles Badge */}
        {size === 'lg' || size === 'xl' ? (
          <div className="absolute -top-1 -right-1 p-1 rounded-full bg-indigo-500/30 backdrop-blur-md border border-indigo-400/40 animate-bounce">
            <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
          </div>
        ) : null}
      </div>

      {/* Brand Text Branding */}
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className={`font-extrabold tracking-tight bg-gradient-to-r from-white via-indigo-200 to-cyan-300 bg-clip-text text-transparent font-display ${sizeDimensions.text}`}>
              Quest<span className="text-cyan-400">Flow</span>
            </span>
            <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-gradient-to-r from-indigo-500/20 to-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase tracking-widest">
              RPG v2.0
            </span>
          </div>
          {subtitle && (
            <p className={`text-slate-400 font-medium ${sizeDimensions.sub}`}>
              {subtitle}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
