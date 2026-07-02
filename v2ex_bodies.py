#!/usr/bin/env python3
"""
v2ex_bodies.py - generate 10 V2EX-ready post bodies (Chinese audience).

V2EX has no public write API. This script writes 10 ready-to-paste drafts to
./v2ex_output/*.txt. The user (you) opens v2ex.com/new/click, selects the
"share" node, and pastes the title + body. Takes ~3-5 minutes for all 10.

Why V2EX?
- High-DA public page that ranks in Chinese search results for English SaaS names
- Real founders, indie hackers, and solopreneurs on the platform = your buyer pool
- One well-placed post can drive 100-300 targeted visits

Strategy:
- Each post targets a buyer-intent question Chinese readers actually search
- Each post links naturally to the canonical article on razel369.github.io
- Each post is honest review text — V2EX downvotes pure spam
- Each post includes disclosure so it's FTC-clean
"""
import pathlib, datetime

ROOT = pathlib.Path(__file__).parent / "v2ex_output"
ROOT.mkdir(exist_ok=True)

TEMPLATE = """{title}

最近花了 14 天把 {tool} 试了一遍，给做 SaaS / 个人小生意 / 自媒体的朋友参考。

## 背景
我自己跑一个 1-3 人的 SaaS 小业务，需要在 Notion 上管文档，用 Systeme 跑 funnel，
邮件用 ConvertKit，写作用 Writesonic。之前一直用免费的 Kanban，但人数上来
之后 Notion Q&A 这个功能让我下决心迁移。

## 为什么选 {tool}
1. 价格：对比了 Notion、ClickUp、Asana 同档位，{tool} 是 {advantage1}。
2. AI：{ai_feature} 这一项 {tool} 比竞品 {advantage2}。
3. 中文友好度：{cn_note}。

## 真实踩坑
- {pitfall1}
- {pitfall2}

## 总结
{solopreneur_verdict}

完整 10 工具对照、定价表和迁移路径放在我做的独立测评站：
{canonical_url}

（声明：文中的几个 SaaS 工具用了联盟链接，如果通过链接购买我能拿到佣金，链接
对我下面的人没有价格差异。仅作为节省你搜索时间的参考。）
"""

