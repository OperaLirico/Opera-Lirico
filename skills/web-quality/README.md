# skills/web-quality

上游：`addyosmani/agent-skills`（MIT，© Addy Osmani）
固定提交：`8c99fa36d90068c82d547f7c12a9d67a3e95f4ee`（2026-11-18）
来源：https://github.com/addyosmani/agent-skills

## 收了哪几个

上游 26 个技能，只收三个和静态站直接相关的：

| 技能 | 用处 |
|---|---|
| `accessibility-engineering` | 键盘可达、对比度、焦点顺序、ARIA 用法；自带 `scripts/audit-a11y.sh` |
| `performance-optimization` | 首屏体积、字体与图片、加载优先级、CWV 口径 |
| `browser-testing-with-devtools` | 用 DevTools 协议做可复现的页面检查，替掉「截个图看一眼」 |

## 这个仓库里有什么

- `METHOD.md`　方法卡（中文）
- `sync.sh`　按固定提交拉全量到 `upstream/`，只读这三个子目录

## 为什么不收其它

`git-workflow`、`ci-cd`、`code-review`、`spec-driven-development`、`interview-me` 这些是给团队写库用的流程技能，本站是一个人维护的静态站，收进来只会加流程负担。

## 用法

```bash
$accessibility-engineering 扫 voice-lab.html 的可达性
$performance-optimization 首页首屏还能压什么
```
