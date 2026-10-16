# 广西12校双选会日历

面向 12 所广西公办本科高校的**校园双选会信息汇总网站**，数据来自各校官网就业信息网 / 官方就业平台公告，由 **GitHub Actions 每天 08:00（北京时间）自动抓取更新**，托管于 GitHub Pages。

## 覆盖高校（固定 12 所）

广西大学、广西科技大学、桂林电子科技大学、广西师范大学、南宁师范大学、桂林理工大学、广西民族大学、广西财经学院、广西科技师范学院、北部湾大学、广西工业学院、桂林航天工业学院。

## 网站功能

- 按日期时间轴展示未来已公布的双选会 / 招聘会（含线上网络双选会、自治区级专场）
- 每条信息附**举办日期、线上/线下、地点、官方公告链接**
- 支持按学校筛选、关键词搜索、近 7 天 / 线上视图、日期 / 学校两种排序
- 展示 12 所高校核查状态（每所必查、无遗漏）
- 移动端优先，电脑 / 手机均可使用

## 目录结构

```
├── index.html                 # 页面结构
├── style.css                  # 样式（移动优先）
├── app.js                     # 前端逻辑（内置快照兜底，线上优先读 data/jobfairs.json）
├── data/
│   └── jobfairs.json          # 双选会数据（每日自动更新）
├── scripts/
│   └── fetch_jobfairs.py      # 抓取脚本（Playwright 渲染 + requests 降级）
├── .github/workflows/
│   └── update-data.yml        # 每日定时抓取并提交数据
└── requirements.txt
```

## 每日自动更新

`.github/workflows/update-data.yml` 每天 00:00 UTC（北京时间 08:00）运行：

1. 安装依赖（requests / beautifulsoup4 / Playwright + Chromium）
2. 运行 `scripts/fetch_jobfairs.py` 抓取 12 所高校就业网
3. 有变化则自动提交 `data/jobfairs.json`，GitHub Pages 随之更新

也可在仓库 **Actions → 每日更新双选会数据 → Run workflow** 手动触发。

## 抓取脚本说明

`scripts/fetch_jobfairs.py` 为每所高校配置了入口 URL 与质量守卫：

- **平台适配**：新锦成 / 云就业（bysjy.com.cn）、24365 广西毕业生就业网（gxbys.com）、就业宝（jiuyeb.cn）、各校官网通知公告
- **JS 渲染**：优先 Playwright 无头浏览器渲染后解析；未安装时自动降级 requests 静态抓取
- **质量守卫**：
  - 跨校过滤：标题含其他高校名的场次剔除（防聚合平台混入）
  - 往届过滤：标题含"20XX届"且非 2027/2028 届、含"已举办"、含过去日期的历史场次剔除
  - 时间窗口：只保留举办日期 ≥ 今天的场次；日期不明的标"待确认"，不编造
  - 失败降级：某校抓取失败时保留上次数据，并在 `meta.schools_status` 记录原因（不遗漏）
- **命令**：
  ```bash
  python scripts/fetch_jobfairs.py                # 抓取并更新数据
  python scripts/fetch_jobfairs.py --dry-run      # 只预览不写文件
  python scripts/fetch_jobfairs.py --school 广西大学
  python scripts/fetch_jobfairs.py --no-render    # 禁用渲染
  ```

> 已知限制：个别高校就业平台（如广西大学 jyy.gxu.edu.cn 列表为 JS 异步加载）自动抓取仍在迭代中，这些学校以人工核查数据为基线并随每日运行持续补充；页面数据来源均附官方公告链接，可点击核实。

## 手动更新数据

直接编辑 `data/jobfairs.json` 并提交即可（每条含 school / name / date / mode / location / url / note 字段），提交后 Pages 自动发布。

## 数据来源与免责

数据来自各高校官网就业信息网、官方智慧就业平台（新锦成、云就业、24365 广西毕业生就业网、就业宝等）公开公告；第三方聚合网站仅用于定位官网，不作数据源。信息可能滞后或变动，请以各校官网最新公告为准。
