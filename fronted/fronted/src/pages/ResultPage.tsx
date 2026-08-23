import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeftIcon, BrainIcon, BracketsCurlyIcon, CheckCircleIcon, ChatCircleTextIcon, ClockIcon, PathIcon, SparkleIcon, XIcon } from "@phosphor-icons/react";
import { BookDetail, BookRow, EmptyState, MemoryChip, Portal, ScorePanel, Toast } from "../components";
import { writeMemory } from "../api";
import { useApp } from "../state";
import type { BookScore } from "../types";

type Tab = "why" | "memory" | "trace";
export default function ResultPage() {
  const { recommendation, lastInput, activeUserId, activeUserName, routeBooks, toggleRouteBook } = useApp();
  const [tab, setTab] = useState<Tab>("why");
  const [expanded, setExpanded] = useState<number | null>(null);
  const [detail, setDetail] = useState<BookScore | null>(null);
  const [feedbackBook, setFeedbackBook] = useState<BookScore | null>(null);
  const [feedback, setFeedback] = useState("");
  const [toast, setToast] = useState("");
  const navigate = useNavigate();
  const routePlan = useMemo(() => {
    if (!recommendation) return {
      headline: "先建立核心概念，再逐步完成实践。",
      subtitle: "从基础理解到独立应用",
      stages: [["建立核心概念", "从基础开始", "等待推荐结果"] as [string, string, string]],
    };
    const goal = `${lastInput.goal} ${recommendation.books.map((item) => `${item.book.topic} ${item.book.keywords.join(" ")}`).join(" ")}`.toLowerCase();
    if (/教育|教学| педагог|课程|学习科学/.test(goal)) {
      return {
        headline: "先理解教育现象，再形成教学判断。",
        subtitle: "从核心概念到真实教育场景",
        stages: [
          ["理解核心概念", "建立教育学基本框架与关键概念", "先读概念清晰、能搭建框架的书目"],
          ["比较教育实践", "对照不同制度、课堂与学习情境", "关注案例、研究结论与比较视角"],
          ["形成分析判断", "用理论解释现象并完成自己的分析", "将理论转化为问题分析与研究素材"],
        ],
      };
    }
    if (/心理|认知|脑科学/.test(goal)) {
      return {
        headline: "先建立认知框架，再解释真实行为。",
        subtitle: "从基础概念到案例分析",
        stages: [
          ["建立认知框架", "掌握心理与认知研究的基本概念", "优先阅读基础、易理解的书目"],
          ["理解研究证据", "认识实验、观察与案例背后的证据", "结合案例理解不同研究结论"],
          ["应用与反思", "把理论用于解释具体问题", "尝试记录观察并形成自己的判断"],
        ],
      };
    }
    return {
      headline: "先建立核心概念，再逐步完成实践。",
      subtitle: "从基础理解到独立应用",
      stages: [
        ["建立核心概念", `理解“${lastInput.goal}”的基础框架`, "优先从入门与概念清晰的书目开始"],
        ["连接真实案例", "把概念放进真实问题与案例中理解", "优先选择案例丰富、可操作的书目"],
        ["独立应用与深入", "完成一个小练习并按需深入理论", "将理论书作为查阅与进阶材料"],
      ],
    };
  }, [lastInput.goal, recommendation?.books]);

  if (!recommendation) return <EmptyState title="还没有推荐结果" description="先填写学习目标，馆员会在这里整理路线与推荐证据。" />;

  async function submitFeedback() {
    if (!feedback.trim()) return;
    await writeMemory(activeUserId, feedback, feedbackBook ? { current_book_id: feedbackBook.book.id, current_book_title: feedbackBook.book.title } : undefined);
    setFeedbackBook(null); setFeedback(""); setToast("反馈已压缩为可管理记忆");
  }

  return <div className="result-page page-enter">
    <button className="back-link" onClick={() => navigate("/recommend")}><ArrowLeftIcon />调整学习条件</button>
    <section className="result-summary"><div><span className="eyebrow">为 {activeUserName} 生成</span><h2>{lastInput.goal}学习路线</h2><p>{recommendation.explanation}</p></div><div className="summary-facts"><span><strong>{recommendation.books.length}</strong> 本候选</span><span><strong>{recommendation.memories_used.length}</strong> 条记忆</span><span><strong>{lastInput.time_per_day}</strong> 分钟/天</span></div></section>
    <div className="result-grid">
      <section className="route-list">
        <div className="route-header"><div><PathIcon size={23} /><span><strong>建议阅读顺序</strong><small>从建立直觉到完整实践</small></span></div><span>预计 {Math.ceil(recommendation.books.reduce((sum, item) => sum + item.book.pages, 0) / (lastInput.time_per_day / 3))} 天</span></div>
        {recommendation.books.map((score, index) => <div key={score.book.id}><BookRow score={score} rank={index + 1} onFeedback={() => setFeedbackBook(score)} onOpen={() => setDetail(score)} onAdd={() => { toggleRouteBook(score); setToast(routeBooks.some((item) => item.book.id === score.book.id) ? "已从当前学习路线移除" : "已加入当前学习路线"); }} added={routeBooks.some((item) => item.book.id === score.book.id)} />{expanded === score.book.id ? <div className="inline-score"><ScorePanel score={score} /><button className="score-collapse" onClick={() => setExpanded(null)}><XIcon />收起评分</button></div> : <button className="score-expand" onClick={() => setExpanded(score.book.id)}>展开评分</button>}</div>)}
      </section>
      <aside className="evidence-panel">
        <div className="tabs"><button className={tab === "why" ? "active" : ""} onClick={() => setTab("why")}><SparkleIcon />推荐依据</button><button className={tab === "memory" ? "active" : ""} onClick={() => setTab("memory")}><BrainIcon />引用记忆</button><button className={tab === "trace" ? "active" : ""} onClick={() => setTab("trace")}><BracketsCurlyIcon />执行轨迹</button></div>
        {tab === "why" && <div className="tab-content"><span className="evidence-label">路线逻辑</span><h3>{routePlan.headline}</h3><p>{recommendation.explanation}</p><div className="reading-plan">{routePlan.stages.map(([title, detail, note], index) => <div key={title}><span>阶段{["一", "二", "三"][index]}</span><strong>{title}</strong><small>{detail} · {note}</small></div>)}</div><button className="secondary-action" onClick={() => setFeedbackBook(recommendation.books[0])}><ChatCircleTextIcon />告诉馆员哪里不合适</button></div>}
        {tab === "memory" && <div className="tab-content"><span className="evidence-label">本次实际采用</span><h3>{recommendation.memories_used.length} 条记忆参与排序</h3><p>绿色记忆会影响篇幅过滤、语言偏好和内容风格评分。</p><div className="memory-list">{recommendation.memories_used.map((memory) => <div key={memory.id}><MemoryChip memory={memory} active /><p>来源：“{memory.source}”</p></div>)}</div><div className="memory-receipt"><strong>记忆收据</strong><span>检索候选 <code>{recommendation.memories_used.length + 1}</code></span><span>实际引用 <code>{recommendation.memories_used.length}</code></span><span>平均置信度 <code>{recommendation.memories_used.length ? Math.round(recommendation.memories_used.reduce((sum, memory) => sum + memory.confidence, 0) / recommendation.memories_used.length * 100) : 0}%</code></span></div></div>}
        {tab === "trace" && <div className="tab-content"><span className="evidence-label">Agent 工具链</span><h3>从任务到结果的完整路径</h3><div className="mini-trace">{recommendation.agent_trace.map((step, index) => <div key={`${step.action}-${index}`}><i>{index + 1}</i><span><strong>{step.action}</strong><small>{Object.entries(step.details).map(([key, value]) => `${key}: ${String(value)}`).join(" / ")}</small></span>{step.duration_ms && <code>{step.duration_ms}ms</code>}</div>)}</div></div>}
      </aside>
    </div>
    {feedbackBook && <Portal><div className="modal-backdrop" onMouseDown={() => setFeedbackBook(null)}><section className="feedback-sheet" onMouseDown={(event) => event.stopPropagation()}><button className="icon-button close" onClick={() => setFeedbackBook(null)}><XIcon /></button><span className="feedback-icon"><ChatCircleTextIcon /></span><h2>哪里不合适？</h2><p>你对《{feedbackBook.book.title}》的反馈会成为下一次推荐的依据。</p><div className="quick-feedbacks">{["这本书太厚了", "难度太高", "理论内容太多", "英文阅读较慢", "我已经读过了"].map((item) => <button key={item} onClick={() => setFeedback(item)} className={feedback === item ? "selected" : ""}>{item}</button>)}</div><textarea value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="也可以用自己的话描述..." rows={3} /><button className="primary-action" onClick={submitFeedback}><CheckCircleIcon />保存为记忆</button></section></div></Portal>}
    {detail && <BookDetail book={detail.book} score={detail} onClose={() => setDetail(null)} />}
    {toast && <Toast message={toast} onDone={() => setToast("")} />}
  </div>;
}
