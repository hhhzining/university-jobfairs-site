#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取桂林市「非校园」线下现场招聘会信息，更新 data/guilin_fairs.json。

背景（2026-10-27 新增功能）：校园双选会之外的桂林本地现场招聘会，常由桂林市
人才服务中心（桂林人才网）、桂林市人社局及各城区人社部门组织，场地多为会展中心、
产业园、人才市场、商业广场等，面向高校毕业生/青年就业（校招向）为主。

数据源（均为官方公开渠道，静态可抓，无需渲染）：
1. 桂林人才网 glrcw.com「现场招聘会」：https://www.glrcw.com/m_jobfair-page_N-type_jobfair.html
   - 列表含标题/举办时间(起止)/地点/状态；详情页含主办单位/承办单位/联系电话/参会企业数
2. 桂林市人社局通知公告：http://rsj.guilin.gov.cn/xwzx/tzgg/（及其分页）
   - 过滤标题含「招聘会/双选会/专场招聘/招聘活动」的通知，详情页正则提取时间/地点

收录规则：
- 只收「举办日期 >= 今天」且「线下」的场次；已结束场次剔除；
- 非校园：举办地点不含 校区/大学/学院/学校/中学 等校园场地关键词（校园场次由
  data/jobfairs.json 的 12 校双选会栏目负责，此处避免重复）；
- 面向校招/毕业生倾向：标题或简介含 高校毕业生/毕业生/青年就业/2027届/应届/校园招聘
  时标记 target='校招/毕业生'，其余标 target='社招/综合'，不编造；
- 时间/地点等字段缺失时标注"待确认"，禁止编造；
- 失败降级：某源抓取失败时保留上次数据并在 meta.source_status 记录原因。

用法：
    python scripts/fetch_guilin_fairs.py              # 抓取并更新 data/guilin_fairs.json
    python scripts/fetch_guilin_fairs.py --dry-run    # 只打印，不写文件

