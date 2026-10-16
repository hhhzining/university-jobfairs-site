#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 12 所广西高校官网就业信息网/官方就业平台的双选会信息，更新 data/jobfairs.json。

架构：
- 优先用 Playwright 无头浏览器渲染页面（覆盖新锦成/就业宝等 JS 渲染平台）；
  未安装 Playwright 时自动降级为 requests 静态抓取。
- 每所学校配置 1 个或多个入口 URL，渲染后从 DOM 提取标题含「双选会/招聘会/
  供需见面/组团招聘」等关键词的链接 → 进详情页提取举办日期/地点/线上线下。
- 数据质量守卫（防污染）：
  1. 跨校过滤：标题含其他高校名、或详情 URL 属第三方聚合平台且标题不含本校名 → 剔除；
  2. 导航排除：标题是栏目导航文案（校园双选会/招聘信息等）→ 剔除；
  3. 日期校验：只保留举办日期 >= 今天 或 日期待确认 的场次；已结束场次自动移除。
- 抓取失败的学校保留上次数据，并在 meta.schools_status 记录原因（不遗漏原则）。

用法：
    python scripts/fetch_jobfairs.py                 # 抓取并更新 data/jobfairs.json
    python scripts/fetch_jobfairs.py --dry-run       # 只打印结果，不写文件
    python scripts/fetch_jobfairs.py --school 广西大学   # 只抓指定学校
    python scripts/fetch_jobfairs.py --no-render     # 禁用 Playwright，强制静态抓取

