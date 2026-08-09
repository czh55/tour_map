# 旅游规划 HTML 一站生成工作流

面向「一次旅行 → 一份可视化 HTML 行程方案」的完整制作流程。本工作流基于 2026 冈仁波齐转山行程方案实战沉淀，目标是让任何旅行规划（西藏转山、城市漫游、多段联程）都能按同一套方法快速产出高质量、可离线打开、适合手机阅读的单文件 HTML。

> **核心原则**：全程资源本地化（不依赖任何 CDN）、单文件可离线使用、先内容后美化、浏览器实测兜底。

```
Task Progress:
- [ ] 1. 需求解析：出发地 / 目的地 / 时间窗口 / 硬约束
- [ ] 2. 行程建模：拼假策略 + 天数列举 + 返程倒排
- [ ] 3. 信息调研：网络搜索交通/门票/住宿/费用
- [ ] 4. 资源本地化：下载图片 / 字体 / 地图库到本地
- [ ] 5. HTML 骨架：章节结构 + 核心内容
- [ ] 6. 交互增强：地图 / 侧边节点 / 章节导航 / 返回 TOP
- [ ] 7. 视觉美化：封面图 + 手写体标题 + 主题色
- [ ] 8. 质量验证：浏览器实测 + 结构自检
- [ ] 9. 输出归档：备份版本 + README + Git
- [ ] 10. 汇总收录：guides.json 追加记录，接入汇总门户
```

---

## Step 1：需求解析（先问清边界，再动手）

产出：一份需求清单，**必须拿到全部硬约束后才能建模**。

| 字段 | 必问 | 示例 |
|------|------|------|
| 出发地 | 是 | 北京（工作地） |
| 老家 / 中转 | 否 | 临汾（假期先回老家再出发） |
| 目的地 | 是 | 拉萨 → 塔钦 → 冈仁波齐转山 |
| 时间窗口 | 是 | 2026 国庆 10/1–10/7 |
| 返程硬约束 | 是 | **10/6 必须回到北京** |
| 假期来源 | 是 | 国庆 + 中秋连休、请假天数上限 |
| 预算档位 | 否 | 经济 / 标准 / 舒适 |

**踩坑**：
- 返程硬约束是行程建模的**锚点**，先定它再倒排。
- 老家 + 工作地双端点时，行程链会变长（北京→老家→目的地→老家→北京），需要把往返老家段计入时间。

---

## Step 2：行程建模（拼假 + 倒排）

产出：一条「行程链」+ 逐日计划（天 / 日期 / 动作 / 过夜地）。

**拼假策略**：重叠两个假期（如中秋 9/25–27 + 国庆 10/1–7），只需请假中间 2–3 天即可拼出 10+ 天整段。

**倒排法**（保证硬约束）：
1. 从「返程硬约束日」往前倒排：返程段 → 目的地最后一天 → 核心活动（如转山 3 天）→ 适应期 → 去程段。
2. 高海拔/长线旅行在核心活动前留 **1–2 天适应/休整**。
3. 每天标注：日期、动作、起止时间、海拔、住宿点、可选项。

**输出到 HTML 的两种视图**：
- **推荐行程表**：逐天一行，含「时间 / 行程 / 关键信息 / 过夜地」。
- **逐小时时间线**：精确到小时，可当"当天照着走"的清单（见 Step 6）。

---

## Step 3：信息调研（搜索 + 整理成表）

按类型搜集并用结构化表格组织，避免正文堆砌：

| 类型 | 来源 | 输出形式 |
|------|------|---------|
| 交通（航班/高铁/包车） | 搜索班次、价格、时长 | 表格：班次/时间/价格/备注 |
| 门票 | 景点官方/攻略 | 表格：景点/看点/海拔/门票/停留 |
| 住宿 | 平台搜索 | 表格：地点/价格/注意事项（如弥散供氧） |
| 费用 | 汇总 | 三档预算表（经济/标准/舒适） |
| 安全 | 高反、天气、救援 | callout 警示块 |
| 经验 | 播客/游记 | 单独章节 + 装备清单补充 |

**踩坑**：
- 高原场景务必写清：海拔逐日增量 ≤500m、高反红线症状、救援车联系方式。
- 预算用**三档区间**而非单值，标注「门票/交通为旺季参考价，以现场为准」。

---

## Step 4：资源本地化（最重要，避免中国网络坑）

**这是本项目最大的经验：所有外部资源必须下载到本地，不信任任何 CDN。**

### 4.1 图片（Unsplash）

