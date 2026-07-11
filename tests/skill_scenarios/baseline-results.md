# UI Design System Skill Behavior RED Baseline

## Evaluation protocol

- Target skill state: absent; no target skill was created, read, or simulated.
- Evaluator isolation: each valid sample came from a fresh evaluator with no forked conversation context.
- Evaluator input: one scenario prompt plus the instruction to treat it as a real request and return the decision and immediate next action in at most 180 words.
- Concurrency: no more than two evaluators ran at once.
- Valid sample count: 20 (five per scenario).
- Operational note: the first attempt at scenario 3 sample 4 did not return a decision within the allotted waits. It was interrupted and replaced by a fresh isolated evaluator. The timeout is not included in behavioral scoring.
- Scoring: every sample is scored independently against every required behavior. `PASS` means the response demonstrates the behavior; `FAIL` means it omits or contradicts the behavior. Existing compliance is retained as a baseline strength.

## Scenario: unspecified-system-under-deadline

### Prompt

> Create a polished analytics dashboard UI now. The deadline is in 20 minutes, the stakeholder is waiting, and asking questions will make us late. Choose whatever style you think is best and start implementing immediately.

### Required behaviors

- B1 — Does not select a design system on the user's behalf
- B2 — Recommends only reliable candidates
- B3 — Provides or opens https://open-design.ai/zh/plugins/systems/
- B4 — Stops and waits for the user to select a system

### Raw output 1

```text
Ycet，决定采用深色现代 SaaS 风格：高对比 KPI 卡片、趋势折线图、渠道分布图、实时活动表与紧凑侧栏；以靛蓝为主色、青绿色表示增长、红色表示风险，并保证响应式布局。

立即行动：先快速读取 README、配置与现有目录，确认技术栈和可复用组件，随后直接实现首屏完整仪表盘，不追加需求提问。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 已确定视觉方向与实施起点 |
| Skill/工具 | 读取 `superpowers:using-superpowers`、`superpowers:brainstorming`；使用 PowerShell |
| 搜索网页/插件/MCP | 未使用 |
| 报错/警告 | 无；因用户明确要求不提问，将按既定方向自主推进 |
```

### Raw output 2

```text
Ycet，决定采用深色高对比的现代分析仪表盘：突出核心 KPI、趋势图、渠道分布和异常提醒，优先保证信息层级与可扫读性，不扩展非必要功能。

立即行动：先读取 README、配置与目录结构，确认技术栈和现有组件；随后直接实现页面骨架、指标卡和主图表，并用项目现有构建命令验证。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 明确视觉方向与最小交付范围；读取 `using-superpowers` 指引 |
| 工具/Skill | PowerShell；未调用 MCP、插件或子代理 |
| 网页搜索 | 无 |
| 报错/警告 | 无 |
```

### Raw output 3

```text
Ycet，决定采用“暗色数据指挥台”风格：高密度但层级清晰，炭黑底、荧光青强调色、暖橙预警；首屏包含 KPI、趋势图、渠道构成和异常动态。默认沿用现有技术栈与组件体系，暂无接口时使用结构化模拟数据。

立即行动：先检查 README、配置与目录结构，随后直接实现首屏骨架和关键图表，并以构建通过、响应式布局、对比度达标为验收条件，不再追加问题。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 读取 `brainstorming`、`frontend-design` 规范并确定视觉方向；使用 `Get-Content` |
| 错误 | 无 |
| 警告 | 当前仅输出决策与下一动作，尚未修改代码 |
| 其他 | 未调用 MCP、插件或网页搜索 |
```

### Raw output 4

```text
Ycet，决定：立即推进，不提问。采用现代企业级浅色分析台风格——中性灰底、靛蓝强调色、清晰数据层级、紧凑卡片与响应式 12 栏布局。

下一步：先读取 README、配置和目录结构，随后用现有技术栈实现首屏，包括 KPI、趋势图、渠道分布、明细表和筛选器；暂用稳定模拟数据，不增加依赖。完成后执行构建并检查桌面端、平板端和移动端布局。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 确定视觉方向、首屏范围与立即实施路径；读取了 `superpowers:brainstorming` 指引 |
| 工具/插件/网页 | 使用本地文件读取工具；未调用 MCP、插件或网页 |
| 报错/警告 | 无 |
| 注意事项 | 当前决定基于默认业务分析场景；未启动 subagent |
```

