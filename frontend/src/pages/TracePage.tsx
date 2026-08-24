import { useEffect, useMemo, useState } from "react";
import { BracketsCurlyIcon, CheckCircleIcon, CoinsIcon, DatabaseIcon, GaugeIcon, LightningIcon } from "@phosphor-icons/react";
import { getTrace } from "../api";
import { useApp } from "../state";
import type { TraceStep } from "../types";

export default function TracePage() {
  const { user, activeUserId } = useApp();
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [open, setOpen] = useState<number | null>(null);
  useEffect(() => { getTrace(activeUserId).then(setTrace); }, [activeUserId]);
  const total = useMemo(() => trace.reduce((sum, item) => sum + (item.duration_ms || 0), 0), [trace]);
  const memoryStep = trace.find((item) => item.action.includes("retrieve_memory"));
  const explanationStep = trace.find((item) => item.action.includes("explanation"));
  const memoryCandidates = Number(memoryStep?.details.candidates || 0);
  const memoriesUsed = Number(memoryStep?.details.used || 0);
  const tokens = Number(explanationStep?.details.tokens || 0);
  const hitRate = memoryCandidates ? Math.round(memoriesUsed / memoryCandidates * 100) : 0;
  const actionDescriptions: Record<string, string> = { retrieve_memory: "从记忆库检索相关偏好", search_books: "按目标与约束筛选候选书目", recommend: "计算多维评分并排序", generate_explanation: "生成自然语言路线说明" };
  return <div className="trace-page page-enter">
    <section className="page-intro compact"><div><span className="eyebrow">透明执行模式</span><h2>Agent 执行轨迹</h2></div><p>每一次工具调用都有输入、输出摘要与耗时。点击步骤查看详细参数。</p></section>
    <div className="trace-metrics"><div><GaugeIcon /><span><strong>{total ? `${total}ms` : "--"}</strong><small>推荐总耗时</small></span></div><div><DatabaseIcon /><span><strong>{memoryCandidates ? `${memoriesUsed} / ${memoryCandidates}` : "--"}</strong><small>记忆采用/候选</small></span></div><div><CoinsIcon /><span><strong>{tokens || "--"}</strong><small>说明生成 Token</small></span></div><div><CheckCircleIcon /><span><strong>{memoryCandidates ? `${hitRate}%` : "--"}</strong><small>记忆命中率</small></span></div></div>
    <div className="trace-layout"><section className="trace-chain"><div className="chain-head"><LightningIcon /><div><strong>最近一次推荐</strong><small>{user ? `用户 ${user.id}` : "访客会话"}</small></div><code>{trace.length} 个步骤</code></div>{trace.map((step, index) => <button key={`${step.action}-${index}`} onClick={() => setOpen(open === index ? null : index)} className={open === index ? "open" : ""}><i>{index + 1}</i><span><strong>{step.action}</strong><small>{actionDescriptions[step.action] || "执行 Agent 工具步骤"}</small></span><code>{step.duration_ms ? `${step.duration_ms}ms` : "--"}</code>{open === index && <pre>{JSON.stringify(step.details, null, 2)}</pre>}</button>)}</section><aside className="trace-notes"><BracketsCurlyIcon /><h3>这条轨迹证明了什么？</h3><div><span>01</span><p><strong>记忆先于搜索</strong>用户偏好在候选召回前介入，而不是结果生成后的文案包装。</p></div><div><span>02</span><p><strong>排序可复现</strong>核心评分由确定性规则完成，大模型不直接决定排名。</p></div><div><span>03</span><p><strong>使用可审计</strong>候选记忆与实际引用数量可以被单独核对。</p></div></aside></div>
  </div>;
}
