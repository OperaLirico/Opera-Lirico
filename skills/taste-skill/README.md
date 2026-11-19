# skills/taste-skill

上游：`Leonxlnx/taste-skill`（MIT 许可证，版权所有 © 2026 Leonxlnx）
技能名：`design-taste-frontend`　版本：**2.5.1**
固定提交：`f6b76575f949707b4e3c37cd86cb44b0b98643e8`（2026-11-07）
来源：https://github.com/Leonxlnx/taste-skill

## 它是什么

一个给编程 agent 装「审美」的前端技能。目标不是做得好看，是做得**像一家真公司会发布的网站**：第一屏说清卖什么，每一屏都放着真东西，看上去是为这个客户做的，而不是模板、也不是艺术装置。它的对标是 figma.com 和 x.ai。

它把「品味」拆成可执行的东西：生意类型→页面类型→版式/配色/元素**抽签**（带历史记录，所以每次不一样）→文案先行→脚本 + 闸门检查→报告。

## 这个仓库里有什么，没有什么

有：

- `METHOD.md`　我们读完 31KB 主文件后写的方法卡（中文，用于内部参考）
- `sync.sh`　按固定提交把完整技能（含 `assets/` 与 `scripts/`）拉到 `upstream/`
- `LICENSE`　上游 MIT 许可证原文（法律义务：保留署名）

没有：

- 全量 `assets/`（components、backgrounds、effects、layout、moments、scenes、ui）与 `scripts/`（gate / consistency / check / shoot / perf / copy-lint）。
  原因：它是 Node 22 + Chrome 的工具链，不是本站点的运行依赖；塞进来会让 Pages 的整仓上传变重，且和我们的静态站没有调用关系。需要时用 `sync.sh` 现拉。

## 什么时候用

- 要重做首页/落地页，或有人反馈「这页看着像 AI 做的」
- 新增页面（大师班、曲目、会员）需要一套统一版式
- 只想要它的**检查清单**：一屏一节、左右边齐、无图注、悬停必须有反馈、不许紫色、不许滚动淡入、不许编造评价

## 许可证义务

MIT：保留 `LICENSE`、保留作者署名。我们引用它做方法与清单参考；不照抄它的示例成品。

它自己也写明「不许复制参考站的代码、文案、图片或标志性效果」——这条和我们对 VocalGateway 的边界完全一致。
