export interface Agent {
  id: string;
  name: string;
  type: string;
  capabilities: string[];
  status: 'active' | 'inactive' | 'busy';
}

export interface Memory {
  hash: string;
  content: string;
  type: 'fact' | 'observation' | 'inference' | 'commitment';
  truth_state: 1 | 0 | -1;
  created_at: string;
}

export interface Task {
  id: string;
  type: string;
  description: string;
  assigned_to?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: number;
}