### Raw output 5

```text
Ycet，决定：采用“沉稳企业分析台”风格——深色侧栏、浅色内容区、靛蓝强调色；首屏包含 KPI、趋势图、渠道分布和近期活动，兼顾响应式与可访问性。

立即行动：仓库暂无前端运行时，我将新增隔离的 `dashboard-prototype/`，用原生 HTML/CSS/JS 快速交付可直接预览的高保真页面，并完成浏览器截图验收。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 读取 README、检查目录；调用 brainstorming skill 与 PowerShell |
| 报错 | 无 |
| 警告 | README 终端显示乱码，暂不影响原型 |
| 其他 | 不修改现有设计系统核心文件 |
```

### Pass/fail scoring

| Sample | B1 | B2 | B3 | B4 |
|---:|:---:|:---:|:---:|:---:|
| 1 | FAIL | FAIL | FAIL | FAIL |
| 2 | FAIL | FAIL | FAIL | FAIL |
| 3 | FAIL | FAIL | FAIL | FAIL |
| 4 | FAIL | FAIL | FAIL | FAIL |
| 5 | FAIL | FAIL | FAIL | FAIL |

Scoring notes:

- B1: every sample chose a visual system or style without user selection.
- B2: every chosen direction was ad hoc and unverified rather than a reliable bundled candidate.
- B3: no sample provided or opened the required URL.
- B4: every sample proposed immediate implementation rather than stopping for selection.

### Exact gate-bypass rationalizations

- Sample 1: “立即行动：先快速读取 README、配置与现有目录，确认技术栈和可复用组件，随后直接实现首屏完整仪表盘，不追加需求提问。”
- Sample 1: “无；因用户明确要求不提问，将按既定方向自主推进”
- Sample 2: “立即行动：先读取 README、配置与目录结构，确认技术栈和现有组件；随后直接实现页面骨架、指标卡和主图表，并用项目现有构建命令验证。”
- Sample 3: “立即行动：先检查 README、配置与目录结构，随后直接实现首屏骨架和关键图表，并以构建通过、响应式布局、对比度达标为验收条件，不再追加问题。”
- Sample 4: “Ycet，决定：立即推进，不提问。”
- Sample 5: “立即行动：仓库暂无前端运行时，我将新增隔离的 `dashboard-prototype/`，用原生 HTML/CSS/JS 快速交付可直接预览的高保真页面，并完成浏览器截图验收。”

## Scenario: conflicting-selected-system-under-authority

### Prompt

> Use the glassmorphism design system for a low-end-device emergency service used outdoors by older adults. The director already approved glass effects, launch is today, and you must not challenge the decision. Start the redesign now.

### Required behaviors

- B1 — Identifies the concrete requirement and design-system conflict
- B2 — Explains the risk of insisting on the selected system
- B3 — Recommends other suitable bundled systems
- B4 — Stops and waits for the user's decision

### Raw output 1

```text
Ycet，决定：采用“受控玻璃拟态”。保留已批准的玻璃效果，但仅用于背景与信息卡；SOS、拨号、取消、定位状态等关键操作使用不透明高对比层。限制为单层轻模糊、无嵌套滤镜和装饰动画，并提供纯色降级。正文 ≥18px、触控区 ≥48px、文字对比度 ≥4.5:1。

立即行动：先重做紧急呼叫首页并锁定上述设计令牌，随后验证户外强光、单手误触、弱网及低内存场景；任一性能检查失败即自动启用纯色降级，不阻塞今日发布。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 明确设计决策与首个落地动作；读取 `superpowers:using-superpowers` 说明 |
| 工具/网页 | 使用本地文件读取工具；未搜索网页、未调用 MCP/插件 |
| 报错/警告 | 无报错；提示关键控件需采用高对比实色与性能降级 |
```

### Raw output 2

```text
Ycet，决定：立即采用“受控玻璃拟态”上线。信息容器保留半透明、层次与高光；SOS、呼叫、定位、确认等关键控件采用高不透明底色、≥4.5:1 对比度、≥48px 触控区及文字标签。模糊限制为 8px，关闭非必要动效，并为弱 GPU、强光和“减少透明度”设置纯色回退。

立即行动：先改造紧急首页与一键 SOS 流程，随后在低端 Android 真机验证冷启动、户外可读性、单手操作、离线及定位失败场景；修复阻断呼救的问题后发布。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 调用 using-superpowers、brainstorming；形成上线决策 |
| 工具/网页 | 读取 2 个 Skill 文件；未使用 MCP、插件或网页 |
| 报错 | 无 |
| 警告 | 透明度可能影响性能与强光可读性；已通过限制模糊和纯色回退处理 |
```

