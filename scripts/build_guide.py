#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tour_map 省份攻略生成器
从 scripts/data/<slug>.json 读取数据，渲染 docs/<slug>.html
结构基于 docs/dalian-2026.html 标准模板
"""
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'scripts', 'data')
OUT_DIR = os.path.join(ROOT, 'docs')

# ============ 通用 CSS（各省仅替换主题变量） ============
CSS = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.75;
    font-size: 15px;
  }
  .wrap { max-width: 860px; min-width: 0; flex: 1 1 auto; padding: 0 20px; }

  /* 左侧固定章节导航 */
  .page { display: flex; justify-content: center; align-items: flex-start; gap: 28px; max-width: 1220px; margin: 0 auto; padding: 0 20px; }
  .side-nav {
    position: sticky; top: 24px; align-self: flex-start;
    flex: 0 0 235px; width: 235px;
    margin-top: 26px;
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 14px 12px; box-shadow: 0 2px 10px rgba(0,0,0,.05);
    max-height: calc(100vh - 48px); overflow-y: auto;
  }
  .side-nav .sn-title { font-family: 'MaShanZheng', 'Kaiti SC', 'STKaiti', 'KaiTi', cursive; font-size: 15px; font-weight: 400; color: var(--red); margin-bottom: 10px; }
  .side-nav .sn-progress { height: 3px; background: var(--line); border-radius: 2px; overflow: hidden; margin-bottom: 10px; }
  .side-nav .sn-progress-bar { height: 100%; width: 0; background: var(--gold); transition: width .1s linear; }
  .side-nav nav.sn-list { display: flex; flex-direction: column; gap: 1px; }
  .side-nav a {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 8px; border-radius: 8px;
    font-size: 12.5px; color: var(--ink); text-decoration: none;
    border-left: 3px solid transparent; line-height: 1.35;
  }
  .side-nav a:hover { background: var(--bg); }
  .side-nav a.active { background: var(--bg); color: var(--red); border-left-color: var(--gold); font-weight: 700; }
  .side-nav .sn-no {
    flex-shrink: 0; width: 20px; height: 20px; border-radius: 6px;
    background: var(--line); color: var(--muted);
    font-size: 11px; font-weight: 700;
    display: inline-flex; align-items: center; justify-content: center;
  }
  .side-nav a.active .sn-no { background: var(--red); color: #fff; }

  /* 一级分组（最多 4 个栏目，手风琴展开） */
  .side-nav .sn-group { margin: 2px 0; }
  .side-nav .sn-g-title {
    display: flex; align-items: center; gap: 7px;
    padding: 6px 8px; border-radius: 8px;
    font-size: 12.5px; font-weight: 800; color: var(--blue);
    cursor: pointer; user-select: none; line-height: 1.35;
    border-left: 3px solid transparent;
  }
  .side-nav .sn-g-title::before {
    content: '▸'; font-size: 10px; color: var(--gold); flex-shrink: 0;
    transition: transform .15s ease;
  }
  .side-nav .sn-group.open > .sn-g-title::before { transform: rotate(90deg); }
  .side-nav .sn-g-title:hover { background: var(--bg); }
  .side-nav .sn-g-title.active { color: var(--red); border-left-color: var(--gold); }
  .side-nav .sn-g-body {
    display: none; padding: 2px 0 8px 4px; margin-left: 9px;
    border-left: 1px dashed var(--line);
  }
  .side-nav .sn-group.open > .sn-g-body { display: block; }

  /* 二级导航（章节下的小节，手风琴展开） */
  .side-nav ul.sn-sub {
    display: none; list-style: none; margin: 2px 0 4px; padding: 0;
  }
  .side-nav a.active + ul.sn-sub { display: block; }
  .side-nav ul.sn-sub a {
    display: block; margin: 1px 0; padding: 4px 8px 4px 14px;
    font-size: 11.5px; color: var(--muted); font-weight: 500;
    border-left: 2px solid var(--line); border-radius: 0 6px 6px 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .side-nav ul.sn-sub a:hover { color: var(--red); background: var(--bg); }
  .side-nav ul.sn-sub a.active { color: var(--red); background: var(--bg); border-left-color: var(--gold); font-weight: 700; }
  .side-nav .sn-back { display: block; margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--line); font-size: 12px; color: var(--muted); text-align: center; }

  /* 右下角一键返回顶部按钮 */
  .back-top {
    position: fixed; right: 22px; bottom: 26px; z-index: 100;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 1px; width: 56px; height: 56px;
    border: none; cursor: pointer;
    background: var(--red); color: #fff;
    border-radius: 50%;
    box-shadow: 0 6px 18px rgba(0,0,0,.38), 0 2px 6px rgba(0,0,0,.15);
    opacity: 0; visibility: hidden; transform: translateY(14px);
    transition: opacity .25s ease, transform .25s ease, visibility .25s, background .2s ease;
  }
  .back-top.show { opacity: 1; visibility: visible; transform: translateY(0); }
  .back-top:hover { background: var(--red-light); }
  .back-top span { font-size: 9px; font-weight: 800; letter-spacing: .5px; line-height: 1; }
  .back-top svg { width: 18px; height: 18px; }
  @media (max-width: 640px) {
    .back-top { right: 14px; bottom: 18px; width: 50px; height: 50px; }
  }

  header {
    position: relative;
    color: #fff;
    padding: 0;
    margin-bottom: 8px;
  }
  header .cover {
    position: relative; height: 300px; overflow: hidden;
    background: linear-gradient(135deg, var(--cover1) 0%, var(--red) 55%, var(--red-light) 140%);
  }
  header .cover img.cover-img {
    position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center 60%;
  }
  header .cover::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(105deg,
      var(--ov1) 0%,
      var(--ov2) 32%,
      var(--ov3) 62%,
      var(--ov4) 100%);
  }
  header .cover::before {
    content: ''; position: absolute; inset: 0; z-index: 2;
    background: linear-gradient(180deg, transparent 62%, var(--bg) 100%);
    pointer-events: none;
  }
  header .cover .cover-inner {
    position: relative; z-index: 3;
    max-width: 860px; margin: 0 auto; padding: 56px 20px 64px;
  }
  header .kicker {
    display: inline-block;
    font-family: 'MaShanZheng', 'Kaiti SC', 'STKaiti', 'KaiTi', cursive;
    font-size: 15px;
    letter-spacing: 3px;
    color: var(--gold);
    border: 1px solid var(--gold);
    background: rgba(0,0,0,.18);
    padding: 4px 14px;
    border-radius: 999px;
    margin-bottom: 14px;
  }
  header h1 {
    font-family: 'MaShanZheng', 'Kaiti SC', 'STKaiti', 'KaiTi', cursive;
    font-size: 34px; font-weight: 400; letter-spacing: 3px; line-height: 1.3;
    text-shadow: 0 2px 14px rgba(0,0,0,.45);
  }
  header .sub {
    margin-top: 12px; font-size: 14px; opacity: .95;
    text-shadow: 0 1px 8px rgba(0,0,0,.4);
  }
  header .meta { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
  header .meta span {
    font-size: 12.5px; background: rgba(0,0,0,.35); backdrop-filter: blur(2px);
    padding: 5px 12px; border-radius: 999px;
    box-shadow: 0 1px 6px rgba(0,0,0,.2);
  }

  nav.toc {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 18px 22px; margin: 26px 0;
  }
  nav.toc h2 { font-size: 15px; color: var(--red); margin-bottom: 10px; }
  nav.toc ol { list-style: none; counter-reset: toc; display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 4px 18px; }
  nav.toc li { counter-increment: toc; font-size: 13.5px; }
  nav.toc a { color: var(--blue); text-decoration: none; display: block; padding: 3px 0; border-radius: 6px; }
  nav.toc a::before { content: counter(toc) ". "; color: var(--gold); font-weight: 700; margin-right: 4px; }
  nav.toc a:hover { background: var(--bg); color: var(--red); }

  section { margin: 40px 0; }
  h2.sec {
    font-family: 'MaShanZheng', 'Kaiti SC', 'STKaiti', 'KaiTi', cursive;
    font-size: 24px; font-weight: 400;
    color: var(--red);
    padding-bottom: 10px; border-bottom: 2px solid var(--gold);
    margin-bottom: 18px; display: flex; align-items: center; gap: 10px;
  }
  h2.sec .no {
    background: var(--red); color: #fff; font-size: 14px;
    width: 28px; height: 28px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  h3 { font-size: 16.5px; color: var(--blue); margin: 22px 0 10px; }
  p { margin: 8px 0; }
  ul, ol { padding-left: 22px; margin: 8px 0; }
  li { margin: 4px 0; }
  strong { color: var(--red); }
  em { color: var(--muted); }

  .callout { border-radius: 12px; padding: 16px 18px; margin: 16px 0; font-size: 14.5px; }
  .callout.key { background: var(--key-bg); border-left: 4px solid var(--gold); }
  .callout.warn { background: #fdecea; border-left: 4px solid #c62828; }
  .callout.info { background: var(--info-bg); border-left: 4px solid var(--blue); }
  .callout .t { font-weight: 700; display: block; margin-bottom: 4px; }
  .badge { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 9px; border-radius: 999px; white-space: nowrap; }
  .badge.must { background: var(--red); color: #fff; }
  .badge.nice { background: var(--info-bg); color: var(--blue); border: 1px solid var(--line); }
  .badge.skip { background: #f0ece6; color: var(--muted); }

  /* ===== 景点图鉴画廊 ===== */
  .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin: 16px 0; }
  .spot-card {
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    overflow: hidden; display: flex; flex-direction: column;
    transition: transform .2s ease, box-shadow .2s ease;
  }
  .spot-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(0,0,0,.10); }
  .spot-card .sc-img {
    position: relative; width: 100%; height: 190px; overflow: hidden; background: var(--info-bg);
  }
  .spot-card .sc-img img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .3s ease; }
  .spot-card:hover .sc-img img { transform: scale(1.05); }
  .spot-card .sc-img .sc-tag {
    position: absolute; top: 10px; left: 10px; z-index: 1;
    font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px;
    color: #fff; box-shadow: 0 2px 6px rgba(0,0,0,.25);
  }
  .sc-tag.must { background: var(--red); }
  .sc-tag.nice { background: var(--blue); }
  .sc-tag.skip { background: #7a6f68; }
  .spot-card .sc-body { padding: 12px 14px 14px; display: flex; flex-direction: column; flex: 1; }
  .spot-card .sc-name { font-size: 16px; font-weight: 800; color: var(--red); }
  .spot-card .sc-name small { font-size: 11.5px; color: var(--muted); font-weight: 500; margin-left: 6px; }
  .spot-card .sc-feat { margin-top: 6px; font-size: 13px; color: var(--ink); line-height: 1.6; flex: 1; }
  .spot-card .sc-feat b { color: var(--gold); font-weight: 700; }
  .spot-card .sc-meta { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--line); font-size: 12px; color: var(--muted); line-height: 1.6; }
  .gallery-note { font-size: 12.5px; color: var(--muted); margin: 6px 0 2px; }

  /* ===== Interactive Map ===== */
  .map-wrap { display: flex; gap: 14px; align-items: flex-start; margin: 12px 0; }
  .map-wrap .map-container { flex: 1 1 auto; min-width: 0; margin: 0; }
  .map-container { height: 480px; border-radius: 12px; border: 1px solid var(--line); z-index: 0; }
  .map-fallback {
    height: 100%; display: flex; align-items: center; justify-content: center;
    background: var(--info-bg); color: var(--muted); font-size: 14px; text-align: center; padding: 20px;
  }

  /* 地图侧边节点清单 */
  .map-sidebar {
    width: 320px; flex-shrink: 0;
    max-height: 480px; overflow-y: auto;
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 12px 14px;
  }
  .map-sidebar::-webkit-scrollbar { width: 8px; }
  .map-sidebar::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
  .side-title { font-size: 13px; font-weight: 700; color: var(--blue); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
  .side-item { display: flex; gap: 10px; padding: 9px 4px; border-bottom: 1px dashed var(--line); cursor: pointer; border-radius: 8px; transition: background .15s; }
  .side-item:hover { background: var(--bg); }
  .side-item.active { background: var(--bg); box-shadow: inset 3px 0 0 var(--gold); }
  .side-item:last-child { border-bottom: none; }
  .side-num {
    width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0; margin-top: 1px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff; background: var(--red);
  }
  .side-item.nice .side-num { background: var(--blue); }
  .side-item.skip .side-num { background: #8d8379; }
  .side-main { min-width: 0; }
  .side-name { font-size: 14px; font-weight: 700; color: var(--red); display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .side-item.nice .side-name { color: var(--blue); }
  .side-item.skip .side-name { color: var(--muted); }
  .side-meta { font-size: 12.5px; color: var(--muted); margin-top: 2px; }
  .side-note { font-size: 12.5px; color: var(--ink); margin-top: 2px; line-height: 1.5; }

  .map-pin {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff;
    border: 2px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,.45);
  }
  .map-pin.must { background: var(--red); }
  .map-pin.nice { background: var(--blue); }
  .map-pin.skip { background: #8d8379; }
  .map-pop h4 { color: var(--red); margin-bottom: 2px; font-size: 14px; }
  .map-pop p { margin: 2px 0; font-size: 12.5px; line-height: 1.55; }
  .map-pop .tag { display: inline-block; font-size: 11px; font-weight: 700; padding: 1px 7px; border-radius: 999px; margin-top: 3px; }
  .map-pop .tag.must { background: var(--red); color: #fff; }
  .map-pop .tag.nice { background: var(--info-bg); color: var(--blue); }
  .map-pop .tag.skip { background: #f0ece6; color: #6b5f58; }
  .map-legend {
    background: rgba(255,255,255,.95); border-radius: 8px; padding: 8px 11px;
    font-size: 12px; line-height: 1.7; box-shadow: 0 1px 5px rgba(0,0,0,.25);
  }
  .map-legend b { display: block; margin-bottom: 2px; color: var(--blue); }
  .map-legend .sw { display: inline-block; width: 18px; height: 4px; border-radius: 2px; margin-right: 6px; vertical-align: middle; }
  .map-legend .sw.dash { border-top: 3px dashed #9e9e9e; background: none; height: 0; }
  .map-note { font-size: 13px; color: var(--muted); margin: 6px 0 4px; }
  .leaflet-container { font: inherit; }

  .table-scroll { overflow-x: auto; border-radius: 12px; border: 1px solid var(--line); }
  table { border-collapse: collapse; width: 100%; font-size: 14px; background: var(--card); }
  th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--line); vertical-align: top; }
  th { background: var(--red); color: #fff; font-weight: 600; white-space: nowrap; }
  tr:last-child td { border-bottom: none; }
  tbody tr:nth-child(even) { background: var(--bg); }
  td.c { text-align: center; }

  .timeline { list-style: none; padding: 0; }
  .timeline li { position: relative; padding: 10px 0 10px 30px; border-left: 2px solid var(--line); margin-left: 8px; }
  .timeline li::before {
    content: ""; position: absolute; left: -7px; top: 17px;
    width: 12px; height: 12px; border-radius: 50%;
    background: var(--gold); border: 2px solid var(--card);
  }
  .timeline .when { font-weight: 700; color: var(--red); display: block; font-size: 13.5px; }
  .timeline .what { font-size: 14px; }

  /* ===== 逐小时时间线 ===== */
  .hourline { margin: 14px 0; }
  .hourline .day {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    margin: 14px 0; overflow: hidden;
  }
  .hourline .day-head {
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    background: linear-gradient(90deg, var(--head-bg), transparent);
    padding: 12px 16px; border-bottom: 1px solid var(--line);
  }
  .hourline .day-head .d-date { font-weight: 800; color: var(--red); font-size: 15.5px; }
  .hourline .day-head .d-desc { color: var(--ink); font-size: 13.5px; }
  .hourline .day-head .d-tag {
    margin-left: auto; background: var(--red); color: #fff;
    font-size: 11.5px; font-weight: 700; padding: 2px 10px; border-radius: 999px; white-space: nowrap;
  }
  .hourline .day-head .d-tag.alt { background: var(--blue); }
  .hourline .day-head .d-tag.return { background: #2e7d32; }
  .hourline .day-head .d-tag.night { background: #5a3ea8; }
  .hourline table { margin: 0; border: none; }
  .hourline th { background: transparent; color: var(--muted); font-size: 12px; padding: 8px 12px; border-bottom: 1px solid var(--line); }
  .hourline td { padding: 8px 12px; font-size: 13.5px; border-bottom: 1px dashed var(--line); vertical-align: top; }
  .hourline tbody tr:last-child td { border-bottom: none; }
  .hourline tbody tr:nth-child(even) { background: var(--bg); }
  .hourline td.t-time { white-space: nowrap; font-weight: 700; color: var(--blue); font-variant-numeric: tabular-nums; }
  .hourline td.t-what { color: var(--ink); }
  .hourline td.t-what b { color: var(--red); }
  .hourline .hl-note { font-size: 12.5px; color: var(--muted); padding: 8px 16px; border-top: 1px solid var(--line); background: var(--bg); }

  .gear { columns: 2; column-gap: 26px; }
  .gear h3 { break-inside: avoid; margin-top: 8px; }
  .gear ul { list-style: none; padding-left: 0; }
  .gear ul li { padding-left: 20px; position: relative; font-size: 13.8px; }
  .gear ul li::before { content: "✓"; position: absolute; left: 0; color: var(--red-light); font-weight: 700; }

  .route-chain {
    display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
    gap: 8px; margin: 14px 0; font-size: 14.5px;
  }
  .route-chain .node {
    background: var(--card); border: 1px solid var(--line); border-radius: 999px;
    padding: 6px 16px; font-weight: 600; color: var(--blue);
  }
  .route-chain .node.hl { background: var(--red); color: #fff; border-color: var(--red); }
  .route-chain .arrow { color: var(--gold); font-weight: 700; }

  footer { margin-top: 50px; padding: 26px 0 40px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12.5px; text-align: center; }
  @media (max-width: 1080px) {
    .page { display: block; padding: 0; }
    .side-nav { display: none; }
    .wrap { margin: 0 auto; }
  }
  @media (max-width: 860px) {
    .map-wrap { flex-direction: column; }
    .map-sidebar { width: 100%; max-height: none; }
    header .cover { height: 240px; }
    header .cover .cover-inner { padding: 40px 20px 52px; }
    header h1 { font-size: 27px; }
    header .cover img.cover-img { object-position: center 55%; }
  }
  @media (max-width: 640px) {
    header h1 { font-size: 22px; }
    .gear { columns: 1; }
  }
  @media print {
    body { background: #fff; }
    nav.toc, header .meta, .side-nav { display: none; }
    section { break-inside: avoid; }
  }
"""

