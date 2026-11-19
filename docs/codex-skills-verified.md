# Codex 五款 Skill：核实后的安装与调用

核实日期：2026-11-19。所有仓库、许可证与安装命令均取自各仓库 README 与 OpenAI 官方文档，不采用二手视频描述。

## 先说 Codex 的技能机制（三件事）

1. **目录**：`$CODEX_HOME/skills/<skill-name>/SKILL.md`，默认即 `~/.codex/skills/`。项目里的 `.codex/` 放配置和 `AGENTS.md`，**不是**装技能的地方。
2. **调用**：在提示里写 `$技能名`，例如 `$design-taste-frontend 帮我重做首页`。
3. **生效**：装完下一轮即可用；没出现就重启 Codex。

官方装法两种：Codex 里用内置的 `$skill-installer`（`$skill-installer playwright`，或 `$skill-installer install <GitHub URL>`）；或各仓库自己的 `npx skills add`。

## 五个技能

| 技能 | 仓库（已验证） | 许可证 | 安装 |
|---|---|---|---|
| Caveman | `JuliusBrussee/caveman` | Apache-2.0 | `npx @caveman-ai/cli@latest`（完整版，带本地代理）；只装技能：`npx skills add JuliusBrussee/caveman -g` |
| Taste | `Leonxlnx/taste-skill` | MIT | `npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"` |
| Playwright | `openai/skills` → `skills/.curated/playwright` | 见其 LICENSE.txt | Codex 内：`$skill-installer playwright` |
| GSAP | `greensock/gsap-skills`（官方） | MIT | `npx skills add https://github.com/greensock/gsap-skills` |
| Hypit | `hypit-ai/hypit` | **NOASSERTION**（无明确开源许可） | `npx skills add hypit-ai/hypit -g` |

## 逐个说明与风险

### Caveman（压缩输出）
不是纯提示词技能，而是**本地代理 + 技能**：`npx @caveman-ai/cli@latest` 会接管你在 Claude / Codex / Gemini CLI / OpenCode 等 30+ agent 的调用，跑在你本机、用你自己的 key 或已登录的订阅。它提供 ultracave、megacave 等多档强度。
装之前要知道：它会改 agent 配置，不是拷一个文件夹就完事。只想体验技能层可用 `npx skills add ... -g`。

### Taste（网页视觉方向）
仓库里就一个技能 `design-taste-frontend`（就是我们已收录的 2.5.1）。依赖 **Node 22+** 和已安装的 Chrome / Edge / Chromium（非标准路径用 `CHROME_PATH`），ffmpeg 可选。它不装任何包、不要 API key，自带 Wikimedia 照片可离线。
它的重点不是“好看”，是抽签决定版式与配色、一屏一节、脚本 + 闸门检查到过为止。

### Playwright（浏览器自动化）
OpenAI 官方 curated 列表里的技能，底层是微软 Playwright CLI，读页面结构而不是靠视觉模型看图，所以可复现。适合竞品调研、逐页抓取并整理成表。
注意：`openai/skills` 仓库首页已标 **deprecated**，官方示例迁往 `openai/plugins`；playwright 在 curated 里仍可装，但要有搬家预期。

### GSAP（网页动效）
官方仓库，MIT。据其 README，Webflow 收购后 **所有原 Club 插件（SplitText、MorphSVG 等）对所有人免费，包含商用**，直接装公共 `gsap` npm 包即可，不需要 Club 会员或 `.npmrc` token。

### Hypit（拆解并复刻爆款视频）
许可证为 `NOASSERTION`，**不是**标准开源许可，商用前要自己看清条款。首次使用时 agent 会检查并准备 Hypit 可执行文件，依赖较重（有第三方项目吐槽约 10GB）。
按官方 README，成片要调外部模型，示例成本约 $1/条；所谓“免费”指的是技能本身，不是生成成本。
调用形如：`$hypit Clone this video: /path/to/video.mp4, and replace ...`。

## 视频里三处不准确的地方

1. `skill-installer install <仓库>` 不是 shell 命令，而是 Codex 内的技能调用 `$skill-installer ...`。
2. 安装目录不是项目里的 `.codex/skills`，是用户级 `~/.codex/skills`（即 `$CODEX_HOME/skills`）。
3. “已被 OpenAI 官方库收录”属实，但那个仓库现在标了 deprecated，正在迁到 `openai/plugins`。

## 对我们（OperaLab）的建议顺序

1. **Playwright**：直接有用（抓同行公开页、整理成表），且是官方维护。
2. **Taste**：已收录方法卡，等真重做首页时再装全量。
3. **GSAP**：只在需要动效时用，别给静态站增加运行时依赖。
4. **Caveman**：省 token 真实，但它改全局代理，建议单独环境试，不要直接上生产。
5. **Hypit**：许可证不明 + 依赖重 + 有生成成本，暂缓。
