import { useEffect, useState } from "react";
import { BookOpenIcon, FunnelIcon, MagnifyingGlassIcon, SquaresFourIcon, RowsIcon, XIcon } from "@phosphor-icons/react";
import { BookCover, BookDetail, difficultyNames, EmptyState, Portal, topicNames, useScrollLock } from "../components";
import { getBook, searchBooks } from "../api";
import type { Book } from "../types";

export default function BooksPage() {
  const [filters, setFilters] = useState({ query: "", topic: "", difficulty: "", language: "", max_pages: "" });
  const [books, setBooks] = useState<Book[]>([]);
  const [selected, setSelected] = useState<Book | null>(null);
  const [grid, setGrid] = useState(false);
  const [mobileFilters, setMobileFilters] = useState(false);
  const [error, setError] = useState("");
  useScrollLock(mobileFilters || !!selected);
  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(() => searchBooks(filters).then((items) => { if (active) { setBooks(items); setError(""); } }).catch(() => { if (active) setError("书目服务暂时不可用，请检查后端连接。"); }), 180);
    return () => { active = false; window.clearTimeout(timer); };
  }, [filters]);
  const reset = () => setFilters({ query: "", topic: "", difficulty: "", language: "", max_pages: "" });
  async function openBook(book: Book) { try { setSelected(await getBook(book.id) || book); } catch { setError("无法读取书籍详情，请稍后重试。"); } }
  const filterFields = <><label>学习主题<select value={filters.topic} onChange={(event) => setFilters({ ...filters, topic: event.target.value })}><option value="">全部主题</option>{Object.entries(topicNames).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label><label>难度<select value={filters.difficulty} onChange={(event) => setFilters({ ...filters, difficulty: event.target.value })}><option value="">全部难度</option>{Object.entries(difficultyNames).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label><label>语言<select value={filters.language} onChange={(event) => setFilters({ ...filters, language: event.target.value })}><option value="">全部语言</option><option value="zh">中文</option><option value="en">英文</option></select></label><label>最大页数<input type="number" min="100" step="50" value={filters.max_pages} onChange={(event) => setFilters({ ...filters, max_pages: event.target.value })} placeholder="不限" /></label><button className="reset-filter" onClick={reset}>清除全部</button></>;
  return <div className="books-page page-enter">
    <section className="library-heading"><div><span className="eyebrow">结构化学习书库</span><h2>找到适合当下的书。</h2><p>按主题、难度、语言与篇幅缩小范围，再查看每本书的学习属性。</p></div><div className="search-box"><MagnifyingGlassIcon /><input value={filters.query} onChange={(event) => setFilters({ ...filters, query: event.target.value })} placeholder="搜索标题、关键词或简介" /><button className="mobile-filter-button" onClick={() => setMobileFilters(true)}><FunnelIcon /></button></div></section>
    {error && <p className="inline-error" role="alert">{error}</p>}
    <div className="library-layout"><aside className="filter-panel"><div><FunnelIcon /><strong>筛选条件</strong></div>{filterFields}</aside><section className="book-results"><div className="results-toolbar"><span>找到 <strong>{books.length}</strong> 本书</span><div><button className={!grid ? "active" : ""} onClick={() => setGrid(false)} aria-label="列表视图"><RowsIcon /></button><button className={grid ? "active" : ""} onClick={() => setGrid(true)} aria-label="网格视图"><SquaresFourIcon /></button></div></div>{books.length ? <div className={grid ? "catalog-grid" : "catalog-list"}>{books.map((book) => <button key={book.id} className="catalog-item" onClick={() => openBook(book)}><BookCover book={book} size={grid ? "md" : "sm"} /><div><div className="book-meta"><span>{difficultyNames[book.difficulty]}</span><span>{book.pages} 页</span><span>{book.language === "zh" ? "中文" : "英文"}</span></div><h3>{book.title}</h3><p className="author">{book.author || "作者信息待补"}</p><p>{book.description}</p><div className="ratio-mini"><i style={{ width: `${book.case_ratio * 100}%` }} /><span>案例 {Math.round(book.case_ratio * 100)}%</span></div></div><BookOpenIcon className="open-icon" /></button>)}</div> : <EmptyState title="没有找到匹配书目" description="尝试减少筛选条件或使用更宽泛的关键词。" />}</section></div>
    {mobileFilters && <Portal><div className="modal-backdrop"><section className="mobile-filter-sheet"><button className="icon-button close" onClick={() => setMobileFilters(false)}><XIcon /></button><h2>筛选书目</h2>{filterFields}<button className="primary-action" onClick={() => setMobileFilters(false)}>查看 {books.length} 本结果</button></section></div></Portal>}
    {selected && <BookDetail book={selected} onClose={() => setSelected(null)} />}
  </div>;
}