数据文件：data/jobfairs.json。依赖：requests, beautifulsoup4, playwright(可选)。
"""

import argparse
import datetime
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'jobfairs.json')

UA = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# ---------------------------------------------------------------- 12 校配置
GXBYS = 'https://www.gxbys.com/jobfair'  # 广西毕业生就业网（自治区统一平台，覆盖全区高校承办场次）
SCHOOLS = [
    {'name': '广西大学', 'city': '南宁', 'domain': 'gxu.edu.cn',
     'urls': ['http://jyy.gxu.edu.cn/module/jobfairs?menu_id=34130',
              'http://jyy.gxu.edu.cn/module/jobfairs', GXBYS]},
    {'name': '广西科技大学', 'city': '柳州', 'domain': 'jiuyeb.cn',
     'urls': ['http://gxkejidx.jiuyeb.cn/News/zdylist.html?cateid=1',
              'http://gxkejidx.jiuyeb.cn/News/zdylist.html', GXBYS]},
    {'name': '桂林电子科技大学', 'city': '桂林', 'domain': 'guet.edu.cn',
     'urls': ['https://jy.guet.edu.cn/module/jobfairs?type=1&menu_id=41860',
              'https://jy.guet.edu.cn/module/news?type_id=16936&menu_id=41860',
              'https://jy.guet.edu.cn/module/video_jobfair?panel_type=24&menu_id=41860',
              GXBYS]},
    {'name': '广西师范大学', 'city': '桂林', 'domain': 'gxnu.edu.cn',
     'urls': ['https://gxnu.bysjy.com.cn/module/jobfairs?menu_id=13569', GXBYS]},
    {'name': '南宁师范大学', 'city': '南宁', 'domain': 'nnnu.edu.cn',
     'urls': ['https://nnnu.bysjy.com.cn/module/jobfairs', GXBYS]},
    {'name': '桂林理工大学', 'city': '桂林', 'domain': 'glut.edu.cn',
     'urls': ['https://glut.gxbys.com/jobfair/index', 'https://glut.gxbys.com/', GXBYS]},
    {'name': '广西民族大学', 'city': '南宁', 'domain': 'gxmzu.edu.cn',
     'urls': ['https://jyb.gxmzu.edu.cn/module/jobfairs?menu_id=24306', GXBYS]},
    {'name': '广西财经学院', 'city': '南宁', 'domain': 'gxufe.edu.cn',
     'urls': [GXBYS, 'https://jyxx.gxufe.edu.cn']},
    {'name': '广西科技师范学院', 'city': '来宾', 'domain': 'gxstnu.edu.cn',
     'urls': ['https://gxstnu.gxbys.com/', 'https://gxstnu.gxbys.com/jobfair', GXBYS]},
    {'name': '北部湾大学', 'city': '钦州', 'domain': 'bbgu.edu.cn',
     'urls': ['https://qzhu.bysjy.com.cn/module/jobfairs?type=2&menu_id=13527',
              'https://qzhu.bysjy.com.cn/module/jobfairs?menu_id=13542', GXBYS]},
    {'name': '广西工业学院', 'city': '北海', 'domain': 'gliet.edu.cn',
     'urls': ['https://gliet.gxbys.com/jobfair/index', 'https://gliet.gxbys.com/', GXBYS]},
    {'name': '桂林航天工业学院', 'city': '桂林', 'domain': 'guat.edu.cn',
     'urls': ['https://www.guat.edu.cn/tzgg/tzgg.htm', 'https://news.guat.edu.cn', GXBYS]},
]

# 收录关键词（标题命中即视为双选会/招聘会候选）
INCLUDE_KW = ('双选会', '招聘会', '供需见面', '洽谈会', '组团招聘', '空中双选', '网络招聘会')
# 排除关键词（普通宣讲会/职位信息不收录）
EXCLUDE_KW = ('宣讲会', '招聘简章', '职位发布', '岗位信息', '实习信息', '招聘公告信息')
# 导航类泛化标题（栏目入口，非具体场次）
NAV_TITLES = ('校园双选会', '双选会', '招聘会', '校园招聘会', '网络招聘会', '招聘信息',
              '在线招聘', '校园组团招聘会', '组团招聘会', '专场招聘会', '宣讲会')

# 其他高校/机构名（用于跨校过滤：标题含这些且非本校 → 剔除）
OTHER_NAMES = ('广西大学', '广西科技大学', '桂林电子科技大学', '广西师范大学', '南宁师范大学',
               '桂林理工大学', '广西民族大学', '广西财经学院', '广西科技师范学院', '北部湾大学',
               '广西工业学院', '桂林航天工业学院', '桂林旅游学院', '柳州职业技术大学', '南宁学院',
               '广西城市职业大学', '广西外国语学院', '桂林学院', '南宁理工学院', '桂林信息科技学院',
               '广西警察学院', '梧州学院', '贺州学院', '玉林师范学院', '右江民族医学院',
               '广西医科大学', '广西中医药大学', '广西艺术学院', '广西体育高等专科学校',
               '广西机电职业技术学院', '广西建设职业技术学院', '广西交通职业技术学院',
               '广西电力职业技术学院', '广西职业技术学院', '广西农业职业技术大学',
               '桂林师范高等专科学校', '南宁职业技术大学', '广西职业技术大学', '柳州工学院',
               '北海艺术设计学院', '山西文化旅游职业大学', '河南师范大学', '韶关学院',
               '陕西服装工程学院', '陕西中医药大学', '广东白云学院', '广州大学', '华南师范大学')
OTHER_NAMES_PAT = re.compile('|'.join(sorted(OTHER_NAMES, key=len, reverse=True)))

# 日期正则
RE_DATE_MMDD_YYYY = re.compile(r'(\d{1,2})[-/.](\d{1,2})\s+(20\d{2})')          # 09-18 2026
RE_DATE_FULL = re.compile(r'(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})')            # 2026-10-16
RE_DATE_CN = re.compile(r'(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日')   # 2026年10月16日
RE_DATE_MD = re.compile(r'(\d{1,2})\s*月\s*(\d{1,2})\s*日')                    # 10月16日（无年份）
RE_DATE_RANGE = re.compile(r'(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s*[~至到—\-]\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})')


def today():
    return datetime.date.today()


def norm(d, sep='-'):
    return d.replace('/', sep).replace('.', sep)


# ---------------------------------------------------------------- 抓取引擎
def fetch_page_requests(url, timeout=25):
    r = requests.get(url, headers=UA, timeout=timeout)
    r.encoding = r.apparent_encoding or 'utf-8'
    return r.text


_playwright_ok = None


def playwright_available():
    global _playwright_ok
    if _playwright_ok is None:
        try:
            import playwright  # noqa
            _playwright_ok = True
        except Exception:
            _playwright_ok = False
    return _playwright_ok


def fetch_page_render(url, timeout=40000):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(user_agent=UA['User-Agent'], locale='zh-CN')
        try:
            page.goto(url, timeout=timeout, wait_until='domcontentloaded')
            page.wait_for_timeout(3500)
            return page.content()
        finally:
            browser.close()


def fetch_page(url, use_render):
    if use_render and playwright_available():
        try:
            return fetch_page_render(url)
        except Exception:
            pass
    return fetch_page_requests(url)


# ---------------------------------------------------------------- 解析
def extract_dates(text):
    """提取带年份日期列表（优先）；无年份的仅在无任何带年份日期时作为兜底。"""
    dates = []
    for m in RE_DATE_MMDD_YYYY.finditer(text):
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            dates.append('%04d-%02d-%02d' % (y, mo, d))
    for m in RE_DATE_FULL.finditer(text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            dates.append('%04d-%02d-%02d' % (y, mo, d))
    for m in RE_DATE_CN.finditer(text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            dates.append('%04d-%02d-%02d' % (y, mo, d))
    if not dates:
        for m in RE_DATE_MD.finditer(text):
            mo, d = int(m.group(1)), int(m.group(2))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                y = today().year
                if (y, mo, d) < (today().year, today().month, today().day):
                    y += 1
                dates.append('%04d-%02d-%02d' % (y, mo, d))
    seen, out = set(), []
    for d in dates:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def pick_future_date(dates, today_str):
    for d in dates:
        if d >= today_str:
            return d
    return None


def is_own_fair(title, url, school):
    """跨校/污染过滤：剔除外校场次、导航、往届（非 2027/2028 届）、已举办场次。"""
    name = school['name']
    # 导航类泛化标题
    if title.strip() in NAV_TITLES:
        return False
    if len(title.strip()) < 8 and 'module/' in url:
        return False
    # 已举办的历史场次
    if '已举办' in title or '已结束' in title:
        return False
    # 往届场次：标题含"20XX届"，届次不是 2027/2028 → 剔除
    for m in re.finditer(r'(20\d{2})\s*届', title):
        if m.group(1) not in ('2027', '2028'):
            return False
    # 标题含明确的过去日期（就业宝"09-18 2026 学校举办…"新闻格式）
    for m in RE_DATE_MMDD_YYYY.finditer(title):
        y, mo, d = int(m.group(3)), int(m.group(1)), int(m.group(2))
        if '%04d-%02d-%02d' % (y, mo, d) < today().strftime('%Y-%m-%d'):
            return False
    # 标题含其他高校名 → 剔除（本校名出现则不剔除）
    m = OTHER_NAMES_PAT.search(title)
    if m and m.group(0) != name:
        return False
    # 域名判断
    host = (urlparse(url).hostname or '')
    own_domain = school['domain']
    if own_domain in host:
        # 本校域名：收标题含本校名 / 自治区级"广西20XX届…专场" / "学校|我校+双选|招聘"的通知类场次
        if name in title:
            return True
        if re.search(r'广西\s*20\d{2}\s*届', title):
            return True
        if ('学校' in title or '我校' in title) and ('双选' in title or '招聘' in title):
            return True
        return False
    # 第三方聚合平台（bysjy.com / gxbys.com / jiuyeb.cn 等）→ 仅标题含本校名才收
    if 'bysjy.com' in host or 'gxbys.com' in host or 'jiuyeb.cn' in host:
        return name in title
    # 其他未知域名：仅当标题含本校名
    return name in title


def parse_list_html(html, base_url, school):
    """从渲染后列表页提取候选双选会条目 [(title, url)]，已做质量守卫。"""
    soup = BeautifulSoup(html, 'html.parser')
    items, seen = [], set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('javascript') or href == '#':
            continue
        txt = a.get_text(' ', strip=True)
        if not txt or len(txt) < 4:
            continue
        if any(k in txt for k in EXCLUDE_KW):
            continue
        if not any(k in txt for k in INCLUDE_KW):
            continue
        url = urljoin(base_url, href)
        if not is_own_fair(txt, url, school):
            continue
        if url in seen:
            continue
        seen.add(url)
        items.append({'title': txt, 'url': url})
    return items


def parse_detail(html, title, school):
    """从详情页提取举办日期/地点/线上线下。提取不到标 待确认/留空，不编造。"""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)[:8000]
    full = title + ' ' + text

    date = date_end = None
    m = RE_DATE_RANGE.search(full)
    if m:
        date = norm(m.group(1))
        date_end = norm(m.group(2))
    if not date:
        dates = extract_dates(full)
        d = pick_future_date(dates, today().strftime('%Y-%m-%d'))
        if d:
            date = d
        else:
            # 提取不到未来日期（可能只有发布/报名日）：不剔除，标"待确认"（不遗漏优先）
            date = '待确认'
    if not date:
        date = '待确认'

    mode = ''
    head = full[:1200]
    if re.search(r'线上双选|网络双选|空中双选|线上招聘|网络招聘会', head):
        mode = '线上'
    elif re.search(r'线下|现场双选', head):
        mode = '线下'
    else:
        mode = ''

    location = ''
    loc_kw = re.search(r'(举办)?(地点|场地)\s*[::：]?\s*([^。；;]{4,50})', full)
    if loc_kw:
        location = loc_kw.group(3).strip()
    if not location:
        m2 = re.search(r'([\u4e00-\u9fa5]{0,10}(校区|体育馆|田径场|篮球场|足球场|广场|大学生活动中心|教学楼|报告厅|活动中心))', full)
        if m2:
            location = m2.group(1)
    if not location:
        location = ''

    return {'date': date, 'date_end': date_end, 'mode': mode, 'location': location}


def fetch_school(school, use_render, school_filter=None):
    name = school['name']
    if school_filter and name != school_filter:
        return None, None, None
    all_items, seen_urls, errors = [], set(), []
    got_any = False
    for url in school['urls']:
        try:
            html = fetch_page(url, use_render)
            if not html:
                errors.append('空页面 %s' % url)
                continue
            cands = parse_list_html(html, url, school)
            got_any = True
            for c in cands:
                if c['url'] in seen_urls:
                    continue
                seen_urls.add(c['url'])
                all_items.append(c)
        except Exception as e:
            errors.append('%s: %s' % (url, str(e)[:70]))
    if not got_any:
        return [], '无法访问', '；'.join(errors) or '所有入口抓取失败'

    items = []
    for c in all_items:
        try:
            detail_html = fetch_page(c['url'], use_render)
            info = parse_detail(detail_html, c['title'], school)
        except Exception:
            info = {'date': '待确认', 'date_end': None, 'mode': '', 'location': ''}
        items.append({
            'school': name,
            'city': school['city'],
            'name': c['title'],
            'date': info.get('date'),
            'date_end': info.get('date_end'),
            'mode': info.get('mode', ''),
            'location': info.get('location', ''),
            'url': c['url'],
            'note': '',
        })
    if not items:
        return [], '已查-暂无未来场次', '入口可访问但未解析到未来双选会条目'
    return items, '已查-有未来场次', ''


# ---------------------------------------------------------------- 合并与写盘
def load_old():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def norm_title(t):
    """标题规范化用于去重：去修饰前缀（现场/网络/【..】）与公告后缀（邀请函/通知）。"""
    t = (t or '').strip()
    t = re.sub(r'^(现场|网络|线上|线下|空中)\s*', '', t)
    t = re.sub(r'^【[^】]*】\s*', '', t)
    t = re.sub(r'(邀请函|的通知|通知公告|公告)$', '', t)
    return t.strip()


def merge_and_filter(new_by_school, old):
    tstr = today().strftime('%Y-%m-%d')
    old_items = (old or {}).get('jobfairs', [])

    merged, seen_key = [], set()
    for school in SCHOOLS:
        items = new_by_school.get(school['name'])
        candidates = []
        if items:
            candidates += items
        # 旧数据作为兜底（合并，不覆盖）
        for it in old_items:
            if it.get('school') == school['name']:
                candidates.append(it)
        for it in candidates:
            # 同一学校同一规范化标题视为同一场次（种子数据中同校多场可能共用同一入口 URL，不能按 URL 去重）
            key = (it.get('school'), norm_title(it.get('name')))
            if key in seen_key:
                continue
            seen_key.add(key)
            merged.append(it)

    kept = []
    for it in merged:
        d = it.get('date')
        if d and d != '待确认':
            if d < tstr:
                continue
        kept.append(it)

    def keyf(it):
        d = str(it.get('date') or '')
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
            return (0, d, it.get('school', ''))
        return (1, d, it.get('school', ''))
    kept.sort(key=keyf)
    return kept


def main():
    ap = argparse.ArgumentParser(description='抓取 12 所广西高校双选会并更新 data/jobfairs.json')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--school', default=None)
    ap.add_argument('--no-render', action='store_true')
    args = ap.parse_args()

    use_render = not args.no_render
    old = load_old()
    old_status = (old or {}).get('meta', {}).get('schools_status', {})

    new_by_school, status_map = {}, {}
    tstr = today().strftime('%Y-%m-%d')
    now_iso = datetime.datetime.now().astimezone().isoformat(timespec='minutes')

    for school in SCHOOLS:
        name = school['name']
        if args.school and name != args.school:
            continue
        try:
            items, status, note = fetch_school(school, use_render, args.school)
        except Exception as e:
            items, status, note = None, '抓取异常', str(e)[:120]
        if items is None:
            continue
        future_items = [it for it in items if not (it.get('date') and it['date'] != '待确认' and it['date'] < tstr)]
        new_by_school[name] = future_items
        prev = old_status.get(name, {})
        if status == '已查-有未来场次':
            status_map[name] = {'status': status, 'note': '本次抓取 %d 条' % len(future_items)}
        elif status == '已查-暂无未来场次':
            status_map[name] = {'status': status, 'note': note or '本次未解析到双选会条目'}
        else:
            status_map[name] = {'status': '保留上次数据',
                                'note': '%s；上次:%s' % (note, prev.get('status', '未知'))}

    for school in SCHOOLS:
        if school['name'] not in status_map:
            status_map[school['name']] = old_status.get(school['name'], {'status': '待查', 'note': ''})

    kept = merge_and_filter(new_by_school, old)

    data = {
        'meta': {
            'updated_at': now_iso,
            'note': '数据由 GitHub Actions 每日自动抓取更新；抓取失败的学校保留上次数据。',
            'school_count': len(SCHOOLS),
            'jobfair_count': len(kept),
            'schools_status': status_map,
        },
        'schools': [{'name': s['name'], 'city': s['city']} for s in SCHOOLS],
        'jobfairs': kept,
    }

    print('抓取完成，共 %d 场未来双选会（截至 %s）' % (len(kept), tstr))
    for name, st in status_map.items():
        print('  %s: %s %s' % (name, st.get('status'), st.get('note', '')))
    if args.dry_run:
        print('[dry-run] 未写文件')
        return
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('已写入:', DATA_PATH)


if __name__ == '__main__':
    main()
