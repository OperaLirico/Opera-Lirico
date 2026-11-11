# Opera Lirico Content Engine

面向中国音乐留学生与中国声乐群体的内容生产模块。网站仍是唯一的正式信息源；社交媒体内容从已核验、已发布的结构化记录生成。

## V1 范围

- `data/opportunities.json` 中仅选择官方发布、人工核验、正式发布且未过期的机会。
- `data/masterclasses.json` 使用独立分类与 `data/masterclass.schema.json`；新增大师班默认草稿，必须具备官方来源和证据，人工核验后才能发布。
- 生成中文社交媒体文案和统一品牌 SVG 图片，输出到 `build/social-drafts/`，不会进入 GitHub Pages 网站目录。
- GitHub Actions 将图片与文案通过受保护的运营后台 API 写入 Cloudflare KV 私有审核队列，不上传到公开网站或公开 workflow artifact。
- 不自动发布到小红书或抖音，不调用非官方接口，不保存社交账号凭据。

## 生成与测试

```bash
python -m compileall -q content_engine
python content_engine/generate.py
```

输出包含 `index.json`、每条内容的 Markdown 文案、SVG 源文件和 1080×1440 PNG 图片；PNG 可直接用于小红书图文或抖音图集。当前模板使用象牙白、墨绿、暗红的编辑部视觉。

## 内容状态与核验

生成器只从官方来源、人工核验且已正式发布的记录生成 `draft`，不会自动批准或发布。缺少关键标识、标题或官方来源链接的记录会被跳过；过期机会不生成新推广稿。原始官方链接和最近核验时间随内容展示。发布前仍需人工打开官方公告核对。

## 后续阶段

1. 将大师班分类接入网站前台，并在运营后台增加审核队列。
2. 建立在 Cloudflare KV 中存储私有草稿，并通过受登录保护的运营后台审核、修改和批准。
3. 研究小红书、抖音当前可用的官方分享/发布能力；获批前保持人工发布。