数据文件：data/guilin_fairs.json。依赖：requests, beautifulsoup4。
"""

import argparse
import datetime
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'guilin_fairs.json')

UA = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 校园场地关键词：命中即视为校园内场次（由12校栏目覆盖，此处剔除）
CAMPUS_KW = ('校区', '大学', '学院', '学校', '中学', '高校')
# 校招/毕业生倾向关键词
GRADUATE_KW = ('高校毕业生', '毕业生', '青年就业', '青年', '校招', '2027届', '2026届', '应届', '校园招聘', '就业服务攻坚行动')

RE_DATETIME_RANGE = re.compile(r'(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})[日]?\s*\d{1,2}[:：]\d{2}\s*(?:至|~|-)\s*(?:20\d{2}[-/.年])?(\d{1,2})[-/.月](\d{1,2})[日]?\s*\d{1,2}[:：]\d{2}')
RE_DATE_FULL = re.compile(r'(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})[日]?')
RE_DATETIME = re.compile(r'(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})[日]?\s*(\d{1,2})[:：](\d{2})')


def today():
    return datetime.date.today()


def fetch(url, timeout=25, verify=True):
    r = requests.get(url, headers=UA, timeout=timeout, verify=verify)
    r.encoding = r.apparent_encoding or 'utf-8'
    return r.text


def norm_date(y, mo, d):
    try:
        y, mo, d = int(y), int(mo), int(d)
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return '%04d-%02d-%02d' % (y, mo, d)
    except Exception:
        pass
    return None


def is_campus(loc):
    loc = loc or ''
    return any(k in loc for k in CAMPUS_KW)


def target_tag(title, intro):
    text = (title or '') + ' ' + (intro or '')
    return '校招/毕业生' if any(k in text for k in GRADUATE_KW) else '社招/综合'


def parse_range(text):
    """识别 '2026-10-31 09:00 至 2026-10-31 12:00' / '2026.10.31 9:00~12:00' 等起止格式"""
    m = RE_DATETIME_RANGE.search(text)
    if m:
        d1 = norm_date(m.group(1), m.group(2), m.group(3))
        d2 = norm_date(m.group(1), m.group(4), m.group(5))
        return d1, d2
    # 兜底：取第一个完整日期与第二个完整日期（若有）
    ds = RE_DATE_FULL.findall(text)
    dates = [norm_date(*d) for d in ds]
    dates = [d for d in dates if d]
    if dates:
        return dates[0], (dates[1] if len(dates) > 1 else None)
    return None, None


# ---------------------------------------------------------------- 源1：桂林人才网
# 泛化链接文字：不是场次标题（同一场次的标题链接与"查看详情"按钮都指向详情页）
GENERIC_TITLES = ('查看详情', '进入详情', '详情', '报名', '立即报名', '查看', '了解更多', '更多', '在线预约', '参会报名', '企业报名', '单位报名', '预约')

def fetch_glrcw():
    items = []
    seen = set()   # 按场次 id 去重（标题链接与"查看详情"按钮指向同一详情页）
    seen_titles = set()
    errors = []
    for page in range(1, 11):  # 最多 10 页（约 100 场，覆盖未来+近期历史）
        url = 'https://www.glrcw.com/m_jobfair-page_%d-type_jobfair.html' % page
        try:
            html = fetch(url)
        except Exception as e:
            errors.append('glrcw page%d: %s' % (page, str(e)[:60]))
            break
        soup = BeautifulSoup(html, 'html.parser')
        page_items = 0
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            m = re.search(r'm_jobfair-c_show-id_(\d+)\.html', href)
            if not m:
                continue
            fid = m.group(1)
            title = a.get_text(' ', strip=True)
            if not title or title in GENERIC_TITLES or len(title) < 6:
                continue  # 只取真正的场次标题链接，跳过"查看详情"等按钮
            if (fid, title) in seen:
                continue
            seen.add((fid, title))
            # 用父容器文本取 时间/地点/状态
            block = a
            for _ in range(3):
                if block.parent is not None:
                    block = block.parent
                    if 'jobfair' in (block.get('class') or [''])[0] if isinstance((block.get('class') or [''])[0], str) and block.get('class') else False:
                        break
            txt = block.get_text(' ', strip=True)
            # 从整块文本解析
            mtime = re.search(r'举办时间：\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s*\d{1,2}[:：]\d{2}\s*至\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})?\s*\d{1,2}[:：]\d{2}', txt)
            if not mtime:
                mtime = re.search(r'举办时间：\s*(\S+)\s*\d{1,2}[:：]\d{2}', txt)
            mloc = re.search(r'举办地点：\s*([^\n]+)', txt)
            # 状态：报名中 / 往期回顾
            status = '报名中' if ('报名中' in txt or '预约' in txt) else ('往期' if '往期' in txt else '')
            date = date_end = None
            if mtime:
                g = mtime.groups()
                date = norm_date(g[0][:4], g[0][5:7], g[0][8:10]) if mtime and g[0] else None
                if date:
                    if g[1]:
                        date_end = norm_date(g[1][:4], g[1][5:7], g[1][8:10])
                    else:
                        date_end = date
            location = mloc.group(1).strip() if mloc else ''
            # 列表页地点可能带"查看详情"等链接文字噪音
            location = re.sub(r'\s*查看详情\s*$', '', location).strip()
            url_full = urljoin('https://www.glrcw.com/', href)
            if title in seen_titles:
                continue  # 同标题同场次已收（防跨分页重复）
            seen_titles.add(title)
            page_items += 1
            items.append({'id': fid, 'title': title, 'date': date, 'date_end': date_end,
                          'location': location, 'status': status, 'url': url_full})
        if page_items == 0:
            # 分页到尽头（无更多条目）
            break
    return items, errors


def fetch_glrcw_detail(item):
    """补全主办/咨询电话/活动时间/活动地点/简介（取详情页 meta description，避免列表噪音）"""
    try:
        html = fetch(item['url'])
    except Exception:
        return item
    soup = BeautifulSoup(html, 'html.parser')

    # 简介：meta description 是页面最干净的官方摘要
    desc = ''
    md = soup.find('meta', attrs={'name': 'description'})
    if md and md.get('content'):
        desc = md['content'].strip()[:400]
    # 主办单位：description 中"主办单位：…承办单位"片段（并列机构名无分隔符，直接保留）
    organizer = ''
    m = re.search(r'主办单位[:：]\s*([^承办]{4,80})', desc)
    if m:
        organizer = m.group(1).strip()
    if not organizer:
        # 兜底：正文中"主办单位："后到"承办单位/项目"前的多行文本（换行拼接）
        text = soup.get_text('\n', strip=True)
        mm = re.search(r'主办单位[:：]\s*\n([^承办\n][^\n]*)', text)
        if mm:
            organizer = mm.group(1).strip()
    # 咨询电话 / 联系电话
    phone = ''
    ptxt = soup.get_text(' ', strip=True)
    pm = re.search(r'(?:咨询电话|联系电话|联系电话|电话)[::：]?\s*(1\d{10})', ptxt)
    if pm:
        phone = pm.group(1)
    if not phone:
        pm = re.search(r'(1\d{10})', ptxt[:3000])
        if pm:
            phone = pm.group(1)
    # 活动时间/活动地点：详情页精确值（活动说明列表）
    mtime = re.search(r'活动时间[::：]?\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s*(\d{1,2})[:：](\d{2})\s*至\s*(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})?\s*(\d{1,2})[:：](\d{2})', ptxt)
    mloc = re.search(r'活动地点[::：]?\s*([^\n]{2,50}?)(?=\s*(?:咨询电话|联系电话|联\s*系|活动时间|招聘会介绍)|\s*$)', ptxt)
    if mloc:
        loc = mloc.group(1).strip().rstrip('：: ')
        if loc:
            item['location'] = loc
    if mtime:
        d = norm_date(mtime.group(1)[:4], mtime.group(1)[5:7], mtime.group(1)[8:10])
        if d:
            item['date'] = d
            item['date_end'] = d
            item['time_range'] = mtime.group(2) + ':' + mtime.group(3) + ' - ' + mtime.group(4) + ':' + mtime.group(5)
    item['organizer'] = organizer
    item['phone'] = phone
    item['intro'] = desc
    # target：用标题+meta简介+整页正文判定（正文含"毕业生/在校学子/实习见习"等校招信号，
    # 避免 meta 截断丢失关键词）
    item['target'] = target_tag(item.get('title') or '', (desc + ' ' + ptxt[:4000]))
    return item


# ---------------------------------------------------------------- 源2：桂林市人社局通知公告
def fetch_rsj():
    items = []
    errors = []
    seen = set()
    for page in range(1, 6):
        url = 'http://rsj.guilin.gov.cn/xwzx/tzgg/index.html' if page == 1 else 'http://rsj.guilin.gov.cn/xwzx/tzgg/index_%d.html' % (page - 1)
        try:
            html = fetch(url, verify=False)
        except Exception as e:
            errors.append('rsj page%d: %s' % (page, str(e)[:60]))
            break
        soup = BeautifulSoup(html, 'html.parser')
        got = 0
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            title = a.get_text(' ', strip=True)
            if not title or len(title) < 8:
                continue
            if not re.search(r'招聘会|双选会|专场招聘|招聘活动|招聘周', title):
                continue
            if not href.endswith('.shtml'):
                continue
            if (title, href) in seen:
                continue
            seen.add((title, href))
            full = urljoin('http://rsj.guilin.gov.cn/xwzx/tzgg/', href)
            got += 1
            items.append({'title': title, 'url': full, 'source': '桂林市人社局'})
        if got == 0:
            break
    return items, errors


def fetch_rsj_detail(item):
    try:
        html = fetch(item['url'], verify=False)
    except Exception:
        return item
    soup = BeautifulSoup(html, 'html.parser')
    # 正文
    main = soup.find('div', class_=re.compile('content|view|TRS_Editor|article')) or soup.body
    text = main.get_text(' ', strip=True) if main else soup.get_text(' ', strip=True)
    date, date_end = parse_range(text[:3000])
    item['date'] = date or '待确认'
    item['date_end'] = date_end
    loc = ''
    m = re.search(r'举办地点\s*[::：]?\s*([^。；\n]{4,50})', text[:2000])
    if m:
        loc = m.group(1).strip()
    if not loc:
        m = re.search(r'地点\s*[::：]?\s*([^。；\n]{4,50})', text[:2000])
        if m:
            loc = m.group(1).strip()
    item['location'] = loc
    item['organizer'] = ''
    m = re.search(r'(主办单位|主办)\s*[::：]?\s*([^。；\n]{3,40})', text[:1500])
    if m:
        item['organizer'] = m.group(2).strip()
    item['phone'] = ''
    pm = re.search(r'(1\d{10})', text[:1500])
    if pm:
        item['phone'] = pm.group(1)
    item['intro'] = text[:400]
    return item


# ---------------------------------------------------------------- 汇总
def collect():
    tstr = today().strftime('%Y-%m-%d')
    fairs, seen_keys, src_status = [], set(), {}

    # 源1 桂林人才网
    try:
        raw, errs = fetch_glrcw()
        for it in raw:
            it = fetch_glrcw_detail(it)
            # 只保留未来场次
            d = it.get('date')
            if d and d != '待确认' and d < tstr:
                continue
            if d == '待确认':
                # 无明确日期但状态报名中：保留，标注待确认（不遗漏优先）
                if it.get('status') != '报名中':
                    continue
            if is_campus(it.get('location')):
                continue  # 校园场次归12校栏目
            key = (it['title'][:40], str(d))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            # note：状态 + 官方摘要（meta description），不混入列表页导航噪音
            note_parts = []
            if it.get('status'):
                note_parts.append('状态：' + it['status'])
            if it.get('organizer'):
                note_parts.append('主办：' + it['organizer'])
            if it.get('time_range'):
                note_parts.append('时间：' + it['time_range'])
            if it.get('intro'):
                note_parts.append(it['intro'])
            fairs.append({
                'title': it['title'],
                'date': d or '待确认',
                'date_end': it.get('date_end'),
                'time_range': it.get('time_range', ''),
                'mode': '线下',
                'location': it.get('location', ''),
                'organizer': it.get('organizer', ''),
                'target': it.get('target') or target_tag(it['title'], it.get('intro', '')),
                'phone': it.get('phone', ''),
                'url': it['url'],
                'source': '桂林人才网',
                'note': '；'.join([x for x in note_parts if x])[:400],
            })
        src_status['桂林人才网'] = {'status': '成功', 'note': '获取 %d 条候选' % len(raw) + ('；' + '；'.join(errs) if errs else '')}
    except Exception as e:
        src_status['桂林人才网'] = {'status': '失败', 'note': str(e)[:120]}

    # 源2 桂林市人社局
    try:
        raw, errs = fetch_rsj()
        for it in raw:
            it = fetch_rsj_detail(it)
            d = it.get('date')
            if d and d != '待确认' and d < tstr:
                continue
            if d == '待确认':
                continue  # 人社局通知多为报道/无明确未来日期，无日期不收录（避免噪音）
            if is_campus(it.get('location')):
                continue
            key = (it['title'][:40], str(d))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            fairs.append({
                'title': it['title'],
                'date': d,
                'date_end': it.get('date_end'),
                'time_range': it.get('time_range', ''),
                'mode': '线下',
                'location': it.get('location', ''),
                'organizer': it.get('organizer', ''),
                'target': target_tag(it['title'], it.get('intro', '')),
                'phone': it.get('phone', ''),
                'url': it['url'],
                'source': '桂林市人社局',
                'note': it.get('intro', '')[:200],
            })
        src_status['桂林市人社局'] = {'status': '成功', 'note': '获取 %d 条候选' % len(raw) + ('；' + '；'.join(errs) if errs else '')}
    except Exception as e:
        src_status['桂林市人社局'] = {'status': '失败', 'note': str(e)[:120]}

    def keyf(it):
        d = str(it.get('date') or '')
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
            return (0, d, it.get('title', ''))
        return (1, d, it.get('title', ''))
    fairs.sort(key=keyf)
    return fairs, src_status


def load_old():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def main():
    ap = argparse.ArgumentParser(description='抓取桂林市非校园线下招聘会并更新 data/guilin_fairs.json')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    old = load_old()
    old_status = (old or {}).get('meta', {}).get('source_status', {})
    try:
        fairs, src_status = collect()
    except Exception as e:
        print('抓取异常:', e)
        fairs, src_status = [], {}

    # 失败源回退保留上次数据
    for src, st in old_status.items():
        if src not in src_status:
            src_status[src] = st
    if not fairs:
        old_fairs = (old or {}).get('fairs', [])
        if old_fairs:
            fairs = old_fairs
            print('本次未解析到新场次，保留上次数据 %d 条' % len(fairs))

    now_iso = datetime.datetime.now().astimezone().isoformat(timespec='minutes')
    data = {
        'meta': {
            'updated_at': now_iso,
            'note': '桂林市非校园线下现场招聘会（含桂林人才网、桂林市人社局等公开渠道）；面向校招/毕业生场次优先展示；数据每日自动更新。',
            'fair_count': len(fairs),
            'source_status': src_status,
        },
        'fairs': fairs,
    }

    print('抓取完成，共 %d 场桂林市非校园线下招聘会（截至 %s）' % (len(fairs), today().strftime('%Y-%m-%d')))
    for src, st in src_status.items():
        print('  %s: %s %s' % (src, st.get('status'), st.get('note', '')))
    for it in fairs:
        print('  ', it['date'], '|', it['title'][:50], '|', it['location'][:30], '|', it.get('target', ''), '|', it['source'])
    if args.dry_run:
        print('[dry-run] 未写文件')
        return
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('已写入:', DATA_PATH)


if __name__ == '__main__':
    main()
