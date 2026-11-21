# marketingskills 方法卡（只记我们收的四个）

## 一、seo-audit

优先级是钉死的，从上往下：

1. 能不能被抓、能不能被索引（robots、sitemap、架构、参数页）
2. 技术底子（速度、可渲染、移动端）
3. 页面本身（标题、描述、H 层级、内链）
4. 内容值不值得排
5. 权威与链接

第 1、2 没过就别谈第 3。它的经验值：**已经在 8–20 位的页面，是最快的收益**（`references/rankings-push.md`）。对本站意义在于：机会条目现在是首页上的卡片，没有独立 URL，第 3 条无从谈起。

## 二、schema

判据四条：准（不标不存在的内容）、用 JSON-LD、只用 Google 支持的、上线前验证。

本站能落地的最小集：

- `WebSite` + `Organization`（已有，补 `sameAs`）
- `Event`：每条开放招募/比赛一条，`name` / `startDate` / `endDate` / `location` / `organizer` / `offers`（报名费或免费）。截止日期驱动的条目，这是最值钱的一类标记。
- `BreadcrumbList`：等条目有独立页时再加。

模板见上游 `references/schema-examples.md`。

## 三、cro

它查的顺序：价值主张是否一屏说清 → 行动点是否唯一且显眼 → 表单字段是否都能解释 → 信任证据（来源、更新时间、真实机构名）→ 摩擦（跳转、加载、失败态）。
本站的信任证据是强项（官方来源链接），弱项在「订阅」这一步的理由不足：为什么要留邮箱。

## 四、emails

主题行 ≤ 45 字符、一封一个目的、首段给结论、退订口径明确。周报的节奏建议它也有，但发送频率由你定。

## 五、用法

```bash
# 装到 agent 之后
$seo-audit 审计本站
$schema 给开放招募页加 Event 标记
$cro 审订阅流程
```

需要完整 references 时先跑 `sync.sh`。
