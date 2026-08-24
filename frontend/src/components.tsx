import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { ArrowRightIcon, BookOpenIcon, BrainIcon, CheckCircleIcon, ClockIcon, MapPinIcon, SparkleIcon, XIcon } from "@phosphor-icons/react";
import { useEffect } from "react";
import type { CSSProperties, ReactNode } from "react";
import { createPortal } from "react-dom";
import type { Book, BookScore, Memory } from "./types";

/**
 * 把浮层渲染到 document.body 下。页面容器（.page-enter）带 transform 入场动画，
 * 动画结束后由于 animation-fill-mode 的存在 transform 仍不是 none，会让内部所有
 * position: fixed 的元素改为相对该容器（整页文档）定位——表现为弹窗一打开就停在
 * 内容中部/底部、且自身无法滚动。Portal 让浮层脱离该祖先，fixed 恢复相对视口。
 */
export function Portal({ children }: { children: ReactNode }) {
  return createPortal(children, document.body);
}

export const topicNames: Record<string, string> = {
  "Python基础": "Python基础",
  "C/C++": "C/C++",
  "操作系统": "操作系统",
  "Java": "Java",
  "算法": "算法",
  "数据结构": "数据结构",
  "计算机网络": "计算机网络",
  "数据库": "数据库",
  "机器学习": "机器学习",
  "深度学习": "深度学习",
  "人工智能": "人工智能",
  "软件工程": "软件工程",
  "电路基础": "电路基础",
  "模拟电子": "模拟电子",
  "数字电子": "数字电子",
  "信号与系统": "信号与系统",
  "通信原理": "通信原理",
  "单片机": "单片机",
  "嵌入式": "嵌入式",
  "FPGA": "FPGA",
  "自动控制": "自动控制",
  "电磁场": "电磁场",
  "传感器": "传感器",
  "数字信号处理": "数字信号处理",
  "中国古典文学": "中国古典文学",
  "中国现代文学": "中国现代文学",
  "中国当代文学": "中国当代文学",
  "科幻文学": "科幻文学",
  "外国文学": "外国文学",
  "中国史": "中国史",
  "世界史": "世界史",
  "史学理论": "史学理论",
  "中国哲学": "中国哲学",
  "西方哲学": "西方哲学",
  "微观经济学": "微观经济学",
  "宏观经济学": "宏观经济学",
  "经济思想史": "经济思想史",
  "政治经济学": "政治经济学",
  "经济学原理": "经济学原理",
  "国际经济学": "国际经济学",
  "计量经济学": "计量经济学",
  "金融学": "金融学",
  "会计学": "会计学",
  "统计学": "统计学",
  "博弈论": "博弈论",
  "发展经济学": "发展经济学",
  "行为经济学": "行为经济学",
  "通俗经济学": "通俗经济学",
  "投资学": "投资学",
  "管理学原理": "管理学原理",
  "组织行为学": "组织行为学",
  "市场营销": "市场营销",
  "人力资源": "人力资源",
  "战略管理": "战略管理",
  "运营管理": "运营管理",
  "供应链管理": "供应链管理",
  "项目管理": "项目管理",
  "质量管理": "质量管理",
  "财务管理": "财务管理",
  "成本管理": "成本管理",
  "信息系统": "信息系统",
  "公司治理": "公司治理",
  "创业管理": "创业管理",
  "创新管理": "创新管理",
  "领导力": "领导力",
  "管理学": "管理学",
  "企业管理": "企业管理",
  "高等数学": "高等数学",
  "数学分析": "数学分析",
  "线性代数": "线性代数",
  "概率论": "概率论",
  "离散数学": "离散数学",
  "微分方程": "微分方程",
  "复变函数": "复变函数",
  "实变函数": "实变函数",
  "泛函分析": "泛函分析",
  "代数学": "代数学",
  "拓扑学": "拓扑学",
  "微分几何": "微分几何",
  "数值计算": "数值计算",
  "最优化": "最优化",
  "图论": "图论",
  "组合数学": "组合数学",
  "数论": "数论",
  "几何学": "几何学",
  "数学科普": "数学科普",
  "大学物理": "大学物理",
  "电磁学": "电磁学",
  "量子力学": "量子力学",
  "理论力学": "理论力学",
  "电动力学": "电动力学",
  "热力学": "热力学",
  "固体物理": "固体物理",
  "光学": "光学",
  "原子物理": "原子物理",
  "核物理": "核物理",
  "粒子物理": "粒子物理",
  "天体物理": "天体物理",
  "生物物理": "生物物理",
  "数学物理": "数学物理",
  "物理科普": "物理科普",
  "力学": "力学",
  "无机化学": "无机化学",
  "有机化学": "有机化学",
  "分析化学": "分析化学",
  "物理化学": "物理化学",
  "结构化学": "结构化学",
  "高分子化学": "高分子化学",
  "生物化学": "生物化学",
  "环境化学": "环境化学",
  "药物化学": "药物化学",
  "催化化学": "催化化学",
  "电化学": "电化学",
  "光化学": "光化学",
  "化学史": "化学史",
  "化学科普": "化学科普",
  "普通化学": "普通化学",
  "普通生物学": "普通生物学",
  "细胞生物学": "细胞生物学",
  "分子生物学": "分子生物学",
  "遗传学": "遗传学",
  "生态学": "生态学",
  "动物学": "动物学",
  "植物学": "植物学",
  "微生物学": "微生物学",
  "生理学": "生理学",
  "发育生物学": "发育生物学",
  "神经生物学": "神经生物学",
  "进化生物学": "进化生物学",
  "基因组学": "基因组学",
  "蛋白质组学": "蛋白质组学",
  "生物信息学": "生物信息学",
  "遗传学科普": "遗传学科普",
  "法理学": "法理学",
  "宪法学": "宪法学",
  "民法学": "民法学",
  "刑法学": "刑法学",
  "行政法学": "行政法学",
  "经济法学": "经济法学",
  "商法学": "商法学",
  "知识产权法": "知识产权法",
  "国际法学": "国际法学",
  "国际私法": "国际私法",
  "国际经济法": "国际经济法",
  "诉讼法学": "诉讼法学",
  "证据法学": "证据法学",
  "法律逻辑": "法律逻辑",
  "法制史": "法制史",
  "法律思想史": "法律思想史",
  "法哲学": "法哲学",
  "法律随笔": "法律随笔",
  "教育学原理": "教育学原理",
  "教育心理学": "教育心理学",
  "教育史": "教育史",
  "教育研究": "教育研究",
  "课程论": "课程论",
  "教育哲学": "教育哲学",
  "教育社会学": "教育社会学",
  "教育经济学": "教育经济学",
  "教育管理": "教育管理",
  "高等教育": "高等教育",
  "比较教育": "比较教育",
  "教育实践": "教育实践",
  "艺术理论": "艺术理论",
  "美术史": "美术史",
  "艺术哲学": "艺术哲学",
  "美学": "美学",
  "绘画": "绘画",
  "书法": "书法",
  "音乐": "音乐",
  "影视": "影视",
  "设计": "设计",
  "建筑": "建筑",
  "体育理论": "体育理论",
  "运动生理": "运动生理",
  "运动解剖": "运动解剖",
  "运动心理": "运动心理",
  "运动训练": "运动训练",
  "体育保健": "体育保健",
  "学校体育": "学校体育",
  "社会体育": "社会体育",
  "体育统计": "体育统计",
  "科研方法": "科研方法",
  "田径": "田径",
  "篮球": "篮球",
  "足球": "足球",
  "游泳": "游泳",
  "武术": "武术",
  "语言学": "语言学",
  "现代汉语": "现代汉语",
  "古代汉语": "古代汉语",
  "英语": "英语",
  "翻译": "翻译",
  "日语": "日语",
  "法语": "法语",
  "社会语言学": "社会语言学",
  "认知语言学": "认知语言学",
  "语言学科普": "语言学科普",
  "普通心理学": "普通心理学",
  "发展心理学": "发展心理学",
  "社会心理学": "社会心理学",
  "人格心理学": "人格心理学",
  "认知心理学": "认知心理学",
  "实验心理学": "实验心理学",
  "心理测量": "心理测量",
  "心理统计": "心理统计",
  "变态心理学": "变态心理学",
  "临床心理学": "临床心理学",
  "咨询心理学": "咨询心理学",
  "管理心理学": "管理心理学",
  "消费心理学": "消费心理学",
  "心理学入门": "心理学入门",
  "精神分析": "精神分析",
  "个体心理学": "个体心理学",
  "社会学原理": "社会学原理",
  "研究方法": "研究方法",
  "社会分层": "社会分层",
  "城市社会学": "城市社会学",
  "农村社会学": "农村社会学",
  "家庭社会学": "家庭社会学",
  "经济社会学": "经济社会学",
  "政治社会学": "政治社会学",
  "文化社会学": "文化社会学",
  "社会学理论": "社会学理论",
  "社会学": "社会学",
  "解剖学": "解剖学",
  "组织学": "组织学",
  "病理学": "病理学",
  "病理生理": "病理生理",
  "药理学": "药理学",
  "诊断学": "诊断学",
  "内科学": "内科学",
  "外科学": "外科学",
  "妇产科学": "妇产科学",
  "儿科学": "儿科学",
  "神经病学": "神经病学",
  "精神病学": "精神病学",
  "中医学": "中医学",
  "军事理论": "军事理论",
  "军事思想": "军事思想",
  "军事战略": "军事战略",
  "军事技术": "军事技术",
  "国防科技": "国防科技",
  "军事运筹": "军事运筹",
  "军事史": "军事史",
  "百科全书": "百科全书",
  "辞典": "辞典",
  "地图集": "地图集",
  "科普": "科普",
  "历史科普": "历史科普",
};
export const difficultyNames = { beginner: "入门", intermediate: "进阶", advanced: "高阶" };

