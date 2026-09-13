/**
 * QuestFlow API Client.
 * Connects to FastAPI backend with auto-token injection and seamless offline/demo resiliency.
 */
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

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('questflow_token') || 'usr_alex_chen';
  return {
    'Content-Type': 'application/json',
    'X-User-Id': token,
    'Authorization': `Bearer ${token}`
  };
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'API Request Failed';
    try {
      const err = await res.json();
      errorDetail = err.detail || err.message || errorDetail;
    } catch {
      errorDetail = res.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export async function signupUser(payload: {
  username: string;
  email: string;
  password: string;
  class_name: string;
  title?: string;
}): Promise<{ token: string; user: User; character: CharacterStats; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<{ token: string; user: User; character: CharacterStats; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function demoLoginUser(persona: string): Promise<{
  token: string;
  user: User;
  character: CharacterStats;
  message: string;
}> {
  const res = await fetch(`${API_BASE_URL}/api/auth/demo-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ persona })
  });
  return handleResponse(res);
}

export async function fetchMe(): Promise<{ user: User; character: CharacterStats }> {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Task CRUD API
// ---------------------------------------------------------------------------

export async function fetchTasks(params?: {
  category?: string;
  attribute_tag?: string;
  is_completed?: number;
  search?: string;
}): Promise<Task[]> {
  const query = new URLSearchParams();
  if (params?.category && params.category !== 'All') query.append('category', params.category);
  if (params?.attribute_tag && params.attribute_tag !== 'all') query.append('attribute_tag', params.attribute_tag);
  if (params?.is_completed !== undefined) query.append('is_completed', String(params.is_completed));
  if (params?.search) query.append('search', params.search);

  const res = await fetch(`${API_BASE_URL}/api/tasks?${query.toString()}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function createTask(payload: {
  title: string;
  description?: string;
  category: string;
  attribute_tag: string;
  difficulty: string;
  priority: string;
  due_date?: string;
  subtasks?: Array<{ id: string; title: string; completed: boolean }>;
}): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/api/tasks`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function updateTask(taskId: string, payload: Partial<Task>): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function deleteTask(taskId: string): Promise<{ message: string; task_id: string }> {
  const res = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function completeTask(taskId: string): Promise<CompleteTaskResult> {
  const res = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/complete`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function uncompleteTask(taskId: string): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/uncomplete`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Character & Inventory API
// ---------------------------------------------------------------------------

export async function fetchCharacterSheet(): Promise<{
  user: User;
  base_stats: CharacterStats;
  gear_bonuses: Record<string, number>;
  total_stats: Record<string, number>;
  radar_data: Array<{ attribute: string; value: number; base: number; gear: number }>;
  equipped_items: InventoryItem[];
}> {
  const res = await fetch(`${API_BASE_URL}/api/character`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function fetchInventory(): Promise<InventoryItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/inventory`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function equipItem(inventoryId: string, equip: boolean = true): Promise<{ message: string; item_id: string }> {
  const res = await fetch(`${API_BASE_URL}/api/inventory/equip`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ inventory_id: inventoryId, equip })
  });
  return handleResponse(res);
}

export async function useItem(inventoryId: string): Promise<{ message: string; leveled_up: boolean; new_level: number }> {
  const res = await fetch(`${API_BASE_URL}/api/inventory/use`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ inventory_id: inventoryId })
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Shop & Economy API
// ---------------------------------------------------------------------------

export async function fetchShopCatalogue(): Promise<ShopItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/shop`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function buyShopItem(itemId: string, currency: 'gold' | 'gems' = 'gold'): Promise<{
  message: string;
  item: ShopItem;
  new_gold: number;
  new_gems: number;
}> {
  const res = await fetch(`${API_BASE_URL}/api/shop/buy`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ item_id: itemId, currency })
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Boss Raid & Analytics API
// ---------------------------------------------------------------------------

export async function fetchBossRaid(): Promise<BossRaid> {
  const res = await fetch(`${API_BASE_URL}/api/boss`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function fetchAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${API_BASE_URL}/api/analytics`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function resetDemoDatabase(): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/demo/reset`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Compatibility Stubs for Legacy Files
// ---------------------------------------------------------------------------
export async function createCustomTicket(_payload: any): Promise<any> { return {}; }
export async function fetchDbOverview(): Promise<any> { return {}; }
export async function updateProductInventory(_id: string, _stock: number): Promise<any> { return {}; }
export async function updatePolicyRules(_cat: string, _rules: any): Promise<any> { return {}; }