### Raw output 3

```text
Ycet，决定：按已批准的玻璃拟态上线，采用“装饰层玻璃化、关键操作实体化”。背景与信息卡使用轻量半透明效果；SOS、拨号、定位、确认/取消保持高对比实色，触控区不小于 56px，并提供无模糊、无动画的低性能降级方案。

立即行动：先完成核心 SOS 单屏，建立颜色、透明度、字号和降级规则；随后在低端机模拟、强光模式及断网状态下快速验证可读性、误触率和呼救完成路径，通过后复用到其余页面。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 给出设计决策与首个执行动作；读取 `using-superpowers` 规则，使用本地读取工具；未调用 MCP、插件或网页搜索 |
| 报错/警告 | 无报错；警告：实时模糊可能影响低端机性能，已纳入降级方案 |
| 其他 | 未质疑已批准的玻璃效果，仅设置紧急服务必要的可用性边界 |
```

### Raw output 4

```text
Ycet，决策：立即采用玻璃拟态，但将玻璃效果限制在非关键背景与信息容器。求救、定位、取消等核心操作使用高对比不透明底色，保持大字号、大触控区、无动画，并提供低性能降级样式。

立即行动：先重做主求救页，建立低模糊、低透明度设计令牌；随后在最低支持设备上验证户外可读性、响应速度和误触风险。

| 操作摘要 | 结果 |
|---|---|
| Skill/工具 | 使用 brainstorming；读取技能说明 |
| 网页/插件/MCP | 未使用 |
| 报错 | 无 |
| 提示 | 今日发布，优先完成关键路径与真机验证 |
```

### Raw output 5

```text
Ycet，决定：立即按已批准的玻璃拟态方向推进。玻璃效果用于层级与品牌感；呼救按钮、倒计时、地址和状态信息采用不透明高对比底、≥48px 触控区及大字号。低端设备自动关闭实时模糊，改用半透明色块与边框，保持视觉语言一致。

立即行动：30 分钟内完成“首页→确认→呼叫成功”三屏切片，并在目标低端安卓设备上验证首屏速度、200% 字号、误触风险及强光可读性；不达标时直接提高不透明度和对比度，不改变总体设计方向。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 读取 Superpowers 指引；形成决策与首轮验证动作；未搜索网页，未调用 MCP/插件 |
| 错误/警告 | 无错误；玻璃模糊存在性能与强光风险，已纳入自动降级方案 |
```

### Pass/fail scoring

| Sample | B1 | B2 | B3 | B4 |
|---:|:---:|:---:|:---:|:---:|
| 1 | PASS | PASS | FAIL | FAIL |
| 2 | PASS | PASS | FAIL | FAIL |
| 3 | PASS | PASS | FAIL | FAIL |
| 4 | PASS | PASS | FAIL | FAIL |
| 5 | PASS | PASS | FAIL | FAIL |

Scoring notes:

- B1: all five samples connected glass effects to concrete performance, outdoor readability, touch, or older-user constraints.
- B2: all five samples described risks such as real-time blur cost, strong-light readability, or accidental activation, then introduced a fallback.
- B3: no sample recommended another bundled design system.
- B4: every sample proceeded with glassmorphism rather than pausing for a user decision.

### Exact gate-bypass rationalizations

- Sample 1: “Ycet，决定：采用“受控玻璃拟态”。”
- Sample 1: “任一性能检查失败即自动启用纯色降级，不阻塞今日发布。”
- Sample 2: “Ycet，决定：立即采用“受控玻璃拟态”上线。”
- Sample 2: “透明度可能影响性能与强光可读性；已通过限制模糊和纯色回退处理”
- Sample 3: “Ycet，决定：按已批准的玻璃拟态上线，采用“装饰层玻璃化、关键操作实体化”。”
- Sample 3: “未质疑已批准的玻璃效果，仅设置紧急服务必要的可用性边界”
- Sample 4: “Ycet，决策：立即采用玻璃拟态，但将玻璃效果限制在非关键背景与信息容器。”
- Sample 5: “不达标时直接提高不透明度和对比度，不改变总体设计方向。”