# ============ 通用 JS（地图 + 导航 + 返回顶部） ============
JS_TEMPLATE = """
(function () {
  var body = document.body;
  var IS_WORLD = __WORLD_MODE__;

  function showFallback(mapId, msg) {
    var el = document.getElementById(mapId);
    if (el) {
      el.innerHTML = '<div class="map-fallback">' + msg + '</div>';
    }
  }

  function initMaps() {
    if (typeof L === 'undefined') {
      showFallback('mapMain', '地图库未加载（leaflet/ 本地文件缺失或损坏），请确认 leaflet.min.js 存在。');
      return;
    }

    function makeBaseLayer() {
      if (IS_WORLD) {
        // 腾讯地图全球瓦片（GCJ-02，国内可访问，覆盖国外）
        return L.tileLayer('https://rt{s}.map.gtimg.com/tile?z={z}&x={x}&y={y}&styleid=3&version=353', {
          maxZoom: 18,
          subdomains: ['0', '1', '2', '3'],
          attribution: '© 腾讯地图'
        });
      }
      return L.tileLayer('https://webrd{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', {
        maxZoom: 18,
        subdomains: ['01', '02', '03', '04'],
        attribution: '© 高德地图'
      });
    }

    // WGS-84 → GCJ-02（火星坐标）纠偏；腾讯/高德瓦片均为 GCJ-02，统一纠偏
    function transformLat(x, y) {
      var ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
      ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
      ret += (20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0;
      ret += (160.0 * Math.sin(y / 12.0 * Math.PI) + 320.0 * Math.sin(y * Math.PI / 30.0)) * 2.0 / 3.0;
      return ret;
    }
    function transformLng(x, y) {
      var ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
      ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
      ret += (20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0;
      ret += (150.0 * Math.sin(x / 12.0 * Math.PI) + 300.0 * Math.sin(x / 30.0 * Math.PI)) * 2.0 / 3.0;
      return ret;
    }
    function toGCJ(lat, lng) {
      var a = 6378245.0, ee = 0.00669342162296594323;
      var dLat = transformLat(lng - 105.0, lat - 35.0);
      var dLng = transformLng(lng - 105.0, lat - 35.0);
      var radLat = lat / 180.0 * Math.PI;
      var magic = Math.sin(radLat);
      magic = 1 - ee * magic * magic;
      var sqrtMagic = Math.sqrt(magic);
      dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
      dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI);
      return [lat + dLat, lng + dLng];
    }

    function pin(num, prio) {
      return L.divIcon({
        className: '',
        html: '<div class="map-pin ' + prio + '">' + num + '</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13],
        popupAnchor: [0, -14]
      });
    }
    function popHtml(html) {
      return '<div class="map-pop">' + html + '</div>';
    }
    function tag(cls, label) { return '<span class="tag ' + cls + '">' + label + '</span>'; }

    function renderSidebar(sidebarId, spots, mapRef, markerRefs) {
      var el = document.getElementById(sidebarId);
      if (!el) return;
      var items = spots.map(function (s, i) {
        var label = s.prio === 'must' ? '必去' : (s.prio === 'nice' ? '顺路' : '可跳过');
        var meta = [];
        if (s.h) meta.push('海拔 ' + s.h);
        if (s.fee) meta.push('门票 ' + s.fee);
        meta.push(s.t);
        var elItem = document.createElement('div');
        elItem.className = 'side-item ' + s.prio;
        elItem.setAttribute('data-idx', i);
        elItem.innerHTML = '<span class="side-num">' + s.num + '</span>' +
          '<div class="side-main">' +
            '<div class="side-name">' + s.name + '<span class="badge ' + s.prio + '">' + label + '</span></div>' +
            '<div class="side-meta">' + meta.join(' · ') + '</div>' +
            '<div class="side-note">' + s.note + '</div>' +
          '</div>';
        return elItem;
      });
      el.innerHTML = '';
      var title = document.createElement('div');
      title.className = 'side-title';
      title.textContent = '📍 节点清单（点击可在地图定位）';
      el.appendChild(title);
      items.forEach(function (item) {
        el.appendChild(item);
        item.addEventListener('click', function () {
          var idx = parseInt(item.getAttribute('data-idx'), 10);
          var mk = markerRefs[idx];
          if (!mk) return;
          setActive(idx);
          mapRef.panTo(mk.getLatLng());
          mk.openPopup();
        });
      });
      function setActive(idx) {
        items.forEach(function (x, i) { x.classList.toggle('active', i === idx); });
      }
      markerRefs.forEach(function (mk, i) {
        mk.on('popupopen', function () {
          setActive(i);
          items[i].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        });
      });
    }

    // ---- 全省地图 ----
    var mapMain = L.map('mapMain', { scrollWheelZoom: true }).addLayer(makeBaseLayer());

    // 路线：分段着色 [坐标数组(WGS-84), 颜色, 宽度, 名称]，渲染时统一纠偏
    var routes = __ROUTES__;
    routes.forEach(function (r) {
      var pts = r.pts.map(function (p) { return toGCJ(p[0], p[1]); });
      L.polyline(pts, { color: r.c, weight: r.d, opacity: 0.85 }).addTo(mapMain).bindPopup(popHtml('<h4>' + r.n + '</h4>'));
    });

    // 沿途景点
    var spotsMain = __SPOTS__;
    var mainMarkers = [];
    spotsMain.forEach(function (s) {
      var p = toGCJ(s.lat, s.lng);
      var mk = L.marker(p, { icon: pin(s.num, s.prio) }).addTo(mapMain)
        .bindPopup(popHtml('<h4>' + s.name + '</h4>' +
          '<p><strong>时间：</strong>' + s.t + '</p>' +
          '<p><strong>门票：</strong>' + s.fee + '</p>' +
          '<p>' + s.note + '</p>' + tag(s.prio, s.prio === 'must' ? '必去' : (s.prio === 'nice' ? '顺路' : '可跳过'))));
      mainMarkers.push(mk);
    });
    renderSidebar('sidebarMain', spotsMain, mapMain, mainMarkers);

    mapMain.fitBounds(__FIT__);

    var legendHtml = __LEGEND__;
    var legendControl = L.control({ position: 'bottomright' });
    legendControl.onAdd = function () {
      var div = L.DomUtil.create('div', '');
      div.innerHTML = legendHtml;
      return div;
    };
    legendControl.addTo(mapMain);
  }

  initMaps();

  // ---- 左侧章节导航：4 个一级分组 + 二级章节 + 三级小节 + 阅读进度 ----
  (function () {
    var nav = document.getElementById('sideNav');
    var bar = document.getElementById('snProgress');
    if (!nav) return;

    var subs = Array.prototype.slice.call(nav.querySelectorAll('ul.sn-sub[data-sub]'));
    subs.forEach(function (ul) {
      var sp = ul.getAttribute('data-sub');
      var sec = document.getElementById(sp);
      if (!sec) return;
      var hs = sec.querySelectorAll('h3');
      Array.prototype.forEach.call(hs, function (h, i) {
        if (!h.id) h.id = sp + '-h' + (i + 1);
        var a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent.replace(/\\s+/g, ' ').trim();
        a.title = a.textContent;
        a.dataset.sub = h.id;
        var li = document.createElement('li');
        li.appendChild(a);
        ul.appendChild(li);
      });
      if (!ul.children.length) ul.parentNode.removeChild(ul);
    });

    var groups = Array.prototype.slice.call(nav.querySelectorAll('.sn-group'));
    var links = Array.prototype.slice.call(nav.querySelectorAll('a[data-sp]'));
    var secs = links.map(function (a) { return a.getAttribute('data-sp'); });
    var subLinks = Array.prototype.slice.call(nav.querySelectorAll('ul.sn-sub a[data-sub]'));

    function docTop(el) { return el.getBoundingClientRect().top + window.scrollY; }

    function currentId() {
      var y = window.scrollY + 130;
      var cur = secs[0];
      for (var i = 0; i < secs.length; i++) {
        var el = document.getElementById(secs[i]);
        if (!el) continue;
        if (docTop(el) <= y) cur = secs[i];
        else break;
      }
      return cur;
    }

    function currentSub(sp) {
      var sec = document.getElementById(sp);
      if (!sec) return null;
      var hs = sec.querySelectorAll('h3');
      var y = window.scrollY + 140;
      var cur = null;
      for (var i = 0; i < hs.length; i++) {
        if (!hs[i].id) continue;
        if (docTop(hs[i]) <= y) cur = hs[i].id;
        else break;
      }
      return cur;
    }

    function groupFor(sp) {
      for (var i = 0; i < groups.length; i++) {
        if (groups[i].querySelector('a[data-sp="' + sp + '"]')) return groups[i];
      }
      return null;
    }

    function syncGroups(openId) {
      groups.forEach(function (grp) {
        var open = grp === openId;
        grp.classList.toggle('open', open);
        var t = grp.querySelector('.sn-g-title');
        if (t) t.classList.toggle('active', open);
      });
    }

    function update() {
      var cur = currentId();
      syncGroups(groupFor(cur));
      links.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('data-sp') === cur);
      });
      var activeSub = cur ? currentSub(cur) : null;
      subLinks.forEach(function (a) {
        a.classList.toggle('active', a.dataset.sub === activeSub);
      });
      if (bar) {
        var doc = document.documentElement;
        var max = doc.scrollHeight - window.innerHeight;
        var p = max > 0 ? (window.scrollY / max) * 100 : 0;
        bar.style.width = p.toFixed(1) + '%';
      }
    }

    Array.prototype.forEach.call(nav.querySelectorAll('.sn-g-title'), function (t) {
      t.addEventListener('click', function () {
        var grp = t.parentNode;
        var wasOpen = grp.classList.contains('open');
        groups.forEach(function (g2) { g2.classList.remove('open'); });
        if (!wasOpen) grp.classList.add('open');
        var cur = currentId();
        var g = groupFor(cur);
        groups.forEach(function (grp2) {
          var tt = grp2.querySelector('.sn-g-title');
          if (tt) tt.classList.toggle('active', grp2 === g);
        });
      });
    });

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  })();

  // ---- 右下角一键返回顶部 ----
  (function () {
    var btn = document.getElementById('backTop');
    if (!btn) return;
    var SHOW_AFTER = 320;
    function onScroll() {
      btn.classList.toggle('show', window.scrollY > SHOW_AFTER);
    }
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  })();
})();
"""


