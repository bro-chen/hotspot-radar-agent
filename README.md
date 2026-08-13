# 热点情报雷达 Agent

基于 Coze 平台搭建的多源热点自动采集与分析智能体，覆盖科技、AI、金融三大领域，支持每日自动触发和邮件推送。

---

## 1. 在线体验

**直接体验已发布的 Agent：** [https://www.coze.cn/s/1ky7eCMJtk0/](https://www.coze.cn/s/1ky7eCMJtk0/)

在对话框输入"帮我采集今天的热点"+"发送到邮箱XXXXX"即可触发，完成后报告将自动发送到你的邮箱。
一般会有5-10分钟的运行时间，请耐心等待~

---

## 2. 项目简介

### 解决什么问题

互联网热点信息分散在数十个平台，手动浏览、筛选、分析耗时且容易遗漏。本 Agent 通过自动化工作流，将多源信息采集 → 去重聚类 → AI 分析评估 → 结构化报告生成 → 邮件推送全流程串联，每天自动为你生成一份高质量的热点分析报告。

### 核心工作流

```
用户触发（手动/定时）
      ↓
多源数据采集（搜索 API + 公开数据源）
      ↓
数据清洗 & 去重聚类（按事件合并相似信息）
      ↓
AI 分析评估（价值评分 S/A/B/C + 可信度分析 + 风险提示）
      ↓
结构化 HTML 报告生成
      ↓
邮件自动推送
```

### 使用的 AI 能力

- **多源信息融合**：自动从多个搜索渠道采集并聚合原始数据
- **智能去重聚类**：通过语义相似度将分散来源归并为独立事件
- **价值分级评估**：基于影响范围、时效性、行业关联度进行 S/A/B/C 四级评分
- **可信度分析**：交叉验证信息来源，标注可信度等级和风险提示
- **结构化报告生成**：生成可阅读的 HTML 格式分析报告

---

## 3. 真实案例

> 📸 以下为实际运行截图，展示从触发到收到邮件的完整过程。
> 
--发送到默认邮箱
<img width="2879" height="1706" alt="y1" src="https://github.com/user-attachments/assets/759e66c7-65de-4271-a1ed-a8e5117cdcc3" />
<img width="2879" height="1706" alt="y3" src="https://github.com/user-attachments/assets/5704c4b7-abc4-4517-b7fa-7180f4c998c2" />

--发送到指定邮箱
<img width="2879" height="1706" alt="y2" src="https://github.com/user-attachments/assets/6deec57c-fcd4-4008-988c-3a49089979c1" />
<img width="2879" height="1706" alt="y4" src="https://github.com/user-attachments/assets/624d9552-3882-4c62-8d26-8a940e8a5e50" />


---

## 4. 项目文件说明

```
hotspot-radar-github/
├── README.md                          # 本文件
├── workflow/
│   └── hotspot_radar_workflow.md      # 工作流核心逻辑说明（数据采集→分析→报告→邮件）
├── scheduled-trigger/
│   └── hotspot_daily_trigger.py       # 定时触发脚本（CodeAct，每天 8:00 自动调用工作流 API）
├── config/
│   └── hotspot_config_template.json   # 配置文件模板（需填入自己的 API Token）
└── docs/
    └── architecture.md                # 系统架构说明
```

### 关键文件

| 文件 | 说明 |
|------|------|
| `workflow/hotspot_radar_workflow.md` | 工作流的设计逻辑、节点说明、参数定义 |
| `scheduled-trigger/hotspot_daily_trigger.py` | 定时触发脚本，通过 Calendar + CodeAct 每天自动执行 |
| `config/hotspot_config_template.json` | 配置模板，部署时复制为 `hotspot_config.json` 并填入 Token |
| `docs/architecture.md` | 完整系统架构图和各组件说明 |

---

## 5. 当前局限 & 风控措施

### 已知局限

| 局限 | 说明 | 改进方向 |
|------|------|---------|
| 采集源有限 | 当前依赖搜索 API，无法直接抓取微信公众号、抖音等封闭平台内容 | 接入更多数据源 API 或 RSS |
| 执行耗时 | 工作流完整执行约 5-10 分钟（含多源采集+AI 分析） | 并行化采集节点、使用更快的模型 |
| 语言限制 | 目前仅支持中文热点 | 可配置多语言关键词扩展 |
| 推送渠道 | 当前仅支持邮件 | 后续扩展企业微信、飞书等 |

### 风控措施

| 风险 | 控制手段 |
|------|---------|
| **信息虚假/编造** | 所有结论必须标注信息来源链接；AI 分析结论与事实明确区分；可信度低的条目自动标注风险提示 |
| **误判/过度解读** | 价值评分基于多维指标综合评估，不做单一指标判断；S/A 级信息需交叉验证才标记为高可信 |
| **信息安全** | API Token 仅存在于配置文件中，不硬编码在代码里；不采集或存储用户个人敏感信息 |
| **发布管控** | 报告通过邮件私发，不在公开平台发布；报告内注明"AI 生成，仅供参考" |

---

## 技术栈

- **平台**：[Coze](https://www.coze.cn)（扣子）
- **工作流引擎**：Coze Workflow（扣子编程部署）
- **定时调度**：CodeAct + Calendar 定时触发
- **AI 模型**：豆包 1.8 深度思考
- **报告格式**：HTML（邮件内嵌）
- **开发语言**：Python

---

## 许可证

MIT License
