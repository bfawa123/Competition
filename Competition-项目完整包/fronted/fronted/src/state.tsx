import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { BookScore, RecommendationResponse, UserInput } from "./types";

interface LocalUser { id: string; name: string; initials: string }
interface AppState {
  user: LocalUser | null;
  activeUserId: string;
  activeUserName: string;
  users: LocalUser[];
  setUser: (user: LocalUser) => void;
  addUser: (name: string) => void;
  lastInput: UserInput;
  setLastInput: (input: UserInput) => void;
  recommendation: RecommendationResponse | null;
  setRecommendation: (value: RecommendationResponse | null) => void;
  routeBooks: BookScore[];
  toggleRouteBook: (book: BookScore) => void;
  dark: boolean;
  setDark: (value: boolean) => void;
}

const sampleUserIds = new Set(["demo_freshman", "user_researcher", "user_local"]);

function loadUsers(): LocalUser[] {
  try {
    const parse = (key: string) => {
      try { const value = JSON.parse(localStorage.getItem(key) || "null"); return Array.isArray(value) ? value as LocalUser[] : []; } catch { return []; }
    };
    const realUsers = [...parse("lingxi-users"), ...parse("zhiyu-users")].filter((item, index, all) => !sampleUserIds.has(item.id) && all.findIndex((candidate) => candidate.id === item.id) === index);
    return realUsers;
  } catch { return []; }
}

function loadGuestSessionId(): string {
  try {
    const stored = sessionStorage.getItem("lingxi-guest-id");
    if (stored) return stored;
    const id = `guest_${crypto.randomUUID()}`;
    sessionStorage.setItem("lingxi-guest-id", id);
    return id;
  } catch { return `guest_${Date.now().toString(36)}`; }
}

function loadSession<T>(nextKey: string, fallback: T): T {
  try { return JSON.parse(sessionStorage.getItem(nextKey) || "null") || fallback; }
  catch { return fallback; }
}

const defaultInput: UserInput = { goal: "", difficulty: "beginner", time_per_day: 30, language: "zh", additional_constraints: "希望案例多一些，循序渐进" };
const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [users, setUsers] = useState<LocalUser[]>(loadUsers);
  const [user, setCurrentUser] = useState<LocalUser | null>(users[0] ?? null);
  const [guestSessionId] = useState(loadGuestSessionId);
  const activeUserId = user?.id ?? guestSessionId;
  const activeUserName = user?.name ?? "访客";
  const [lastInput, setLastInput] = useState<UserInput>(() => {
    return loadSession("lingxi-last-input", defaultInput);
  });
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(() => {
    try {
      const stored = JSON.parse(sessionStorage.getItem("lingxi-recommendation") || "null") as { userId?: string; value?: RecommendationResponse } | null;
      return stored?.userId === (users[0]?.id ?? guestSessionId) ? stored.value || null : null;
    } catch { return null; }
  });
  const [routeBooks, setRouteBooks] = useState<BookScore[]>(() => loadSession(`lingxi-route-books-${users[0]?.id ?? guestSessionId}`, []));
  const [dark, setDark] = useState(() => (localStorage.getItem("lingxi-theme") || localStorage.getItem("zhiyu-theme")) === "dark");

  useEffect(() => { localStorage.setItem("lingxi-users", JSON.stringify(users)); localStorage.removeItem("zhiyu-users"); }, [users]);
  useEffect(() => { localStorage.setItem("lingxi-theme", dark ? "dark" : "light"); localStorage.removeItem("zhiyu-theme"); document.documentElement.dataset.theme = dark ? "dark" : "light"; }, [dark]);
  useEffect(() => { sessionStorage.setItem("lingxi-last-input", JSON.stringify(lastInput)); sessionStorage.removeItem("zhiyu-last-input"); }, [lastInput]);
  useEffect(() => { if (recommendation) sessionStorage.setItem("lingxi-recommendation", JSON.stringify({ userId: activeUserId, value: recommendation })); else sessionStorage.removeItem("lingxi-recommendation"); sessionStorage.removeItem("zhiyu-recommendation"); }, [recommendation, activeUserId]);
  useEffect(() => { setRouteBooks(loadSession(`lingxi-route-books-${activeUserId}`, [])); }, [activeUserId]);
  useEffect(() => { sessionStorage.setItem(`lingxi-route-books-${activeUserId}`, JSON.stringify(routeBooks)); }, [activeUserId, routeBooks]);

  const addUser = (name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    const next = { id: `user_${Date.now().toString(36)}`, name: trimmed, initials: trimmed.slice(0, 1) };
    setUsers((current) => [...current, next]);
    setCurrentUser(next);
    setRecommendation(null);
    setRouteBooks([]);
  };

  const setUser = (next: LocalUser) => {
    setCurrentUser(next);
    setRecommendation(null);
    setRouteBooks([]);
  };

  const toggleRouteBook = (book: BookScore) => setRouteBooks((current) => current.some((item) => item.book.id === book.book.id) ? current.filter((item) => item.book.id !== book.book.id) : [...current, book]);

  const value = useMemo(() => ({ user, activeUserId, activeUserName, users, setUser, addUser, lastInput, setLastInput, recommendation, setRecommendation, routeBooks, toggleRouteBook, dark, setDark }), [user, activeUserId, activeUserName, users, lastInput, recommendation, routeBooks, dark]);
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error("useApp must be used inside AppProvider");
  return context;
}