- 用 WebSearch 搜 `景点名 + unsplash`，从结果页提取 `images.unsplash.com/photo-xxx` 直链。
- 下载参数：`?fm=jpg&q=70&w=1200&auto=format&fit=crop`（1200px 足够网页展示，q=70 控制体积）。
- 存到 `images/{slug}.jpg`，命名用英文 slug（`potala.jpg`、`kailash.jpg`）。
- **必须 `file` 验证是 JPEG**（curl 可能返回 404 页面存成 .jpg）。
- 图库许可：Unsplash License 可免费商用/非商用，页脚注明出处即可。

### 4.2 中文字体（Google Fonts → 本地 TTF）

- 书法/手写体中文首选：**Ma Shan Zheng（马善政楷书）**，URL 经 `fonts.googleapis.com/css2?family=Ma+Shan+Zheng` 解析出 `.ttf` 直链。
- 下载到 `fonts/`，用 `@font-face` + `font-display: swap`，回退链 `Kaiti SC / STKaiti / KaiTi / cursive`。
- 楷书只有 400 字重，标题 `font-weight` 改为 400，避免伪粗体变形。

### 4.3 地图库（Leaflet → 本地文件）

- 从官方 GitHub release 下载 `leaflet.min.js` / `leaflet.min.css` + images 目录到 `leaflet/`。
- 底图用**高德矢量瓦片**（无需 key）：
  ```
  https://webrd{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
  subdomains: ['01','02','03','04']
  ```
- **GCJ-02 坐标偏移**：高德用火星坐标，GPS 坐标（WGS-84）必须先转换再画 marker/线，否则偏移几百米。实现标准转换函数 `wgs84togcj02`。
- **Leaflet 硬性约束**：一个 `L.tileLayer` 实例不能同时被两个 map 使用 → 用 `makeBaseLayer()` 工厂函数为每个 map 新建实例。

### 4.4 自检

```bash
file images/*.jpg          # 全部应为 JPEG image data
ls fonts/ leaflet/         # 确认文件齐全
```

---

## Step 5：HTML 骨架

单文件 `{名称}.html`，结构：

```
<head>  <meta viewport> + <title> + 本地 CSS </head>
<header>  封面图 banner + 标题 + 副标题 + 关键 meta 徽章 </header>
<aside class="side-nav">  章节导航（见 Step 6）</aside>
<div class="wrap">
  <nav class="toc">  顶部目录（可选）</nav>
  <section id="s1">...<section id="s13">  按章节编号
  <footer>  数据来源 + 版本日期 </footer>
</div>
<script>  交互逻辑 + 地图初始化 </script>
```

**主题设计**（西藏转山示例）：
- CSS 变量集中管理色板：`--red` 藏红 `#8B2F1B`、`--gold` 鎏金 `#c9a227`、`--blue` 藏青 `#1e3a5f`、`--ink/--muted/--bg/--card/--line`。
- 内容组件：`.callout`（key 金/warn 红/info 蓝）、`.badge`（must 必去/nice 顺路/skip 可跳过）、`.table-scroll` 表格、`.gear` 双栏清单。

---

## Step 6：交互增强

### 6.1 高德地图 + 侧边节点清单
- 两个地图：路线全景图（景点 marker）+ 局部放大图（转山环线）。
- **侧边栏**：地图右侧 `aside.map-sidebar`，直接列出每个节点内容（名称/时间/费用/备注），无需点击弹窗。
- 双向联动：点击侧边项 → 地图 pan + 开 popup；点击 marker → 侧边高亮 + scrollIntoView。

### 6.2 章节导航（信息架构）
用户抱怨"13 个章节太多"后沉淀出的**三级结构**：
- **一级**：最多 4 个分组（如 行程规划 / 沿途看点 / 费用备选 / 准备与应对），手风琴展开。
- **二级**：原章节（13 个），归入一级分组。
- **三级**：章节内 `h3` 小节，JS 自动扫描生成锚点（`s4-h1` 等）并填充列表。
- 滚动时同步高亮：分组 → 章节 → 小节逐级联动。
- 关键实现：所有三级列表由 JS 从 DOM 的 `h3` 自动生成，**无需手写维护**；无小节的章节自动移除空列表。

### 6.3 一键返回 TOP
- 右下角固定圆形按钮，滚动 >320px 淡入，点击 `scrollTo({behavior:'smooth'})` 平滑回顶。

---

## Step 7：视觉美化

- **封面图**：header 用全宽 banner 图（`object-fit: cover`），左侧深色渐变遮罩保证文字可读，底部渐变衔接正文背景色。
- **手写体标题**：封面 h1 / 章节 h2 / 导航标题应用楷书，正文保持系统字体。
- **响应式**：`.page` flex（侧边导航 + 内容）；`max-width:1080px` 隐藏侧边导航；`max-width:860px` 封面降高、地图侧栏转纵向；`max-width:640px` 字号缩减。

