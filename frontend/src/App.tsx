import React, { useState, useEffect, useCallback } from 'react';
import type { 
  User, 
  CharacterStats, 
  Task, 
  InventoryItem, 
  ShopItem, 
  BossRaid, 
  AnalyticsData, 
  CompleteTaskResult 
} from './types';
import { 
  fetchMe, 
  loginUser, 
  signupUser, 
  demoLoginUser, 
  fetchTasks, 
  createTask, 
  updateTask, 
  deleteTask, 
  completeTask, 
  uncompleteTask, 
  fetchCharacterSheet, 
  equipItem, 
  fetchShopCatalogue, 
  buyShopItem, 
  fetchBossRaid, 
  fetchAnalytics, 
  resetDemoDatabase 
} from './api';
import { AuthGateway } from './components/AuthGateway';
import { TopHUD } from './components/TopHUD';
import { QuestBoard } from './components/QuestBoard';
import { CharacterSheet } from './components/CharacterSheet';
import { BossArena } from './components/BossArena';
import { ArmoryShop } from './components/ArmoryShop';
import { AnalyticsView } from './components/AnalyticsView';
import { LevelUpModal } from './components/LevelUpModal';
import { sound } from './soundEngine';

export const App: React.FC = () => {
  // Auth & Session State
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [character, setCharacter] = useState<CharacterStats | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState<boolean>(false);

  // App Navigation & Theme State
  const [activeTab, setActiveTab] = useState<string>('quests');
  const [currentTheme, setCurrentTheme] = useState<string>('cyberpunk');

  // Game Systems State
  const [tasks, setTasks] = useState<Task[]>([]);
  const [equippedItems, setEquippedItems] = useState<InventoryItem[]>([]);
  const [gearBonuses, setGearBonuses] = useState<Record<string, number>>({});
  const [totalStats, setTotalStats] = useState<Record<string, number>>({});
  const [radarData, setRadarData] = useState<Array<{ attribute: string; value: number; base: number; gear: number }>>([]);
  const [shopItems, setShopItems] = useState<ShopItem[]>([]);
  const [boss, setBoss] = useState<BossRaid | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  
  // Modals
  const [openCreateTaskModal, setOpenCreateTaskModal] = useState<boolean>(false);
  const [levelUpState, setLevelUpState] = useState<{
    isOpen: boolean;
    newLevel: number;
    attributeIncreased?: string;
    statGain?: number;
  }>({
    isOpen: false,
    newLevel: 1
  });
  const [isResetting, setIsResetting] = useState<boolean>(false);

  // Apply Theme Attribute to DOM
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', currentTheme);
  }, [currentTheme]);

  // Load all user game data
  const loadGameData = useCallback(async () => {
    try {
      const [
        tasksData,
        charSheet,
        shopData,
        bossData,
        analyticsData
      ] = await Promise.all([
        fetchTasks(),
        fetchCharacterSheet(),
        fetchShopCatalogue(),
        fetchBossRaid(),
        fetchAnalytics()
      ]);

      setTasks(tasksData);
      setCharacter(charSheet.base_stats);
      setGearBonuses(charSheet.gear_bonuses);
      setTotalStats(charSheet.total_stats);
      setRadarData(charSheet.radar_data);
      setEquippedItems(charSheet.equipped_items);
      setShopItems(shopData);
      setBoss(bossData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Error loading QuestFlow game data:', err);
    }
  }, []);

  // Initialize Auth on Startup
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('questflow_token');
      if (token) {
        try {
          const { user, character } = await fetchMe();
          setCurrentUser(user);
          setCharacter(character);
          setCurrentTheme(user.theme_preference || 'cyberpunk');
          loadGameData();
        } catch {
          console.warn('Session expired or offline. Resetting auth token.');
          localStorage.removeItem('questflow_token');
        }
      }
    };
    initAuth();
  }, [loadGameData]);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement)?.tagName)) {
        if (e.key === 'Escape') {
          setOpenCreateTaskModal(false);
          setLevelUpState((prev) => ({ ...prev, isOpen: false }));
        }
        return;
      }

      switch (e.key.toLowerCase()) {
        case 'n':
          e.preventDefault();
          setOpenCreateTaskModal(true);
          sound.playButtonTick();
          break;
        case '1':
          setActiveTab('quests');
          sound.playButtonTick();
          break;
        case '2':
          setActiveTab('character');
          sound.playButtonTick();
          break;
        case '3':
          setActiveTab('boss');
          sound.playButtonTick();
          break;
        case '4':
          setActiveTab('shop');
          sound.playButtonTick();
          break;
        case '5':
          setActiveTab('analytics');
          sound.playButtonTick();
          break;
        case 'm':
          sound.toggleMute();
          break;
        case 'escape':
          setOpenCreateTaskModal(false);
          setLevelUpState((prev) => ({ ...prev, isOpen: false }));
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auth Handlers
  const handleLogin = async (data: { email: string; password: string }) => {
    setIsLoadingAuth(true);
    setAuthError(null);
    try {
      const res = await loginUser(data);
      localStorage.setItem('questflow_token', res.token);
      setCurrentUser(res.user);
      setCharacter(res.character);
      setCurrentTheme(res.user.theme_preference || 'cyberpunk');
      sound.playQuestComplete();
      await loadGameData();
    } catch (err: any) {
      setAuthError(err.message || 'Login failed.');
    } finally {
      setIsLoadingAuth(false);
    }
  };

  const handleSignup = async (data: {
    username: string;
    email: string;
    password: string;
    class_name: string;
    title?: string;
  }) => {
    setIsLoadingAuth(true);
    setAuthError(null);
    try {
      const res = await signupUser(data);
      localStorage.setItem('questflow_token', res.token);
      setCurrentUser(res.user);
      setCharacter(res.character);
      sound.playLevelUpFanfare();
      await loadGameData();
    } catch (err: any) {
      setAuthError(err.message || 'Signup failed.');
    } finally {
      setIsLoadingAuth(false);
    }
  };

  const handleDemoLogin = async (persona: string) => {
    setIsLoadingAuth(true);
    setAuthError(null);
    try {
      const res = await demoLoginUser(persona);
      localStorage.setItem('questflow_token', res.token);
      setCurrentUser(res.user);
      setCharacter(res.character);
      setCurrentTheme(res.user.theme_preference || 'cyberpunk');
      sound.playQuestComplete();
      await loadGameData();
    } catch (err: any) {
      setAuthError(err.message || 'Demo login failed.');
    } finally {
      setIsLoadingAuth(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('questflow_token');
    setCurrentUser(null);
    setCharacter(null);
    sound.playButtonTick();
  };

  // Task Actions
  const handleCreateTask = async (data: any) => {
    try {
      const created = await createTask(data);
      setTasks((prev) => [created, ...prev]);
      sound.playQuestComplete();
    } catch (err) {
      console.error('Failed to create task:', err);
    }
  };

  const handleUpdateTask = async (taskId: string, data: any) => {
    try {
      const updated = await updateTask(taskId, data);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      sound.playButtonTick();
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      const res: CompleteTaskResult = await completeTask(taskId);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? res.task : t)));
      setCharacter(res.character);

      if (res.leveled_up) {
        setLevelUpState({
          isOpen: true,
          newLevel: res.new_level,
          attributeIncreased: res.attribute_increased,
          statGain: res.stat_gain
        });
      }

      if (res.loot_drop) {
        sound.playLootDrop();
      }

      const [bossData, analyticsData, charSheet] = await Promise.all([
        fetchBossRaid(),
        fetchAnalytics(),
        fetchCharacterSheet()
      ]);
      setBoss(bossData);
      setAnalytics(analyticsData);
      setGearBonuses(charSheet.gear_bonuses);
      setTotalStats(charSheet.total_stats);
      setRadarData(charSheet.radar_data);
    } catch (err) {
      console.error('Failed to complete task:', err);
    }
  };

  const handleUncompleteTask = async (taskId: string) => {
    try {
      const updated = await uncompleteTask(taskId);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    } catch (err) {
      console.error('Failed to uncomplete task:', err);
    }
  };

  // Armory Actions
  const handleBuyShopItem = async (itemId: string, currency: 'gold' | 'gems') => {
    try {
      await buyShopItem(itemId, currency);
      await loadGameData();
    } catch (err: any) {
      alert(err.message || 'Failed to purchase item.');
    }
  };

  const handleEquipItem = async (inventoryId: string, equip: boolean) => {
    try {
      await equipItem(inventoryId, equip);
      const charSheet = await fetchCharacterSheet();
      setEquippedItems(charSheet.equipped_items);
      setGearBonuses(charSheet.gear_bonuses);
      setTotalStats(charSheet.total_stats);
      setRadarData(charSheet.radar_data);
    } catch (err) {
      console.error('Failed to equip item:', err);
    }
  };

  // Demo Reset
  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      await resetDemoDatabase();
      sound.playQuestComplete();
      await loadGameData();
    } catch (err) {
      console.error('Failed to reset demo database:', err);
    } finally {
      setIsResetting(false);
    }
  };

  // Unauthenticated View
  if (!currentUser || !character) {
    return (
      <AuthGateway
        onAuthSuccess={(token, user, character) => {
          localStorage.setItem('questflow_token', token);
          setCurrentUser(user);
          setCharacter(character);
          loadGameData();
        }}
        onLogin={handleLogin}
        onSignup={handleSignup}
        onDemoLogin={handleDemoLogin}
        isLoading={isLoadingAuth}
        error={authError}
        clearError={() => setAuthError(null)}
      />
    );
  }

  // Authenticated View
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-slate-950">
      <TopHUD
        user={currentUser}
        character={character}
        currentTheme={currentTheme}
        onThemeChange={setCurrentTheme}
        onLogout={handleLogout}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'quests' && (
          <QuestBoard
            tasks={tasks}
            onCompleteTask={handleCompleteTask}
            onUncompleteTask={handleUncompleteTask}
            onCreateTask={handleCreateTask}
            onUpdateTask={handleUpdateTask}
            onDeleteTask={handleDeleteTask}
            isLoading={false}
            openCreateModal={openCreateTaskModal}
            setOpenCreateModal={setOpenCreateTaskModal}
          />
        )}

        {activeTab === 'character' && (
          <CharacterSheet
            user={currentUser}
            stats={character}
            equippedItems={equippedItems}
            gearBonuses={gearBonuses}
            totalStats={totalStats}
            radarData={radarData}
            onEquipItem={handleEquipItem}
          />
        )}

        {activeTab === 'boss' && boss && (
          <BossArena
            boss={boss}
            character={character}
            onRefreshBoss={async () => {
              const b = await fetchBossRaid();
              setBoss(b);
            }}
          />
        )}

        {activeTab === 'shop' && (
          <ArmoryShop
            items={shopItems}
            character={character}
            onBuyItem={handleBuyShopItem}
            isLoading={false}
          />
        )}

        {activeTab === 'analytics' && analytics && (
          <AnalyticsView
            analytics={analytics}
            character={character}
          />
        )}
      </main>

      <LevelUpModal
        isOpen={levelUpState.isOpen}
        newLevel={levelUpState.newLevel}
        attributeIncreased={levelUpState.attributeIncreased}
        statGain={levelUpState.statGain}
        onClose={() => setLevelUpState((prev) => ({ ...prev, isOpen: false }))}
      />

      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>QuestFlow RPG Gamified Life Engine • Built with React 19, FastAPI & SQLite</span>
          <div className="flex items-center gap-3 text-[11px] text-slate-400">
            <span>Shortcuts: <strong>N</strong> (New Quest) • <strong>1-5</strong> (Tabs) • <strong>M</strong> (Mute)</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
