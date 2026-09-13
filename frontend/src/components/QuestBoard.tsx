import React, { useState } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  CheckCircle2, 
  Circle, 
  Trash2, 
  Edit3, 
  Coins, 
  Sparkles, 
  X, 
  Brain, 
  Dumbbell, 
  Zap, 
  Shield, 
  MessageSquare, 
  ListTodo, 
  Clock 
} from 'lucide-react';
import { sound } from '../soundEngine';
import type { Task, AttributeType, DifficultyTier, PriorityLevel, CategoryType } from '../types';

interface QuestBoardProps {
  tasks: Task[];
  onCompleteTask: (taskId: string) => Promise<void>;
  onUncompleteTask: (taskId: string) => Promise<void>;
  onCreateTask: (data: any) => Promise<void>;
  onUpdateTask: (taskId: string, data: any) => Promise<void>;
  onDeleteTask: (taskId: string) => Promise<void>;
  isLoading: boolean;
  openCreateModal: boolean;
  setOpenCreateModal: (open: boolean) => void;
}

const ATTRIBUTE_ICONS: Record<AttributeType, { icon: any; label: string; color: string; bg: string }> = {
  intellect: { icon: Brain, label: 'Intellect', color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/30' },
  strength: { icon: Dumbbell, label: 'Strength', color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/30' },
  agility: { icon: Zap, label: 'Agility', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  vitality: { icon: Shield, label: 'Vitality', color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/30' },
  charisma: { icon: MessageSquare, label: 'Charisma', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
};

const DIFFICULTY_MAP: Record<DifficultyTier, { label: string; color: string; xp: number; gold: number }> = {
  trivial: { label: 'Trivial', color: 'text-slate-400 bg-slate-800 border-slate-700', xp: 15, gold: 5 },
  easy: { label: 'Easy', color: 'text-emerald-400 bg-emerald-950/60 border-emerald-800', xp: 30, gold: 12 },
  medium: { label: 'Medium', color: 'text-cyan-400 bg-cyan-950/60 border-cyan-800', xp: 60, gold: 25 },
  hard: { label: 'Hard', color: 'text-amber-400 bg-amber-950/60 border-amber-800', xp: 120, gold: 50 },
  epic: { label: 'Epic Raid', color: 'text-fuchsia-400 bg-fuchsia-950/60 border-fuchsia-800', xp: 250, gold: 110 },
};

const PRIORITY_COLORS: Record<PriorityLevel, string> = {
  low: 'text-slate-400',
  medium: 'text-blue-400',
  high: 'text-amber-400',
  urgent: 'text-rose-400 font-bold animate-pulse',
};

export const QuestBoard: React.FC<QuestBoardProps> = ({
  tasks,
  onCompleteTask,
  onUncompleteTask,
  onCreateTask,
  onUpdateTask,
  onDeleteTask,
  isLoading,
  openCreateModal,
  setOpenCreateModal,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<CategoryType>('All');
  const [selectedAttribute, setSelectedAttribute] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(null);

  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const [taskTitle, setTaskTitle] = useState<string>('');
  const [taskDesc, setTaskDesc] = useState<string>('');
  const [taskCategory, setTaskCategory] = useState<'Habit' | 'Daily' | 'Quest' | 'Todo'>('Quest');
  const [taskAttribute, setTaskAttribute] = useState<AttributeType>('intellect');
  const [taskDifficulty, setTaskDifficulty] = useState<DifficultyTier>('medium');
  const [taskPriority, setTaskPriority] = useState<PriorityLevel>('medium');
  const [taskDueDate, setTaskDueDate] = useState<string>('');
  const [subtasks, setSubtasks] = useState<Array<{ id: string; title: string; completed: boolean }>>([]);
  const [newSubtaskInput, setNewSubtaskInput] = useState<string>('');

  const openCreateDialog = () => {
    setEditingTask(null);
    setTaskTitle('');
    setTaskDesc('');
    setTaskCategory('Quest');
    setTaskAttribute('intellect');
    setTaskDifficulty('medium');
    setTaskPriority('medium');
    setTaskDueDate('');
    setSubtasks([]);
    setOpenCreateModal(true);
    sound.playButtonTick();
  };

  const openEditDialog = (task: Task) => {
    setEditingTask(task);
    setTaskTitle(task.title);
    setTaskDesc(task.description || '');
    setTaskCategory(task.category);
    setTaskAttribute(task.attribute_tag);
    setTaskDifficulty(task.difficulty);
    setTaskPriority(task.priority);
    setTaskDueDate(task.due_date || '');
    setSubtasks(task.subtasks || []);
    setOpenCreateModal(true);
    sound.playButtonTick();
  };

  const handleAddSubtask = () => {
    if (!newSubtaskInput.trim()) return;
    setSubtasks([...subtasks, { id: `sub_${Date.now()}`, title: newSubtaskInput.trim(), completed: false }]);
    setNewSubtaskInput('');
    sound.playButtonTick();
  };

  const handleRemoveSubtask = (id: string) => {
    setSubtasks(subtasks.filter((s) => s.id !== id));
    sound.playButtonTick();
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskTitle.trim()) return;

    if (editingTask) {
      await onUpdateTask(editingTask.id, {
        title: taskTitle.trim(),
        description: taskDesc.trim(),
        category: taskCategory,
        attribute_tag: taskAttribute,
        difficulty: taskDifficulty,
        priority: taskPriority,
        due_date: taskDueDate || undefined,
        subtasks
      });
    } else {
      await onCreateTask({
        title: taskTitle.trim(),
        description: taskDesc.trim(),
        category: taskCategory,
        attribute_tag: taskAttribute,
        difficulty: taskDifficulty,
        priority: taskPriority,
        due_date: taskDueDate || undefined,
        subtasks
      });
    }
    setOpenCreateModal(false);
  };

  const handleToggleComplete = async (task: Task) => {
    if (task.is_completed) {
      await onUncompleteTask(task.id);
    } else {
      setCompletingTaskId(task.id);
      sound.playQuestComplete();
      await onCompleteTask(task.id);
      setCompletingTaskId(null);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (selectedCategory !== 'All' && t.category !== selectedCategory) return false;
    if (selectedAttribute !== 'all' && t.attribute_tag !== selectedAttribute) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = t.title.toLowerCase().includes(q);
      const matchDesc = t.description?.toLowerCase().includes(q);
      if (!matchTitle && !matchDesc) return false;
    }
    return true;
  });

  const activeCount = tasks.filter((t) => !t.is_completed).length;
  const completedCount = tasks.filter((t) => t.is_completed).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 no-scrollbar">
          {(['All', 'Habit', 'Daily', 'Quest', 'Todo'] as CategoryType[]).map((cat) => (
            <button
              key={cat}
              onClick={() => { setSelectedCategory(cat); sound.playButtonTick(); }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                selectedCategory === cat
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {cat === 'All' ? 'All Quests' : `${cat}s`}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2.5">
          <div className="relative flex-1 md:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search quest log..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <button
            onClick={openCreateDialog}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl font-bold text-xs bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white shadow-lg shadow-cyan-500/20 transition-all cursor-pointer shrink-0"
            title="Create New Quest (Shortcut: N)"
          >
            <Plus className="w-4 h-4" />
            <span>New Quest</span>
            <span className="hidden sm:inline-block text-[9px] px-1 rounded bg-black/20 text-cyan-200">
              N
            </span>
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 shrink-0">
          <Filter className="w-3 h-3" /> Attribute:
        </span>
        <button
          onClick={() => { setSelectedAttribute('all'); sound.playButtonTick(); }}
          className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer shrink-0 ${
            selectedAttribute === 'all'
              ? 'bg-slate-700 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          All Stats
        </button>
        {(['intellect', 'strength', 'agility', 'vitality', 'charisma'] as AttributeType[]).map((attr) => {
          const cfg = ATTRIBUTE_ICONS[attr];
          const Icon = cfg.icon;
          const isSel = selectedAttribute === attr;
          return (
            <button
              key={attr}
              onClick={() => { setSelectedAttribute(attr); sound.playButtonTick(); }}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer shrink-0 ${
                isSel
                  ? `${cfg.bg} ${cfg.color} border shadow-sm`
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{cfg.label}</span>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Active Quests: <strong className="text-cyan-400">{activeCount}</strong></span>
        <span>Completed: <strong className="text-emerald-400">{completedCount}</strong></span>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80">
          <ListTodo className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-300">No Quests Found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {searchQuery || selectedAttribute !== 'all' || selectedCategory !== 'All'
              ? 'Try adjusting your filters or search terms.'
              : 'Your quest journal is clear! Create an epic new quest to level up.'}
          </p>
          <button
            onClick={openCreateDialog}
            className="mt-4 px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-colors cursor-pointer"
          >
            + Add First Quest
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredTasks.map((task) => {
            const attrCfg = ATTRIBUTE_ICONS[task.attribute_tag] || ATTRIBUTE_ICONS.intellect;
            const AttrIcon = attrCfg.icon;
            const diffCfg = DIFFICULTY_MAP[task.difficulty] || DIFFICULTY_MAP.medium;
            const isDone = !!task.is_completed;
            const isCompleting = completingTaskId === task.id;

            return (
              <div
                key={task.id}
                className={`relative group rounded-2xl p-4 transition-all duration-200 border ${
                  isDone
                    ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                    : 'bg-slate-900/70 border-slate-800/80 hover:border-slate-700 hover:shadow-xl hover:shadow-cyan-950/20'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-bold border ${attrCfg.bg} ${attrCfg.color}`}>
                      <AttrIcon className="w-3 h-3" />
                      <span>{attrCfg.label}</span>
                    </span>

                    <span className="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {task.category}
                    </span>

                    <span className={`px-2 py-0.5 rounded-lg text-[10px] font-bold border ${diffCfg.color}`}>
                      {diffCfg.label}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-bold shrink-0">
                    <span className="flex items-center gap-0.5 text-cyan-400">
                      <Sparkles className="w-3 h-3" /> +{task.xp_reward} XP
                    </span>
                    <span className="flex items-center gap-0.5 text-amber-400">
                      <Coins className="w-3 h-3" /> +{task.gold_reward}G
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleComplete(task)}
                    disabled={isCompleting}
                    className={`mt-0.5 p-1 rounded-lg transition-all cursor-pointer shrink-0 ${
                      isDone
                        ? 'text-emerald-400 hover:text-emerald-300 bg-emerald-500/10'
                        : 'text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10'
                    }`}
                    title={isDone ? 'Mark as incomplete' : 'Complete Quest'}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 fill-emerald-500/20" />
                    ) : (
                      <Circle className="w-5 h-5" />
                    )}
                  </button>

                  <div className="flex-1 min-w-0">
                    <h4 className={`text-sm font-bold tracking-tight ${isDone ? 'line-through text-slate-400' : 'text-slate-100'}`}>
                      {task.title}
                    </h4>
                    {task.description && (
                      <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                        {task.description}
                      </p>
                    )}

                    {task.subtasks && task.subtasks.length > 0 && (
                      <div className="mt-2.5 space-y-1">
                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-semibold">
                          <span>Checklist Progress</span>
                          <span>
                            {task.subtasks.filter((s) => s.completed).length} / {task.subtasks.length}
                          </span>
                        </div>
                        <div className="w-full h-1 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full bg-cyan-400 transition-all duration-300"
                            style={{
                              width: `${Math.round(
                                (task.subtasks.filter((s) => s.completed).length / task.subtasks.length) * 100
                              )}%`
                            }}
                          />
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-[11px] text-slate-400">
                      <div className="flex items-center gap-2">
                        {task.due_date && (
                          <span className="flex items-center gap-1 text-slate-400">
                            <Clock className="w-3 h-3 text-slate-500" />
                            {task.due_date}
                          </span>
                        )}
                        <span className={`text-[10px] uppercase font-bold ${PRIORITY_COLORS[task.priority]}`}>
                          • {task.priority}
                        </span>
                      </div>

                      <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openEditDialog(task)}
                          className="p-1 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition-colors cursor-pointer"
                          title="Edit Quest"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            sound.playButtonTick();
                            onDeleteTask(task.id);
                          }}
                          className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors cursor-pointer"
                          title="Abandon Quest"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {openCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 overflow-hidden max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                  <Plus className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">
                  {editingTask ? 'Edit Quest Details' : 'Forge New Quest'}
                </h3>
              </div>
              <button
                onClick={() => setOpenCreateModal(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="space-y-4 pt-4 overflow-y-auto pr-1">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Quest Objective Title *
                </label>
                <input
                  type="text"
                  required
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  placeholder="e.g. Implement Fast ReAct Reasoning Loop"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Description / Lore / Context
                </label>
                <textarea
                  rows={2}
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                  placeholder="Explain requirements, steps, or lore..."
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Quest Category
                  </label>
                  <select
                    value={taskCategory}
                    onChange={(e) => setTaskCategory(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Quest">Core Quest</option>
                    <option value="Daily">Daily Routine</option>
                    <option value="Habit">Continuous Habit</option>
                    <option value="Todo">Quick Todo</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Attribute Stat To Level Up
                  </label>
                  <select
                    value={taskAttribute}
                    onChange={(e) => setTaskAttribute(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="intellect">🧠 Intellect (Coding, Study, Logic)</option>
                    <option value="strength">⚔️ Strength (Gym, Workouts, Grit)</option>
                    <option value="agility">⚡ Agility (Speed tasks, Flexibility)</option>
                    <option value="vitality">🛡️ Vitality (Health, Sleep, Water)</option>
                    <option value="charisma">🔮 Charisma (Communication, Writing)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Difficulty Tier (Reward Scaling)
                  </label>
                  <select
                    value={taskDifficulty}
                    onChange={(e) => setTaskDifficulty(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="trivial">Trivial (+15 XP, +5G)</option>
                    <option value="easy">Easy (+30 XP, +12G)</option>
                    <option value="medium">Medium (+60 XP, +25G)</option>
                    <option value="hard">Hard (+120 XP, +50G)</option>
                    <option value="epic">Epic (+250 XP, +110G)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Priority Level
                  </label>
                  <select
                    value={taskPriority}
                    onChange={(e) => setTaskPriority(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="low">Low Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="high">High Priority</option>
                    <option value="urgent">Urgent Boss Blocker</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Due Date (Optional)
                </label>
                <input
                  type="date"
                  value={taskDueDate}
                  onChange={(e) => setTaskDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Subtask Checklist
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={newSubtaskInput}
                    onChange={(e) => setNewSubtaskInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddSubtask();
                      }
                    }}
                    placeholder="Add subtask step..."
                    className="flex-1 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                  />
                  <button
                    type="button"
                    onClick={handleAddSubtask}
                    className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-800 text-cyan-300 hover:bg-slate-700 cursor-pointer"
                  >
                    Add
                  </button>
                </div>

                {subtasks.length > 0 && (
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {subtasks.map((sub) => (
                      <div key={sub.id} className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                        <span className="text-slate-300">{sub.title}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSubtask(sub.id)}
                          className="text-slate-500 hover:text-rose-400 cursor-pointer"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setOpenCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white shadow-lg shadow-cyan-500/20 cursor-pointer"
                >
                  {editingTask ? 'Save Changes' : 'Create Quest'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
