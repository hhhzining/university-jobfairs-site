#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 12 所广西高校官网就业信息网/官方就业平台的双选会信息，更新 data/jobfairs.json。

架构（v2 修复版，2026-10-16）：
- 每个学校按「官方数据通道」优先抓取，DOM 渲染兜底：
  * 新锦成平台 JSON 接口（广西大学 / 北部湾大学）：GET /module/getjobfairs，字段含
    meet_day(举办日期) / address(地点) / is_online(线上) / inner_school / is_over；
    用 inner_school==1 过滤本校场次、is_over!=true 过滤已结束场次。
  * 桂理工 jy.glut.edu.cn SPA API：GET /api/view/jobFair/list，jobFairType==1 为双选会，
    startTime 为举办日期。
  * 其余学校：Playwright 渲染官网列表页 → DOM 提取 → 详情页补日期/地点。
- 数据质量守卫（防污染，保持 v1）：
  1. 跨校过滤：标题含其他高校名 → 剔除；
  2. 导航排除：栏目导航文案 → 剔除；
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
import time
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
GXBYS = 'https://www.gxbys.com/jobfair'  # 广西毕业生就业网（自治区统一平台，兜底）
SCHOOLS = [
    {'name': '广西大学', 'city': '南宁', 'domain': 'gxu.edu.cn',
     'api': {'type': 'bysjy', 'url': 'https://gxu.bysjy.com.cn/module/getjobfairs?start=0&count=100&type=&address=&organisers=&keyword=&day=&panel_id=',
             'detail': 'https://gxu.bysjy.com.cn/detail/jobfair?id=%s'},
     'urls': ['http://jyy.gxu.edu.cn/module/jobfairs?menu_id=34130',
              'http://jyy.gxu.edu.cn/module/jobfairs', GXBYS]},
    {'name': '广西科技大学', 'city': '柳州', 'domain': 'jiuyeb.cn',
     'urls': ['http://gxkejidx.jiuyeb.cn/Chuangye/sxlb.html?status=0',
              'http://gxkejidx.jiuyeb.cn/News/zdylist.html?cateid=1',
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
     'api': {'type': 'glut',
             'url': 'https://jy.glut.edu.cn/api/view/jobFair/list?pageNum=1&pageSize=50'},
     'urls': ['https://glut.gxbys.com/jobfair/index', 'https://glut.gxbys.com/', GXBYS]},
    {'name': '广西民族大学', 'city': '南宁', 'domain': 'gxmzu.edu.cn',
     'urls': ['https://jyb.gxmzu.edu.cn/module/jobfairs?menu_id=24306', GXBYS]},
    {'name': '广西财经学院', 'city': '南宁', 'domain': 'gxufe.edu.cn',
     'urls': ['https://jyxx.gxufe.edu.cn/News/newsList.html?cateid=cd403865-981f-6b48-e8e5-4825b43a6e9d',
              'https://jyxx.gxufe.edu.cn', GXBYS]},
    {'name': '广西科技师范学院', 'city': '来宾', 'domain': 'gxstnu.edu.cn',
     'urls': ['https://gxstnu.gxbys.com/', 'https://gxstnu.gxbys.com/jobfair', GXBYS]},
    {'name': '北部湾大学', 'city': '钦州', 'domain': 'bbgu.edu.cn',
     'api': {'type': 'bysjy', 'url': 'https://qzhu.bysjy.com.cn/module/getjobfairs?start=0&count=100&type=1&address=&organisers=&keyword=&day=&panel_id=',
             'detail': 'https://qzhu.bysjy.com.cn/detail/jobfair?id=%s'},
     'urls': ['https://qzhu.bysjy.com.cn/module/jobfairs?menu_id=13524&type=1',
              'https://qzhu.bysjy.com.cn/module/jobfairs?menu_id=13524&type=2', GXBYS]},
    {'name': '广西工业学院', 'city': '北海', 'domain': 'gliet.edu.cn',
     'urls': ['https://gliet.gxbys.com/jobfair/index', 'https://gliet.gxbys.com/', GXBYS]},
    {'name': '桂林航天工业学院', 'city': '桂林', 'domain': 'guat.edu.cn',
     'urls': ['https://www.guat.edu.cn/tzgg/tzgg.htm',
              'https://www.guat.edu.cn/tzgg/tzgg/101.htm',
              'https://www.guat.edu.cn/tzgg/tzgg/100.htm',
              'https://news.guat.edu.cn', GXBYS]},
]

# 收录关键词（标题命中即视为双选会/招聘会候选）
INCLUDE_KW = ('双选会', '招聘会', '供需见面', '洽谈会', '组团招聘', '空中双选', '网络招聘会', '招聘邀请函')
# 排除关键词（普通宣讲会/职位信息不收录）
EXCLUDE_KW = ('宣讲会', '招聘简章', '职位发布', '岗位信息', '实习信息', '招聘公告信息')
# 已确认往届/已办场次的详情 URL（人工核验），新旧数据均剔除
KNOWN_PAST_URLS = ('nnnu.bysjy.com.cn/detail/jobfair?id=29132',
                   'gxstnu.gxbys.com/jobfair/view/id/40402')
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


def fetch_json(url, timeout=25):
    # 官方接口瞬时抖动常见：做 2 次退避重试，全部失败才抛异常（触发 DOM 兜底）
    last_err = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            data = r.json()
            # 新锦成/桂理工接口信封校验：code != 1 视为失败，不静默返回空
            if isinstance(data, dict) and 'code' in data and data.get('code') != 1:
                raise RuntimeError('API code=%s' % data.get('code'))
            return data
        except Exception as e:
            last_err = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError('接口请求失败: %s' % str(last_err)[:80])


# ---------------------------------------------------------------- 官方数据通道
def parse_bysjy_api(data, school, detail_tpl):
    """新锦成 getjobfairs JSON → 本校未来双选会条目。

    过滤规则：inner_school==1（本校场次）、is_over != True（未结束）、
    meet_day >= 今天、标题命中收录关键词且不含排除关键词。
    """
    rows = data.get('data') or []
    tstr = today().strftime('%Y-%m-%d')
    items = []
    for it in rows:
        if str(it.get('inner_school')) != '1':
            continue
        if it.get('is_over') in (True, '1', 'true', 1):
            continue
        title = (it.get('title') or '').strip()
        if not title or not any(k in title for k in INCLUDE_KW):
            continue
        if any(k in title for k in EXCLUDE_KW):
            continue
        day = (it.get('meet_day') or '').strip()
        if day and day < tstr:
            continue
        mode = '线上' if str(it.get('is_online')) == '1' else ('线上+线下' if str(it.get('is_online')) == '2' else '线下')
        location = (it.get('address') or '').strip()
        fair_id = it.get('fair_id')
        url = detail_tpl % fair_id if fair_id else ''
        items.append({'title': title, 'url': url, 'date': day or '待确认',
                      'date_end': None, 'mode': mode, 'location': location})
    return items


def parse_glut_api(data, school):
    """桂理工 jy.glut.edu.cn /api/view/jobFair/list → 未来双选会条目。

    jobFairType==1 为双选会（2=企业宣讲会）；startTime 为举办日期。
    """
    rows = data.get('rows') or []
    tstr = today().strftime('%Y-%m-%d')
    items = []
    for it in rows:
        if it.get('jobFairType') != 1:
            continue
        title = (it.get('jobFairName') or '').strip()
        if not title or not any(k in title for k in INCLUDE_KW):
            continue
        st = (it.get('startTime') or '')[:10]
        if not st or st < tstr:
            continue
        mode = '线上' if it.get('jobFairOnlineType') == 2 else '线下'
        location = (it.get('jobFairAddress') or it.get('locationOther') or '').strip()
        fid = it.get('jobFairId')
        url = 'https://jy.glut.edu.cn/jobfair/detail?jobFairId=%s' % fid if fid else 'https://jy.glut.edu.cn/index'
        items.append({'title': title, 'url': url, 'date': st,
                      'date_end': (it.get('endTime') or '')[:10] or None,
                      'mode': mode, 'location': location})
    return items


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
        if dates:
            d = pick_future_date(dates, today().strftime('%Y-%m-%d'))
            if d:
                date = d
            elif re.search(r'20(27|28)\s*届', title):
                # 标题含 2027/2028 届次但详情只有过去日期：不遗漏优先，保留待确认
                date = '待确认'
            else:
                # 详情日期全部为过去且标题无未来届次 → 历史/已办场次，剔除
                date = None
        else:
            # 完全提取不到日期：不剔除，标"待确认"（不遗漏优先）
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

    # 通道 1：官方数据 API（新锦成 / 桂理工）
    api = school.get('api')
    if api:
        try:
            data = fetch_json(api['url'])
            got_any = True
            if api['type'] == 'bysjy':
                cands = parse_bysjy_api(data, school, api['detail'])
            elif api['type'] == 'glut':
                cands = parse_glut_api(data, school)
            else:
                cands = []
            for c in cands:
                k = (c['title'], c.get('date'))
                if k in seen_urls:
                    continue
                seen_urls.add(k)
                all_items.append(c)
        except Exception as e:
            errors.append('API %s: %s' % (api['url'][:60], str(e)[:70]))

    # 通道 2：列表页 DOM
    for url in school['urls']:
        try:
            html = fetch_page(url, use_render)
            if not html:
                errors.append('空页面 %s' % url)
                continue
            cands = parse_list_html(html, url, school)
            # 科技大（就业宝）sxlb：<a> 文本为 日期+标题+统计+地点+状态 拼接，标题截到"双选会/招聘会/邀请函"为止
            if name == '广西科技大学' and 'sxlb' in url:
                for c in cands:
                    m = re.search(r'(.+?(?:双选会|招聘会|邀请函))', c['title'])
                    if m:
                        c['title'] = m.group(1).strip()
            # 财经学院通知公告：仅收"邀请函"且面向 2027/2028 届的招聘/双选通知（剔除历史活动/转发热点），并清洗编号/发布月前缀
            if name == '广西财经学院':
                cleaned = []
                for c in cands:
                    t = re.sub(r'^\d{1,3}\s+20\d{2}[-/.]\d{1,2}\s*【[^】]*】\s*', '', c['title'])
                    t = re.sub(r'^(现场|网络|线上|线下|空中)\s*', '', t).strip()
                    t = re.split(r'尊敬的|尊敬', t)[0].strip()
                    if re.search(r'20\d{2}[-/.]0[1-9](?:[-/.]\d{1,2})?', t) and not re.search(r'20(27|28)\s*届', t):
                        continue  # 过去月份活动（无未来届次）→ 历史通知
                    if ('邀请函' in t and ('招聘' in t or '双选' in t)
                            and ('2027' in t or '2028' in t or name in t)):
                        c['title'] = t
                        cleaned.append(c)
                cands = cleaned
            got_any = True
            for c in cands:
                if c['url'] in seen_urls:
                    continue
                if any(p in c['url'] for p in KNOWN_PAST_URLS):
                    continue
                seen_urls.add(c['url'])
                all_items.append(c)
        except Exception as e:
            errors.append('%s: %s' % (url, str(e)[:70]))
    if not got_any:
        return [], '无法访问', '；'.join(errors) or '所有入口抓取失败'

    items = []
    for c in all_items:
        if c.get('date') is not None and c.get('url'):
            # API 通道已带完整字段
            items.append({
                'school': name,
                'city': school['city'],
                'name': c['title'],
                'date': c.get('date'),
                'date_end': c.get('date_end'),
                'mode': c.get('mode', ''),
                'location': c.get('location', ''),
                'url': c.get('url'),
                'note': '',
            })
            continue
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
    """标题规范化用于去重：去修饰前缀（现场/网络/【..】/日期/编号/公文前缀）与公告后缀（邀请函/通知/双选会）。"""
    t = (t or '').strip()
    t = re.sub(r'^(关于组织参加|关于参加|组织参加|关于举办)\s*', '', t)
    t = re.sub(r'^(现场|网络|线上|线下|空中)\s*', '', t)
    t = re.sub(r'^【[^】]*】\s*', '', t)
    # 日期/时间前缀：2026-10-27 14:00 …、2026-08 …
    t = re.sub(r'^(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s+\d{1,2}:\d{2}\s*', '', t)
    t = re.sub(r'^(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s*', '', t)
    # 编号+发布月前缀：13 2026-08 【Top】…
    t = re.sub(r'^\d{1,3}\s+20\d{2}[-/.]\d{1,2}\s*【[^】]*】\s*', '', t)
    t = re.sub(r'^20\d{2}[-/.]\d{1,2}\s*【[^】]*】\s*', '', t)
    # 结尾发布日期/时间后缀：…的通知 2026-10-10
    t = re.sub(r'\s+(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\s*$', '', t)
    t = re.sub(r'\.\.\.$', '', t)
    t = re.split(r'尊敬的|尊的', t)[0].strip()  # 先去掉正文粘连（邀请函 尊敬的用人单位…）
    t = re.sub(r'(邀请函|的通知|通知公告|公告)$', '', t)
    # 同一场次的"双选会/招聘会"口径差异归一（不同名仅差此后缀视为同场）
    t = re.sub(r'(双选会|招聘会)$', '', t)
    t = re.sub(r'双选$', '', t)
    return t.strip()


def title_score(t):
    """标题规范度打分：越完整规范越高（去重时保留高分者）。"""
    s = 0
    if not re.match(r'^\d{4}[-/.]\d{1,2}', t):
        s += 2          # 无日期前缀
    if '双选会' in t or '招聘会' in t or '招聘' in t:
        s += 1
    if '通知' not in t:
        s += 1
    if '邀请函' in t:
        s += 1
    return s


def key_title(it):
    """去重键用标题：科技大 sxlb 旧数据带"标题+统计+地点+状态"拼接，先截到双选会/招聘会/邀请函为止。
    仅对含统计/状态特征的标题截断（"X 家用人单位 Y 个职位 / Z人 … 待举办"），干净标题（如网络双选会第一/二场）不截断。"""
    t = it.get('name') or ''
    if it.get('school') == '广西科技大学' and re.search(r'待举办|家用人单位|个职位', t):
        m = re.search(r'(.+?(?:双选会|招聘会|邀请函))', t)
        if m:
            t = m.group(1)
    return t


def merge_and_filter(new_by_school, old):
    tstr = today().strftime('%Y-%m-%d')
    old_items = (old or {}).get('jobfairs', [])

    merged_map = {}
    for school in SCHOOLS:
        candidates = []
        if new_by_school.get(school['name']):
            candidates += new_by_school[school['name']]
        # 旧数据作为兜底（合并，不覆盖）
        for it in old_items:
            if it.get('school') != school['name']:
                continue
            if any(p in (it.get('url') or '') for p in KNOWN_PAST_URLS):
                continue  # 已确认往届/已办场次
            # 旧数据守卫：历史垃圾（已办/往届/去年已过月份通知）不再兜底
            t = it.get('name') or ''
            if '已举办' in t or '已结束' in t:
                continue
            mj = re.findall(r'(20\d{2})\s*届', t)
            if mj and all(g not in ('2027', '2028') for g in mj):
                continue
            if re.search(r'20\d{2}[-/.]0[1-9](?:[-/.]\d{1,2})?', t) and not re.search(r'20(27|28)\s*届', t):
                continue
            candidates.append(it)
        for it in candidates:
            # 同一学校同一规范化标题视为同一场次；同标题多条时保留标题更规范的
            key = (it.get('school'), norm_title(key_title(it)))
            if key not in merged_map or title_score(key_title(it)) > title_score(key_title(merged_map[key])):
                merged_map[key] = it

    merged = list(merged_map.values())

    kept = []
    for it in merged:
        d = it.get('date')
        if not d:
            continue  # 已过/历史场次（解析判定 date=None）
        if d != '待确认':
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