export function BookCover({ book, size = "md" }: { book: Book; size?: "sm" | "md" | "lg" }) {
  const palette = ["cover-blue", "cover-green", "cover-orange", "cover-ink", "cover-cyan"][book.id % 5];
  if (book.cover) {
    return (
      <div className={`book-cover-img cover-${size}`} aria-label={`${book.title} 封面`}>
        <img src={book.cover} alt={`${book.title} 封面`} loading="lazy" onError={(e) => { e.currentTarget.style.display = "none"; }} />
      </div>
    );
  }
  return (
    <div className={`book-cover ${palette} cover-${size}`} aria-label={`${book.title} 封面`}>
      <span className="cover-topic">{topicNames[book.topic] || book.topic}</span>
      <strong>{book.title}</strong>
      <span className="cover-author">{book.author || "作者信息待补"}</span>
      <span className="cover-mark" aria-hidden="true"><i /><i /><i /></span>
    </div>
  );
}

export function ScorePanel({ score, compact = false }: { score: BookScore; compact?: boolean }) {
  const items = [
    ["主题匹配", score.topic_score, 30], ["难度匹配", score.difficulty_score, 25],
    ["时间适配", score.time_score, 20], ["偏好匹配", score.preference_score, 20],
  ] as const;
  return (
    <div className={`score-panel ${compact ? "compact" : ""}`}>
      {items.map(([label, value, weight]) => (
        <div className="score-row" key={label}>
          <span>{label}</span>
          <div className="score-meter" aria-label={`${label} ${Math.round(value * 100)} 分`}><motion.i initial={{ scaleX: 0 }} animate={{ scaleX: value }} transition={{ duration: .55 }} /></div>
          <code>{value.toFixed(2)} × {weight}</code>
        </div>
      ))}
      {!compact && <div className="score-total"><span>综合得分</span><strong>{score.total_score.toFixed(1)}</strong></div>}
    </div>
  );
}

