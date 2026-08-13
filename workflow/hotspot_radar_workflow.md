# 工作流核心逻辑

## 概述

热点情报雷达工作流部署在 Coze 扣子编程平台（code.coze.cn），通过 Web 服务 API 对外暴露。支持同步/异步两种调用方式，当前使用异步端点 `/async_run`（工作流执行时间约 5-10 分钟，超出同步端点超时限制）。

## 部署信息

| 配置项 | 值 |
|--------|-----|
| 部署平台 | Coze 扣子编程 (code.coze.cn) |
| 服务地址 | `https://6ds42m4p2p.coze.site` |
| 异步执行端点 | `POST /async_run` |
| 同步执行端点 | `POST /run`（备用，可能超时） |
| 任务状态查询 | `GET /task/{task_id}` |
| 参数查询 | `GET /graph_parameter` |
| 鉴权方式 | Bearer Token（JWT，部署后生成，永久有效） |

## 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `keywords` | Array[String] | 否 | `["科技热点 最新", "AI人工智能 突破", "金融市场 行情"]` | 搜索关键词列表 |
| `recipient_email` | String | 否 | 用户邮箱 | 报告接收邮箱 |
| `trigger_type` | String | 否 | `"auto"` | 触发类型：`manual`（手动）/ `auto`（定时） |

## 输出参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `report_html` | String | 生成的 HTML 分析报告内容 |
| `email_status` | String | 邮件发送状态（sent/failed） |
| `total_raw_count` | Integer | 原始采集总条数 |
| `cluster_count` | Integer | 去重聚类后的独立事件数 |
| `s_a_count` | Integer | S/A 级高价值热点数量 |

## 工作流节点

```
┌─────────────────────────────────────────────────────────────┐
│                        工作流执行流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① 接收输入参数                                              │
│     └─ keywords, recipient_email, trigger_type              │
│                         ↓                                   │
│  ② 多源数据采集                                               │
│     ├─ 搜索渠道 A：关键词检索 → 提取标题/摘要/来源/链接         │
│     ├─ 搜索渠道 B：关键词检索 → 提取标题/摘要/来源/链接         │
│     └─ 搜索渠道 C：关键词检索 → 提取标题/摘要/来源/链接         │
│                         ↓                                   │
│  ③ 数据清洗 & 去重聚类                                        │
│     ├─ 去除重复/低质/无关条目                                  │
│     └─ 按语义相似度合并为独立事件簇                              │
│                         ↓                                   │
│  ④ AI 分析评估                                                │
│     ├─ 价值评分：S / A / B / C 四级                           │
│     ├─ 可信度评估：高 / 中 / 低                                │
│     ├─ 关键信息提取 & 摘要生成                                  │
│     └─ 风险提示（来源不明/未交叉验证的条目）                      │
│                         ↓                                   │
│  ⑤ 生成结构化 HTML 报告                                      │
│     ├─ 标题 + 时间 + 摘要                                     │
│     ├─ S/A 级热点详情（含来源链接）                              │
│     ├─ B/C 级热点简表                                        │
│     └─ 底部标注：AI 生成，仅供参考                               │
│                         ↓                                   │
│  ⑥ 邮件推送                                                  │
│     └─ 将 HTML 报告发送到 recipient_email                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 异步调用示例

```bash
curl -X POST 'https://6ds42m4p2p.coze.site/async_run' \
  -H 'Authorization: Bearer <YOUR_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "keywords": ["科技", "AI", "金融"],
    "recipient_email": "your@email.com",
    "trigger_type": "auto"
  }'
```

响应示例：
```json
{
  "task_id": "0f5c5e2cae7249ed81596966e8cdb1f8",
  "status": "pending",
  "created_at": "2026-08-13T11:55:00+08:00",
  "deadline": "2026-08-13T12:25:00+08:00"
}
```

## 注意事项

- 重新部署工作流后，旧的 API Token 会失效，需要重新创建 Token 并更新所有引用
- 工作流执行时间较长（5-10 分钟），建议使用异步端点
- 插件中 `keywords` 参数必须配置为 Array 类型，请求方式选择 Body
