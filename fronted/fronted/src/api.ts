import { deleteMockMemory, getMockBooks, getMockMemories, makeComparison, makeRecommendation, mockTrace, writeMockMemory } from "./mockData";
import type { Book, CompareResponse, Memory, RecommendationResponse, TraceStep, UserInput } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
let source: "api" | "demo" = "api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...init, signal: controller.signal, headers: { "Content-Type": "application/json", ...init?.headers } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    source = "api";
    if (response.status === 204) return undefined as T;
    return await response.json() as T;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function getDataSource() { return source; }

export async function checkHealth(): Promise<boolean> {
  try { await request<Record<string, unknown>>(""); return true; } catch { source = "demo"; return false; }
}

export async function recommend(input: UserInput, userId: string): Promise<RecommendationResponse> {
  try { return await request("/api/agent/recommend", { method: "POST", body: JSON.stringify({ user_input: input, user_id: userId }) }); }
  catch (error) { if (API_BASE) throw error; source = "demo"; await new Promise((resolve) => setTimeout(resolve, 900)); return makeRecommendation(input, userId); }
}

export async function listMemories(userId: string): Promise<Memory[]> {
  try { const data = await request<{ memories: Memory[] }>(`/api/memory/list/${encodeURIComponent(userId)}`); return data.memories; }
  catch (error) { if (API_BASE) throw error; source = "demo"; return getMockMemories(userId); }
}

export async function writeMemory(userId: string, feedback: string, context?: Record<string, unknown>): Promise<Memory> {
  try { const data = await request<{ memory: Memory }>("/api/memory/write", { method: "POST", body: JSON.stringify({ user_id: userId, feedback, context }) }); return data.memory; }
  catch (error) { if (API_BASE) throw error; source = "demo"; return writeMockMemory(userId, feedback); }
}

export async function removeMemory(userId: string, memoryId: string): Promise<void> {
  try { await request(`/api/memory/${encodeURIComponent(userId)}/${encodeURIComponent(memoryId)}`, { method: "DELETE" }); }
  catch (error) { if (API_BASE) throw error; source = "demo"; deleteMockMemory(userId, memoryId); }
}

export async function searchBooks(filters: Record<string, string>): Promise<Book[]> {
  const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  const applyKeyword = (books: Book[]) => {
    const keyword = (filters.query || "").toLowerCase();
    return keyword ? books.filter((book) => `${book.title} ${book.description} ${book.keywords.join(" ")}`.toLowerCase().includes(keyword)) : books;
  };
  try { const data = await request<{ books: Book[] }>(`/api/books/search?${query}`); return applyKeyword(data.books); }
  catch (error) {
    source = "demo";
    return applyKeyword(getMockBooks().filter((book) => (!filters.topic || book.topic === filters.topic) && (!filters.difficulty || book.difficulty === filters.difficulty) && (!filters.language || book.language === filters.language) && (!filters.max_pages || book.pages <= Number(filters.max_pages))));
  }
}

export async function getBook(bookId: number): Promise<Book | undefined> {
  try { return await request<Book>(`/api/books/${bookId}`); }
  catch (error) { source = "demo"; return getMockBooks().find((book) => book.id === bookId); }
}

export async function getComparison(userId: string): Promise<CompareResponse> {
  try { return await request(`/api/demo/compare/${encodeURIComponent(userId)}`); }
  catch (error) { if (API_BASE) throw error; source = "demo"; await new Promise((resolve) => setTimeout(resolve, 650)); return makeComparison(userId); }
}

export async function getTrace(userId: string): Promise<TraceStep[]> {
  try { const data = await request<{ trace: TraceStep[] }>(`/api/agent/trace/${encodeURIComponent(userId)}`); return data.trace; }
  catch (error) { if (API_BASE) throw error; source = "demo"; return mockTrace; }
}
