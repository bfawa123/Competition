import { useEffect, useMemo, useState } from "react";
import { BrainIcon, CalendarBlankIcon, CheckCircleIcon, ClockCounterClockwiseIcon, PlusIcon, ShieldCheckIcon, TrashIcon, XIcon } from "@phosphor-icons/react";
import { listMemories, removeMemory, writeMemory } from "../api";
import { EmptyState, MemoryChip, Portal, Toast } from "../components";
import { useApp } from "../state";
import type { Memory } from "../types";

const typeNames = { fixed_profile: "固定画像", preference: "偏好记忆", task_feedback: "任务反馈" };
export default function MemoriesPage() {
  const { activeUserId } = useApp();
  const [memories, setMemories] = useState<Memory[]>([]);
  const [selected, setSelected] = useState<Memory | null>(null);
  const [adding, setAdding] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [confirm, setConfirm] = useState<Memory | null>(null);
  const [toast, setToast] = useState("");
  const load = () => listMemories(activeUserId).then((items) => { setMemories(items); return items; });
  useEffect(() => {
    let active = true;
    setSelected(null);
    listMemories(activeUserId).then((items) => { if (active) { setMemories(items); setSelected(items[0] || null); } });
    return () => { active = false; };
  }, [activeUserId]);
  const average = useMemo(() => memories.length ? Math.round(memories.reduce((sum, item) => sum + item.confidence, 0) / memories.length * 100) : 0, [memories]);

  async function add() { if (!feedback.trim()) return; const memory = await writeMemory(activeUserId, feedback); setFeedback(""); setAdding(false); await load(); setSelected(memory); setToast("新记忆已写入"); }
  async function remove() { if (!confirm || confirm.user_id !== activeUserId) return; await removeMemory(activeUserId, confirm.id); setConfirm(null); setSelected(null); const items = await load(); setSelected(items[0] || null); setToast("记忆已删除，后续推荐不再引用"); }

  return <div className="memories-page page-enter">
    <section className="page-intro compact"><div><span className="eyebrow">你的数据，由你控制</span><h2>记忆中心</h2></div><p>查看馆员记录了什么、它来自哪里，以及何时参与过推荐。</p><button className="primary-action small" onClick={() => setAdding(true)}><PlusIcon />写入记忆</button></section>
    <section className="memory-story"><div><span className="eyebrow">可核对的长期偏好</span><h3>每一条记忆，都有来源。</h3><p>反馈被压缩成可管理的索引卡片，参与相关任务的筛选与排序。你可以查看、复核，或随时删除。</p></div><img src="/assets/memory-archive-editorial.png" alt="纸质档案卡、笔记本与钥匙组成的记忆档案插图" /></section>
    <div className="memory-metrics"><div><BrainIcon /><span><strong>{memories.length}</strong><small>全部记忆</small></span></div><div><ShieldCheckIcon /><span><strong>{average}%</strong><small>平均置信度</small></span></div><div><ClockCounterClockwiseIcon /><span><strong>{memories.reduce((sum, item) => sum + item.usage_count, 0)}</strong><small>累计引用</small></span></div><div><CalendarBlankIcon /><span><strong>{memories[0]?.created_at.slice(5, 10) || "暂无"}</strong><small>最近写入</small></span></div></div>
    <div className="memory-workspace">
      <section className="memory-table">
        <div className="table-head"><span>记忆内容</span><span>类型</span><span>置信度</span><span>引用</span></div>
        {memories.length ? memories.map((memory) => <button key={memory.id} className={selected?.id === memory.id ? "selected" : ""} onClick={() => setSelected(memory)}><MemoryChip memory={memory} /><span className="type-label">{typeNames[memory.type]}</span><span className="confidence"><i><b style={{ width: `${memory.confidence * 100}%` }} /></i><code>{Math.round(memory.confidence * 100)}%</code></span><code>{memory.usage_count} 次</code></button>) : <EmptyState title="还没有长期记忆" description="提交一次学习反馈后，结构化记录会出现在这里。" />}
      </section>
      <aside className="memory-detail">{selected ? <><div className="detail-top"><span className="memory-big-icon"><BrainIcon weight="duotone" /></span><button className="icon-button danger" onClick={() => setConfirm(selected)}><TrashIcon /></button></div><span className="type-label">{typeNames[selected.type]}</span><h2>{selected.field}</h2><p className="memory-value">{String(selected.value)}</p><div className="source-quote"><span>来源原文</span><p>“{selected.source}”</p></div><dl><div><dt>置信度</dt><dd>{Math.round(selected.confidence * 100)}%</dd></div><div><dt>创建时间</dt><dd>{new Date(selected.created_at).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</dd></div><div><dt>最后使用</dt><dd>{selected.last_used ? new Date(selected.last_used).toLocaleDateString("zh-CN") : "尚未引用"}</dd></div><div><dt>使用次数</dt><dd>{selected.usage_count} 次</dd></div></dl><div className="control-note"><ShieldCheckIcon /><p><strong>这条记忆会如何使用？</strong><span>仅在相关学习任务中参与候选过滤或偏好评分。</span></p></div></> : <EmptyState title="选择一条记忆" description="右侧会显示来源、置信度和使用记录。" />}</aside>
    </div>
    {adding && <Portal><div className="modal-backdrop" onMouseDown={() => setAdding(false)}><section className="feedback-sheet" onMouseDown={(event) => event.stopPropagation()}><button className="icon-button close" onClick={() => setAdding(false)}><XIcon /></button><span className="feedback-icon memory"><BrainIcon /></span><h2>告诉馆员一件事</h2><p>自然语言反馈会被压缩为结构化记忆，并保留原文供你核对。</p><textarea rows={4} value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="例如：我每天只有 30 分钟，更喜欢中文案例。" /><button className="primary-action" onClick={add}><CheckCircleIcon />提取并保存</button></section></div></Portal>}
    {confirm && <Portal><div className="modal-backdrop"><section className="confirm-dialog"><span><TrashIcon /></span><h2>删除这条记忆？</h2><p>删除后，后续推荐将不再参考“{confirm.source}”。</p><div><button className="secondary-action" onClick={() => setConfirm(null)}>取消</button><button className="danger-action" onClick={remove}>确认删除</button></div></section></div></Portal>}
    {toast && <Toast message={toast} onDone={() => setToast("")} />}
  </div>;
}
