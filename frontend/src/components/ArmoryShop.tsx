import React, { useState } from 'react';
import { 
  Coins, 
  Gem, 
  ShoppingBag, 
  Check, 
  Lock, 
  Sword, 
  Shield, 
  Crown, 
  Flame, 
  FlaskConical, 
  Palette, 
  Award,
  Layers,
  Sparkles
} from 'lucide-react';
import { sound } from '../soundEngine';
import type { ShopItem, CharacterStats } from '../types';

interface ArmoryShopProps {
  items: ShopItem[];
  character: CharacterStats;
  onBuyItem: (itemId: string, currency: 'gold' | 'gems') => Promise<void>;
  isLoading?: boolean;
}

const RARITY_COLORS: Record<string, { border: string; bg: string; text: string; glow: string }> = {
  common: { border: 'border-slate-700', bg: 'bg-slate-900/60', text: 'text-slate-300', glow: '' },
  rare: { border: 'border-cyan-500/50', bg: 'bg-cyan-950/20', text: 'text-cyan-300', glow: 'shadow-cyan-500/10' },
  epic: { border: 'border-purple-500/50', bg: 'bg-purple-950/20', text: 'text-purple-300', glow: 'shadow-purple-500/15' },
  legendary: { border: 'border-amber-500/60', bg: 'bg-amber-950/20', text: 'text-amber-300', glow: 'shadow-amber-500/20' },
};

const ITEM_ICONS: Record<string, any> = {
  weapon: Sword,
  helmet: Crown,
  armor: Shield,
  pet: Sparkles,
  aura: Flame,
  potion: FlaskConical,
  theme: Palette,
  badge: Award
};

export const ArmoryShop: React.FC<ArmoryShopProps> = ({
  items,
  character,
  onBuyItem
}) => {
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [purchasingId, setPurchasingId] = useState<string | null>(null);

  const categories = [
    { id: 'all', label: 'All Items' },
    { id: 'weapon', label: 'Weapons' },
    { id: 'armor', label: 'Armor & Helmets' },
    { id: 'pet', label: 'Companions' },
    { id: 'aura', label: 'Auras & FX' },
    { id: 'potion', label: 'Consumables' },
    { id: 'theme', label: 'Themes & Badges' },
  ];

  const filteredItems = items.filter((item) => {
    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'armor') return item.item_type === 'armor' || item.item_type === 'helmet';
    if (selectedFilter === 'theme') return item.item_type === 'theme' || item.item_type === 'badge';
    return item.item_type === selectedFilter;
  });

  const handlePurchase = async (item: ShopItem) => {
    const currency = item.price_gems > 0 ? 'gems' : 'gold';
    setPurchasingId(item.id);
    sound.playCoinPickup();
    try {
      await onBuyItem(item.id, currency);
    } finally {
      setPurchasingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">The Royal Armory & Item Bazaar</h3>
            <p className="text-xs text-slate-400">
              Spend quest-earned Gold & Soul Gems on powerful gear, boosts, and aesthetics.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold">
            <Coins className="w-4 h-4 text-amber-400" />
            <span>{character.gold} Gold</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-bold">
            <Gem className="w-4 h-4 text-cyan-400" />
            <span>{character.gems} Gems</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => { setSelectedFilter(cat.id); sound.playButtonTick(); }}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              selectedFilter === cat.id
                ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-600/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredItems.map((item) => {
          const rarityCfg = RARITY_COLORS[item.rarity] || RARITY_COLORS.common;
          const Icon = ITEM_ICONS[item.item_type] || Layers;
          const isOwned = !!item.is_owned;
          const isLevelLocked = character.level < item.min_level;
          const canAfford = item.price_gems > 0 
            ? character.gems >= item.price_gems 
            : character.gold >= item.price_gold;
          const isBuying = purchasingId === item.id;

          return (
            <div
              key={item.id}
              className={`relative rounded-2xl p-4 border transition-all duration-200 flex flex-col justify-between ${rarityCfg.bg} ${rarityCfg.border} ${rarityCfg.glow} shadow-lg`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-center text-cyan-300 shadow-inner">
                    <Icon className="w-5 h-5" />
                  </div>

                  <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider ${rarityCfg.text} bg-black/40 border border-current/30`}>
                    {item.rarity}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white leading-tight">
                  {item.name}
                </h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2">
                  {item.description}
                </p>

                {item.stat_bonus && Object.keys(item.stat_bonus).length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-slate-800/60">
                    {Object.entries(item.stat_bonus).map(([k, v]) => (
                      <span key={k} className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-950/80 text-cyan-300 border border-slate-800">
                        +{v} {k.toUpperCase()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <div>
                  {isOwned ? (
                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                      <Check className="w-3.5 h-3.5" /> In Inventory
                    </span>
                  ) : isLevelLocked ? (
                    <span className="text-xs font-bold text-slate-500 flex items-center gap-1">
                      <Lock className="w-3.5 h-3.5" /> Req Lvl {item.min_level}
                    </span>
                  ) : item.price_gems > 0 ? (
                    <span className="text-xs font-bold text-cyan-300 flex items-center gap-1">
                      <Gem className="w-3.5 h-3.5 text-cyan-400" /> {item.price_gems} Gems
                    </span>
                  ) : (
                    <span className="text-xs font-bold text-amber-300 flex items-center gap-1">
                      <Coins className="w-3.5 h-3.5 text-amber-400" /> {item.price_gold} Gold
                    </span>
                  )}
                </div>

                <button
                  onClick={() => handlePurchase(item)}
                  disabled={isOwned || isLevelLocked || !canAfford || isBuying}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${
                    isOwned
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : canAfford && !isLevelLocked
                      ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:opacity-90'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {isBuying ? (
                    <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : isOwned ? (
                    'Acquired'
                  ) : (
                    'Acquire'
                  )}
                </button>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};
