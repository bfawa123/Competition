export type Difficulty = "beginner" | "intermediate" | "advanced";
export type Language = "zh" | "en";

export interface UserInput {
  goal: string;
  difficulty: Difficulty;
  time_per_day: number;
  language: Language;
  additional_constraints?: string;
}

export interface Book {
  id: number;
  title: string;
  author?: string;
  topic: string;
  difficulty: Difficulty;
  pages: number;
  language: Language;
  case_ratio: number;
  theory_ratio: number;
  prerequisites: string[];
  goals: string[];
  keywords: string[];
  availability: boolean;
  description?: string;
  cover?: string;
  location?: string;
  space?: string;
}

export interface Memory {
  id: string;
  user_id: string;
  type: "fixed_profile" | "preference" | "task_feedback";
  field: string;
  value: unknown;
  confidence: number;
  source: string;
  created_at: string;
  last_used?: string | null;
  usage_count: number;
}

export interface TraceStep {
  action: string;
  details: Record<string, unknown>;
  timestamp: string;
  duration_ms?: number;
}

export interface BookScore {
  book: Book;
  total_score: number;
  topic_score: number;
  difficulty_score: number;
  time_score: number;
  preference_score: number;
  rejection_penalty?: number;
  explanation: string;
}

export interface RecommendationResponse {
  books: BookScore[];
  memories_used: Memory[];
  explanation: string;
  agent_trace: TraceStep[];
}
