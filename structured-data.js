// 把 data/opportunities.json 里已核验并已发布的条目补成 schema.org Event 块。
// 只读现有字段（标题、地点、起止时间、主办方、报名费），不新增任何描述性文字。
// 沿用站点既有规则：未核验或未发布的不进入结构化数据。
(function () {
  'use strict';

  var SITE = 'https://operalirico.github.io/Opera-Lirico/';
  var ORG = {
    '@type': 'Organization',
    '@id': SITE + '#org',
    name: 'OperaLab.',
    url: SITE
  };

  function line(item) {
    var node = {
      '@type': 'Event',
      '@id': (item.announcement_url || item.source_url || SITE) + '#' + item.id,
      name: item.title_zh || item.title,
      url: item.announcement_url || item.source_url,
      eventStatus: 'https://schema.org/EventScheduled'
    };

    if (item.application_open_at) node.startDate = item.application_open_at;
    if (item.application_deadline_at) node.endDate = item.application_deadline_at;
    if (item.location) node.location = { '@type': 'Place', name: item.location };

    if (item.source_name) {
      node.organizer = { '@type': 'Organization', name: item.source_name };
      if (item.source_url) node.organizer.url = item.source_url;
    }

    if (typeof item.fee_eur === 'number' && item.fee_eur > 0) {
      node.offers = {
        '@type': 'Offer',
        price: item.fee_eur,
        priceCurrency: 'EUR',
        url: node.url
      };
      if (item.application_deadline_at) node.offers.validThrough = item.application_deadline_at;
    }

    return node;
  }

  function inject(graph) {
    if (document.querySelector('script[data-structured-data="events"]')) return;
    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.setAttribute('data-structured-data', 'events');
    script.textContent = JSON.stringify({ '@context': 'https://schema.org', '@graph': graph });
    document.head.appendChild(script);
  }

  fetch('data/opportunities.json', { cache: 'no-store' })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      if (!data || !Array.isArray(data.items)) return;

      var published = data.items.filter(function (item) {
        return item &&
          item.publication_status === 'published' &&
          item.review_status === 'verified' &&
          item.title &&
          item.application_deadline_at;
      });

      if (!published.length) return;

      var graph = [ORG].concat(published.slice(0, 12).map(line));
      inject(graph);
    })
    .catch(function () { /* 结构化数据不是渲染依赖，失败不影响页面 */ });
})();
