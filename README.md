# tour_map

一次旅行 → 一份可视化 HTML 行程方案的**制作工作流**。沉淀自 2026 冈仁波齐转山行程方案实战，包含可复用的组件、本地化资源与踩坑清单。

## 结构

```
tour_map/
├── docs/                          # GitHub Pages 部署源（/docs）
│   ├── index.html                 # 入口页（项目导航，由 guides.json 自动生成卡片）
│   ├── guides.json                # 攻略索引（44 篇：3 篇专题 + 31 省 + 10 国）
│   ├── kailash-kora-2026.html     # 专题攻略（冈仁波齐转山）
│   ├── <province>-2026.html       # 31 省 10 天全景攻略（数据生成）
│   ├── <country>-2026.html        # 10 国国际攻略试点（20–30 天，数据生成）
│   ├── WORKFLOW.md                # 制作工作流（权威，下个项目照此执行）
│   ├── images/                    # 景点图片（Unsplash License，本地化，按省/国分目录）
│   ├── fonts/                     # 手写体字体（MaShanZheng 楷书，本地化）
│   └── leaflet/                   # 地图库（Leaflet 本地文件 + 高德瓦片）
├── scripts/
│   ├── build_guide.py             # 攻略 HTML 生成器（JSON → HTML，支持国内/国际双模式）
│   └── data/<slug>.json           # 各省/国攻略数据（结构对齐 beijing.json / japan.json）
└── README.md
```

## 31 省攻略

- 每省一份 10 天 9 晚全景攻略，含交互地图（Leaflet + GCJ-02 纠偏）、景点图鉴、三档预算、备选方案、美食与出行贴士。
- 数据驱动：改 `scripts/data/<province>.json` 后运行 `python3 scripts/build_guide.py` 即可重新生成 HTML。
- 收录于 `docs/guides.json`，门户 `index.html` 自动渲染卡片并支持搜索/标签筛选。

## 国际攻略试点（10 国）

- 首批 10 个热门大国（日本/泰国/土耳其/法国/西班牙/意大利/埃及/美国/澳大利亚/印度），天数按国土面积与可玩性分配（15–30 天），北京出发、人民币预算。
- **国际模式**：JSON 顶层 `"mode": "world"` 即启用——底图自动切换为高德全球瓦片（国内可访问、GCJ-02 坐标系；海外只提供到 z9 级别底图，`maxNativeZoom: 9` 防止放大后请求空白瓦片），标题/文案按实际天数动态生成。
- 样板：`scripts/data/japan.json`（20 天），新国照此结构扩写；运行 `python3 scripts/build_guide.py japan.json` 重渲染。
- 每国含：签证/时差/电源/货币四要素、20 天级逐日时间线、交互地图、景点图鉴、三档预算、备选方案、美食与出行贴士。

## 核心经验

- **资源全本地化**：图片 / 字体 / 地图库全部下载到项目内，不依赖任何 CDN，单文件可离线打开，在中国网络下稳定。
- **高德地图 + GCJ-02**：WGS-84 坐标需转换后再画 marker，否则漂移几百米。
- **三级章节导航**：一级分组 ≤4 个，二级章节，三级小节由 JS 自动从 `h3` 生成。
- **地图侧边节点清单**：每个节点内容直接显示在地图旁，无需点击弹窗。
- **响应式 + 手写体 + 封面图**：手机友好、主题色板 CSS 变量管理。

## 使用

1. 阅读 `docs/WORKFLOW.md`，按 9 步流程执行。
2. 从成品 HTML 复制组件（导航 / 地图 / 返回 TOP / 色板）到新项目。
3. 本地预览：`python3 -m http.server 8899` 后访问（`file://` 无法测试）。

## 许可说明

- 图片来自 Unsplash（Unsplash License，可免费商用/非商用）。
- 字体 Ma Shan Zheng 来自 Google Fonts（SIL OFL 协议）。
- Leaflet 为 BSD-2-Clause 开源库。
