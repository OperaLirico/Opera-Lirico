# 曲库整理与扩充规则

## 当前主曲库

主曲库只展示经过选择的常见核心曲目，按以下顺序组织：

1. 歌剧咏叹调
2. 古典咏叹调 / Arie antiche
3. 意大利艺术歌曲
4. 德奥艺术歌曲（Lieder）
5. 法国艺术歌曲（Mélodies）
6. 其他语言的经典艺术歌曲（有明确教学/演唱价值时再收录）

每条作品使用 `section` 和 `priority` 控制分组与排序。搜索命中时，先按作品名匹配度，再按优先级排序。

## 选择标准

- 优先常见声乐教材、标准曲集、音乐学院学习与考试中反复出现的作品。
- 优先辨识度高、演出/教学使用广泛、能代表重要作曲家和风格的作品。
- 先确保作品名称、作曲者/归属争议、原文和来源准确，再补充中文大意、声部建议和乐谱链接。
- 不用 LiederNet 收录数量或随机扫描结果代表热门程度。
- 作品归属存在争议时必须明确标注，不把传统归属写成确定事实。
- 没有核验原文或乐谱来源时，不得编造歌词、乐谱链接或声部范围。

## 自动导入档案

旧版本曾随机扫描 LiederNet，并将大量未分类条目直接加入主曲库。这些记录已移入 `data/repertoire_archive.json`，不由前端加载。档案保留供未来人工筛选，不等于推荐曲目。

随机批量导入已暂停。日常工作流保留原有步骤，但更新脚本不会再把随机冷门作品自动写入公开曲库。

## 下一轮扩充建议

- 歌剧咏叹调：Puccini、Verdi、Mozart、Donizetti、Rossini、Bizet、Gounod、Handel 等常见曲目。首批已加入 Nessun dorma、La donna è mobile、Casta Diva、Libiamo、Voi che sapete。
- 古典咏叹调：以常见的 24/26 首意大利歌曲与咏叹调曲集为核心，再补充同类经典作品。首批已加入 Amarilli, mia bella 与 Nina；Nina 的传统作曲者归属存在争议，页面明确提示。
- 德奥艺术歌曲：Schubert、Schumann、Brahms、Wolf、Strauss、Mahler。首批已加入 Schubert《Ständchen》《An die Musik》及 Brahms《Wiegenlied》。
- 法国艺术歌曲：Fauré、Debussy、Duparc、Ravel、Hahn、Poulenc。首批已加入 Duparc《L'invitation au voyage》。

扩充时按作品逐条核验，不为追求数量而批量填充未经确认的条目。
