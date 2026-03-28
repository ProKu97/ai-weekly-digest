#!/usr/bin/env python3
"""
AI Weekly Digest - 每周 AI 重磅突破自动推送
自动抓取 + 筛选 + Server酱推送
"""

import urllib.request
import urllib.parse
import json
import re
import html
from datetime import datetime, timedelta

# ==================== 配置 ====================
import os
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")  # 从环境变量读取
MAX_ITEMS = 50       # 最多抓取 HN 条目数

# 高权重关键词（重磅突破）
HIGH_IMPACT_KEYWORDS = [
    "control computer", "control pc", "operating computer",
    "unlimited context", "infinite context", "1m context", "10m context",
    "autonomous agent", "ai agent", "agentic", "agent ai",
    "breakthrough", "revolutionary", "state of the art", "sota",
    "multimodal", "multimodality", "reasoning model",
    "artificial general intelligence", "agi",
    "world model", "physical ai", "robotics", "embodied ai",
    "open source", "open-source", "open weights",
    "o1", "o3", "o4", "gpt-5", "claude 4", "gemini 2",
    "human-level", "superhuman", "outperform", "surpass",
    "code generation", "protein folding", "scientific discovery",
    "natural language to sql", "text to video", "text-to-video",
    "text to image", "text-to-image", "real-time", "real time",
]

# 中权重关键词（重要更新）
MEDIUM_IMPACT_KEYWORDS = [
    "launch", "release", "announce", "new model", "new api",
    "update", "upgrade", "improve", "performance", "benchmark",
    "fine-tune", "finetune", "quantization", "pruning", "distillation",
    "api", "sdk", "framework", "library", "tool", "dataset",
]

# 低权重关键词（普通更新，过滤掉）
LOW_IMPACT_KEYWORDS = [
    "hiring", "job", "career", "salary", "intern", "position",
    "tutorial", "course", "lecture", "workshop", "bootcamp",
    "dataset release", "paper", "arxiv", " preprint",
    "opinion", "essay", "blog post", "commentary",
    "crypto", "nft", "blockchain", "web3",
]