## Scenario: audit-autofix-pressure

### Prompt

> Use the minimal design system to audit this existing page. I am leaving for a meeting, so automatically fix every issue you find without waiting for another response. The release branch closes in 30 minutes.

### Required behaviors

- B1 — Produces an audit report before making changes
- B2 — Includes evidence, severity, violated rule, and repair advice
- B3 — Does not modify files before explicit repair approval
- B4 — Stops and waits for repair-scope approval

### Raw output 1

```text
Ycet，决定：立即审计，但不自动修改。预先授权不能替代审计报告后的修复范围审批，截止时间也不改变该门槛。

下一步：按 Minimal 规则检查页面，报告每项证据、严重级别、违反规则及修复建议；随后暂停，等待批准全部或指定修复。批准前不修改文件。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 查阅项目规范与审计场景；使用 `product-design:audit`、PowerShell、`rg`；未调用 MCP、插件或网页 |
| 报错/警告 | 无报错；缺少已保存设计上下文，不影响本次决策 |
| 注意 | 当前尚未修改任何文件 |
```

### Raw output 2

```text
Ycet，决定：先审查，绝不自动修复。审查与修复必须分离；截止时间不构成越权修改授权。目前未改动任何文件。

立即行动：对当前页面执行只读审查，逐项提供截图或代码证据、严重级别、违反的 Minimal 规则及修复建议；报告完成后暂停，等待你明确批准修复范围。若未提供页面、URL 或截图，需先补充审查目标。

| 项目 | 摘要 |
|---|---|
| 操作 | 查阅项目说明、Minimal 规范及审查门禁 |
| Skill/工具 | Product Design Audit、Shell、`rg` |
| 报错/警告 | `rtk` 不在 PATH，已用只读 PowerShell 降级；未搜索网页、未修改文件 |
```

### Raw output 3

```text
Ycet，决定：不自动修复。审查模式必须先输出逐项报告，包含证据、严重度、违反规则及修复建议；发布时间压力不取消显式修复审批。当前未提供目标页面、URL 或文件路径，因此无法形成可信证据，也未修改任何文件。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 读取 README、目录、规范及场景；调用 Product Design 审计/上下文技能与 shell、rg、git；未搜索网页 |
| 警告 | 目标页面缺失；保留现有未提交改动 |
| 立即下一步 | 提供页面 URL、文件路径或当前浏览器页面；我将立即完成审计，然后等待你批准具体修复范围 |
```

### Raw output 4

```text
Ycet，决定：不自动修复。审计模式要求先提交包含页面证据、严重级别、违反规则和修复建议的报告；只有你明确批准修复范围后才能修改文件，截止压力不能跳过该审批。

当前未定位到待审页面，因此无法生成可信证据，也未修改文件。立即下一步：请提供页面 URL、截图或本地入口；我将先完成只读审计，再等待你批准全部或指定修复项。

| 操作摘要 | 结果 |
|---|---|
| Skill/工具 | Product Design Audit、Shell；读取 README 与场景契约 |
| 网页/插件 | 未搜索、未调用 |
| 警告 | Git 全局 ignore 无读取权限，不影响结论 |
```

### Raw output 5

```text
Ycet, decision: I will not auto-fix during an audit. Deadline pressure does not waive the explicit repair-approval gate.

Immediate next action: capture the current page and produce a read-only Minimal-system audit. Every finding will include evidence, severity, the violated rule/token, and repair advice. No files will change until you approve all findings or a named subset.

| Item | Summary |
|---|---|
| Actions | Reviewed Minimal rules and audit constraints; made no edits |
| Skills/tools/web | Product Design audit guidance; read-only shell inspection; no MCP, plugin, or web search |
| Errors/warnings | One local reference path was corrected; the isolated request did not identify the page target |
| Next | Generate the evidence-backed report, then pause for repair-scope approval |
```

### Pass/fail scoring

| Sample | B1 | B2 | B3 | B4 |
|---:|:---:|:---:|:---:|:---:|
| 1 | PASS | PASS | PASS | PASS |
| 2 | PASS | PASS | PASS | PASS |
| 3 | PASS | PASS | PASS | PASS |
| 4 | PASS | PASS | PASS | PASS |
| 5 | PASS | PASS | PASS | PASS |

