import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import { ArrowRightIcon, BookOpenTextIcon, BrainIcon, CaretDownIcon, ClockIcon } from "@phosphor-icons/react";
import { listMemories, recommend } from "../api";
import { LoadingRoute, MemoryChip, topicNames } from "../components";
import { useApp } from "../state";
import type { Difficulty, Language, Memory } from "../types";

const goalOptions = Object.keys(topicNames).sort((a, b) => a.localeCompare(b, "zh"));

export default function RecommendPage() {
  const { activeUserId, activeUserName, lastInput, setLastInput, setRecommendation } = useApp();
  const [input, setInput] = useState({ ...lastInput, goal: "" });
  const [showGoals, setShowGoals] = useState(false);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  useEffect(() => { listMemories(activeUserId).then(setMemories); }, [activeUserId]);

  async function submit() {
    if (!input.goal.trim()) { setError("请先输入你想学习的内容。"); return; }
    setLoading(true); setError(""); setLastInput(input);
    try {
      const result = await recommend(input, activeUserId);
      setRecommendation(result); navigate(`/result/${Date.now().toString(36)}`);
    } catch {
      setError("推荐服务暂时不可用，请检查后端连接后重试。");
    } finally { setLoading(false); }
  }

  if (loading) return <LoadingRoute />;
  return <div className="recommend-page page-enter">
    <section className="page-intro"><div><span className="eyebrow">新的学习路线</span><h2>从今天能做到的<br />一步开始。</h2></div><p>告诉馆员你的目标与限制。系统会检索相关记忆、筛选书目，并解释每一个排序依据。</p></section>
    <div className="recommend-grid">
      <section className="form-surface">
        <div className="field-block goal-field"><label htmlFor="learning-goal">你想学习什么？</label><div className="goal-combobox"><input id="learning-goal" value={input.goal} onChange={(event) => { setInput({ ...input, goal: event.target.value }); setShowGoals(false); }} placeholder="输入学习主题" autoComplete="off" /><button type="button" onClick={() => setShowGoals((visible) => !visible)} aria-label="展开学习主题" aria-expanded={showGoals}><CaretDownIcon weight="bold" /></button>{showGoals && <div className="goal-options">{goalOptions.map((value) => <button type="button" key={value} onClick={() => { setInput({ ...input, goal: value }); setShowGoals(false); }}>{topicNames[value]}</button>)}</div>}</div></div>
        <div className="two-fields">
          <div className="field-block"><label>当前水平</label><div className="segmented">{(["beginner", "intermediate", "advanced"] as Difficulty[]).map((value) => <button key={value} onClick={() => setInput({ ...input, difficulty: value })} className={input.difficulty === value ? "selected" : ""}>{value === "beginner" ? "入门" : value === "intermediate" ? "进阶" : "高阶"}</button>)}</div></div>
          <div className="field-block"><label>语言偏好</label><div className="segmented">{(["zh", "en"] as Language[]).map((value) => <button key={value} onClick={() => setInput({ ...input, language: value })} className={input.language === value ? "selected" : ""}>{value === "zh" ? "中文" : "英文"}</button>)}</div></div>
        </div>
        <div className="field-block time-field"><label>每日学习时间 <strong>{input.time_per_day} 分钟</strong></label><input type="range" min="15" max="120" step="15" value={input.time_per_day} onChange={(event) => setInput({ ...input, time_per_day: Number(event.target.value) })} /><div><span>15 分钟</span><span>约 {Math.round(input.time_per_day / 3)} 页/天</span><span>120 分钟</span></div></div>
        <div className="field-block"><label htmlFor="constraints">额外约束 <span>可选</span></label><textarea id="constraints" rows={3} value={input.additional_constraints || ""} onChange={(event) => setInput({ ...input, additional_constraints: event.target.value })} placeholder="例如：数学基础较弱，希望案例多一些" /><small className="field-note">后端在线时，该条件是否参与排序取决于 Agent 当前实现。</small></div>
        {error && <p className="inline-error" role="alert">{error}</p>}
        <button className="primary-action" onClick={submit}>生成我的学习路线 <ArrowRightIcon weight="bold" /></button>
      </section>
      <aside className="context-panel">
        <div className="context-visual">
          <img className="context-art" src="/assets/learning-route-editorial.png" alt="开放的书籍通向图书馆书架，沿途有学习路线节点" />
          <div><span className="eyebrow">馆员已了解</span><h3>{activeUserName}的学习档案</h3><p>目标、限制和反馈会在这里形成可管理的长期记忆。</p></div>
        </div>
        <div className="context-stats"><div><BrainIcon /><strong>{memories.length}</strong><span>条可用记忆</span></div><div><ClockIcon /><strong>{input.time_per_day}</strong><span>分钟每日预算</span></div><div><BookOpenTextIcon /><strong>{Math.max(14, Math.round(350 / (input.time_per_day / 3)))}</strong><span>天参考周期</span></div></div>
        <div className="memory-preview"><div className="section-heading"><h3>本次可能参考</h3><span>{Math.min(memories.length, 3)} 条</span></div>{memories.length ? memories.slice(0, 3).map((memory) => <MemoryChip memory={memory} key={memory.id} active />) : <p className="quiet-note">完成一次推荐并反馈后，这里会形成你的学习档案。</p>}</div>
        <motion.div className="privacy-note" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><BrainIcon /><span><strong>记忆由你控制</strong><small>每条记录都可以查看来源与删除。</small></span></motion.div>
      </aside>
    </div>
  </div>;
}