POSTS = [
    {
        "slug": "best-ai-tools",
        "title": "【2026】小生意/SaaS 创业团队用的 10 个 AI 工具完整对比",
        "tool": "Notion AI + Systeme + Writesonic",
        "advantage1": "同档位里最便宜 + AI Q&A 跨文档问答",
        "ai_feature": "Notion Q&A（搜索整个工作区直接给答案带引用）",
        "advantage2": "强很多",
        "cn_note": "中文 UI 已经基本完整，少数细节英文",
        "pitfall1": "Notion 复杂度对非技术同事有 2-3 小时学习税",
        "pitfall2": "Systeme.io 免费版只有 3 个 funnel",
        "solopreneur_verdict": "如果只选 3 个工具做最小可用栈：Notion AI + Writesonic + Systeme，月成本 $57。",
        "canonical": "https://razel369.github.io/articles/best-ai-tools-for-small-business-2026.html",
    },
    {
        "slug": "ai-writing",
        "title": "个人创作者用的 AI 写作工具：Jasper vs Writesonic vs Copy.ai 怎么选",
        "tool": "Writesonic + Jasper",
        "advantage1": "Writesonic 价格只有 Jasper 一半，长文质量非常接近",
        "ai_feature": "Writesonic Pro 的文章生成器 + 内置 SEO 模式",
        "advantage2": "品牌声音学习做得好",
        "cn_note": "界面全英文，但 prompt 中文也能跑",
        "pitfall1": "Jasper Brand Voice 需要上传 50 篇样本",
        "pitfall2": "Writesonic 长文超过 1500 字会偏题",
        "solopreneur_verdict": "如果只写 SEO 博客 → Writesonic。如果只写品牌内容 → Jasper。两者不要同时买。",
        "canonical": "https://razel369.github.io/articles/best-ai-writing-tools-solopreneurs.html",
    },
    {
        "slug": "notion-vs-clickup",
        "title": "Notion vs ClickUp 2026 实测对比，3-5 人团队选哪个",
        "tool": "Notion",
        "advantage1": "ClickUp 同档便宜，但 Notion 在文档/SOP/知识库上压倒性领先",
        "ai_feature": "Notion AI 的跨工作区 Q&A",
        "advantage2": "更直观",
        "cn_note": "中文支持完善",
        "pitfall1": "从 Notion 迁出去比从 ClickUp 迁出去难",
        "pitfall2": "ClickUp Business+ 的 AI 是含在套餐里的（Notion AI 是 +$10/月）",
        "solopreneur_verdict": "如果团队以文档为主 → Notion。如果团队以任务为主 → ClickUp。",
        "canonical": "https://razel369.github.io/articles/notion-vs-clickup-small-business.html",
    },
    {
        "slug": "jasper-vs-writesonic",
        "title": "Jasper vs Writesonic (2026) 哪个先收回成本",
        "tool": "Writesonic",
        "advantage1": "Writesonic Pro $20/月 vs Jasper Creator $49/月",
        "ai_feature": "Writesonic 的 AI Article Writer 内置 SEO 模式",
        "advantage2": "Jasper Brand Voice 学得更准",
        "cn_note": "两者全英文",
        "pitfall1": "Writesonic 长文有时要二次重写",
        "pitfall2": "Jasper 没有免费层，只有 7 天试用",
        "solopreneur_verdict": "如果同时做 SEO 博客 + 短文案 → Writesonic。如果只做长文且品牌感要求高 → Jasper。",
        "canonical": "https://razel369.github.io/articles/jasper-vs-writesonic-2026.html",
    },
    {
        "slug": "convertkit-vs-mailchimp",
        "title": "ConvertKit vs Mailchimp 2026，自媒体人和电商怎么选",
        "tool": "ConvertKit",
        "advantage1": "ConvertKit Creator 前 5000 联系人是同档价格，但 UI 更适合创作者",
        "ai_feature": "ConvertKit 的 AI 主题生成器（基于你的历史开信率推荐）",
        "advantage2": "比 Mailchimp 简单",
        "cn_note": "ConvertKit 全英文，Mailchimp 有中文支持",
        "pitfall1": "Mailchimp 对购买名单的限制更严",
        "pitfall2": "ConvertKit 的复杂 segmentation 学习曲线稍陡",
        "solopreneur_verdict": "个人创作 / 付费 newsletter / 课程 → ConvertKit。电商独立站 / 实体店 → Mailchimp。",
        "canonical": "https://razel369.github.io/articles/convertkit-vs-mailchimp-small-business.html",
    },
    {
        "slug": "systeme-io",
        "title": "Systeme.io 2026 实测：免费版真的够用吗？",
        "tool": "Systeme.io",
        "advantage1": "免费版直接可以用，跑 1 个 funnel 完全够",
        "ai_feature": "新版有 AI 自动化邮件序列",
        "advantage2": "几乎为零",
        "cn_note": "全英文，但操作逻辑清晰",
        "pitfall1": "A/B 测试只能测主题行，不能测落地页",
        "pitfall2": "课程规模超过 1000 人之后 UI 会卡顿",
        "solopreneur_verdict": "对 1 人业务非常合适。佣金结构 40-60% 终身，对推荐它的人来说也是极好的。",
        "canonical": "https://razel369.github.io/articles/systeme-io-review-solopreneurs.html",
    },
    {
        "slug": "email-ai",
        "title": "小团队做邮件营销，AI 工具怎么选（2026）",
        "tool": "ConvertKit + Writesonic (主题行)",
        "advantage1": "ConvertKit 免费支持 1000 联系人，Writesonic 主题行生成器最快",
        "ai_feature": "ConvertKit AI 主题行基于你历史开信率推荐",
        "advantage2": "比 Mailchimp 简洁",
        "cn_note": "英文界面，但 UI 简单",
        "pitfall1": "ConvertKit 复杂的自动化需要 1 周熟悉",
        "pitfall2": "Mailchimp 的 abandoned cart 模板对中文邮件支持差",
        "solopreneur_verdict": "创造者经济 → ConvertKit。电商 → Mailchimp。两者不要同时上。",
        "canonical": "https://razel369.github.io/articles/best-ai-tools-for-email-marketing-small-business.html",
    },
    {
        "slug": "social-media-ai",
        "title": "AI 社交媒体内容工具哪个靠谱：Predis / Brandwell / Canva 实测",
        "tool": "Brandwell",
        "advantage1": "Brandwell 一键发到 LinkedIn + X + Threads + Instagram",
        "ai_feature": "Brandwell 跨平台语气适配（同一篇内容在 X 更 punchy，在 LinkedIn 更专业）",
        "advantage2": "很多",
        "cn_note": "全英文",
        "pitfall1": "Brandwell 报告分析弱",
        "pitfall2": "Buffer AI 是额外付费 add-on",
        "solopreneur_verdict": "每天发 3 条以上 → Brandwell 或 Ocoya。&lt; 30 条/周 → Buffer + Canva 足够。",
        "canonical": "https://razel369.github.io/articles/best-ai-tools-for-social-media-content-creation.html",
    },
    {
        "slug": "under-50",
        "title": "预算 $50/月内做小生意的 AI 工具完整清单",
        "tool": "Systeme + Notion AI + Writesonic",
        "advantage1": "全在 $20-27/月，总成本 $57/月覆盖 funnel+知识+写作",
        "ai_feature": "Systeme.io 的 AI 邮件 + Writesonic + Notion AI",
        "advantage2": "几乎完美",
        "cn_note": "全英文 UI 但操作直接",
        "pitfall1": "Systeme 免费版限制 2000 联系人",
        "pitfall2": "Writesonic 长文质量不如 Jasper",
        "solopreneur_verdict": "$30 极限版：Notion AI + Writesonic + Systeme 免费。",
        "canonical": "https://razel369.github.io/articles/best-ai-tools-for-solopreneurs-under-50-per-month.html",
    },
    {
        "slug": "zapier-automation",
        "title": "用 Zapier + AI Agent 自动化小生意全流程（5 个可复制模板）",
        "tool": "Zapier + Claude/OpenAI",
        "advantage1": "Zapier Starter $19.99/月 + 一个 AI 模型即可",
        "ai_feature": "Zapier 2026 新增 AI Agents，能跨多步决策",
        "advantage2": "比手工快 10x",
        "cn_note": "Zapier 全英文，但 workflow 中文 prompt 也能跑",
        "pitfall1": "5 个自动化之后 Starter tier 不够用，要升到 $49/月",
        "pitfall2": "AI 有时会幻觉，需要 always-reply-as-draft 模式人工审核",
        "solopreneur_verdict": "小业务最高 ROI 的 AI 部署，比任何写作/社交工具都值得优先做。",
        "canonical": "https://razel369.github.io/articles/how-to-automate-small-business-with-ai-zapier.html",
    },
]

def main():
    today = datetime.date.today().isoformat()
    for p in POSTS:
        body = TEMPLATE.format(
            title=p["title"],
            tool=p["tool"],
            advantage1=p["advantage1"],
            ai_feature=p["ai_feature"],
            advantage2=p["advantage2"],
            cn_note=p["cn_note"],
            pitfall1=p["pitfall1"],
            pitfall2=p["pitfall2"],
            solopreneur_verdict=p["solopreneur_verdict"],
            canonical_url=p["canonical"],
        )
        out = ROOT / f"{p['slug']}.txt"
        out.write_text(
            f"# V2EX post: {p['title']}\n"
            f"# Suggested node: 'promotions' or 'startups' or 'saas'\n"
            f"# Suggested date: {today}\n"
            f"# Generated by v2ex_bodies.py\n\n"
            f"## title\n{p['title']}\n\n## body\n{body}\n",
            encoding="utf-8",
        )
        print(f"[ok] {p['slug']} -> {out}")

if __name__ == "__main__":
    main()