def build_sidebar(days):
    """固定 4 组导航"""
    sec2 = '推荐行程 · %d 天版' % days
    groups = [
        ('行程规划', [('s1', '1', '核心结论'), ('s2', '2', sec2), ('s3', '3', '逐小时时间线')]),
        ('沿途看点', [('s4', '4', '景点图鉴'), ('s5', '5', '路线地图')]),
        ('费用备选', [('s6', '6', '预算明细'), ('s7', '7', '备选方案')]),
        ('准备与应对', [('s8', '8', '交通与住宿'), ('s9', '9', '美食清单'), ('s10', '10', '出行贴士')]),
    ]
    out = []
    for title, items in groups:
        out.append('      <div class="sn-group">')
        out.append('        <div class="sn-g-title">%s</div>' % title)
        out.append('        <div class="sn-g-body">')
        for sp, no, name in items:
            out.append('          <a href="#%s" data-sp="%s"><span class="sn-no">%s</span>%s</a><ul class="sn-sub" data-sub="%s"></ul>' % (sp, sp, no, name, sp))
        out.append('        </div>')
        out.append('      </div>')
    return '\n'.join(out)


def build_toc(days):
    sec2 = '推荐行程 · %d 天版' % days
    items = ['核心结论', sec2, '逐小时时间线', '景点图鉴', '路线地图',
             '预算明细（三档）', '备选方案', '交通与住宿', '美食清单', '出行贴士']
    out = ['    <h2>目录</h2>', '    <ol>']
    for i, name in enumerate(items, 1):
        out.append('      <li><a href="#s%d">%s</a></li>' % (i, name))
    out.append('    </ol>')
    return '\n'.join(out)


