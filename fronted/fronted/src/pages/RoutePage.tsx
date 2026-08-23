import { useMemo, useState } from "react";
import { BookOpenTextIcon, CalendarBlankIcon, CheckCircleIcon, ClockIcon, FlagIcon, PathIcon, PaperPlaneTiltIcon, SparkleIcon, TrashIcon, XIcon } from "@phosphor-icons/react";
import { BookCover, EmptyState, ScorePanel } from "../components";
import { useApp } from "../state";
import { askLearningAssistant } from "../services/assistantApi";

export default function RoutePage() {
  const { activeUserName, routeBooks, toggleRouteBook, lastInput } = useApp();
  const [expanded, setExpanded] = useState<number | null>(null);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("我可以帮你调整每天的页数、阅读顺序，或者解释为什么这样安排。");
  const pagesPerDay = Math.max(5, Math.round(lastInput.time_per_day / 3));
  const totalPages = routeBooks.reduce((sum, item) => sum + item.book.pages, 0);
  const totalDays = Math.max(1, Math.ceil(totalPages / pagesPerDay));

  const routeProfile = useMemo(() => {
    const topics = routeBooks.map(({ book }) => `${book.topic} ${book.title} ${book.keywords.join(" ")}`).join(" ");
    const isCode = /python|编程|算法|数据结构|软件|程序|代码|java|c\/c\+\+/i.test(topics);
    const isHumanity = /教育|文学|历史|哲学|经济|管理|心理|社会/i.test(topics);
    if (isCode) return { headline: "先建立概念，再用练习把知识变成能力", stages: ["建立概念地图", "拆解案例与练习", "完成一个小型实践"], details: ["先读定义、基本模型和关键术语，避免一开始陷入细节。", "主线书推进核心章节，补充书同步提供例题、代码或案例。", "用输出检验理解，把书中的方法迁移到真实问题。"] };
    if (isHumanity) return { headline: "从背景与观点出发，逐步形成自己的判断", stages: ["搭建背景框架", "比较观点与材料", "形成主题化表达"], details: ["先理解时代、概念和作者的问题意识，建立阅读坐标。", "交替阅读不同书籍，标记相同主题的差异与证据。", "用摘要、时间线或短评沉淀自己的理解，完成一次回看。"] };
    return { headline: "循序推进核心知识，再用回顾完成连接", stages: ["建立基础框架", "理解重点内容", "回顾与迁移"], details: ["先掌握这组书共同的基础概念和阅读方法。", "按页数拆分重点章节，并穿插第二本书进行互相印证。", "每隔几天回顾笔记，把零散知识连接成可复用的结构。"] };
  }, [routeBooks]);
  const schedule = useMemo(() => Array.from({ length: Math.min(totalDays, 7) }, (_, day) => {
    const first = routeBooks[day % routeBooks.length];
    const second = routeBooks.length > 1 ? routeBooks[(day + 1) % routeBooks.length] : null;
    const firstPages = second ? Math.max(3, Math.round(pagesPerDay * .6)) : pagesPerDay;
    return { day: day + 1, focus: routeProfile.stages[day === 0 ? 0 : day === 6 ? 2 : 1], items: [{ book: first, pages: firstPages }, ...(second ? [{ book: second, pages: pagesPerDay - firstPages }] : [])] };
  }), [pagesPerDay, routeBooks, totalDays, routeProfile]);

  const askAssistant = async () => {
    const text = question.trim();
    if (!text) return;
    setAnswer("正在结合当前路线整理回答…");
    try {
      const remoteAnswer = await askLearningAssistant(text, { userName: activeUserName, input: lastInput, books: routeBooks, currentPage: "route" });
      if (remoteAnswer) {
        setAnswer(remoteAnswer);
      } else {
        setAnswer("问答接口还没有配置。请后端同学完成 /api/assistant/chat，并在前端配置 VITE_DEEPSEEK_API_URL 后，这里就会由 DeepSeek 结合当前路线回答。");
      }
    } catch {
      setAnswer("暂时连接不到学习助手服务，请检查后端接口是否已启动。");
    }
    setQuestion("");
  };

  if (!routeBooks.length) return <EmptyState icon={<PathIcon />} title="还没有加入路线的书籍" description="在推荐结果中点击“加入路线”，选中的书籍会集中显示在这里。" />;

  return <div className="route-page page-enter">
    <section className="route-hero">
      <div><span className="eyebrow"><PathIcon /> {activeUserName}的学习规划</span><h2>把几本书，排成<br /><em>每天做得到的进度。</em></h2><p>这不是简单的书单。路线会把每日时间拆成多个阅读任务，让你在同一天里并行推进不同书籍。</p></div>
      <div className="route-hero-mark"><span>ROUTE</span><strong>{String(routeBooks.length).padStart(2, "0")}</strong><small>本加入书籍</small></div>
    </section>
    <section className="route-overview">
      <div className="overview-main"><span className="eyebrow">当前路线</span><h3>{routeProfile.headline}</h3><p>这条路线根据当前书架的主题、难度、页数和每日时间动态拆分。主线书负责搭框架，补充书负责案例、练习或对照，不同书籍组合会生成不同的学习节奏。</p><div className="route-progress"><i style={{ width: "8%" }} /><span>第 1 天</span><span>{totalDays} 天计划</span></div></div>
      <div className="overview-stats"><div><ClockIcon /><strong>{lastInput.time_per_day}<small>分钟/天</small></strong></div><div><BookOpenTextIcon /><strong>{totalPages}<small>总页数</small></strong></div><div><CalendarBlankIcon /><strong>{totalDays}<small>预计天数</small></strong></div></div>
    </section>
    <div className="route-content-grid">
      <section className="daily-plan">
        <div className="section-heading route-section-heading"><div><span className="eyebrow">Daily rhythm</span><h3>每日阅读安排</h3></div><span>每天可并行阅读 {routeBooks.length > 1 ? "2" : "1"} 本</span></div>
        <div className="schedule-list">{schedule.map((entry) => <article className="schedule-day" key={entry.day}><div className="day-marker"><strong>{String(entry.day).padStart(2, "0")}</strong><span>DAY</span></div><div className="day-content"><div className="day-title"><span>{entry.focus}</span><small>{lastInput.time_per_day} 分钟 · 约 {pagesPerDay} 页</small></div>{entry.items.map(({ book, pages }) => <div className="daily-book" key={book.book.id}><BookCover book={book.book} size="sm" /><div><strong>{book.book.title}</strong><span>阅读第 {Math.max(1, (entry.day - 1) * pages)}–{entry.day * pages} 页</span></div><b>{pages} 页</b></div>)}</div></article>)}</div>
        {totalDays > 7 && <div className="schedule-more"><CalendarBlankIcon /> 前 7 天展示具体节奏，后续按同样比例循环推进，直到完成全部 {totalPages} 页。</div>}
      </section>
      <aside className="route-library">
        <div className="section-heading route-section-heading"><div><span className="eyebrow">The reading shelf</span><h3>路线书架</h3></div><span>{routeBooks.length} 本</span></div>
        <div className="route-book-stack">{routeBooks.map((score, index) => <article className="route-book-card" key={score.book.id}><div className="route-book-top"><span className="book-index">0{index + 1}</span><BookCover book={score.book} size="sm" /><div><strong>{score.book.title}</strong><small>{score.book.pages} 页 · {score.book.language === "zh" ? "中文" : "英文"}</small></div><button className="icon-button danger" onClick={() => toggleRouteBook(score)} aria-label={`移除${score.book.title}`}><TrashIcon /></button></div><p>{index === 0 ? "主线 · 负责搭建基础框架" : "并行补充 · 用于案例、练习与拓展"}</p><button className="route-score-toggle" onClick={() => setExpanded(expanded === score.book.id ? null : score.book.id)}>{expanded === score.book.id ? "收起评分" : `匹配分 ${score.total_score.toFixed(1)} · 查看依据`}</button>{expanded === score.book.id && <ScorePanel score={score} compact />}</article>)}</div>
      </aside>
    </div>
    <div className="route-note"><FlagIcon /><span><strong>这条路线不是固定答案</strong><small>读完一天后，你可以回到推荐页反馈“太难、太厚或想增加案例”，馆员会据此重新调整后续安排。</small></span><CheckCircleIcon /></div>
    <button className="route-assistant-launch" onClick={() => setAssistantOpen((value) => !value)} aria-label="打开灵犀学习助手"><SparkleIcon /> <span>问问灵犀</span></button>
    {assistantOpen && <section className="route-assistant" aria-label="灵犀学习助手"><div className="route-assistant-head"><span><SparkleIcon /> 灵犀学习助手</span><button onClick={() => setAssistantOpen(false)} aria-label="关闭"><XIcon /></button></div><p className="route-assistant-answer">{answer}</p><div className="route-assistant-input"><input value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") askAssistant(); }} placeholder="问问这条路线怎么学…" /><button onClick={askAssistant} aria-label="发送问题"><PaperPlaneTiltIcon /></button></div></section>}
  </div>;
}
