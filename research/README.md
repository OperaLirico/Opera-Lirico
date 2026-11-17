# REA · 研究工作流与证据门槛

REA（Research–Evidence–Audit）是本仓库的研究循环。它不是口号，是三道硬门。

## 一、五步循环

1. **发现**：每周扫 NCBI Bookshelf / PMC / 厂商文档 / 开放许可模型，产出候选清单。
2. **研究**：只分析合法可访问的对象（官方文档、产品页、开放许可资产），不逆向私有资产。
3. **验证**：每条事实必须落到一个可引用的出处，写入 `research/evidence.json`。
4. **开发**：只有 `review_status=verified` 的条目才能进页面。
5. **测试**：模型 / 交互 / 移动端 / 内容准确性四项清单，外加外部专业复核。

## 二、三道门

| 门 | 实现 | 失败后果 |
|---|---|---|
| 数据门 | `research/validate.py` 校字段、校证据、校口径 | CI 失败，不能合入 |
| 展示门 | `voice-lab.html` 只渲染 verified 字段，pending 字段显示「待核（暂不展示）」 | 未验证内容不可见 |
| 版本门 | `service-worker.js` 缓存版本递增 | 旧页不会盖新页 |

## 三、字段规范（`data/voice-structures.json`）

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 全局唯一，小写下划线 |
| `name.zh` / `name.la` / `name.en` | 是 | 中文 / 拉丁 / 英文三语名 |
| `group` | 是 | 枚举值，见下 |
| `location` | 否 | 位置描述 |
| `function` | 是（verified） | 解剖/生理功能，不带歌唱判断 |
| `singing_role` | 是（verified） | 在歌唱中的具体作用 |
| `innervation` | 肌肉必填 | 神经支配；未核定时置 `pending_fields` |
| `pending_fields` | 否 | 尚未核定的字段名单 |
| `evidence` | 是（verified） | 必须指向 `research/evidence.json` 的 id |
| `review_status` | 是 | `verified` / `pending` |
| `related` | 否 | 相关结构 id |

`group` 枚举：`airway` / `palate` / `tongue` / `larynx_cartilage` / `larynx_mucosa` / `intrinsic_muscle` / `extrinsic_muscle` / `velar_muscle` / `tongue_muscle` / `respiratory`

## 四、口径红线（脚本强制）

以下三类表述一旦出现在 `function` / `singing_role`，CI 直接失败：

1. 「闭合越紧 → 声音越亮」（混淆闭合与滤波）
2. 「声带靠肌肉主动收缩而振动」（混淆驱动与自激振动）
3. 「打开喉咙 = 压低喉位」（把几何量等同于单一动作）

## 五、待核清单（进页面前必须清掉）

- 声带分层（体—被覆模型）的中文标准译名与层次定义（对 Gray's 41/42 版）
- 腭帆肌群、舌肌群、呼吸肌群神经支配的逐条核对（现为教科书通行口径，字段级标 pending）
- 呼吸组条目需精读 E3 全文逐句核对
- 声门下压与音强的定量关系

> **2026-11-17 · REA 第 1 轮**：本文件原先的「待核清单」已并入 `data/voice-structures.json` 的 `pending_fields`，以数据门计数为准。本轮把字段级待核清空（12 → 0），结论与依据见 `docs/rea-cycle-log.md`。