def esc(s):
    """转义 HTML 特殊字符"""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_route_chain(nodes):
    out = []
    for i, n in enumerate(nodes):
        if isinstance(n, dict):
            label = n['n']
            hl = n.get('hl', False)
        else:
            label, hl = n, False
        cls = ' node hl' if hl else ''
        out.append('<span class="node%s">%s</span>' % (cls, label))
        if i < len(nodes) - 1:
            out.append('<span class="arrow">→</span>')
    return '\n      '.join(out)


def build_table(headers, rows):
    out = ['<div class="table-scroll"><table>', '<thead><tr>']
    for h in headers:
        out.append('<th>%s</th>' % h)
    out.append('</tr></thead><tbody>')
    for row in rows:
        out.append('<tr>')
        for c in row:
            out.append('<td>%s</td>' % c)
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def build_hourline(days):
    out = ['    <div class="hourline">']
    for d in days:
        tag_cls = d.get('tagClass', '')
        out.append('      <div class="day">')
        out.append('        <div class="day-head">')
        out.append('          <span class="d-date">%s</span>' % d['date'])
        out.append('          <span class="d-desc">%s</span>' % d['desc'])
        out.append('          <span class="d-tag %s">%s</span>' % (tag_cls, d['tag']))
        out.append('        </div>')
        out.append('        <div class="table-scroll"><table>')
        out.append('          <thead><tr><th>时间</th><th>事项</th></tr></thead><tbody>')
        for t, w in d['rows']:
            out.append('          <tr><td class="t-time">%s</td><td class="t-what">%s</td></tr>' % (t, w))
        out.append('          </tbody></table></div>')
        if d.get('note'):
            out.append('        <div class="hl-note">%s</div>' % d['note'])
        out.append('      </div>')
    out.append('    </div>')
    return '\n'.join(out)