---

## Step 8：质量验证（必须实测）

### 8.1 静态自检

```bash
# HTML 标签平衡（Python，处理 XHTML 自闭合 <link />）
python3 -c "..."   # 未闭合栈为空 + 无 mismatch

# JS 语法
node -e "new Function(allScriptsText)"
```

### 8.2 浏览器实测（CDP）
- `python3 -m http.server 8899` 起本地服务（**`file://` 无法被浏览器工具导航**）。
- 检查：地图瓦片加载、marker 数量、侧边节点渲染、分组导航高亮切换、图片全部加载（`img.complete && naturalWidth>0`）、字体加载（`document.fonts.check('16px MaShanZheng')`）。
- 用 `Emulation.setDeviceMetricsOverride` 模拟手机屏验证响应式。

---

## 踩坑清单（按出现频率）

1. **CDN 不可靠** → Leaflet/字体/图片一律本地化，离线可用是第一优先级。
2. **`file://` 无法测** → 永远起 `http.server`。
3. **高德坐标偏移** → WGS-84 必须转 GCJ-02，否则 marker 漂移。
4. **Leaflet 单实例限制** → 每个地图独立的 tileLayer。
5. **图片 URL 404** → 下载后必须 `file` 验证，非法请求会存成文本文件。
6. **章节太多** → 一级分组 ≤4，二级章节，三级小节自动生成。
7. **`<link />` 自闭合** → HTML 解析器需用 `handle_startendtag` 处理，否则误报 head 不闭合。
8. **正文改版导致编号错乱** → 章节 h2 序号、h3 子序号、交叉引用三处同步检查。

---

## 复用清单（下个项目直接套用）

| 组件 | 位置 | 说明 |
|------|------|------|
| 色板变量 | `:root` CSS | 换主题只需改 9 个变量 |
| 章节导航 JS | `<script>` | 复制即可，自动适配任意 h2/h3 |
| GCJ-02 转换 | JS 函数 | WGS-84 → 高德坐标 |
| 本地图库 | `leaflet/` | 已下载好，直接引用 |
| 本地字体 | `fonts/` | MaShanZheng TTF |
| 本地图片 | `images/` | Unsplash 下载 |
| 地图侧栏 | `.map-wrap` | 节点内容直接展示 |
| 返回 TOP | `.back-top` | 右下角浮动按钮 |

---

## Step 10：添加到攻略汇总页（多攻略站点）

`docs/index.html` 是旅游攻略**汇总门户**（数据驱动），不是单页。新增一篇攻略后，汇总页会自动出现新卡片。

**目录结构**：

```
docs/
├── index.html                # 汇总门户（无需改动）
├── guides.json               # 攻略索引数据（追加一条记录）
├── {攻略名}.html             # 攻略成品（相对路径引用资源）
├── images/<slug>/            # 该攻略的图片资源
├── fonts/  leaflet/          # 共享资源（不重复下载）
└── WORKFLOW.md
```

**添加步骤**：

1. 攻略 HTML 成品放入 `docs/`，图片等资源放入 `docs/images/<slug>/`，相对路径引用。
2. 在 `docs/guides.json` 数组末尾追加一条记录：
   ```json
   {
     "slug": "kailash-kora-2026",
     "title": "2026 冈仁波齐转山行程方案",
     "cover": "images/kailash2.jpg",
     "html": "kailash-kora-2026.html",
     "date": "2026-10",
     "destination": "西藏",
     "days": 13,
     "difficulty": "高海拔徒步",
     "summary": "北京→临汾→拉萨→冈仁波齐转山→返京，13 天全行程",
     "tags": ["转山", "西藏", "高海拔徒步"]
   }
   ```
   字段说明：
   - `slug`：唯一标识，用作资源目录名。
   - `title` / `cover` / `html`：必填，卡片标题、封面图、跳转地址（均为相对路径）。
   - `summary` / `destination` / `tags`：参与汇总页搜索与标签筛选；`tags` 自动聚合为筛选 chips。
   - `date` / `days` / `difficulty`：元信息，为未来卡片布局扩展预留。
3. 推送后 GitHub Pages 自动构建，汇总页即出现新卡片，无需改 `index.html`。

**约定**：
- `cover` 缺省时卡片用主题色渐变占位，不会破版。
- 搜索覆盖 `title` / `summary` / `destination` / `tags`；标签筛选为多选（AND 逻辑）。
- 汇总页 JS 用 `createElement` + `textContent` 渲染，避免注入，无需转义 HTML。
