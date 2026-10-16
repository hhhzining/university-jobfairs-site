#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日 19:00（北京时间）自动发送双选会邮件提醒。

内容：未来 7 天（今天起 7 天内）已公布的招聘/双选会场次，
      并将「明天」的场次置顶重点标记。
收件人：1079594841@qq.com（可用环境变量 TO_EMAIL 覆盖）

发送通道：QQ 邮箱 SMTP（smtp.qq.com:465）。
  发件邮箱  -> 环境变量 SMTP_EMAIL（GitHub Secrets）
  授权码    -> 环境变量 SMTP_AUTH_CODE（GitHub Secrets，非登录密码）

用法：
  python scripts/send_daily_email.py            # 正常发送
  python scripts/send_daily_email.py --dry-run  # 只打印邮件正文，不发送（本地验证）
"""
import json
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.utils import formataddr

CN_TZ = timezone(timedelta(hours=8))
WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
RE_DATE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')


def today_cn():
    return datetime.now(CN_TZ).date()


def fmt_date(d):
    return d.strftime('%Y-%m-%d')


def weekday_cn(d):
    return WEEKDAYS[d.weekday()]


def valid_date(s):
    m = RE_DATE.match(s or '')
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
    except ValueError:
        return None


def esc_html(s):
    return (str(s or '')
            .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def build_html(today, window, morrow):
    """生成黑白极简风 HTML 邮件正文。"""
    total = len(window)
    morrow_total = len(morrow)

    # 明天区块（置顶、重点标记）
    morrow_rows = ''
    for it in morrow:
        d = it['_d']
        morrow_rows += (
            '<div style="border:2px solid #0a0a0a;border-radius:12px;padding:14px 16px;'
            'margin-bottom:10px;background:#0a0a0a;color:#fff;">'
            '<div style="font-size:13px;font-weight:800;letter-spacing:.05em;margin-bottom:6px;">'
            '【明天】%s %s · %s</div>'
            '<div style="font-size:15px;font-weight:700;line-height:1.5;color:#fff;">%s</div>'
            '<div style="font-size:12.5px;color:#c9c9c9;margin-top:6px;">%s%s</div>'
            '<div style="margin-top:8px;"><a href="%s" style="color:#fff;font-size:12.5px;font-weight:700;'
            'border:1px solid #fff;border-radius:8px;padding:4px 12px;text-decoration:none;">查看官方公告</a></div>'
            '</div>'
        ) % (
            esc_html(fmt_date(d)), esc_html(weekday_cn(d)), esc_html(it.get('school', '')),
            esc_html(it.get('name', '')),
            ('地点：%s' % esc_html(it.get('location', ''))) if it.get('location') else '地点：待确认',
            ('（%s）' % esc_html(it.get('note', ''))) if it.get('note') else '',
            esc_html(it.get('url', '')),
        )

    # 其余 7 天内场次
    other_rows = ''
    for it in window:
        if it in morrow:
            continue
        d = it['_d']
        other_rows += (
            '<div style="border:1px solid #d9d9d9;border-radius:12px;padding:12px 14px;margin-bottom:8px;">'
            '<div style="font-size:12px;color:#8a8a8a;font-weight:700;margin-bottom:4px;">'
            '%s %s · %s</div>'
            '<div style="font-size:14px;font-weight:700;line-height:1.5;">%s</div>'
            '<div style="font-size:12.5px;color:#404040;margin-top:5px;">%s%s</div>'
            '<div style="margin-top:6px;"><a href="%s" style="color:#0a0a0a;font-size:12px;font-weight:700;'
            'text-decoration:underline;">查看官方公告</a></div>'
            '</div>'
        ) % (
            esc_html(fmt_date(d)), esc_html(weekday_cn(d)), esc_html(it.get('school', '')),
            esc_html(it.get('name', '')),
            ('地点：%s' % esc_html(it.get('location', ''))) if it.get('location') else '地点：待确认',
            ('（%s）' % esc_html(it.get('note', ''))) if it.get('note') else '',
            esc_html(it.get('url', '')),
        )

    body = (
        '<div style="background:#f4f4f4;padding:24px 12px;font-family:\'Noto Sans SC\',\'Microsoft YaHei\',sans-serif;">'
        '<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #0a0a0a;border-radius:16px;'
        'overflow:hidden;">'
        '<div style="background:#0a0a0a;color:#fff;padding:18px 20px;">'
        '<div style="font-size:12px;font-weight:700;letter-spacing:.06em;">广西12校双选会信息服务平台 · 每日提醒</div>'
        '<div style="font-size:20px;font-weight:900;margin-top:4px;">未来 7 天共有 %d 场双选会</div>'
        '<div style="font-size:12.5px;color:#c9c9c9;margin-top:6px;">%s 生成 · 数据来自各校官网就业信息网 · 明天 %d 场</div>'
        '</div>'
        '<div style="padding:18px 20px;">'
        '%s'  # 明天区块
        '%s'  # 其余区块
        '<div style="margin-top:14px;border-top:1px solid #e0e0e0;padding-top:12px;font-size:11.5px;color:#8a8a8a;">'
        '本邮件由 GitHub Actions 于每日 19:00（北京时间）自动发送 · 信息仅供参考，具体以各校官方公告为准 · '
        '© 2026 Jeremy He</div>'
        '</div></div></div>'
    ) % (total, esc_html(fmt_date(today)), morrow_total, morrow_rows, other_rows)

    return body


def load_fairs():
    with open('data/jobfairs.json', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('jobfairs', [])


def pick_window(fairs, today):
    """返回窗口内场次（今天..今天+6），并在每条上挂 _d（date 对象）。"""
    end = today + timedelta(days=6)
    window = []
    for it in fairs:
        d = valid_date(it.get('date'))
        if d is None:
            continue
        if today <= d <= end:
            copy = dict(it)
            copy['_d'] = d
            window.append(copy)
    window.sort(key=lambda x: x['_d'])
    return window


def send(subject, html, smtp_email, auth, to_email):
    msg = MIMEText(html, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = formataddr(('广西12校双选会提醒', smtp_email))
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.qq.com', 465, timeout=30) as srv:
        srv.login(smtp_email, auth)
        srv.sendmail(smtp_email, [to_email], msg.as_string())


def main():
    dry_run = '--dry-run' in sys.argv

    to_email = (os.environ.get('TO_EMAIL') or '1079594841@qq.com').strip()
    smtp_email = (os.environ.get('SMTP_EMAIL') or '').strip()
    auth = (os.environ.get('SMTP_AUTH_CODE') or '').strip()

    if not dry_run and (not smtp_email or not auth):
        print('❌ 未配置 SMTP 发送参数，邮件未发送。')
        print('配置方法（GitHub 仓库 → Settings → Secrets and variables → Actions）：')
        print('  新建 SMTP_EMAIL    = 发件 QQ 邮箱（如 1079594841@qq.com）')
        print('  新建 SMTP_AUTH_CODE = 该邮箱的 SMTP 授权码（QQ邮箱设置→账户→开启SMTP服务获取，非登录密码）')
        sys.exit(1)

    today = today_cn()
    fairs = load_fairs()
    window = pick_window(fairs, today)
    morrow = [it for it in window if it['_d'] == today + timedelta(days=1)]

    subject = '【双选会提醒】未来7天 %d 场 · 明天 %d 场（%s）' % (len(window), len(morrow), fmt_date(today))
    html = build_html(today, window, morrow)

    if dry_run:
        print('=== DRY RUN ===')
        print('收件人:', to_email)
        print('发件人:', smtp_email or '(未配置 SMTP_EMAIL)')
        print('主题:', subject)
        print('窗口: %s ~ %s，命中 %d 场，其中明天 %d 场' % (
            fmt_date(today), fmt_date(today + timedelta(days=6)), len(window), len(morrow)))
        print('正文长度:', len(html))
        print(html)
        return

    send(subject, html, smtp_email, auth, to_email)
    print('✅ 邮件已发送至 %s（未来 7 天 %d 场，明天 %d 场）' % (to_email, len(window), len(morrow)))


if __name__ == '__main__':
    main()
