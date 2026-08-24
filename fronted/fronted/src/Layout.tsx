import { useEffect, useState, type ReactNode } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { BooksIcon, BrainIcon, CpuIcon, MoonIcon, PathIcon, PlusIcon, SparkleIcon, SunIcon, UserCircleIcon } from "@phosphor-icons/react";
import { useApp } from "./state";

const nav = [
  ["/recommend", "推荐", SparkleIcon], ["/memories", "记忆", BrainIcon],
  ["/books", "书库", BooksIcon], ["/route", "路线", PathIcon], ["/trace", "轨迹", CpuIcon], ["/users", "用户", UserCircleIcon],
] as const;

const titles: Record<string, string> = { recommend: "推荐工作台", result: "学习路线", route: "我的路线", memories: "记忆中心", books: "书目检索", trace: "Agent 轨迹", users: "用户管理", about: "关于我们", features: "功能介绍", help: "帮助中心", privacy: "隐私政策", terms: "用户协议" };
const footerNav = [
  ["/about", "关于我们"],
  ["/features", "功能介绍"],
  ["/help", "帮助中心"],
  ["/privacy", "隐私政策"],
  ["/terms", "用户协议"],
] as const;

export default function Layout({ children }: { children: ReactNode }) {
  const { user, users, setUser, dark, setDark } = useApp();
  const [showUsers, setShowUsers] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const section = location.pathname.split("/")[1] || "recommend";

  useEffect(() => { window.scrollTo({ top: 0, behavior: "instant" }); }, [location.pathname]);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate("/recommend")} aria-label="返回推荐工作台"><span className="brand-mark"><i /><i /></span><strong>灵犀</strong><small>AI 馆员</small></button>
        <nav>{nav.map(([path, label, Icon]) => <NavLink key={path} to={path} className={({ isActive }) => isActive ? "active" : ""}><Icon size={21} weight="duotone" /><span>{label}</span></NavLink>)}</nav>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div><span className="crumb">灵犀 / {titles[section]}</span><h1>{titles[section]}</h1></div>
          <div className="top-actions">
            <button className="icon-button" onClick={() => setDark(!dark)} aria-label={dark ? "切换浅色模式" : "切换深色模式"}>{dark ? <SunIcon /> : <MoonIcon />}</button>
            <div className="user-switcher">
              <button onClick={() => setShowUsers(!showUsers)}><span>{user?.initials ?? "-"}</span><strong>{user?.name ?? "未设置用户"}</strong></button>
              {showUsers && <div className="user-menu">{users.map((item) => <button key={item.id} onClick={() => { setUser(item); setShowUsers(false); }} className={item.id === user?.id ? "selected" : ""}><span>{item.initials}</span><div><strong>{item.name}</strong><small>{item.id}</small></div></button>)}<button onClick={() => { navigate("/users"); setShowUsers(false); }}><PlusIcon /><strong>管理用户</strong></button></div>}
            </div>
          </div>
        </header>
        <main id="main-content">{children}</main>
        <footer className="site-footer">
          <div className="site-footer-inner">
            <span className="site-footer-brand">灵犀 · AI 馆员</span>
            <nav aria-label="辅助导航">
              {footerNav.map(([path, label]) => <NavLink key={path} to={path}>{label}</NavLink>)}
            </nav>
            <span className="site-footer-note">让每一次阅读，都更接近真正的理解</span>
          </div>
        </footer>
      </div>
      <nav className="mobile-nav">{nav.slice(0, 5).map(([path, label, Icon]) => <NavLink key={path} to={path}><Icon /><span>{label}</span></NavLink>)}</nav>
    </div>
  );
}
