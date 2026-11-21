# skills/impeccable

上游：`pbakaus/impeccable`（Apache-2.0，© Paul Bakaus）
技能名：`impeccable`　版本：**4.10.0**
固定提交：`b49177d32788f2dc585c42831d845dacf1ebed2c`（2026-11-18）
来源：https://github.com/pbakaus/impeccable

## 它是什么

给编程 agent 装「设计判断力」的技能。它不盖房子，它审房子：`critique` 按启发式打分批注、`audit` 查可访问性/性能/响应式、`polish`/`bolder`/`quieter`/`typeset`/`layout` 给方向。

和 taste-skill 的分工：

- taste 是**闸门**：PASS/FAIL，不过就得改，容易为了过而改结构。
- impeccable 是**评审**：先定这个页面属于哪种 surface（Persuade / Operate / Read / Experience），再按那套标准评。操作性页面不会被拿落地页的教条去打分。

## 这个仓库里有什么

- `METHOD.md`　方法卡（中文）：四种 surface、我们会用到的命令、评分从哪来
- `sync.sh`　按固定提交拉全量到 `upstream/`
- `README.md`　本文件

没有：

- `upstream/`　不提交。它带一个自包含启动器（`scripts/impeccable`，首次运行下载二进制，不依赖 Node），属于本地工具链，不是本站运行依赖。
- `LICENSE`　由 `sync.sh` 一并拉取；署名要求见下。

## 什么时候用

- 想听「这页哪里俗、为什么」，而不是只想知道过没过
- 需要技术体检（对比度、键盘可达、布局抖动、动画减负）
- 页面发灰、发怯，需要往上推一档（`bolder`）；或太吵，需要收（`quieter`）

## 许可证义务

Apache-2.0：保留署名与许可声明，改动过的文件需注明。我们只引用其方法与清单，不照抄示例成品。