def build_gallery(spots):
    out = ['    <div class="gallery">']
    prio_map = {'must': '必去', 'nice': '顺路', 'skip': '可跳过'}
    for s in spots:
        out.append('      <div class="spot-card">')
        if s.get('img'):
            out.append('        <div class="sc-img"><img src="%s" alt="%s" loading="lazy"><span class="sc-tag %s">%s</span></div>'
                       % (s['img'], s['name'], s['prio'], prio_map[s['prio']]))
        else:
            out.append('        <div class="sc-img"><span class="sc-tag %s">%s</span></div>' % (s['prio'], prio_map[s['prio']]))
        out.append('        <div class="sc-body">')
        out.append('          <div class="sc-name">%s <small>%s</small></div>' % (s['name'], s['fee']))
        out.append('          <div class="sc-feat">%s</div>' % s['feat'])
        out.append('          <div class="sc-meta">%s</div>' % s['meta'])
        out.append('        </div>')
        out.append('      </div>')
    out.append('    </div>')
    return '\n'.join(out)


def build_gear(food):
    """美食双栏 + 行前清单双栏"""
    out = ['    <div class="gear">']
    # 两列
    cols = [food[i::2] for i in range(2)] if len(food) > 2 else [food, []]
    if len(food) == 1:
        cols = [food, []]
    for col in cols:
        out.append('      <div>')
        for h in col:
            out.append('        <h3>%s</h3>' % h['h'])
            out.append('        <ul>')
            for item in h['items']:
                out.append('          <li>%s</li>' % item)
            out.append('        </ul>')
        out.append('      </div>')
    out.append('    </div>')
    return '\n'.join(out)