export function MemoryChip({ memory, active = false }: { memory: Memory; active?: boolean }) {
  const names: Record<string, string> = { language: "语言偏好", pages: "篇幅限制", prefer_cases: "案例偏好", difficulty: "难度偏好", time: "时间画像" };
  return (
    <div className={`memory-chip ${active ? "is-active" : ""}`}>
      <BrainIcon size={17} weight="duotone" />
      <span><strong>{names[memory.field] || memory.field}</strong><small>{String(memory.value)}</small></span>
      <code>{Math.round(memory.confidence * 100)}%</code>
    </div>
  );
}

export function BookRow({ score, rank, onFeedback, onOpen, onAdd, added = false }: { score: BookScore; rank: number; onFeedback?: () => void; onOpen?: () => void; onAdd?: () => void; added?: boolean }) {
  const reduce = useReducedMotion();
  const book = score.book;
  return (
    <motion.article layout={!reduce} className={`book-row ${rank === 1 ? "is-top" : ""}`}>
      <span className="rank">{String(rank).padStart(2, "0")}</span>
      <BookCover book={book} size="sm" />
      <div className="book-copy">
        <div className="book-meta"><span>{difficultyNames[book.difficulty]}</span><span>{book.pages} 页</span><span>{book.language === "zh" ? "中文" : "英文"}</span></div>
        <h3>{book.title}</h3>
        <p className="author">{book.author || "作者信息待补"}</p>
        <p className="reason">{score.explanation}</p>
        <div className="book-actions">
          <button className="text-button" onClick={onOpen}>查看详情 <ArrowRightIcon /></button>
          {onAdd && <button className={`text-button ${added ? "is-added" : ""}`} onClick={onAdd}>{added ? "已加入路线" : "加入路线"}</button>}
          {onFeedback && <button className="text-button muted" onClick={onFeedback}>反馈不合适</button>}
        </div>
      </div>
      <div className="book-score"><div className="score-orbit" style={{ "--score": `${score.total_score * 3.6}deg` } as CSSProperties}><strong>{score.total_score.toFixed(1)}</strong></div><span>匹配分</span><small><ClockIcon /> 约 {Math.ceil(book.pages / 10)} 天</small></div>
    </motion.article>
  );
}