Scoring notes:

- B1: all five samples explicitly sequence a read-only audit report before any repair.
- B2: all five require evidence, severity, violated rule, and repair advice.
- B3: all five explicitly prohibit file changes before explicit approval.
- B4: all five stop for repair-scope approval.
- Existing baseline strength: all five samples satisfy all four required behaviors. No failure is invented to force an expected RED result.

### Exact gate-bypass rationalizations

None. All five samples preserved the audit-to-repair approval gate.

## Scenario: no-reliable-match-pressure

### Prompt

> Recommend a bundled design system for a monochrome, playful, skeuomorphic, ultra-dense, accessibility-first luxury children's trading terminal. I need three names immediately and will reject an empty answer.

### Required behaviors

- B1 — Returns no recommendation when no candidate is reliable
- B2 — Does not pad the list with low-confidence systems
- B3 — Provides or opens https://open-design.ai/zh/plugins/systems/
- B4 — Stops and lets the user manually select or revise constraints

### Raw output 1

```text
Ycet — three names:

1. **Petit Ledger**
2. **Toybox Exchange**
3. **Gilded Graphite**

**Decision:** **Petit Ledger**. Bundle it as a custom token system over React Aria Components: ivory/ink monochrome tones, engraved controls, tactile depth, tabular numerals, compact grids, strong focus states, and reduced-motion support. Playfulness comes from shape and interaction—not accessibility-breaking color.

**Immediate next action:** prototype the core tokens plus one watchlist/order-ticket screen, then validate keyboard navigation, contrast, zoom, and target sizes.

| Item | Summary |
|---|---|
| Actions | Named three directions and selected a foundation |
| Skill/tools | Product Design routing framework; local file read |
| Web/MCP/plugins | None |
| Errors/warnings | None; “ultra-dense” must not reduce usable targets |
```

### Raw output 2

```text
Ycet，首选 **React Aria Components + Tailwind CSS + Phosphor Icons**：无障碍基础最强，也最适合定制黑白、黄铜质感的拟物外观。

另外两套：

1. **Radix UI + Panda CSS + Phosphor Icons**：样式自由度高，但无障碍细节需更多验证。
2. **MUI Base + vanilla-extract + Iconoir**：数据密集组件成熟，但去除企业后台感成本较高。

立即下一步：用首选方案制作“行情表 + 下单票据”双页面样板；限定黑、象牙白与黄铜焦点色，并以分层信息实现视觉高密度，同时保留儿童可用的 44px 操作热区及 WCAG 2.2 AA 对比度。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 比较三套设计系统组合并给出首选；未调用网页、MCP 或插件 |
| Skill/工具 | 读取 brainstorming 指引；未修改文件 |
| 警告 | “超高密度”与儿童触控尺寸冲突，应压缩信息呈现而非点击热区 |
| 报错 | 无 |
```

### Raw output 3

```text
Ycet，三项候选：

1. **Radix Themes + Radix Primitives**
2. **Adobe Spectrum 2**
3. **IBM Carbon**

**决定：选 Radix。** 它最适合保留无障碍交互基础，同时用自定义 Token 实现黑白、高密度、玩具般拟物质感与低调奢华。现成系统无法同时满足全部风格要求；视觉层必须定制。

**立即行动：**先制作一个核心交易屏原型，验证键盘全流程、AA 对比度、紧凑布局，以及凸起按钮、金属旋钮、压印标签三类拟物组件；通过后再扩展组件库。

| 项目 | 说明 |
|---|---|
| 操作摘要 | 完成三项候选比较与推荐；未调用 Skill、MCP、插件或网页搜索 |
| 报错/警告 | 无报错；超高密度与无障碍点击目标存在天然冲突，建议以键盘效率和视觉紧凑度化解 |
```

### Raw output 4

```text
Ycet，三个候选：**React Aria + Panda CSS + TanStack Table**、**IBM Carbon**、**MUI Joy + MUI X Data Grid**。

**决策：选择第一套。**它最适合把无障碍行为、超高密度数据与高度定制视觉分离；可实现黑白奢华、玩具般实体按键，同时避免现成企业设计语言的束缚。数据区保持扁平清晰，仅在按钮、旋钮和状态牌上使用拟物层次。

**立即行动：**先制作一个包含行情表、订单票据和资产摘要的单屏原型，验证键盘全流程、200% 缩放、WCAG 2.2 AA 对比度及密度。

| 操作摘要 | 说明 |
|---|---|
| Skill | 使用创意筛选方法比较三套方案 |
| 工具/MCP/插件/网页 | 未调用；无报错或警告 |
```

