/* Newsletter signup form. Posts to the operations Worker's public /api/subscribe route,
   which writes the subscriber to Buttondown with a voice-part metadata field.
   The endpoint returns codes only; all user-facing copy lives here. */
(function () {
  "use strict";

  var form = document.getElementById("newsletterForm");
  if (!form) return;
  var status = document.getElementById("nlStatus");
  var button = document.getElementById("nlSubmit");
  var email = document.getElementById("nlEmail");
  var voice = document.getElementById("nlVoice");
  var consent = document.getElementById("nlConsent");
  var honeypot = document.getElementById("nlHp");
  var config = window.OPERA_LIRICO_CONFIG || {};
  var endpoint = config.subscribeEndpoint || "";

  var MESSAGES = {
    pending_confirmation: "提交成功。请到邮箱点确认链接，确认后才开始收简报。没收到就看一眼垃圾邮件。",
    invalid_email: "这个邮箱地址看起来不完整，检查一下再提交。",
    invalid_voice: "请先选择一个声部。",
    consent_required: "需要先勾选同意，才能给你发邮件。",
    rate_limited: "提交太频繁了，过十分钟再试。",
    upstream_rate_limited: "邮件服务刚刚限流，过一会儿再提交一次。",
    not_configured: "订阅服务还没配置好，暂时收不了。",
    upstream_error: "邮件服务返回异常，稍后再试一次；一直失败可以发邮件告诉站点维护者。",
    upstream_unreachable: "连不上邮件服务，检查网络后再试。",
    origin_not_allowed: "这个页面来源不被允许提交。",
    network: "网络没通，稍后再试。"
  };

  function say(key) {
    status.textContent = MESSAGES[key] || MESSAGES.upstream_error;
    status.dataset.state = key === "pending_confirmation" ? "ok" : "error";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.textContent = "";
    status.dataset.state = "";

    var address = (email.value || "").trim();
    if (!address || !/^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/.test(address)) return say("invalid_email");
    if (!voice.value) return say("invalid_voice");
    if (!consent.checked) return say("consent_required");
    if (!endpoint) return say("not_configured");

    button.disabled = true;
    var original = button.textContent;
    button.textContent = "正在提交…";

    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // No credentials: this endpoint is public and sets nothing on the browser.
      body: JSON.stringify({
        email: address.toLowerCase(),
        voice: voice.value,
        consent: true,
        hp: (honeypot && honeypot.value) || "",
        page: location.pathname
      })
    })
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        if (result.data && result.data.result === "pending_confirmation") {
          say("pending_confirmation");
          form.reset();
          return;
        }
        say((result.data && result.data.error) || "upstream_error");
      })
      .catch(function () { say("network"); })
      .then(function () {
        button.disabled = false;
        button.textContent = original;
      });
  });
})();