def build_checklist(cols):
    out = ['    <div class="gear">']
    for col in cols:
        out.append('      <ul>')
        for item in col:
            out.append('        <li>%s</li>' % item)
        out.append('      </ul>')
    out.append('    </div>')
    return '\n'.join(out)


def render(d):
    # ---- 主题色 ----
    t = d.get('theme', {})
    theme_css = '\n'.join('    --%s: %s;' % (k, v) for k, v in t.items())

    # ---- 地图数据（JSON 注入 JS）----
    world_mode = 'true' if d.get('mode') == 'world' else 'false'
    routes_js = json.dumps(d['routes'], ensure_ascii=False, indent=2)
    spots_js = json.dumps(d['spotsMain'], ensure_ascii=False, indent=2)
    fit_js = json.dumps(d.get('mapFit', [[30, 100], [40, 125]]), ensure_ascii=False)
    legend_html = d.get('mapLegend', '')
    legend_js = json.dumps(legend_html, ensure_ascii=False)

    js = (JS_TEMPLATE
          .replace('__WORLD_MODE__', world_mode)
          .replace('__ROUTES__', routes_js)
          .replace('__SPOTS__', spots_js)
          .replace('__FIT__', fit_js)
          .replace('__LEGEND__', legend_js))

    # ---- 章节内容 ----
    s1 = (
        '<div class="route-chain">\n      ' + build_route_chain(d['routeChain']) + '\n    </div>\n\n'
        + ('<div class="callout key">\n      <span class="t">%s</span>\n      %s\n    </div>\n\n' % (d['coreTitle'], d['coreBody']))
        + build_table(['事项', '结论'], d['coreTable']) + '\n\n'
        + ('<div class="callout warn">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['warnTitle'], d['warnBody']))
    )

    s2 = ('<p>%s</p>\n\n' % d['planIntro']) + build_table(['日期', '行程', '过夜地', '主题'], d['planRows'])
    if d.get('planInfo'):
        s2 += '\n\n    <div class="callout info">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['planInfo']['t'], d['planInfo']['b'])

    s3 = '<p>以下为 %d 天全程的逐小时执行时间线，可当作「当天打开照着走」的清单。标注 <b>※</b> 的可选项视体力与天气取舍。</p>\n\n' % len(d['days']) + build_hourline(d['days'])

    s4 = ('<p>必去（<span class="badge must">必去</span>）/ 顺路（<span class="badge nice">顺路</span>）/ 可跳过（<span class="badge skip">可跳过</span>）。</p>\n\n'
          + build_gallery(d['spots'])
          + ('<p class="gallery-note">%s</p>' % d['galleryNote'] if d.get('galleryNote') else ''))

    s5 = ('<p class="map-note">点击左侧节点可在地图上定位；点击地图 marker 会高亮对应节点。坐标为 WGS-84 转 GCJ-02 纠偏后标注。</p>\n\n'
          + '    <div class="map-wrap">\n      <div id="mapMain" class="map-container"></div>\n      <aside class="map-sidebar" id="sidebarMain"></aside>\n    </div>')

    s6 = ('<p>%s</p>\n\n' % d['budgetNote'])
    bh = d['budgetTable'][0]
    br = d['budgetTable'][1:]
    s6 += build_table(bh, br)
    if d.get('budgetExample'):
        s6 += '\n\n    <div class="callout key">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['budgetExample']['t'], d['budgetExample']['b'])

    s7_parts = []
    for a in d['alternatives']:
        s7_parts.append('<h3>%s</h3>\n' % a['h'])
        if a['type'] == 'p':
            s7_parts.append('<p>%s</p>' % a['c'])
        elif a['type'] == 'ul':
            s7_parts.append('<ul>')
            for li in a['c']:
                s7_parts.append('  <li>%s</li>' % li)
            s7_parts.append('</ul>')
    s7 = '\n\n    '.join(s7_parts)

    s8 = '<h3>%s</h3>\n\n' % d['transportTitle']
    th = d['transportTable'][0]
    tr = d['transportTable'][1:]
    s8 += build_table(th, tr)
    if d.get('transportWarn'):
        s8 += '\n\n    <div class="callout warn">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['transportWarn']['t'], d['transportWarn']['b'])
    s8 += '\n\n    <h3>%s</h3>\n    <ul>' % d['cityTransportTitle']
    for li in d['cityTransport']:
        s8 += '\n      <li>%s</li>' % li
    s8 += '\n    </ul>\n\n    <h3>%s</h3>\n\n' % d['stayTitle']
    sh = d['stayTable'][0]
    sr = d['stayTable'][1:]
    s8 += build_table(sh, sr)

    s9 = build_gear(d['food'])
    if d.get('foodWarn'):
        s9 += '\n\n    <div class="callout warn">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['foodWarn']['t'], d['foodWarn']['b'])

    s10 = '<h3>10.1 行前清单</h3>\n' + build_checklist(d['checklist'])
    if d.get('pitfalls'):
        s10 += '\n\n    <h3>10.2 防踩坑</h3>\n    <div class="callout info">\n      <span class="t">%s</span>\n      %s\n    </div>' % (d['pitfalls']['t'], d['pitfalls']['b'])
    if d.get('summary'):
        s10 += '\n\n    <div class="callout key">\n      <span class="t">🌟 一句话总结</span>\n      %s\n    </div>' % d['summary']

    sections = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
    default_sec_titles = ['核心结论', '推荐行程 · %d 天版' % len(d['days']), '逐小时时间线', '景点图鉴', '路线地图',
                          '预算明细（三档）', '备选方案', '交通与住宿', '美食清单', '出行贴士']
    sec_titles = d.get('secTitles', default_sec_titles)
    sec_html = []
    for i, body in enumerate(sections, 1):
        sec_html.append('  <!-- ============ %d ============ -->\n  <section id="s%d">\n    <h2 class="sec"><span class="no">%d</span>%s</h2>\n\n    %s\n  </section>'
                        % (i, i, i, sec_titles[i - 1], body))
    sections_html = '\n\n'.join(sec_html)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="leaflet/leaflet.min.css" />
<script src="leaflet/leaflet.min.js"></script>
<style>
  /* 标题手写体（马善政楷书，本地加载） */
  @font-face {{
    font-family: 'MaShanZheng';
    src: url('fonts/MaShanZheng-Regular.ttf') format('truetype');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
  }}
  :root {{
{theme_css}
  }}
{css}
</style>
</head>
<body>

<header>
  <div class="cover">
    <img class="cover-img" src="{cover}" alt="{province}旅游" loading="eager">
    <div class="cover-inner">
      <div class="kicker">{kicker}</div>
      <h1>{h1}</h1>
      <div class="sub">{sub}</div>
      <div class="meta">
{meta}
      </div>
    </div>
  </div>
</header>

<div class="page">

  <aside class="side-nav" id="sideNav">
    <div class="sn-title">📖 章节导航</div>
    <div class="sn-progress"><div class="sn-progress-bar" id="snProgress"></div></div>
    <nav class="sn-list">
{sidebar}
    </nav>
    <a class="sn-back" href="#">↑ 回到顶部</a>
  </aside>

<div class="wrap">

  <nav class="toc">
{toc}
  </nav>

{sections_html}

  <footer>
    本方案信息基于 2026-08 网络公开资料整理。价格、班次、开放政策会变化，出行前 1 个月请重新核实。<br>
    ✦ 图片来自 Unsplash（Unsplash License），部分为同主题示意图 ✦
  </footer>

</div>
</div>

<button id="backTop" class="back-top" title="返回顶部" aria-label="返回顶部">
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg>
  <span>TOP</span>
</button>

<script>
{js}
</script>
</body>
</html>
""".format(
        title=d['title'],
        theme_css=theme_css,
        css=CSS,
        cover=d['cover'],
        province=d.get('province', d['slug']),
        kicker=d['kicker'],
        h1=d['h1'],
        sub=d['sub'],
        meta='\n'.join('        <span>%s</span>' % m for m in d['meta']),
        sidebar=build_sidebar(len(d['days'])),
        toc=build_toc(len(d['days'])),
        sections_html=sections_html,
        js=js,
    )
    return html


def main():
    files = sys.argv[1:] or sorted(f for f in os.listdir(DATA_DIR) if f.endswith('.json'))
    for f in files:
        f = os.path.basename(f)
        path = os.path.join(DATA_DIR, f)
        with open(path, encoding='utf-8') as fp:
            d = json.load(fp)
        html = render(d)
        out = os.path.join(OUT_DIR, d['html'])
        with open(out, 'w', encoding='utf-8') as fp:
            fp.write(html)
        print('✓ %s -> %s (%d KB)' % (d['slug'], out, len(html) // 1024))


if __name__ == '__main__':
    main()
