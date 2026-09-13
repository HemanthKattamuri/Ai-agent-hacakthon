/**
 * QuestFlow RPG Engine Types & Interfaces (with backward-compatibility exports)
 */

export type AttributeType = 'intellect' | 'strength' | 'agility' | 'vitality' | 'charisma';

export type CategoryType = 'All' | 'Habit' | 'Daily' | 'Quest' | 'Todo';

export type DifficultyTier = 'trivial' | 'easy' | 'medium' | 'hard' | 'epic';

export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent';

export type ItemType = 'weapon' | 'armor' | 'helmet' | 'pet' | 'aura' | 'potion' | 'theme' | 'badge';

export type ItemRarity = 'common' | 'rare' | 'epic' | 'legendary';

export interface User {
  id: string;
  username: string;
  email: string;
  class_name: string;
  title: string;
  avatar_url?: string;
  theme_preference: 'cyberpunk' | 'fantasy' | 'solar' | 'void';
  created_at: string;
}

export interface CharacterStats {
  user_id: string;
  level: number;
  current_xp: number;
  next_level_xp: number;
  hp: number;
  max_hp: number;
  mp: number;
  max_mp: number;
  gold: number;
  gems: number;
  streak_count: number;
  last_active_date?: string;
  streak_freeze_count: number;
  intellect: number;
  strength: number;
  agility: number;
  vitality: number;
  charisma: number;
  tasks_completed_count: number;
  boss_damage_dealt: number;
}

export interface Subtask {
  id: string;
  title: string;
  completed: boolean;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category: 'Habit' | 'Daily' | 'Quest' | 'Todo';
  attribute_tag: AttributeType;
  difficulty: DifficultyTier;
  priority: PriorityLevel;
  xp_reward: number;
  gold_reward: number;
  is_completed: boolean | number;
  completed_at?: string;
  due_date?: string;
  streak_count: number;
  subtasks: Subtask[];
  created_at?: string;
}

export interface InventoryItem {
  id: string;
  user_id: string;
  item_id: string;
  item_name: string;
  item_type: ItemType;
  rarity: ItemRarity;
  stat_bonus: Record<string, number>;
  is_equipped: boolean | number;
  icon: string;
  description: string;
  purchased_at?: string;
}

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  item_type: ItemType;
  rarity: ItemRarity;
  price_gold: number;
  price_gems: number;
  stat_bonus: Record<string, number>;
  icon: string;
  min_level: number;
  is_owned?: boolean;
  can_afford_gold?: boolean;
  can_afford_gems?: boolean;
  is_level_locked?: boolean;
}

export interface BossRaid {
  id: string;
  user_id: string;
  name: string;
  description: string;
  avatar_icon: string;
  current_hp: number;
  max_hp: number;
  attack_power: number;
  reward_xp: number;
  reward_gold: number;
  reward_gems: number;
  is_defeated: boolean | number;
}

export interface ActivityLog {
  id: string;
  user_id: string;
  action_type: string;
  message: string;
  xp_gained?: number;
  gold_gained?: number;
  attribute_increased?: string;
  timestamp: string;
}

export interface AnalyticsData {
  attribute_breakdown: Array<{ attribute_tag: string; count: number; total_xp: number }>;
  activity_matrix: Array<{ date: string; day: string; completed_tasks: number; level: number }>;
  recent_logs: ActivityLog[];
}

export interface CompleteTaskResult {
  task: Task;
  xp_gained: number;
  gold_gained: number;
  gems_gained: number;
  leveled_up: boolean;
  new_level: number;
  attribute_increased: string;
  stat_gain: number;
  boss_damage: number;
  boss_name: string;
  boss_hp_remaining: number;
  boss_defeated: boolean;
  boss_rewards?: { xp: number; gold: number; gems: number; name: string };
  loot_drop?: { type: string; amount: number; message: string };
  character: CharacterStats;
}

// ---------------------------------------------------------------------------
// Legacy / Compatibility Types
// ---------------------------------------------------------------------------

export interface Ticket {
  id: string;
  ticket_code: string;
  customer_id: string;
  customer_name?: string;
  customer_email?: string;
  customer_tier?: string;
  trust_score?: number;
  total_spend?: number;
  order_id?: string;
  product_id?: string;
  product_name?: string;
  product_stock?: number;
  total_amount?: number;
  order_date?: string;
  delivery_date?: string;
  order_status?: string;
  order_tracking?: string;
  title: string;
  message: string;
  issue_type: string;
  priority: string;
  status: string;
  created_at: string;
}

export interface ToolCallLog {
  id: string;
  case_id: string;
  timestamp: string;
  tool_name: string;
  input_params: Record<string, any>;
  result: Record<string, any>;
  status: string;
  duration_ms: number;
}

export type StepType = 
  | 'GOAL' 
  | 'DECISION' 
  | 'TOOL_CALL' 
  | 'OBSERVATION' 
  | 'ACTION' 
  | 'REPLANNING' 
  | 'VERIFICATION' 
  | 'OUTCOME';

export interface AgentTimelineStep {
  step_index: number;
  timestamp: string;
  step_type: StepType;
  title: string;
  summary: string;
  tool_name?: string;
  tool_input?: Record<string, any>;
  tool_output?: Record<string, any>;
  status: 'COMPLETED' | 'FAILED' | 'WARNING' | 'IN_PROGRESS';
  details?: Record<string, any>;
}

export interface VerificationBadge {
  verified: boolean;
  verified_at: string;
  audit_hash: string;
  action_type: string;
  target_id: string;
  db_proof: Record<string, any>;
  integrity_check: string;
}

export interface AgentCaseState {
  status: 'Pending' | 'Investigating' | 'Action Taken' | 'Replanning' | 'Resolved' | 'Escalated';
  goal?: string;
  initial_plan?: string;
  current_plan?: string;
  replan_reason?: string;
  final_resolution?: string;
  verification_badge?: VerificationBadge;
  actions_taken?: Array<Record<string, any>>;
}

export interface DatabaseOverview {
  products: Array<any>;
  orders: Array<any>;
  replacements: Array<any>;
  refunds: Array<any>;
  store_credits: Array<any>;
  escalations: Array<any>;
  policies: Array<any>;
}

export interface ToolDoc {
  name: string;
  description: string;
  params: Record<string, string>;
}
