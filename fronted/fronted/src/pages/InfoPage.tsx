import { ArrowLeftIcon, BookOpenTextIcon, LifebuoyIcon, LockKeyIcon, SparkleIcon, UsersThreeIcon } from "@phosphor-icons/react";
import { useNavigate } from "react-router-dom";

type InfoKind = "about" | "features" | "help" | "privacy" | "terms";
const illustration: Record<InfoKind, string> = {
  about: "/assets/zhiyu-library-path.png",
  features: "/assets/learning-route-editorial.png",
  help: "/assets/memory-archive-editorial.png",
  privacy: "/assets/feedback-transform-editorial.png",
  terms: "/assets/zhiyu-library-path.png",
};

const content: Record<InfoKind, { icon: typeof SparkleIcon; eyebrow: string; title: string; intro: string; sections: [string, string][] }> = {
  about: {
    icon: UsersThreeIcon, eyebrow: "ABOUT LINGXI", title: "关于我们",
    intro: "灵犀是一位面向学习者的 AI 图书馆馆员，帮助用户从书库、记忆与反馈中找到更适合自己的阅读路径。",
    sections: [["我们的愿景", "把分散的知识整理成可理解、可行动、可持续生长的个人学习路线。"], ["我们正在做的事", "我们关注真实的学习场景：如何找到下一本书，如何记住读过的内容，以及如何让每一次反馈都成为下一次推荐的依据。"],["背景","来自大连理工大学第二届黑客松的学习项目，融合教育研究与技术，贴近真实学习场景。"]],
  },
  features: {
    icon: SparkleIcon, eyebrow: "FEATURES", title: "功能介绍",
    intro: "从发现一本书开始，到形成一条可执行的路线，灵犀把检索、推荐、记忆和复盘放在同一个工作台里。",
    sections: [["智能推荐", "结合你的目标、兴趣、时间与已有记忆，生成有依据的书目建议。"], ["路线规划", "把推荐结果组织为清晰的阅读顺序，并提供阶段性的阅读节奏。"], ["记忆反馈", "记录你的反馈与偏好，在后续相似任务中持续调整推荐理由。"], ["结果追踪", "查看推荐过程中的检索依据、处理步骤和最终结果，帮助你理解系统如何形成判断。"]],
  },
  help: {
    icon: LifebuoyIcon, eyebrow: "HELP CENTER", title: "帮助中心",
    intro: "本中心说明灵犀的主要使用流程、推荐结果的理解方式以及常见问题的处理方法。",
    sections: [["如何开始使用", "进入推荐工作台后，请先选择学习目标、主题方向和可投入的时间，再补充当前的阅读需求。信息越具体，系统越容易生成符合实际情况的阅读建议。"], ["如何获得更好的推荐", "建议同时填写已读书目、感兴趣的方向和明确的限制条件。你也可以在结果页提交反馈，系统会将反馈作为后续相似任务的参考依据。"], ["如何理解推荐结果", "推荐结果由主题匹配、阅读目标、时间安排和已有记忆等因素共同影响。结果中的解释用于说明推荐依据，不代表对书籍价值或学习效果的绝对判断。"], ["联系我们", "如果页面出现加载失败、数据异常或功能无响应，请先刷新页面并确认网络连接；问题仍未解决时，请记录页面、操作步骤和错误提示，发送至我们的项目团队邮箱 "]],
  },
  privacy: {
    icon: LockKeyIcon, eyebrow: "PRIVACY", title: "隐私政策",
    intro: "本政策说明灵犀在提供书目推荐、阅读路线和记忆反馈服务过程中，如何收集、使用、保存和保护相关信息。",
    sections: [["信息收集", "为提供基本功能，系统可能处理用户主动填写的学习目标、主题偏好、阅读时间、书目反馈以及用户在应用中的操作记录。我们仅收集实现推荐、路线规划和反馈功能所必要的信息。"], ["使用目的", "收集的信息用于生成个性化阅读路线、提供书目检索与推荐、分析反馈对推荐结果的影响、改进产品功能并提升系统稳定性。未经说明，信息不会被用于与本项目无关的商业用途。"], ["信息保存与管理", "相关信息将按照项目实际运行环境进行保存。用户可以通过用户管理和记忆中心查看、调整或清理部分个人偏好与记忆内容；如需删除无法在页面操作的数据，可联系项目团队处理。"], ["安全保护", "我们会采取合理的技术和管理措施保护信息安全，包括访问权限控制、必要的传输与存储保护以及异常操作监测。尽管如此，互联网环境不存在绝对安全的存储或传输方式。"], ["第三方服务", "如系统运行依赖模型服务、数据接口或其他第三方基础设施，我们会在必要范围内传递完成服务所需的信息，并要求相关服务遵守适用的安全与隐私要求。"], ["政策更新与联系我们", "我们可能根据功能变化、法律要求或安全实践更新本政策。更新内容将在本页面公布；如对隐私处理有疑问，请通过项目公布的联系渠道与我们沟通。"]],
  },
  terms: {
    icon: BookOpenTextIcon, eyebrow: "TERMS OF USE", title: "用户协议",
    intro: "本协议约定用户使用灵犀相关功能时的权利、义务和责任。使用本服务即表示用户已阅读、理解并同意本协议。",
    sections: [["接受条款", "用户开始使用灵犀，即视为接受本协议及其后续更新内容。如用户不同意相关条款，应停止使用本服务。"], ["服务内容", "灵犀提供书目检索、个性化推荐、阅读路线规划、记忆记录和结果解释等学习辅助功能。具体功能以当前页面实际提供的内容为准。"], ["用户义务", "用户应遵守法律法规和平台规则，不得上传违法、有害、侵权或含有恶意代码的内容，不得利用本服务实施攻击、干扰系统运行或侵犯他人合法权益。"], ["内容与结果说明", "用户提交的内容应由用户自行承担相应责任。AI 生成的推荐、解释和路线仅作为学习辅助信息，不构成医疗、法律、财务或其他专业意见，用户应结合可靠资料进行独立判断。"], ["服务变更与中断", "项目团队可根据产品迭代、维护、安全或运营需要调整、暂停部分功能。因网络故障、第三方服务异常或其他不可归责于项目团队的原因造成的服务中断，项目团队将在合理范围内协助处理。"], ["协议更新与责任限制", "本协议可能因服务变化或法律要求进行更新，更新后将通过本页面公示。对于用户违反本协议造成的损失，项目团队有权采取限制访问、删除相关内容等措施，并依法追究相应责任。"]],
  },
};

export default function InfoPage({ kind }: { kind: InfoKind }) {
  const navigate = useNavigate();
  const item = content[kind];
  const Icon = item.icon;
  return <div className="info-page page-enter">
    <button className="back-link" onClick={() => navigate(-1)}><ArrowLeftIcon /> 返回上一页</button>
    <section className="info-hero">
      <img className="info-illustration" src={illustration[kind]} alt="" aria-hidden="true" />
      <div className="info-icon"><Icon size={28} weight="duotone" /></div>
      <span className="eyebrow">{item.eyebrow}</span>
      <h2>{item.title}</h2>
      <p>{item.intro}</p>
    </section>
    <section className={`info-sections info-sections-${kind}`}>
      {item.sections.map(([title, text]) => <article key={title}><h3>{title}</h3><p>{text}</p></article>)}
    </section>
  </div>;
}
