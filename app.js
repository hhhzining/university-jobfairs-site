/* 广西12校双选会信息服务平台 · 逻辑层（黑白版 · 分页查询） */
(function () {
  'use strict';

  // ===== 内置快照（随代码发布，线上加载失败时兜底）=====
  var FALLBACK = {
   "meta": {
    "updated_at": "2026-10-28T00:51+08:00",
    "note": "数据由 GitHub Actions 每日自动抓取更新；每校数据仅来自该校官网就业信息网/官方就业平台；抓取失败的学校保留上次数据。",
    "school_count": 12,
    "jobfair_count": 27,
    "schools_status": {
     "桂林理工大学": {
      "status": "已查-有未来场次",
      "note": "本次抓取 2 条，累计 2 条"
     },
     "广西大学": {
      "status": "已查-暂无未来场次",
      "note": "入口可访问但未解析到未来双选会条目"
     },
     "广西科技大学": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 13 条（官网未同步/跨平台场次）"
     },
     "桂林电子科技大学": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 2 条（官网未同步/跨平台场次）"
     },
     "广西师范大学": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 2 条（官网未同步/跨平台场次）"
     },
     "南宁师范大学": {
      "status": "已查-暂无未来场次",
      "note": "入口可访问但未解析到未来双选会条目；剔除跨校/聚合源条目 1 条"
     },
     "广西民族大学": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 4 条（官网未同步/跨平台场次）"
     },
     "广西财经学院": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 1 条（官网未同步/跨平台场次）"
     },
     "广西科技师范学院": {
      "status": "已查-暂无未来场次",
      "note": "入口可访问但未解析到未来双选会条目"
     },
     "北部湾大学": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 2 条（官网未同步/跨平台场次）"
     },
     "广西工业学院": {
      "status": "已查-暂无未来场次",
      "note": "入口可访问但未解析到未来双选会条目"
     },
     "桂林航天工业学院": {
      "status": "已查-有未来场次",
      "note": "本次实时未解析到，历史保留 1 条（官网未同步/跨平台场次）"
     }
    }
   },
   "schools": [
    {
     "name": "广西大学",
     "city": "南宁"
    },
    {
     "name": "广西科技大学",
     "city": "柳州"
    },
    {
     "name": "桂林电子科技大学",
     "city": "桂林"
    },
    {
     "name": "广西师范大学",
     "city": "桂林"
    },
    {
     "name": "南宁师范大学",
     "city": "南宁"
    },
    {
     "name": "桂林理工大学",
     "city": "桂林"
    },
    {
     "name": "广西民族大学",
     "city": "南宁"
    },
    {
     "name": "广西财经学院",
     "city": "南宁"
    },
    {
     "name": "广西科技师范学院",
     "city": "来宾"
    },
    {
     "name": "北部湾大学",
     "city": "钦州"
    },
    {
     "name": "广西工业学院",
     "city": "北海"
    },
    {
     "name": "桂林航天工业学院",
     "city": "桂林"
    }
   ],
   "jobfairs": [
    {
     "school": "北部湾大学",
     "city": "钦州",
     "name": "职聚滨海运河城 青春启航向未来——2026年工会就业服务进校园暨北部湾大学2027届毕业生双选会",
     "date": "2026-10-30",
     "date_end": null,
     "mode": "线下",
     "location": "北部湾大学大学生创业园一楼大厅（钦州市滨海新城滨海大道12号）",
     "url": "https://qzhu.bysjy.com.cn/detail/jobfair?id=31533",
     "note": ""
    },
    {
     "school": "广西民族大学",
     "city": "南宁",
     "name": "广西民族大学2027届毕业生武鸣校区专场招聘会",
     "date": "2026-10-31",
     "date_end": null,
     "mode": "",
     "location": "、规模 1.时间：2026年 10 月 31 日（周 六 ） 9 ： 3 0—1 3 : 3 0 2",
     "url": "https://jyb.gxmzu.edu.cn/detail/jobfair?id=31393",
     "note": ""
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届生物化工类毕业生双选会",
     "date": "2026-11-03",
     "date_end": null,
     "mode": "线下",
     "location": "柳石校区田径场",
     "url": "http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=60c2a359-db4c-2383-9f79-cf3851a336de",
     "note": "2027届，生物化工类专场（中型），08:30开始"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届医学类毕业生专场双选会",
     "date": "2026-11-03",
     "date_end": null,
     "mode": "线下",
     "location": "柳石校区田径场",
     "url": "http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=596be7e1-d822-512b-ccbc-540ecb93af51",
     "note": "2027届，医学类专场，09:00开始"
    },
    {
     "school": "广西民族大学",
     "city": "南宁",
     "name": "广西民族大学武鸣校区理工类、管理类专业2027届毕业生联合招聘会",
     "date": "2026-11-04",
     "date_end": null,
     "mode": "",
     "location": "广西民族大学武鸣校区南广场 （三）规模： 预设展位 40个，预计参加学生150 0 人 （四）费用：",
     "url": "https://jyb.gxmzu.edu.cn/detail/jobfair?id=31859",
     "note": ""
    },
    {
     "school": "桂林理工大学",
     "city": "桂林",
     "name": "有色金属行业百校千企精准促就业行动 校园巡回招聘（桂林理工大学站）暨 桂林理工大学2027届毕业生秋季 综合双选会（校友企业专场）邀请函",
     "date": "2026-11-05",
     "date_end": "2026-11-05",
     "mode": "线下",
     "location": "桂林理工大学雁山校区体育训练馆",
     "url": "https://jy.glut.edu.cn/m/pages/jobfair/jobfair-detail?jobFairId=7040",
     "note": "参会单位 47 家；提供岗位 166 个"
    },
    {
     "school": "桂林电子科技大学",
     "city": "桂林市",
     "name": "2026年广东省专精特新企业校园招聘会（广西专场）",
     "date": "2026-11-06",
     "date_end": null,
     "mode": "线下",
     "location": "桂林电子科技大学花江校区正德广场",
     "url": "https://jy.guet.edu.cn/module/jobfairs",
     "note": "广东省专精特新企业组团来校招聘；9:30开始；约500个展位"
    },
    {
     "school": "桂林航天工业学院",
     "city": "桂林市",
     "name": "2027届毕业生航天航空暨校友单位招聘会",
     "date": "2026-11-07",
     "date_end": null,
     "mode": "线下",
     "location": "待确认",
     "url": "https://www.guat.edu.cn/info/1005/23531.htm",
     "note": "航天航空行业及校友单位专场；时间地点待学校后续通知（9月10日校园招聘计划发布会公布）"
    },
    {
     "school": "北部湾大学",
     "city": "钦州",
     "name": "北部湾大学经济管理学院2027届毕业生秋季就业双选会",
     "date": "2026-11-10",
     "date_end": null,
     "mode": "线下",
     "location": "北部湾大学四号教学楼",
     "url": "https://qzhu.bysjy.com.cn/detail/jobfair?id=31706",
     "note": ""
    },
    {
     "school": "广西科技大学",
     "city": "柳州",
     "name": "2026-11-10 15:00 广西科技大学2026年秋季校园综合双选会",
     "date": "2026-11-10",
     "date_end": null,
     "mode": "",
     "location": "报到时间： 1 1 月 1 0 日 14 :30— 15 : 0 0",
     "url": "http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=075f3724-c6b7-5276-dd64-ae7bc5dbcf6a",
     "note": ""
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2026年秋季校园双选会（第二场）",
     "date": "2026-11-10",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "拟举办（2027届招聘安排表预排），下午"
    },
    {
     "school": "广西民族大学",
     "city": "南宁",
     "name": "广西民族大学2027届毕业生秋季第二场双选会",
     "date": "2026-11-14",
     "date_end": null,
     "mode": "",
     "location": "、规模 1.时间：2026年 11 月 14 日（周 六 ） 9：00—14:00 2.地点：广西民",
     "url": "https://jyb.gxmzu.edu.cn/detail/jobfair?id=31288",
     "note": ""
    },
    {
     "school": "桂林理工大学",
     "city": "桂林",
     "name": "桂林理工大学南宁分校2027届毕业生秋季线下双选会邀请函",
     "date": "2026-11-20",
     "date_end": "2026-11-20",
     "mode": "线下",
     "location": "空港校区体育馆（广西扶绥县空港大道21号）",
     "url": "https://jy.glut.edu.cn/m/pages/jobfair/jobfair-detail?jobFairId=7045",
     "note": "参会单位 17 家；提供岗位 45 个"
    },
    {
     "school": "广西民族大学",
     "city": "南宁",
     "name": "广西民族大学民族学与社会学学院、马克思主义学院、政治与公共管理学院2027届毕业生综合类专场招聘会",
     "date": "2026-11-21",
     "date_end": null,
     "mode": "",
     "location": "、规模 1.时间：2026年11月 21 日（ 星期 六） 9：00—14:00 2.地点：广西民族",
     "url": "https://jyb.gxmzu.edu.cn/detail/jobfair?id=31567",
     "note": ""
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "2027届毕业生网络双选会（第一场）",
     "date": "2026-12-01",
     "date_end": null,
     "mode": "线上",
     "location": "就业宝平台",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届，网络双选会；拟举办，具体时段另行通知"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届土木建筑工程类毕业生专场双选会",
     "date": "2026-12-10",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届，土木建筑类专场（中型）；拟举办"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027年春季校园双选会",
     "date": "2027-03-19",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "拟举办，上午"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届生物化工类毕业生专场双选会",
     "date": "2027-03-30",
     "date_end": null,
     "mode": "线下",
     "location": "柳石校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届，中型专场；拟举办"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届计算机科学与技术类、电子工程类毕业生专场双选会",
     "date": "2027-04-09",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届，中型专场；拟举办，上午"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西2027届高校毕业生“宏志助航计划”就业双选会（柳州专场）",
     "date": "2027-04-16",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "拟举办，上午"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学2027届毕业生“百日冲刺”双选会暨2028届毕业生实习见习专场招聘会",
     "date": "2027-06-11",
     "date_end": null,
     "mode": "线下",
     "location": "文昌校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "拟举办，上午"
    },
    {
     "school": "广西师范大学",
     "city": "桂林",
     "name": "广西师范大学2027届毕业生秋季综合类双选会",
     "date": "待确认",
     "date_end": null,
     "mode": "线下",
     "location": "（一）时间： 202 6 年 10 月 27 日（ 星期二 ） 14：3 0-1 7 ： 3 0 （",
     "url": "https://gxnu.bysjy.com.cn/detail/jobfair?id=31457",
     "note": ""
    },
    {
     "school": "广西师范大学",
     "city": "桂林",
     "name": "【广西师范大学雁山校区】 第五届云校招“名企优岗广西行”2027届毕业生秋季巡回双选会",
     "date": "待确认",
     "date_end": null,
     "mode": "线下",
     "location": "组织方：云校招 参会人员：广西师范大学2027届毕业生 活动时间：2026年9月20日14:30-1",
     "url": "https://gxnu.bysjy.com.cn/detail/jobfair?id=30160",
     "note": ""
    },
    {
     "school": "广西财经学院",
     "city": "南宁",
     "name": "广西财经学院2027届毕业生秋季校园招聘邀请函",
     "date": "待确认",
     "date_end": null,
     "mode": "",
     "location": "信息，用人单位可以在“宣讲会申请栏”实时查询审核状态",
     "url": "https://jyxx.gxufe.edu.cn/News/newsXiang.html?cateid=cd403865-981f-6b48-e8e5-4825b43a6e9d&id=5d22442d-dd6d-5d90-ce1c-f4cabebd2bbd",
     "note": ""
    },
    {
     "school": "桂林电子科技大学",
     "city": "桂林",
     "name": "“奔甬而来”;全国巡回招聘 宁波-桂林电子科技大学招聘会",
     "date": "待确认",
     "date_end": null,
     "mode": "线下",
     "location": "花江校区大学生活动中心 二、参会企业 桂林电子科技大学版权所有 可信网站验证 安全联盟 可信网站验证",
     "url": "https://jy.guet.edu.cn/detail/news?id=1772188&menu_id=41860&type_id=16936",
     "note": ""
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学柳石校区2027届毕业生秋季专场双选会",
     "date": "待确认（拟2026年11月）",
     "date_end": null,
     "mode": "线下",
     "location": "柳石校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届；拟举办，具体日期以就业网后续公布为准"
    },
    {
     "school": "广西科技大学",
     "city": "柳州市",
     "name": "广西科技大学柳石校区2027届毕业生春季专场双选会",
     "date": "待确认（拟2027年4月）",
     "date_end": null,
     "mode": "线下",
     "location": "柳石校区",
     "url": "http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90",
     "note": "2027届；拟举办，具体日期以就业网公布为准"
    }
   ]
  };

  var G_FALLBACK = {
   "meta": {
    "updated_at": "2026-10-28T01:02+08:00",
    "note": "桂林市非校园线下现场招聘会（含桂林人才网、桂林市人社局等公开渠道）；面向校招/毕业生场次优先展示；数据每日自动更新。",
    "fair_count": 1,
    "source_status": {
     "桂林人才网": {
      "status": "成功",
      "note": "获取 100 条候选"
     },
     "桂林市人社局": {
      "status": "成功",
      "note": "获取 0 条候选"
     }
    }
   },
   "fairs": [
    {
     "title": "光引未来・才聚桂林--2026年光电产业人才专场招聘会",
     "date": "2026-10-31",
     "date_end": "2026-10-31",
     "time_range": "09:00 - 12:00",
     "mode": "线下",
     "location": "桂林创意产业园区创意大厦一楼",
     "organizer": "桂林市人力资源和社会保障局桂林高新技术产业开发区管理委员会",
     "target": "校招/毕业生",
     "phone": "17307738093",
     "url": "https://www.glrcw.com/m_jobfair-c_show-id_203.html",
     "source": "桂林人才网",
     "note": "状态：报名中；主办：桂林市人力资源和社会保障局桂林高新技术产业开发区管理委员会；时间：09:00 - 12:00；光引未来・才聚桂林--2026年光电产业人才专场招聘会主办单位：桂林市人力资源和社会保障局桂林高新技术产业开发区管理委员会承办单位：桂林市人才服务中心光电创意概念验证中心成果转化基地桂林电子科技大学科技园项目实施单位：桂林盛才人力科技有限公司现场活动（一）行业专家分享会（9:00--10:00）邀请光电产业行业专家开展专题分享，围绕光电行业发展趋势、产业人才能力要求、职业发展路径、求职择业要点开展"
    }
   ]
  };
  // ---- 12 校就业信息网入口（高校覆盖点击跳转）----
  var SCHOOL_URLS = {
    '广西大学': 'https://jyy.gxu.edu.cn/module/jobfairs',
    '广西科技大学': 'http://gxkejidx.jiuyeb.cn/',
    '桂林电子科技大学': 'https://jy.guet.edu.cn/module/jobfairs',
    '广西师范大学': 'https://gxnu.bysjy.com.cn/module/jobfairs',
    '南宁师范大学': 'https://nnnu.bysjy.com.cn/module/jobfairs',
    '桂林理工大学': 'https://jy.glut.edu.cn/',
    '广西民族大学': 'https://jyb.gxmzu.edu.cn/module/jobfairs',
    '广西财经学院': 'https://jyxx.gxufe.edu.cn/',
    '广西科技师范学院': 'https://gxstnu.gxbys.com/',
    '北部湾大学': 'https://qzhu.bysjy.com.cn/module/jobfairs',
    '广西工业学院': 'https://gliet.gxbys.com/',
    '桂林航天工业学院': 'https://www.guat.edu.cn/tzgg/tzgg.htm'
  };

  // ---- 状态 ----
  var PAGE_SIZE = 10;
  var state = {
    data: null,
    isFallback: false,
    search: '',
    school: '',
    form: '',
    view: 'all',        // all | 7d | month
    sortMode: 'date',   // date | school
    page: 1,
    gData: null,
    gFallback: false,
    gSearch: '',
    gTarget: '',
    gPage: 1
  };

  var $ = function (id) { return document.getElementById(id); };

  // ---- 工具 ----
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function fmtDate(d) {
    var p = d.split('-');
    return { y: +p[0], m: +p[1], d: +p[2] };
  }
  function todayStr() {
    var t = new Date();
    return t.getFullYear() + '-' + pad(t.getMonth() + 1) + '-' + pad(t.getDate());
  }
  function addDays(s, n) {
    var p = s.split('-');
    var dt = new Date(+p[0], +p[1] - 1, +p[2]);
    dt.setDate(dt.getDate() + n);
    return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate());
  }
  function fmtUpdated(iso) {
    if (!iso) return '更新时间未知';
    var dt = new Date(iso);
    if (isNaN(dt)) {
      var m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
      if (!m) return '更新时间未知';
      return m[1] + '-' + m[2] + '-' + m[3] + ' ' + m[4] + ':' + m[5];
    }
    // 统一转北京时间显示（Actions 服务器为 UTC，相差 8 小时）
    var bj = new Date(dt.getTime() + 8 * 3600 * 1000);
    return bj.getUTCFullYear() + '-' + pad(bj.getUTCMonth() + 1) + '-' + pad(bj.getUTCDate()) +
      ' ' + pad(bj.getUTCHours()) + ':' + pad(bj.getUTCMinutes());
  }
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function isRealDate(dd) { return /^\d{4}-\d{2}-\d{2}$/.test(dd || ''); }

  // ---- 加载数据 ----
  function load() {
    if (location.protocol === 'file:') {
      state.data = FALLBACK;
      state.isFallback = true;
      render();
      return;
    }
    fetch('data/jobfairs.json', { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(function (d) { state.data = d; state.isFallback = false; render(); })
      .catch(function () {
        state.data = FALLBACK;
        state.isFallback = true;
        render();
      });
  }

  // ---- 渲染 ----
  function render() {
    var d = state.data;
    if (!d) return;
    var fairs = d.jobfairs || [];
    var t = todayStr();
    // 兜底过滤：真实日期早于今天的场次不展示（数据每日更新，但本地/当天数据可能含昨日场次）
    var active = fairs.filter(function (it) {
      return !isRealDate(it.date) || it.date >= t;
    });

    // 更新时间（统一标注"更新时间"，避免用户误认为发布时间）
    $('updatedAt').textContent = '更新时间 ' + fmtUpdated(d.meta.updated_at) + (state.isFallback ? '（内置快照）' : '');

    // KPI（基于过滤后的有效场次）
    var near = active.filter(function (it) {
      return isRealDate(it.date) && it.date >= t && it.date <= addDays(t, 6);
    }).length;
    var online = active.filter(function (it) { return (it.mode || '').indexOf('线上') >= 0; }).length;
    $('stTotal').textContent = active.length;
    $('stNear').textContent = near;
    $('stSchools').textContent = d.schools ? d.schools.length : 12;
    $('stOnline').textContent = online;

    // 学校下拉
    var sel = $('schoolSelect');
    sel.innerHTML = '<option value="">全部学校</option>';
    (d.schools || []).forEach(function (s) {
      var o = document.createElement('option');
      o.value = s.name;
      o.textContent = s.name + (s.city ? '（' + s.city + '）' : '');
      if (state.school === s.name) o.selected = true;
      sel.appendChild(o);
    });

    // 筛选
    var kw = state.search.trim();
    var list = active.filter(function (it) {
      if (state.school && it.school !== state.school) return false;
      if (state.form === '线上' && (it.mode || '').indexOf('线上') < 0) return false;
      if (state.form === '线下' && (it.mode || '').indexOf('线下') < 0) return false;
      if (state.view === '7d') {
        if (!isRealDate(it.date)) return false;
        if (it.date < t || it.date > addDays(t, 6)) return false;
      }
      if (state.view === 'month') {
        if (!isRealDate(it.date)) return false;
        var ft = t.split('-'), fd = it.date.split('-');
        if (fd[0] !== ft[0] || fd[1] !== ft[1]) return false;
        if (it.date < t) return false;
      }
      if (kw) {
        var hay = (it.name + it.school + (it.location || '')).toLowerCase();
        if (hay.indexOf(kw.toLowerCase()) < 0) return false;
      }
      return true;
    });

    // 排序
    var sortFn = state.sortMode === 'school'
      ? function (a, b) {
          var r = a.school.localeCompare(b.school, 'zh');
          return r !== 0 ? r : dateKey(a).localeCompare(dateKey(b));
        }
      : function (a, b) { return dateKey(a).localeCompare(dateKey(b)); };
    list.sort(sortFn);

    // 分页
    var total = list.length;
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (state.page > pages) state.page = pages;
    if (state.page < 1) state.page = 1;
    var slice = list.slice((state.page - 1) * PAGE_SIZE, state.page * PAGE_SIZE);

    $('resultCount').textContent = '共 ' + total + ' 场';
    renderList(slice, t);
    renderPager(total, pages);
    renderSchools(d);
    renderFloater(active, t);
  }

  function dateKey(it) {
    var dd = it.date || '';
    if (isRealDate(dd)) return '0' + dd;
    return '1' + dd;
  }

  // ---- 列表：按月份分组表格（当前页） ----
  function renderList(items, t) {
    var wrap = $('fairList');
    var empty = $('emptyState');
    if (!items.length) {
      wrap.innerHTML = '';
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    var groups = [];
    var tbd = [];
    items.forEach(function (it) {
      if (isRealDate(it.date)) {
        var key = it.date.slice(0, 7);
        var g = groups.filter(function (x) { return x.key === key; })[0];
        if (!g) { g = { key: key, items: [] }; groups.push(g); }
        g.items.push(it);
      } else {
        tbd.push(it);
      }
    });
    groups.sort(function (a, b) { return a.key.localeCompare(b.key); });

    var html = '';
    var idx = 0;
    groups.forEach(function (g) {
      var y = g.key.slice(0, 4), m = +g.key.slice(5, 7);
      html += '<div class="group-head"><span>' + y + '年' + m + '月</span>' +
              '<span class="g-count">' + g.items.length + ' 场</span><span class="g-line"></span></div>';
      g.items.forEach(function (it) { html += rowHtml(it, t, idx++); });
    });
    if (tbd.length) {
      html += '<div class="group-head"><span>日期待定</span>' +
              '<span class="g-count">' + tbd.length + ' 场</span><span class="g-line"></span></div>';
      tbd.forEach(function (it) { html += rowHtml(it, t, idx++); });
    }
    wrap.innerHTML = html;
  }

  // 从公告原文（地点/备注）中提取时间信息，如"上午 9:30"；匹配不到返回空串（不编造）
  function timeInfo(it) {
    var src = ((it.location || '') + ' ' + (it.note || ''));
    var period = '';
    var pm = src.match(/上午|下午|晚上|中午/);
    if (pm) period = pm[0];
    var hm = src.match(/(\d{1,2})\s*[:：]\s*(\d{2})/);
    var hmTxt = '';
    if (hm && +hm[1] >= 6 && +hm[1] <= 23) hmTxt = hm[1] + ':' + hm[2];
    if (!period && !hmTxt) return '';
    return (period ? period : '') + (hmTxt ? (period ? ' ' : '') + hmTxt : '');
  }

  function rowHtml(it, t, idx) {
    var delay = Math.min((idx || 0) * 0.02, 0.4);
    var dd = it.date || '';
    var dayHtml, hot = false, hotCls = '';
    if (isRealDate(dd)) {
      var f = fmtDate(dd);
      var days = Math.round((new Date(+f.y, +f.m - 1, +f.d) - new Date(+t.split('-')[0], +t.split('-')[1] - 1, +t.split('-')[2])) / 86400000);
      var badge;
      if (days === 0) { badge = '<span class="fd-badge today">今天举行</span>'; hot = true; hotCls = 'hot-today'; }
      else if (days === 1) { badge = '<span class="fd-badge tomorrow">明天举行</span>'; hot = true; hotCls = 'hot-tomorrow'; }
      else if (days === 2) { badge = '<span class="fd-badge dayafter">后天举行</span>'; hot = true; hotCls = 'hot-dayafter'; }
      else if (days <= 7) { badge = '<span class="fd-badge soon">' + days + ' 天后</span>'; }
      else { badge = '<span class="fd-badge later"></span>'; }
      dayHtml = '<span class="fd-day">' + f.m + '/' + f.d + '</span><span class="fd-ym">' + f.y + '年</span>' + badge;
    } else {
      var m = dd.match(/拟(\d{4})年(\d{1,2})月/);
      dayHtml = '<span class="fd-tbd">' + (m ? m[1] + '年' + m[2] + '月' : '日期待定') + '</span><span class="fd-ym">以公告为准</span>' +
                '<span class="fd-badge tbd">待定</span>';
    }

    var mode = (it.mode || '').trim();
    var tagCls = mode.indexOf('线上') >= 0 ? 'tag-online' : (mode.indexOf('线下') >= 0 ? 'tag-offline' : 'tag-unknown');
    var tagTxt = mode || '待确认';
    var loc = (it.location || '').trim();
    var note = (it.note || '').trim();
    var timeTxt = timeInfo(it);

    return '<div class="fair-row' + (hot ? ' hot ' + hotCls : '') + '" role="row" style="animation-delay:' + delay + 's">' +
        '<div class="f-date" role="cell">' + dayHtml + '</div>' +
        '<div class="f-main" role="cell">' +
          '<div class="f-title-row">' +
            '<a class="f-title" href="' + esc(it.url) + '" target="_blank" rel="noopener" title="' + esc(it.name) + '">' + esc(it.name) + '</a>' +
            '<a class="f-action" href="' + esc(it.url) + '" target="_blank" rel="noopener">公告' +
              '<svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
            '</a>' +
          '</div>' +
          '<div class="f-meta">' +
            '<span class="f-school">' + esc(it.school) + (it.city ? '<span class="f-city">' + esc(it.city) + '</span>' : '') + '</span>' +
            '<span class="tag ' + tagCls + '">' + esc(tagTxt) + '</span>' +
            (timeTxt ? '<span class="f-time"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>' + esc(timeTxt) + '</span>' : '') +
            (loc && loc !== '待确认' ? '<span class="f-loc"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-5.1-7-11a7 7 0 1 1 14 0c0 5.9-7 11-7 11z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/></svg><span>' + esc(loc) + '</span></span>' : '') +
          '</div>' +
          (note ? '<p class="f-note">' + esc(note) + '</p>' : '') +
        '</div>' +
      '</div>';
  }

  // ---- 分页控件 ----
  function renderPager(total, pages) {
    var box = $('pager');
    if (total <= PAGE_SIZE) { box.hidden = true; box.innerHTML = ''; return; }
    box.hidden = false;
    var cur = state.page;
    var html = '<span class="pager-info">第 ' + cur + ' / ' + pages + ' 页 · 共 ' + total + ' 场</span>';
    html += '<button type="button" data-page="' + (cur - 1) + '"' + (cur === 1 ? ' disabled' : '') + ' aria-label="上一页">‹ 上一页</button>';
    var seq = [];
    if (pages <= 7) {
      for (var i = 1; i <= pages; i++) seq.push(i);
    } else {
      var set = [1, pages, cur - 1, cur, cur + 1];
      set.forEach(function (p) { if (p >= 1 && p <= pages && seq.indexOf(p) < 0) seq.push(p); });
      seq.sort(function (a, b) { return a - b; });
      var out = [];
      for (var k = 0; k < seq.length; k++) {
        if (k > 0 && seq[k] - seq[k - 1] > 1) out.push('gap');
        out.push(seq[k]);
      }
      seq = out;
    }
    seq.forEach(function (p) {
      if (p === 'gap') { html += '<span class="gap">…</span>'; return; }
      html += '<button type="button" data-page="' + p + '"' + (p === cur ? ' class="current" aria-current="page"' : '') + '>' + p + '</button>';
    });
    html += '<button type="button" data-page="' + (cur + 1) + '"' + (cur === pages ? ' disabled' : '') + ' aria-label="下一页">下一页 ›</button>';
    box.innerHTML = html;
  }

  // ---- 高校覆盖（点击跳转各校就业信息网） ----
  function renderSchools(d) {
    var grid = $('schoolGrid');
    var st = d.meta.schools_status || {};
    var html = '';
    (d.schools || []).forEach(function (s, i) {
      var info = st[s.name] || {};
      var ok = (info.status || '').indexOf('有未来场次') >= 0;
      var statusTxt = ok ? '有未来场次' : '暂无';
      var noteTxt = (info.note || '');
      var url = SCHOOL_URLS[s.name] || '#';
      var delay = Math.min(i * 0.03, 0.3);
      html +=
        '<a class="school-item ' + (ok ? 'ok' : 'no') + '" href="' + url + '" target="_blank" rel="noopener" role="listitem" title="' + esc(noteTxt) + '" style="animation-delay:' + delay + 's">' +
          '<span class="s-row"><span class="s-name">' + esc(s.name) + (s.city ? '<span class="s-city">' + esc(s.city) + '</span>' : '') + '</span>' +
          '<span class="s-status">' + esc(statusTxt) + '</span></span>' +
          '<span class="s-go">进入就业信息网<svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
        '</a>';
    });
    grid.innerHTML = html;
  }

  // ---- 右下角悬浮框：今日双选会提示（当天关闭后不再显示） ----
  function renderFloater(active, t) {
    var old = $('todayFloater');
    if (old) old.remove();
    var today = active.filter(function (it) { return isRealDate(it.date) && it.date === t; });
    var closedToday = false;
    try { closedToday = sessionStorage.getItem('floaterClosed') === t; } catch (e) { /* 隐私模式忽略 */ }
    if (!today.length || closedToday) return;

    var f = fmtDate(t);
    var w = document.createElement('div');
    w.id = 'todayFloater';
    w.className = 'floater';
    w.innerHTML =
      '<button type="button" class="floater-fab" aria-expanded="false" aria-label="今日双选会提示">' +
        '<span class="floater-dot" aria-hidden="true"></span>' +
        '<span class="floater-txt"><b>' + today.length + '</b> 场今日双选会</span>' +
        '<svg class="floater-chev" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
      '</button>' +
      '<div class="floater-panel" hidden>' +
        '<div class="floater-head"><span>' + f.m + '/' + f.d + ' · 今日双选会</span>' +
          '<button type="button" class="floater-close" aria-label="关闭提示">' +
            '<svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>' +
          '</button></div>' +
        '<div class="floater-list">' +
          today.map(function (it) {
            var ti = timeInfo(it);
            var loc = (it.location || '').trim();
            var metaParts = [];
            if (ti) metaParts.push(ti);
            if (loc && loc !== '待确认') metaParts.push(loc);
            return '<a class="floater-item" href="' + esc(it.url) + '" target="_blank" rel="noopener">' +
              '<span class="fi-school">' + esc(it.school) + (it.mode ? ' · ' + esc(it.mode) : '') + '</span>' +
              '<span class="fi-name">' + esc(it.name) + '</span>' +
              (metaParts.length ? '<span class="fi-meta">' + esc(metaParts.join(' · ')) + '</span>' : '') +
            '</a>';
          }).join('') +
        '</div>' +
      '</div>';
    document.body.appendChild(w);

    var fab = w.querySelector('.floater-fab');
    var panel = w.querySelector('.floater-panel');
    var closePanel = function () {
      panel.hidden = true;
      fab.classList.remove('open');
      fab.setAttribute('aria-expanded', 'false');
    };
    fab.addEventListener('click', function () {
      var willOpen = panel.hidden;
      panel.hidden = !willOpen;
      fab.setAttribute('aria-expanded', String(willOpen));
      fab.classList.toggle('open', willOpen);
    });
    w.querySelector('.floater-close').addEventListener('click', function () {
      try { sessionStorage.setItem('floaterClosed', t); } catch (e) { /* 忽略 */ }
      w.remove();
    });
    // 点击悬浮框以外区域或按 ESC：收起面板
    var docHandler = function (ev) {
      if (!panel.hidden && !w.contains(ev.target)) closePanel();
    };
    var escHandler = function (ev) {
      if (ev.key === 'Escape' && !panel.hidden) closePanel();
    };
    setTimeout(function () {
      document.addEventListener('click', docHandler);
      document.addEventListener('keydown', escHandler);
    }, 0);
    w.addEventListener('DOMNodeRemoved', function () {
      document.removeEventListener('click', docHandler);
      document.removeEventListener('keydown', escHandler);
    });
  }

  // ---- 桂林市现场招聘会（非校园）：加载 ----
  function loadGuilin() {
    if (location.protocol === 'file:') {
      state.gData = G_FALLBACK;
      state.gFallback = true;
      renderGuilin();
      return;
    }
    fetch('data/guilin_fairs.json', { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(function (d) { state.gData = d; state.gFallback = false; renderGuilin(); })
      .catch(function () {
        state.gData = G_FALLBACK;
        state.gFallback = true;
        renderGuilin();
      });
  }

  function gDateStr(it) { return (it.date || '').slice(0, 10); }
  function gIsDate(d) { return /^\d{4}-\d{2}-\d{2}$/.test(d); }

  // ---- 桂林市现场招聘会：渲染 ----
  function renderGuilin() {
    var d = state.gData;
    if (!d) return;
    var fairs = d.fairs || [];
    var t = todayStr();
    // 兜底：剔除真实日期早于今天的场次
    var active = fairs.filter(function (it) { return !gIsDate(gDateStr(it)) || gDateStr(it) >= t; });
    var count = $('guilinCount');
    count.textContent = '共 ' + active.length + ' 场' + (state.gFallback ? '（内置快照）' : '');
    count.title = '更新时间 ' + fmtUpdated(d.meta.updated_at) + (state.gFallback ? '（内置快照，线上数据加载失败）' : '');

    var kw = state.gSearch.trim();
    var list = active.filter(function (it) {
      if (state.gTarget && it.target !== state.gTarget) return false;
      if (kw) {
        var hay = (it.title + ' ' + (it.location || '') + ' ' + (it.organizer || '') + ' ' + (it.source || '')).toLowerCase();
        if (hay.indexOf(kw.toLowerCase()) < 0) return false;
      }
      return true;
    });
    list.sort(function (a, b) {
      var da = gDateStr(a), db = gDateStr(b);
      if (gIsDate(da) && gIsDate(db)) return da.localeCompare(db);
      if (gIsDate(da)) return -1;
      if (gIsDate(db)) return 1;
      return (a.title || '').localeCompare(b.title || '');
    });

    var total = list.length;
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (state.gPage > pages) state.gPage = pages;
    if (state.gPage < 1) state.gPage = 1;
    var slice = list.slice((state.gPage - 1) * PAGE_SIZE, state.gPage * PAGE_SIZE);
    var empty = $('guilinEmpty');
    if (!total) { $('guilinList').innerHTML = ''; empty.hidden = false; return; }
    empty.hidden = true;

    // 按月分组
    var groups = [];
    var tbd = [];
    slice.forEach(function (it) {
      var dd = gDateStr(it);
      if (gIsDate(dd)) {
        var key = dd.slice(0, 7);
        var g = groups.filter(function (x) { return x.key === key; })[0];
        if (!g) { g = { key: key, items: [] }; groups.push(g); }
        g.items.push(it);
      } else { tbd.push(it); }
    });
    groups.sort(function (a, b) { return a.key.localeCompare(b.key); });

    var html = '';
    var idx = 0;
    groups.forEach(function (g) {
      html += '<div class="group-head"><span>' + g.key.slice(0, 4) + '年' + (+g.key.slice(5, 7)) + '月</span>' +
              '<span class="g-count">' + g.items.length + ' 场</span><span class="g-line"></span></div>';
      g.items.forEach(function (it) { html += gRowHtml(it, t, idx++); });
    });
    if (tbd.length) {
      html += '<div class="group-head"><span>日期待定</span><span class="g-count">' + tbd.length + ' 场</span><span class="g-line"></span></div>';
      tbd.forEach(function (it) { html += gRowHtml(it, t, idx++); });
    }
    html += '<div class="g-pager" id="gPager"></div>';
    $('guilinList').innerHTML = html;
    renderGPager(total, pages);
  }

  function gRowHtml(it, t, idx) {
    var delay = Math.min(idx * 0.02, 0.4);
    var dd = gDateStr(it);
    var dayHtml, hot = false, hotCls = '';
    if (gIsDate(dd)) {
      var f = fmtDate(dd);
      var days = Math.round((new Date(+f.y, +f.m - 1, +f.d) - new Date(+t.split('-')[0], +t.split('-')[1] - 1, +t.split('-')[2])) / 86400000);
      var badge;
      if (days === 0) { badge = '<span class="fd-badge today">今天举行</span>'; hot = true; hotCls = 'hot-today'; }
      else if (days === 1) { badge = '<span class="fd-badge tomorrow">明天举行</span>'; hot = true; hotCls = 'hot-tomorrow'; }
      else if (days === 2) { badge = '<span class="fd-badge dayafter">后天举行</span>'; hot = true; hotCls = 'hot-dayafter'; }
      else if (days <= 7) { badge = '<span class="fd-badge soon">' + days + ' 天后</span>'; }
      else { badge = '<span class="fd-badge later"></span>'; }
      dayHtml = '<span class="fd-day">' + f.m + '/' + f.d + '</span><span class="fd-ym">' + f.y + '年</span>' + badge;
    } else {
      dayHtml = '<span class="fd-tbd">日期待定</span><span class="fd-ym">以公告为准</span><span class="fd-badge tbd">待定</span>';
    }

    var target = it.target || '社招/综合';
    var targetCls = target.indexOf('校招') >= 0 ? 'g-target-grad' : 'g-target-job';
    var timeTxt = '';
    if (gIsDate(dd) && dd === (it.date_end || '').slice(0, 10)) {
      var hm = (it.date || '').match(/(\d{1,2}):(\d{2})/);
      var hm2 = (it.date_end || '').match(/(\d{1,2}):(\d{2})/);
      if (hm && hm2 && (+hm[1] <= 23)) timeTxt = hm[1] + ':' + hm[2] + ' - ' + hm2[1] + ':' + hm2[2];
    }
    var loc = (it.location || '').trim();
    var org = (it.organizer || '').trim();
    var note = (it.note || '').trim();
    var phone = (it.phone || '').trim();
    var srcBadge = it.source === '桂林人才网' ? 'g-src-glrcw' : 'g-src-rsj';

    var meta = [];
    if (timeTxt) meta.push('<span class="f-time"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>' + esc(timeTxt) + '</span>');
    if (loc && loc !== '待确认') meta.push('<span class="f-loc"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-5.1-7-11a7 7 0 1 1 14 0c0 5.9-7 11-7 11z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/></svg><span>' + esc(loc) + '</span></span>');

    return '<div class="fair-row' + (hot ? ' hot ' + hotCls : '') + '" role="row" style="animation-delay:' + delay + 's">' +
        '<div class="f-date" role="cell">' + dayHtml + '</div>' +
        '<div class="f-main" role="cell">' +
          '<div class="f-title-row">' +
            '<a class="f-title" href="' + esc(it.url) + '" target="_blank" rel="noopener" title="' + esc(it.title) + '">' + esc(it.title) + '</a>' +
            '<a class="f-action" href="' + esc(it.url) + '" target="_blank" rel="noopener">公告' +
              '<svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
            '</a>' +
          '</div>' +
          '<div class="f-meta">' +
            '<span class="tag ' + targetCls + '">' + esc(target) + '</span>' +
            '<span class="tag g-src ' + srcBadge + '">' + esc(it.source || '') + '</span>' +
            (org && org !== '待确认' ? '<span class="g-org">主办：' + esc(org) + '</span>' : '') +
            meta.join('') +
          '</div>' +
          (note ? '<p class="f-note">' + esc(note) + '</p>' : '') +
          (phone ? '<p class="g-phone">咨询电话：' + esc(phone) + '</p>' : '') +
        '</div>' +
      '</div>';
  }

  function renderGPager(total, pages) {
    var box = $('gPager');
    if (!box) return;
    if (total <= PAGE_SIZE) { box.innerHTML = ''; return; }
    var cur = state.gPage;
    var html = '<span class="pager-info">第 ' + cur + ' / ' + pages + ' 页 · 共 ' + total + ' 场</span>';
    html += '<button type="button" data-gpage="' + (cur - 1) + '"' + (cur === 1 ? ' disabled' : '') + ' aria-label="上一页">‹ 上一页</button>';
    var seq = [];
    if (pages <= 7) { for (var i = 1; i <= pages; i++) seq.push(i); }
    else {
      var set = [1, pages, cur - 1, cur, cur + 1];
      set.forEach(function (p) { if (p >= 1 && p <= pages && seq.indexOf(p) < 0) seq.push(p); });
      seq.sort(function (a, b) { return a - b; });
      var out = [];
      for (var k = 0; k < seq.length; k++) {
        if (k > 0 && seq[k] - seq[k - 1] > 1) out.push('gap');
        out.push(seq[k]);
      }
      seq = out;
    }
    seq.forEach(function (p) {
      if (p === 'gap') { html += '<span class="gap">…</span>'; return; }
      html += '<button type="button" data-gpage="' + p + '"' + (p === cur ? ' class="current" aria-current="page"' : '') + '>' + p + '</button>';
    });
    html += '<button type="button" data-gpage="' + (cur + 1) + '"' + (cur === pages ? ' disabled' : '') + ' aria-label="下一页">下一页 ›</button>';
    box.innerHTML = html;
  }

  // ---- 交互 ----
  function resetPage() { state.page = 1; }
  $('searchInput').addEventListener('input', function (e) { state.search = e.target.value; resetPage(); render(); });
  $('schoolSelect').addEventListener('change', function (e) { state.school = e.target.value; resetPage(); render(); });
  $('formSelect').addEventListener('change', function (e) { state.form = e.target.value; resetPage(); render(); });
  $('sortToggle').addEventListener('click', function () {
    state.sortMode = state.sortMode === 'date' ? 'school' : 'date';
    $('sortLabel').textContent = state.sortMode === 'date' ? '按日期排序' : '按学校排序';
    resetPage(); render();
  });
  var tabs = document.querySelectorAll('.tab');
  tabs.forEach(function (tb) {
    tb.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-selected', 'false'); });
      tb.classList.add('active');
      tb.setAttribute('aria-selected', 'true');
      state.view = tb.getAttribute('data-view');
      resetPage(); render();
    });
  });
  $('guilinSearch').addEventListener('input', function (e) { state.gSearch = e.target.value; state.gPage = 1; renderGuilin(); });
  $('guilinTarget').addEventListener('change', function (e) { state.gTarget = e.target.value; state.gPage = 1; renderGuilin(); });
  document.addEventListener('click', function (e) {
    var gbtn = e.target.closest ? e.target.closest('#gPager button[data-gpage]') : null;
    if (gbtn) {
      var gp = +gbtn.getAttribute('data-gpage');
      if (gp >= 1 && gp !== state.gPage) { state.gPage = gp; renderGuilin(); }
      return;
    }
    var btn = e.target.closest ? e.target.closest('#pager button[data-page]') : null;
    if (!btn) return;
    var p = +btn.getAttribute('data-page');
    if (p >= 1 && p !== state.page) { state.page = p; render(); }
  });

  load();
  loadGuilin();
})();
