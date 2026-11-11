# Opera Lirico Content Engine

面向中国音乐留学生与中国声乐群体的内容生产模块。网站仍是唯一的正式信息源；社交媒体内容从已核验、已发布的结构化记录生成。

## V1 范围

- `data/opportunities.json` 中仅选择 `publisher_status=official`、`review_status=verified`、`publication_status=published` 且申请截止日期尚未过期的机会。
- `data/masterclasses.json` 使用独立分类与 `data/masterclass.schema.json`；新增大师班默认草稿，必须具备官方来源和证据，人工核验后才能发布。
- 生成中文社交媒体文案和统一品牌 SVG 封面，输出到 `content/drafts/`。
- 不自动发布到小红书或抖音，不调用非官方接口，不保存社交账号凭据。

## 生成

```bash
python content_engine/generate.py
```

输出包含 `index.json`、每条内容的 Markdown 文案和 SVG 图片。SVG 可直接作为图片文件导入设计软件或转换为 PNG。当前模板使用象牙白、墨绿、暗红和衬线标题的编辑部视觉。

## 内容状态

`draft` = 已生成、待人工审核；`approved` = 人工确认后可发布；`published` = 人工记录发布结果。生成器只创建或更新 draft，不会把记录标记为已批准或已发布。

## 核验原则

不从第三方线索自动生成可发布宣传内容；不推断缺失的老师、日期、费用、名额或资格；日期缺失时明确显示“以官方公告为准”。原始官方链接和最近核验时间必须随内容展示。过期机会不生成新推广稿。

## 后续阶段

1. 将大师班分类接入网站前台，并在运营后台增加内容审核队列。
2. 增加人工审核状态写回和发布记录。
3. 研究小红书、抖音各自当前可用的官方分享/发布能力；获批前保持人工发布。
