/* NAOの副業ラボ - 共通スクリプト（フレームワーク不使用） */
(function () {
  "use strict";

  /* ---------- モバイルハンバーガーメニュー ---------- */
  function initNavToggle() {
    var toggle = document.getElementById("nav-toggle");
    var nav = document.getElementById("main-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- 記事一覧のカテゴリ絞り込み ---------- */
  function initFilterBar() {
    var bar = document.getElementById("filter-bar");
    var cards = document.querySelectorAll("#card-grid .card");
    if (!bar) return;
    bar.addEventListener("click", function (e) {
      var btn = e.target.closest(".filter-pill");
      if (!btn) return;
      bar.querySelectorAll(".filter-pill").forEach(function (b) {
        b.classList.remove("active");
      });
      btn.classList.add("active");
      var filter = btn.getAttribute("data-filter");
      cards.forEach(function (card) {
        var show = filter === "all" || card.getAttribute("data-cat") === filter;
        card.classList.toggle("is-hidden", !show);
      });
    });
  }

  /* ---------- スクロールで軽くフェードイン ---------- */
  /* IntersectionObserverが発火する前でもコンテンツが読めるよう、
     早めのrootMarginと強制表示タイマーの二重の安全策を入れている。 */
  function initScrollReveal() {
    var targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;
    function revealAll() {
      targets.forEach(function (el) { el.classList.add("is-visible"); });
    }
    if (!("IntersectionObserver" in window)) {
      revealAll();
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0, rootMargin: "0px 0px 400px 0px" }
    );
    targets.forEach(function (el) { io.observe(el); });
    // セーフティネット：何らかの理由で発火しなかった要素も必ず表示する
    setTimeout(revealAll, 1500);
  }

  /* ---------- 簡易副業診断 ---------- */
  var DIAGNOSIS_QUESTIONS = [
    {
      q: "まず、どちらのスタイルで始めたいですか？",
      options: [
        { label: "スマホだけで、すきま時間に", scores: { poikatsu: 2, sns: 1 } },
        { label: "PCを使ってじっくり取り組みたい", scores: { affiliate: 2, content: 1, crowd: 1 } },
      ],
    },
    {
      q: "初期費用について、どう考えていますか？",
      options: [
        { label: "できるだけかけたくない", scores: { poikatsu: 2, sns: 1, crowd: 1 } },
        { label: "少額の投資なら問題ない", scores: { affiliate: 2, content: 1, skill: 1 } },
      ],
    },
    {
      q: "人と話したり、やり取りするのは得意ですか？",
      options: [
        { label: "得意なほう", scores: { skill: 2, sns: 1, crowd: 1 } },
        { label: "あまり得意ではない", scores: { affiliate: 1, poikatsu: 1, sedori: 1 } },
      ],
    },
    {
      q: "文章を書くのは好きですか？",
      options: [
        { label: "好き・苦にならない", scores: { affiliate: 2, content: 2 } },
        { label: "できれば避けたい", scores: { poikatsu: 1, sedori: 2, crowd: 1 } },
      ],
    },
    {
      q: "収入が欲しいタイミングは？",
      options: [
        { label: "できるだけ早く欲しい", scores: { poikatsu: 2, crowd: 2, sedori: 1 } },
        { label: "時間をかけてでも大きく育てたい", scores: { affiliate: 2, content: 2, skill: 1 } },
      ],
    },
    {
      q: "自分の得意なこと・経験を活かしたいですか？",
      options: [
        { label: "活かしたい", scores: { skill: 2, content: 1 } },
        { label: "特にこだわらない", scores: { poikatsu: 1, crowd: 1, sedori: 1 } },
      ],
    },
    {
      q: "コツコツ作業と、発信・PRするのどちらが好み？",
      options: [
        { label: "コツコツ作業するほう", scores: { crowd: 2, sedori: 2, poikatsu: 1 } },
        { label: "発信してPRするほう", scores: { sns: 2, affiliate: 1, content: 1 } },
      ],
    },
  ];

  var DIAGNOSIS_RESULTS = {
    poikatsu: {
      title: "ポイ活（ポイントサイト）",
      reason: "スマホひとつ・すきま時間・初期費用ゼロで始めやすく、最初の一歩に向いています。",
      difficulty: "★☆☆（やさしい）",
      cost: "0円〜",
      timeline: "早ければ数日〜1ヶ月ほどでポイントが貯まり始めます",
      firstStep: "安全なポイントサイトを1つ選んで無料登録してみましょう。",
      link: "articles/05-poikatsu-basics.html",
      linkLabel: "ポイ活の始め方を見る",
    },
    sns: {
      title: "SNS運用",
      reason: "発信やPRが得意で、すきま時間にスマホで取り組みたい方に向いています。",
      difficulty: "★★☆（継続がカギ）",
      cost: "0円〜",
      timeline: "収益化の目安は数ヶ月〜半年ほど",
      firstStep: "興味のあるジャンルを1つ決めて、日々の発信を始めてみましょう。",
      link: "articles/04-sns-monetize.html",
      linkLabel: "SNS運用で収益化する方法を見る",
    },
    content: {
      title: "コンテンツ販売",
      reason: "自分の知識や経験を形にするのが好きな方、じっくり資産を作りたい方に向いています。",
      difficulty: "★★☆（企画力が必要）",
      cost: "0〜数千円（プラットフォーム利用料など）",
      timeline: "初収益まで1〜3ヶ月ほどが目安",
      firstStep: "得意なテーマを1つ決めて、note・BASEなどに登録してみましょう。",
      link: "articles/02-content-sales-start.html",
      linkLabel: "コンテンツ販売の始め方を見る",
    },
    affiliate: {
      title: "アフィリエイト",
      reason: "文章を書くのが好きで、時間をかけてでも大きく育てたい方に向いています。",
      difficulty: "★★★（継続と工夫が必要）",
      cost: "0〜数千円（サーバー・ドメイン代など）",
      timeline: "初収益まで3〜6ヶ月ほどが目安",
      firstStep: "ASP（アフィリエイトサービス）に登録し、ブログの準備を始めましょう。",
      link: "articles/03-affiliate-blog-start.html",
      linkLabel: "アフィリエイトブログの始め方を見る",
    },
    crowd: {
      title: "クラウドソーシング",
      reason: "PCでコツコツ作業したい方、早めに収入を得たい方に向いています。",
      difficulty: "★★☆（実績づくりが最初の壁）",
      cost: "0円〜",
      timeline: "早ければ登録から数週間で初案件を獲得できます",
      firstStep: "クラウドワークス・ランサーズなどに登録し、簡単な案件から応募してみましょう。",
      link: "articles/06-crowdsourcing-start.html",
      linkLabel: "クラウドソーシングの始め方を見る",
    },
    sedori: {
      title: "せどり・転売",
      reason: "人と話すより黙々とした作業が好きで、早めに収入を得たい方に向いています。",
      difficulty: "★★☆（仕入れの目利きが必要）",
      cost: "数千円〜（仕入れ資金）",
      timeline: "早ければ最初の販売まで数週間",
      firstStep: "まずは身近な不用品から、販売の流れを体験してみましょう。",
      link: "articles/07-sedori-basics.html",
      linkLabel: "せどり・転売の注意点を見る",
    },
    skill: {
      title: "スキル販売",
      reason: "得意なことや経験を活かしたい方、人とのやり取りが苦にならない方に向いています。",
      difficulty: "★★☆（得意分野の言語化が必要）",
      cost: "0円〜",
      timeline: "初受注まで1〜2ヶ月ほどが目安",
      firstStep: "ココナラなどに登録し、自分の得意なことを1つ出品してみましょう。",
      link: "articles/08-skill-selling.html",
      linkLabel: "スキル販売の始め方を見る",
    },
  };

  function initDiagnosis() {
    var root = document.getElementById("diagnosis");
    if (!root) return;
    var qWrap = root.querySelector("#diagnosis-question");
    var resultWrap = root.querySelector("#diagnosis-result");
    var progressEl = root.querySelector("#diagnosis-progress");
    var restartBtn = root.querySelector("#diagnosis-restart");
    var current = 0;
    var scores = {};

    function renderQuestion() {
      var q = DIAGNOSIS_QUESTIONS[current];
      progressEl.textContent = "Q" + (current + 1) + " / " + DIAGNOSIS_QUESTIONS.length;
      var html = '<p class="diagnosis-q">' + q.q + "</p>" + '<div class="diagnosis-options">';
      q.options.forEach(function (opt, i) {
        html +=
          '<button type="button" class="diagnosis-option" data-index="' +
          i +
          '">' +
          opt.label +
          "</button>";
      });
      html += "</div>";
      qWrap.innerHTML = html;
      qWrap.querySelectorAll(".diagnosis-option").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var opt = q.options[parseInt(btn.getAttribute("data-index"), 10)];
          Object.keys(opt.scores).forEach(function (key) {
            scores[key] = (scores[key] || 0) + opt.scores[key];
          });
          current += 1;
          if (current < DIAGNOSIS_QUESTIONS.length) {
            renderQuestion();
          } else {
            renderResult();
          }
        });
      });
    }

    function renderResult() {
      var best = null;
      var bestScore = -1;
      Object.keys(scores).forEach(function (key) {
        if (scores[key] > bestScore) {
          bestScore = scores[key];
          best = key;
        }
      });
      var r = DIAGNOSIS_RESULTS[best] || DIAGNOSIS_RESULTS.poikatsu;
      qWrap.hidden = true;
      progressEl.hidden = true;
      resultWrap.hidden = false;
      resultWrap.innerHTML =
        '<p class="diagnosis-result-label">あなたに向いている副業は…</p>' +
        "<h3>" + r.title + "</h3>" +
        "<p>" + r.reason + "</p>" +
        '<dl class="diagnosis-meta">' +
        "<dt>難易度</dt><dd>" + r.difficulty + "</dd>" +
        "<dt>初期費用の目安</dt><dd>" + r.cost + "</dd>" +
        "<dt>収益化までの目安</dt><dd>" + r.timeline + "</dd>" +
        "<dt>最初にやること</dt><dd>" + r.firstStep + "</dd>" +
        "</dl>" +
        '<a class="btn btn-primary" href="' + r.link + '">' + r.linkLabel + " &raquo;</a>";
      restartBtn.hidden = false;
    }

    restartBtn.addEventListener("click", function () {
      current = 0;
      scores = {};
      qWrap.hidden = false;
      progressEl.hidden = false;
      resultWrap.hidden = true;
      resultWrap.innerHTML = "";
      restartBtn.hidden = true;
      renderQuestion();
    });

    renderQuestion();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNavToggle();
    initFilterBar();
    initScrollReveal();
    initDiagnosis();
  });
})();
