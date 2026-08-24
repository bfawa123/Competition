import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { ArrowDownIcon, ArrowRightIcon, BrainIcon, CheckCircleIcon, LightningIcon, PlayIcon, RepeatIcon, SparkleIcon } from "@phosphor-icons/react";
import { getComparison } from "../api";
import { BookCover, LoadingRoute } from "../components";
import { useApp } from "../state";
import type { CompareResponse } from "../types";

const stages = ["第一次推荐", "用户反馈", "记忆写入", "第二次推荐"];
export default function ComparePage() {
  const { activeUserId } = useApp();
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const requestRef = useRef<Promise<CompareResponse> | null>(null);
  const reduce = useReducedMotion();
  useEffect(() => {
    if (!requestRef.current) requestRef.current = getComparison(activeUserId);
    requestRef.current.then(setData).finally(() => { requestRef.current = null; });
  }, [activeUserId]);
  async function reset() { setLoading(true); setStep(0); const next = await getComparison(activeUserId); setData(next); setLoading(false); }
  if (loading || !data) return <LoadingRoute />;
  const beforeMap = new Map(data.first_recommendation.books.map((item, index) => [item.book.id, index + 1]));
  const memoryFields = data.comparison.memory_added.split(",").map((field) => field.trim()).filter(Boolean);
  const fieldNames: Record<string, string> = { pages: "篇幅偏短", language: "中文优先", prefer_cases: "案例驱动" };
  return <div className="compare-page page-enter">
    <section className="compare-heading"><div><span className="eyebrow">记忆影响核心场景</span><h2>看见一条反馈，<br />如何改变推荐。</h2></div><p>相同用户、相同学习目标。唯一变量是系统是否记住了用户反馈。</p><div><button className="primary-action small" onClick={() => setStep((value) => Math.min(3, value + 1))}>{step === 0 ? <PlayIcon /> : <ArrowRightIcon />}{step === 3 ? "对比已完成" : `展示下一步`}</button><button className="icon-button" onClick={reset} aria-label="重置对比"><RepeatIcon /></button></div></section>
    <div className="comparison-progress">{stages.map((label, index) => <div className={index <= step ? "active" : ""} key={label}><i>{index < step ? <CheckCircleIcon weight="fill" /> : index + 1}</i><span>{label}</span></div>)}</div>
    <div className="feedback-cause"><span><BrainIcon weight="duotone" /></span><div><small>用户原始反馈</small><blockquote>“{data.feedback}”</blockquote></div><ArrowDownIcon /></div>
    <figure className="compare-story"><img src="/assets/feedback-transform-editorial.png" alt="用户反馈经过结构化记忆后影响两组书目排序的流程插图" /><figcaption>把一次自然语言反馈，变成下一次推荐可以复用的证据。</figcaption></figure>
    <AnimatePresence>{step >= 2 && <motion.div className="memory-extraction" initial={reduce ? false : { scaleY: .8, opacity: 0 }} animate={{ scaleY: 1, opacity: 1 }}><BrainIcon /><span><strong>压缩为 {memoryFields.length || 1} 条可复用记忆</strong><small>{memoryFields.map((field) => fieldNames[field] || field).join(" · ")}</small></span><code>{Math.round(data.memory_saved.confidence * 100)}% 置信</code></motion.div>}</AnimatePresence>
    <div className="comparison-board">
      <section><div className="comparison-title"><span>反馈前</span><h3>只依据显式条件</h3><small>引用记忆 0 条</small></div><div className="comparison-books">{data.first_recommendation.books.slice(0, 4).map((score, index) => <div key={score.book.id}><span className="compare-rank">#{index + 1}</span><BookCover book={score.book} size="sm" /><span><strong>{score.book.title}</strong><small>{score.book.pages} 页 · 案例 {Math.round(score.book.case_ratio * 100)}%</small></span><code>{score.total_score.toFixed(1)}</code></div>)}</div></section>
      <div className="change-spine"><span><LightningIcon /></span><strong>记忆影响</strong><i /><p>短篇实战书上升</p><p>长篇理论书下降</p><p>偏好评分最高 +30%</p></div>
      <section className={step >= 3 ? "revealed" : "obscured"}><div className="comparison-title after"><span>记忆后</span><h3>依据反馈重新排序</h3><small>引用记忆 {data.second_recommendation.memories_used} 条</small></div><div className="comparison-books">{data.second_recommendation.books.slice(0, 4).map((score, index) => { const before = beforeMap.get(score.book.id) || index + 1; const change = before - (index + 1); return <motion.div layout={!reduce} key={score.book.id}><span className="compare-rank">#{index + 1}</span><BookCover book={score.book} size="sm" /><span><strong>{score.book.title}</strong><small>{score.book.pages} 页 · 案例 {Math.round(score.book.case_ratio * 100)}%</small></span><code>{score.total_score.toFixed(1)}</code><em className={change > 0 ? "up" : change < 0 ? "down" : "same"}>{change > 0 ? `↑ ${change}` : change < 0 ? `↓ ${Math.abs(change)}` : "-"}</em></motion.div>; })}</div></section>
    </div>
    <section className="impact-summary"><SparkleIcon weight="duotone" /><div><span>变化结论</span><h3>{data.comparison.impact}</h3><p>这不是重新猜测用户需求，而是复用用户亲自确认过的学习偏好。</p></div></section>
  </div>;
}
