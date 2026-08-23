import { useState } from "react";
import { BrainIcon, CheckIcon, PlusIcon, ShieldCheckIcon, UserCircleIcon } from "@phosphor-icons/react";
import { useApp } from "../state";

export default function UsersPage() {
  const { user, users, setUser, addUser } = useApp();
  const [name, setName] = useState("");
  return <div className="users-page page-enter"><section className="page-intro compact"><div><span className="eyebrow">独立学习档案</span><h2>用户管理</h2></div><p>黑客松版本仅在当前浏览器保存用户列表，每个用户通过 ID 使用独立记忆。</p></section><div className="users-layout"><section className="user-list"><div className="section-heading"><h3>本地用户</h3><span>{users.length} 位</span></div>{users.length === 0 ? <div className="empty-users"><UserCircleIcon weight="thin" /><strong>暂无用户</strong><p>创建学习者后，独立档案会显示在这里。</p></div> : users.map((item) => <button key={item.id} className={item.id === user?.id ? "selected" : ""} onClick={() => setUser(item)}><span className="large-avatar">{item.initials}</span><div><strong>{item.name}</strong><small>{item.id}</small></div><span className="user-memory-tag"><BrainIcon />独立记忆</span>{item.id === user?.id && <CheckIcon className="selected-check" weight="bold" />}</button>)}</section><aside className="new-user-panel"><span className="feedback-icon"><UserCircleIcon /></span><h2>新增学习者</h2><p>系统会自动生成安全用户 ID，不需要手动输入。</p><label>用户昵称<input value={name} onChange={(event) => setName(event.target.value)} placeholder="输入用户昵称" /></label><button className="primary-action" onClick={() => { addUser(name); setName(""); }}><PlusIcon />创建并切换</button><div className="control-note"><ShieldCheckIcon /><p><strong>本地用户不等于账号系统</strong><span>删除浏览器记录不会自动清理后端记忆。</span></p></div></aside></div></div>;
}
