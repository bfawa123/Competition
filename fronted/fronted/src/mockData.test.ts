import { describe, expect, it } from "vitest";
import { getMockBooks, getMockMemories, makeComparison, makeRecommendation, writeMockMemory } from "./mockData";

describe("demo recommendation data", () => {
  it("sorts recommendations by descending total score", () => {
    const result = makeRecommendation({ goal: "Python基础", difficulty: "beginner", time_per_day: 30, language: "zh" }, "demo_freshman");
    expect(result.books.length).toBeGreaterThan(2);
    expect(result.books.every((item, index) => index === 0 || result.books[index - 1].total_score >= item.total_score)).toBe(true);
    expect(result.agent_trace.length).toBe(4);
  });

  it("includes easier books in intermediate and advanced recommendations", () => {
    const base = { goal: "Python基础", time_per_day: 30, language: "zh" as const };
    const intermediate = makeRecommendation({ ...base, difficulty: "intermediate" }, "demo_freshman");
    const advanced = makeRecommendation({ ...base, difficulty: "advanced" }, "demo_freshman");

    expect(intermediate.books.some(({ book }) => book.difficulty === "beginner")).toBe(true);
    expect(intermediate.books.every(({ book }) => book.difficulty !== "advanced")).toBe(true);
    expect(advanced.books.some(({ book }) => book.difficulty === "beginner")).toBe(true);
    expect(advanced.books.some(({ book }) => book.difficulty === "intermediate")).toBe(true);
  });

  it("keeps comparison data aligned to the same books", () => {
    const result = makeComparison("demo_freshman");
    const beforeIds = result.first_recommendation.books.map((item) => item.book.id).sort();
    const afterIds = result.second_recommendation.books.map((item) => item.book.id).sort();
    expect(afterIds).toEqual(beforeIds);
    expect(result.second_recommendation.memories_used).toBeGreaterThan(0);
  });

  it("compresses common feedback into a structured demo memory", () => {
    const memory = writeMockMemory("test_user", "这本书太厚了，希望短一些");
    expect(memory.field).toBe("pages");
    expect(memory.value).toBe("prefer_short");
    expect(getMockMemories("test_user").some((item) => item.id === memory.id)).toBe(true);
  });

  it("provides complete book metadata for the demo", () => {
    expect(getMockBooks().every((book) => book.title && book.pages > 0 && book.goals.length > 0)).toBe(true);
  });

  it("isolates memories by user", () => {
    const other = writeMockMemory("isolated_user", "我喜欢中文讲解");
    expect(getMockMemories("demo_freshman").some((item) => item.id === other.id)).toBe(false);
    expect(getMockMemories("isolated_user").map((item) => item.id)).toContain(other.id);
  });
});
