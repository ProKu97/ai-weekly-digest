# 🤖 AI Weekly Digest

> 每周一自动抓取 Hacker News 重磅 AI 突破，推送到微信

## 功能

- 🕵️ 自动抓取 Hacker News Top 50 条目
- 🎯 智能筛选 AI 相关重磅突破（关键词 + 影响分数）
- 📝 生成简洁摘要（每条 2-3 句话）
- 📲 通过 [Server酱](https://sct.ftqq.com/) 推送到微信
- ⏰ 每周一 09:10 (北京时间) 自动执行

## 推送格式示例

```
🤖 AI Weekly Digest
📅 2026-03-21 ~ 2026-03-28
━━━━━━━━━━━━━━━━━━

🔴 **[公司] 发布 [产品]: 新功能能 [功能描述]**
   来源: ...
   👍200 💬50 | url

🟠 **[公司] 发布...**
   ...
━━━━━━━━━━━━━━━━━━
🤖 共 8 条重磅突破 | 由 AI 自动筛选
📌 来源: Hacker News
```

## 筛选逻辑

只选重磅突破，普通更新不写：

- ✅ AI 操控电脑、无限上下文、Agent 自主能力
- ✅ SOTA 性能突破、新型多模态能力
- ✅ 开源重磅模型发布
- ❌ 普通 API 更新、Hiring、教程、论文解读

## 配置步骤

### 1. Fork 本仓库

### 2. 配置 Server酱

1. 访问 [sct.ftqq.com](https://sct.ftqq.com/)，扫码登录
2. 点击「发送消息」→ 获取 `SendKey`
3. 在 GitHub 仓库 → Settings → Secrets → Actions
   新建 `SERVERCHAN_KEY`，填入你的 SendKey

### 3. 手动测试（可选）

在 GitHub 仓库页面：
- 点击 **Actions** 标签
- 选择 **AI Weekly Digest** workflow
- 点击 **Run workflow** 手动触发

### 4. 推送效果

确认微信收到推送消息 🎉

## 文件说明

```
ai-weekly-digest/
├── main.py                 # 主脚本（抓取 + 筛选 + 推送）
├── requirements.txt        # 依赖（仅用 Python 内置库）
├── .github/
│   └── workflows/
│       └── weekly-digest.yml  # GitHub Actions 配置
└── README.md
```

## 技术细节

- **新闻源**: Hacker News API (https://hacker-news.firebaseio.com)
- **语言**: Python 3（仅用内置库，无第三方依赖）
- **推送**: Server酱 免费版 (sct.ftqq.com)
- **调度**: GitHub Actions (每周一 09:10 UTC+8)
