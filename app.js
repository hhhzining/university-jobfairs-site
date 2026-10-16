/* 广西12校双选会日历 · 逻辑层 */
(function () {
  'use strict';

  // ---- 内置快照（fetch 失败 / 本地 file:// 预览时兜底；线上优先读 data/jobfairs.json）----
  var FALLBACK = {
    meta: {
      updated_at: '2026-10-16T00:00:00+08:00',
      note: '内置快照（2026-10-16 人工逐校官网核查）',
      school_count: 12,
      jobfair_count: 38,
      schools_status: {
        '广西大学': {status: '已查-有未来场次'},
        '广西科技大学': {status: '已查-有未来场次'},
        '桂林电子科技大学': {status: '已查-有未来场次'},
        '广西师范大学': {status: '已查-有未来场次'},
        '南宁师范大学': {status: '已查-有未来场次'},
        '桂林理工大学': {status: '已查-有未来场次'},
        '广西民族大学': {status: '已查-有未来场次'},
        '广西财经学院': {status: '已查-有未来场次'},
        '广西科技师范学院': {status: '已查-暂无未来场次'},
        '北部湾大学': {status: '已查-有未来场次'},
        '广西工业学院': {status: '已查-有未来场次'},
        '桂林航天工业学院': {status: '已查-有未来场次'}
      }
    },
    schools: [
      {name: '广西大学', city: '南宁'}, {name: '广西科技大学', city: '柳州'},
      {name: '桂林电子科技大学', city: '桂林'}, {name: '广西师范大学', city: '桂林'},
      {name: '南宁师范大学', city: '南宁'}, {name: '桂林理工大学', city: '桂林'},
      {name: '广西民族大学', city: '南宁'}, {name: '广西财经学院', city: '南宁'},
      {name: '广西科技师范学院', city: '来宾'}, {name: '北部湾大学', city: '钦州'},
      {name: '广西工业学院', city: '北海'}, {name: '桂林航天工业学院', city: '桂林'}
    ],
    jobfairs: [
      {school: '桂林电子科技大学', city: '桂林', name: '广西2027届人工智能及电子信息技术类高校毕业生就业双选会', date: '2026-10-16', mode: '线下', location: '桂林电子科技大学花江校区正德广场', url: 'https://jy.guet.edu.cn/module/jobfairs', note: '自治区级行业类专场，学校承办；今日上午9:30；约600个展位'},
      {school: '桂林航天工业学院', city: '桂林', name: '学校2027届毕业生校园综合双选会', date: '2026-10-17', mode: '线下', location: '南校区田径场', url: 'https://guat.edu.cn/info/1002/23651.htm', note: '面向2027届毕业生综合类；9:30'},
      {school: '广西大学', city: '南宁', name: '广西大学土木建筑工程学院2027届毕业生双选会', date: '2026-10-17', mode: '线下', location: '广西大学东校园大学生活动中心', url: 'http://jyy.gxu.edu.cn/module/jobfairs?menu_id=34130', note: '学院专场，约80个展位'},
      {school: '广西工业学院', city: '北海', name: '广西工业学院（原桂林电子科技大学北海校区）2027届毕业生秋季双选会', date: '2026-10-23', mode: '线下', location: '南珠西校区田径场', url: 'https://gliet.gxbys.com/jobfair/index', note: '58个展位；09:30-13:00'},
      {school: '广西大学', city: '南宁', name: '广西大学2027届毕业生秋季双选会', date: '2026-10-24', mode: '线下', location: '广西大学西校园篮球场及田径场', url: 'http://jyy.gxu.edu.cn/module/jobfairs?menu_id=34130', note: '校级综合类，约600个展位'},
      {school: '广西师范大学', city: '桂林', name: '广西师范大学2027届毕业生秋季综合类双选会', date: '2026-10-27', mode: '线下', location: '雁山校区大创楼一楼大学生就业指导中心', url: 'https://gxnu.bysjy.com.cn/module/jobfairs', note: '14:30；100个展位'},
      {school: '桂林电子科技大学', city: '桂林', name: '第五届云校招"名企优岗广西行"2027届毕业生秋季组团招聘会（花江校区第二场）', date: '2026-10-27', mode: '线下', location: '花江校区学生活动中心', url: 'https://jy.guet.edu.cn/module/jobfairs', note: '云校招巡回；14:30；30个展位'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届机械汽车、自动化类毕业生专场双选会', date: '2026-10-27', mode: '线下', location: '柳东校区南广场', url: 'http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=c4a9fa0e-5aef-719c-eda5-05bf8b95ebb0', note: '机械汽车/自动化类专场（中型）'},
      {school: '桂林理工大学', city: '桂林', name: '【桂林理工大学雁山校区第二场】第五届云校招"名企优岗广西行"2027届毕业生秋季巡回双选会', date: '2026-10-28', mode: '线下', location: '雁山校区新体育馆一楼篮球场', url: 'https://gxnu.bysjy.com.cn/module/jobfairs?menu_id=13569', note: '云校招巡回；14:30；60个展位'},
      {school: '北部湾大学', city: '钦州', name: '职聚滨海运河城 青春启航向未来——2026年工会就业服务进校园暨北部湾大学2027届毕业生双选会', date: '2026-10-30', mode: '线下', location: '北部湾大学大学生创业园一楼大厅', url: 'https://qzhu.bysjy.com.cn/module/jobfairs?menu_id=13542&type=1', note: '钦州市总工会主办；100个展位'},
      {school: '广西民族大学', city: '南宁', name: '广西民族大学2027届毕业生武鸣校区专场招聘会', date: '2026-10-31', mode: '线下', location: '武鸣校区校前广场', url: 'https://jyb.gxmzu.edu.cn/module/jobfairs?menu_id=24306', note: '约60个展位；9:30'},
      {school: '广西财经学院', city: '南宁', name: '广西2027届财经类高校毕业生就业双选会', date: '2026-10-31', mode: '线下', location: '广西财经学院相思湖校区足球场', url: 'https://www.gxbys.com/jobfair91/view?id=40872', note: '财经类专场；9:00-14:30'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届生物化工类毕业生双选会', date: '2026-11-03', mode: '线下', location: '柳石校区田径场', url: 'http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=60c2a359-db4c-2383-9f79-cf3851a336de', note: '生物化工类专场（中型）'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届医学类毕业生专场双选会', date: '2026-11-03', mode: '线下', location: '柳石校区田径场', url: 'http://gxkejidx.jiuyeb.cn/Chuangye/detail.html?id=596be7e1-d822-512b-ccbc-540ecb93af51', note: '医学类专场'},
      {school: '桂林电子科技大学', city: '桂林', name: '2026年广东省专精特新企业校园招聘会（广西专场）', date: '2026-11-06', mode: '线下', location: '花江校区正德广场', url: 'https://jy.guet.edu.cn/module/jobfairs', note: '广东专精特新企业组团来校；约500个展位'},
      {school: '桂林航天工业学院', city: '桂林', name: '2027届毕业生航天航空暨校友单位招聘会', date: '2026-11-07', mode: '线下', location: '待确认', url: 'https://www.guat.edu.cn/info/1005/23531.htm', note: '航天航空行业及校友单位专场；地点待学校通知'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2026年秋季校园双选会（第二场）', date: '2026-11-10', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办（2027届招聘安排表预排）'},
      {school: '北部湾大学', city: '钦州', name: '北部湾大学经济管理学院2027届毕业生秋季就业双选会', date: '2026-11-10', mode: '线下', location: '北部湾大学四号教学楼', url: 'https://qzhu.bysjy.com.cn/module/jobfairs?menu_id=13542&type=1', note: '经济管理学院专场；40个展位'},
      {school: '广西民族大学', city: '南宁', name: '广西民族大学2027届毕业生秋季第二场双选会', date: '2026-11-14', mode: '线下', location: '思源湖校区李宁田径场', url: 'https://jyb.gxmzu.edu.cn/module/jobfairs?menu_id=24306', note: '自治区人社厅、教育厅主办；约150个展位'},
      {school: '广西民族大学', city: '南宁', name: '广西民族大学民族学与社会学学院、马克思主义学院、政治与公共管理学院2027届毕业生综合类专场招聘会', date: '2026-11-21', mode: '线下', location: '相思湖校区灯光球场', url: 'https://jyb.gxmzu.edu.cn/module/jobfairs?menu_id=24306', note: '学院综合类专场，约100个展位'},
      {school: '广西师范大学', city: '桂林', name: '广西2027届师范类毕业生就业双选会（桂林专场）暨教育部直属师范大学2027届广西籍公费师范毕业生就业双选会', date: '2026-11-28', mode: '线下', location: '广西师范大学雁山校区', url: 'https://www.gxbys.com/news/view/aid/312022/preview/1?target=_blank', note: '自治区级师范类专场'},
      {school: '广西科技大学', city: '柳州', name: '2027届毕业生网络双选会（第一场）', date: '2026-12-01', mode: '线上', location: '就业宝平台', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '网络双选会；拟举办'},
      {school: '南宁师范大学', city: '南宁', name: '广西2027届师范类毕业生就业双选会（南宁专场）暨教育部直属师范大学2027届广西籍公费师范毕业生就业双选会', date: '2026-12-05', mode: '线下', location: '南宁师范大学五合校区', url: 'https://www.gxbys.com/news/view/aid/312022/tag/wzgg', note: '自治区统筹师范类专场；具体以学校邀请函为准'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届土木建筑工程类毕业生专场双选会', date: '2026-12-10', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '土木建筑类专场（中型）；拟举办'},
      {school: '广西民族大学', city: '南宁', name: '广西2027届综合性高校毕业生就业双选会暨广西2027届"少数民族高层次骨干人才计划"毕业生就业双选会', date: '2027-01-09', mode: '线下', location: '思源湖校区李宁田径场', url: 'https://www.gxbys.com/news/view/aid/312022/tag/wzgg', note: '自治区统筹综合性专场'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027年春季校园双选会', date: '2027-03-19', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '广西民族大学', city: '南宁', name: '广西2027届高校毕业生"宏志助航计划"就业双选会（南宁专场）', date: '2027-03-20', mode: '线下', location: '相思湖校区灯光球场', url: 'https://www.gxbys.com/news/view/aid/312022/tag/wzgg', note: '自治区统筹宏志助航计划专场'},
      {school: '桂林理工大学', city: '桂林', name: '广西2027届高校毕业生春季双选会暨"百县对百校促就业行动"广西专场人才招聘会', date: '2027-03-26', mode: '线下', location: '桂林理工大学雁山校区体育馆', url: 'https://www.gxbys.com/news/view/aid/312022/preview/1?target=_blank', note: '自治区级春季综合双选会'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届机械汽车、自动化类毕业生专场双选会', date: '2027-03-26', mode: '线下', location: '柳东校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '广西师范大学', city: '桂林', name: '广西2027届高校毕业生"宏志助航计划"就业双选会（桂林专场）', date: '2027-03-27', mode: '线下', location: '广西师范大学雁山校区', url: 'https://www.gxbys.com/news/view/aid/312022/preview/1?target=_blank', note: '自治区级宏志助航计划专场'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届生物化工类毕业生专场双选会', date: '2027-03-30', mode: '线下', location: '柳石校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '桂林电子科技大学', city: '桂林', name: '广西2027届高校毕业生军工类企业就业双选会', date: '2027-04-09', mode: '线下', location: '花江校区', url: 'https://www.gxbys.com/news/view/aid/312022/preview/1?target=_blank', note: '自治区级军工类专场'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届计算机科学与技术类、电子工程类毕业生专场双选会', date: '2027-04-09', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '广西科技大学', city: '柳州', name: '广西2027届高校毕业生"宏志助航计划"就业双选会（柳州专场）', date: '2027-04-16', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '广西科技大学', city: '柳州', name: '2027届毕业生网络双选会（第二场）', date: '2027-06-01', mode: '线上', location: '就业宝平台', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '网络双选会；拟举办'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学2027届毕业生"百日冲刺"双选会暨2028届毕业生实习见习专场招聘会', date: '2027-06-11', mode: '线下', location: '文昌校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学柳石校区2027届毕业生秋季专场双选会', date: '待确认（拟2026年11月）', mode: '线下', location: '柳石校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办，具体日期以就业网公布为准'},
      {school: '广西科技大学', city: '柳州', name: '广西科技大学柳石校区2027届毕业生春季专场双选会', date: '待确认（拟2027年4月）', mode: '线下', location: '柳石校区', url: 'http://gxkejidx.jiuyeb.cn/News/zdydetail.html?cateid=null&id=10ee6de5-569c-243e-af7f-f83e3deaaf90', note: '拟举办，具体日期以就业网公布为准'}
    ]
  };

  // ---- 状态 ----
  var state = {
    data: null,
    isFallback: false,
    search: '',
    school: '',
    view: 'all',
    sortMode: 'date' // date | school
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
    var m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
    if (!m) return '更新时间未知';
    return '更新于 ' + m[1] + '-' + m[2] + '-' + m[3] + ' ' + m[4] + ':' + m[5];
  }
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // ---- 加载数据 ----
  function load() {
    // file:// 本地预览无法 fetch（浏览器限制），直接用内置快照
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

    // 更新时间
    $('updatedAt').textContent = fmtUpdated(d.meta.updated_at) + (state.isFallback ? '（内置快照）' : '');
    $('repoLink').href = 'https://github.com/hhhzining/university-jobfairs-site';

    // 统计
    var near = fairs.filter(function (it) {
      return it.date && it.date.indexOf('待确认') !== 0 && it.date >= t && it.date <= addDays(t, 6);
    }).length;
    var online = fairs.filter(function (it) { return (it.mode || '').indexOf('线上') >= 0; }).length;
    $('stTotal').textContent = fairs.length;
    $('stNear').textContent = near;
    $('stSchools').textContent = d.schools ? d.schools.length : 12;
    $('stOnline').textContent = online;

    // 学校下拉
    var sel = $('schoolSelect');
    sel.innerHTML = '<option value="">全部学校（' + (d.schools ? d.schools.length : 12) + '所）</option>';
    (d.schools || []).forEach(function (s) {
      var o = document.createElement('option');
      o.value = s.name;
      o.textContent = s.name + (s.city ? '（' + s.city + '）' : '');
      if (state.school === s.name) o.selected = true;
      sel.appendChild(o);
    });

    // 筛选
    var kw = state.search.trim();
    var list = fairs.filter(function (it) {
      if (state.school && it.school !== state.school) return false;
      if (state.view === '7d') {
        var dd = it.date || '';
        if (dd.indexOf('待确认') === 0) return false;
        if (dd < t || dd > addDays(t, 6)) return false;
      }
      if (state.view === 'online' && (it.mode || '').indexOf('线上') < 0) return false;
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

    $('resultCount').textContent = '共 ' + list.length + ' 场';
    renderList(list, t);
    renderSchools(d);
  }

  function dateKey(it) {
    var dd = it.date || '';
    if (/^\d{4}-\d{2}-\d{2}$/.test(dd)) return '0' + dd;
    return '1' + dd;
  }

  function renderList(list, t) {
    var wrap = $('fairList');
    var empty = $('emptyState');
    if (!list.length) {
      wrap.innerHTML = '';
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    var html = '';
    list.forEach(function (it) {
      var dd = it.date || '';
      var badge, cls = 'date-badge';
      if (/^\d{4}-\d{2}-\d{2}$/.test(dd)) {
        var f = fmtDate(dd);
        var soon = dd <= addDays(t, 6) ? ' soon' : '';
        badge = '<span class="d">' + f.m + '/' + f.d + '</span><span class="m">' + f.y + '</span>';
        cls += soon;
      } else {
        badge = '<span class="d" style="font-size:13px">待定</span><span class="m">日期</span>';
        cls += ' tbd';
      }
      var mode = (it.mode || '').trim();
      var tagCls = mode.indexOf('线上') >= 0 ? 'tag-online' : (mode.indexOf('线下') >= 0 ? 'tag-offline' : 'tag-unknown');
      var tagTxt = mode || '待确认';
      var loc = (it.location || '').trim();
      var note = (it.note || '').trim();
      html +=
        '<article class="fair-card">' +
          '<div class="' + cls + '">' + badge + '</div>' +
          '<div class="fair-main">' +
            '<a class="fair-title" href="' + esc(it.url) + '" target="_blank" rel="noopener">' + esc(it.name) + '</a>' +
            '<div class="fair-meta">' +
              '<span class="school-name">' + esc(it.school) + (it.city ? ' · ' + esc(it.city) : '') + '</span>' +
              '<span class="tag ' + tagCls + '">' + esc(tagTxt) + '</span>' +
              (loc && loc !== '待确认' ? '<span class="loc-pin"><svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-5.1-7-11a7 7 0 1 1 14 0c0 5.9-7 11-7 11z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/></svg></span><span>' + esc(loc) + '</span>' : '') +
            '</div>' +
            (note ? '<p class="fair-note">' + esc(note) + '</p>' : '') +
            '<a class="fair-link" href="' + esc(it.url) + '" target="_blank" rel="noopener">查看官方公告' +
              '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
            '</a>' +
          '</div>' +
        '</article>';
    });
    wrap.innerHTML = html;
  }

  function renderSchools(d) {
    var grid = $('schoolGrid');
    var st = d.meta.schools_status || {};
    var html = '';
    (d.schools || []).forEach(function (s) {
      var info = st[s.name] || {};
      var ok = (info.status || '').indexOf('有未来场次') >= 0;
      html +=
        '<div class="school-item ' + (ok ? 'ok' : 'no') + '">' +
          '<span><span class="s-name">' + esc(s.name) + '</span>' + (s.city ? '<span class="s-city">' + esc(s.city) + '</span>' : '') + '</span>' +
          '<span class="s-status">' + esc(ok ? '有场次' : '暂无') + '</span>' +
        '</div>';
    });
    grid.innerHTML = html;
  }

  // ---- 交互 ----
  $('searchInput').addEventListener('input', function (e) { state.search = e.target.value; render(); });
  $('schoolSelect').addEventListener('change', function (e) { state.school = e.target.value; render(); });
  $('sortToggle').addEventListener('click', function () {
    state.sortMode = state.sortMode === 'date' ? 'school' : 'date';
    this.textContent = state.sortMode === 'date' ? '按日期排序' : '按学校排序';
    render();
  });
  var tabs = document.querySelectorAll('.tab');
  tabs.forEach(function (tb) {
    tb.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-selected', 'false'); });
      tb.classList.add('active');
      tb.setAttribute('aria-selected', 'true');
      state.view = tb.getAttribute('data-view');
      render();
    });
  });

  load();
})();
