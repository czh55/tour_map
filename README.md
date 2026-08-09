# tour_map

一次旅行 → 一份可视化 HTML 行程方案的**制作工作流**。沉淀自 2026 冈仁波齐转山行程方案实战，包含可复用的组件、本地化资源与踩坑清单。

## 结构

```
tour_map/
├── docs/                          # GitHub Pages 部署源（/docs）
│   ├── index.html                 # 入口页（项目导航）
│   ├── kailash-kora-2026.html      # 实战成品（可离线打开）
│   ├── WORKFLOW.md                # 制作工作流（权威，下个项目照此执行）
│   ├── images/                    # 景点图片（Unsplash License，本地化）
│   ├── fonts/                     # 手写体字体（MaShanZheng 楷书，本地化）
│   └── leaflet/                   # 地图库（Leaflet 本地文件 + 高德瓦片）
└── README.md
```

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
