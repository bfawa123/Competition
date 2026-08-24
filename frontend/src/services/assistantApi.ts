import type { BookScore, UserInput } from "../types";

export interface AssistantContext {
  userName: string;
  input: UserInput;
  books: BookScore[];
  currentPage: "route";
}

export interface AssistantReply {
  answer: string;
}

/**
 * DeepSeek 接口预留位。
 *
 * 后端同学只需要提供一个兼容 POST 的接口，并在前端 .env 中配置：
 * VITE_DEEPSEEK_API_URL=http://127.0.0.1:8000/api/assistant/chat
 *
 * DeepSeek API Key 必须放在后端，不能写进 Vite 前端环境变量。
 */
export async function askLearningAssistant(question: string, context: AssistantContext): Promise<string | null> {
  const endpoint = import.meta.env.VITE_DEEPSEEK_API_URL as string | undefined;
  if (!endpoint) return null;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, context }),
  });
  if (!response.ok) throw new Error(`assistant request failed: ${response.status}`);
  const payload = await response.json() as AssistantReply;
  return typeof payload.answer === "string" ? payload.answer : null;
}