/**
 * 锁定底层页面的视口滚动器（documentElement 与 body），让浮层无法把滚动手势
 * 传递到背后的列表。浮层自身的滚动容器需保留 overflow + overscroll-behavior:
 * contain，这样只有弹窗内部能滚动。同时补偿消失的滚动条宽度，避免背景内容横
 * 向抖动。React 把 onWheel/onTouchMove 注册为被动监听器，preventDefault 会
 * 失效，stopPropagation 也无法阻止默认滚动，所以必须在 CSS 层直接锁住根滚动
 * 器。用引用计数实现，多个浮层同时打开或 React StrictMode 重复挂载都不会把
 * 页面卡死在 overflow:hidden。
 */
let lockCount = 0;
let savedHtmlOverflow = "";
let savedBodyOverflow = "";
let savedBodyPadRight = "";

export function useScrollLock(active: boolean) {
  useEffect(() => {
    if (!active) return;
    const root = document.documentElement;
    const body = document.body;
    if (lockCount === 0) {
      savedHtmlOverflow = root.style.overflow;
      savedBodyOverflow = body.style.overflow;
      savedBodyPadRight = body.style.paddingRight;
      const scrollbar = window.innerWidth - root.clientWidth;
      if (scrollbar > 0) body.style.paddingRight = `${scrollbar}px`;
      root.style.overflow = "hidden";
      body.style.overflow = "hidden";
    }
    lockCount += 1;
    return () => {
      lockCount -= 1;
      if (lockCount === 0) {
        root.style.overflow = savedHtmlOverflow;
        body.style.overflow = savedBodyOverflow;
        body.style.paddingRight = savedBodyPadRight;
      }
    };
  }, [active]);
}

export function BookDetail({ book, score, onClose }: { book: Book; score?: BookScore; onClose: () => void }) {
  useScrollLock(true);
  return <Portal>
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <motion.section className="detail-drawer" role="dialog" aria-modal="true" aria-label="书籍详情" initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }} onMouseDown={(event) => event.stopPropagation()}>
        <button className="icon-button close" onClick={onClose} aria-label="关闭"><XIcon /></button>
        <BookCover book={book} size="lg" />
        <div className="detail-heading"><span>{topicNames[book.topic]}</span><h2>{book.title}</h2><p>{book.author || "作者信息待补"}</p></div>
        <p className="detail-description">{book.description}</p>
        <div className="detail-stats"><div><strong>{book.pages}</strong><span>页数</span></div><div><strong>{Math.round(book.case_ratio * 100)}%</strong><span>案例占比</span></div><div><strong>{difficultyNames[book.difficulty]}</strong><span>难度</span></div></div>
        <div className="ratio"><i style={{ width: `${book.case_ratio * 100}%` }} /><span>案例 {Math.round(book.case_ratio * 100)}%</span><span>理论 {Math.round(book.theory_ratio * 100)}%</span></div>
        <div className="detail-section"><h3>学习目标</h3><div className="tag-list">{book.goals.map((item) => <span key={item}>{item}</span>)}</div></div>
        <div className="detail-section"><h3>前置知识</h3><p>{book.prerequisites.length ? book.prerequisites.join("、") : "无需前置知识"}</p></div>
        <div className="location-line"><MapPinIcon /><span><strong>{book.location || "馆藏位置待补"}</strong><small>{book.space || "学习空间待匹配"}</small></span></div>
        {score && <ScorePanel score={score} />}
      </motion.section>
    </div>
  </Portal>;
}

export function LoadingRoute() {
  const steps = ["检索相关记忆", "筛选候选书目", "计算匹配评分", "生成路线说明"];
  return <div className="loading-route"><SparkleIcon size={26} weight="duotone" /><h2>馆员正在整理路线</h2><div>{steps.map((step, index) => <motion.span key={step} initial={{ opacity: .25 }} animate={{ opacity: [0.25, 1, .25] }} transition={{ delay: index * .35, duration: 1.4, repeat: Infinity }}><i>{index + 1}</i>{step}</motion.span>)}</div></div>;
}

export function Toast({ message, onDone }: { message: string; onDone: () => void }) {
  return <Portal><AnimatePresence><motion.div className="toast" initial={{ y: 24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 10, opacity: 0 }} onAnimationComplete={() => window.setTimeout(onDone, 2200)}><CheckCircleIcon weight="fill" />{message}</motion.div></AnimatePresence></Portal>;
}

export function EmptyState({ icon = <BookOpenIcon />, title, description }: { icon?: React.ReactNode; title: string; description: string }) {
  return <div className="empty-state"><span>{icon}</span><h3>{title}</h3><p>{description}</p></div>;
}