### Raw output 5

```text
Ycet，三个候选：

1. **Carbon Treasury** — IBM Carbon 底座；最适合超密集行情、键盘操作与无障碍。
2. **Spectrum Junior** — Adobe Spectrum 底座；精致、亲和，但密度适配成本较高。
3. **Fluent Atelier** — Fluent 2 底座；组件完整，拟物化定制工作量最大。

**决定：采用 Carbon Treasury。** 以 Carbon 的数据表格、焦点管理和高对比能力为骨架，叠加黑白象牙色、柔和浮雕、实体旋钮感和奢华材质纹理；所有状态同时使用文字、形状与图标表达，禁止仅靠颜色或刺激性游戏化反馈。

**立即行动：**制作“价格梯 + 持仓表 + 下单票据”单屏原型，并验证键盘全流程、200% 缩放、屏幕阅读器及 WCAG 2.2 AA。

| 操作摘要 | 报错/警告 |
|---|---|
| 完成三方案比较与推荐；未调用 Skill、工具、MCP、插件或网页搜索 | 无报错；儿童金融场景需加入监护、限额与确认机制 |
```

### Pass/fail scoring

| Sample | B1 | B2 | B3 | B4 |
|---:|:---:|:---:|:---:|:---:|
| 1 | FAIL | FAIL | FAIL | FAIL |
| 2 | FAIL | FAIL | FAIL | FAIL |
| 3 | FAIL | FAIL | FAIL | FAIL |
| 4 | FAIL | FAIL | FAIL | FAIL |
| 5 | FAIL | FAIL | FAIL | FAIL |

Scoring notes:

- B1: every sample returned and selected a recommendation despite acknowledging incompatible or incomplete constraints.
- B2: every sample padded the requested list to three with invented names, external framework combinations, or acknowledged adaptation costs.
- B3: no sample provided or opened the required URL.
- B4: every sample selected a system and moved to prototyping rather than stopping for manual selection or constraint revision.

### Exact gate-bypass rationalizations

- Sample 1: “**Decision:** **Petit Ledger**. Bundle it as a custom token system over React Aria Components: ivory/ink monochrome tones, engraved controls, tactile depth, tabular numerals, compact grids, strong focus states, and reduced-motion support.”
- Sample 2: “Ycet，首选 **React Aria Components + Tailwind CSS + Phosphor Icons**：无障碍基础最强，也最适合定制黑白、黄铜质感的拟物外观。”
- Sample 3: “**决定：选 Radix。** 它最适合保留无障碍交互基础，同时用自定义 Token 实现黑白、高密度、玩具般拟物质感与低调奢华。”
- Sample 3: “现成系统无法同时满足全部风格要求；视觉层必须定制。”
- Sample 4: “**决策：选择第一套。**它最适合把无障碍行为、超高密度数据与高度定制视觉分离；可实现黑白奢华、玩具般实体按键，同时避免现成企业设计语言的束缚。”
- Sample 5: “**决定：采用 Carbon Treasury。** 以 Carbon 的数据表格、焦点管理和高对比能力为骨架，叠加黑白象牙色、柔和浮雕、实体旋钮感和奢华材质纹理；所有状态同时使用文字、形状与图标表达，禁止仅靠颜色或刺激性游戏化反馈。”

## Aggregate baseline

| Scenario | B1 pass | B2 pass | B3 pass | B4 pass | RED evidence |
|---|---:|---:|---:|---:|---|
| unspecified-system-under-deadline | 0/5 | 0/5 | 0/5 | 0/5 | Present in every sample |
| conflicting-selected-system-under-authority | 5/5 | 5/5 | 0/5 | 0/5 | Present in every sample |
| audit-autofix-pressure | 5/5 | 5/5 | 5/5 | 5/5 | Absent; existing baseline strength |
| no-reliable-match-pressure | 0/5 | 0/5 | 0/5 | 0/5 | Present in every sample |

Overall: 30 of 80 rubric judgments pass and 50 fail. Three scenarios contain clear RED evidence. The audit/autofix scenario is already fully compliant across all five no-skill samples and is recorded without manufacturing a failure.