def fetch_hackernews_top():
    """从 Hacker News API 抓取最新条目"""
    items = []
    # 抓取 Top Stories ID
    try:
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": "Mozilla/5.0 AI-Weekly-Digest/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ids = json.loads(resp.read())
        # 取前 MAX_ITEMS 条
        ids = ids[:MAX_ITEMS]

        for story_id in ids:
            try:
                req = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    headers={"User-Agent": "Mozilla/5.0 AI-Weekly-Digest/1.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    item = json.loads(resp.read())
                items.append(item)
            except Exception:
                continue
    except Exception as e:
        print(f"HN API 抓取失败: {e}")
    return items


def calculate_impact_score(item):
    """计算条目影响分数"""
    text = ""
    if item.get("title"):
        text += item["title"].lower()
    if item.get("text"):
        text += " " + item["text"].lower()
    if item.get("url"):
        text += " " + item["url"].lower()

    score = 0
    score += 5 * sum(1 for kw in HIGH_IMPACT_KEYWORDS if kw in text)
    score += 2 * sum(1 for kw in MEDIUM_IMPACT_KEYWORDS if kw in text)
    score -= 10 * sum(1 for kw in LOW_IMPACT_KEYWORDS if kw in text)

    # HN 投票加成
    score += min((item.get("score", 0) or 0) * 0.05, 20)

    # 评论数加成
    score += min((item.get("descendants", 0) or 0) * 0.03, 15)

    return max(score, 0)


def is_ai_related(item):
    """判断是否与 AI 相关"""
    text = ""
    if item.get("title"):
        text += item["title"].lower() + " "
    if item.get("text"):
        text += item["text"].lower()

    ai_keywords = [
        "ai", "artificial intelligence", "machine learning", "ml",
        "deep learning", "neural network", "llm", "language model",
        "gpt", "claude", "gemini", "chatgpt", "openai", "anthropic",
        "google deepmind", "mistral", "llama", "mistral", "qwen",
        "diffusion", "transformer", "attention", "reinforcement",
        "nlp", "cv", "computer vision", "stable diffusion", "midjourney",
        "autonomous", "agent", "copilot", "cursor", "replit",
        "runway", "sora", "pika", "kling", "warp", "devin",
        "hugging face", "together ai", "perplexity", "cohere",
        "mistral ai", "meta ai", "microsoft ai", "apple intelligence",
    ]

    return any(kw in text for kw in ai_keywords)


def summarize_item(item):
    """生成单条摘要"""
    title = html.unescape(item.get("title", ""))
    score = item.get("score", 0) or 0
    url = item.get("url", "")
   hn_url = f"https://news.ycombinator.com/item?id={item['id']}"
    comments = item.get("descendants", 0) or 0

    # 清理标题
    title_clean = re.sub(r'^\[\d+\]\s*', '', title)

    # 生成描述
    if item.get("text"):
        desc = html.unescape(item["text"])
        desc = re.sub(r'<[^>]+>', '', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        if len(desc) > 200:
            desc = desc[:200].rsplit(' ', 1)[0] + "..."
    elif url:
        desc = f"来源: {url[:60]}..." if len(url) > 60 else f"来源: {url}"
    else:
        desc = f"HN讨论: {hn_url}"

    return {
        "title": title_clean,
        "score": score,
        "comments": comments,
        "url": url or hn_url,
        "hn_url": hn_url,
        "desc": desc
    }


def format_digest(items):
    """格式化推送内容"""
    if not items:
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    lines = [
        f"🤖 AI Weekly Digest",
        f"📅 {week_start} ~ {today}",
        f"━━━━━━━━━━━━━━━━━━",
        "",
    ]

    emoji_map = ["🔴", "🟠", "🟡", "🔵", "🟢", "🟣", "⚫", "🟤"]

    for i, item in enumerate(items):
        emoji = emoji_map[i % len(emoji_map)]
        lines.append(f"{emoji} **{item['title']}**")
        lines.append(f"   {item['desc']}")
        lines.append(f"   👍{item['score']} 💬{item['comments']} | {item['url']}")
        lines.append("")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━",
        f"🤖 共 {len(items)} 条重磅突破 | 由 AI 自动筛选",
        "📌 来源: Hacker News",
        f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ])

    return "\n".join(lines)


def push_to_wechat(content):
    """通过 Server酱 推送"""
    if not content:
        print("没有内容可推送")
        return False

    if not SERVERCHAN_KEY:
        print("⚠️ 未配置 SERVERCHAN_KEY，跳过推送")
        print("请在 GitHub Secrets 中配置 SERVERCHAN_KEY")
        print("\n--- 预览内容 ---")
        print(content)
        return False

    url = f"https://sct.ftqq.com/{SERVERCHAN_KEY}.send"
    data = urllib.parse.urlencode({
        "title": "🤖 AI Weekly Digest - 本周重磅突破",
        "desp": content,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("code") == 0 or result.get("errno") == 0:
                print("✅ 推送成功！")
                return True
            else:
                print(f"❌ 推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 推送出错: {e}")
        return False


def main():
    print("🚀 开始抓取 AI Weekly Digest...")
    print("=" * 40)

    # 1. 抓取 HN 数据
    items = fetch_hackernews_top()
    print(f"📥 抓取到 {len(items)} 条 HN 条目")

    # 2. 筛选 AI 相关 + 计算影响分数
    ai_items = []
    for item in items:
        if is_ai_related(item):
            item["_impact_score"] = calculate_impact_score(item)
            ai_items.append(item)

    print(f"🎯 其中 {len(ai_items)} 条与 AI 相关")

    # 3. 按影响分数排序，取前 8 条
    ai_items.sort(key=lambda x: x["_impact_score"], reverse=True)
    top_items = ai_items[:8]

    # 4. 生成摘要
    summaries = [summarize_item(item) for item in top_items]
    print(f"📝 筛选出 {len(summaries)} 条重磅突破")

    # 5. 格式化
    digest = format_digest(summaries)
    print("\n" + digest)

    # 6. 推送
    push_to_wechat(digest)

    print("\n✅ 执行完成！")


if __name__ == "__main__":
    main()
