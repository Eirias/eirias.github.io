/* ============================================================
   Portfolio interactions: theme + language + nav scrollspy.
   State persists in localStorage. No dependencies.
   ============================================================ */
(function () {
  "use strict";

  var root = document.documentElement;
  var STORE_THEME = "sv-theme";
  var STORE_LANG = "sv-lang";

  /* ---------- theme ---------- */
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var label = document.getElementById("theme-label");
    if (label) label.textContent = theme;
  }

  var savedTheme = localStorage.getItem(STORE_THEME);
  if (!savedTheme) {
    savedTheme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  applyTheme(savedTheme);

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORE_THEME, next);
    });
  }

  /* ---------- language ---------- */
  function applyLang(lang) {
    root.setAttribute("lang", lang);
    var nodes = document.querySelectorAll("[data-en]");
    for (var i = 0; i < nodes.length; i++) {
      var val = nodes[i].getAttribute("data-" + lang);
      if (val != null) nodes[i].innerHTML = val;
    }
    var label = document.getElementById("lang-label");
    if (label) label.textContent = lang.toUpperCase();

    // point résumé downloads at the matching-language PDF
    var cv = lang === "de" ? "assets/cv/CV-DE.pdf" : "assets/cv/CV-EN.pdf";
    ["resume-link", "resume-link-2"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.setAttribute("href", cv);
    });
  }

  // default to EN for first-time visitors; saved choice still wins
  var savedLang = localStorage.getItem(STORE_LANG) || "en";
  applyLang(savedLang);

  var langBtn = document.getElementById("lang-toggle");
  if (langBtn) {
    langBtn.addEventListener("click", function () {
      var next = root.getAttribute("lang") === "de" ? "en" : "de";
      applyLang(next);
      localStorage.setItem(STORE_LANG, next);
    });
  }

  /* ---------- nav scrollspy ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav__link"));
  var sections = links
    .map(function (l) { return document.querySelector(l.getAttribute("href")); })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          links.forEach(function (l) {
            l.classList.toggle("is-active", l.getAttribute("href") === "#" + id);
          });
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { observer.observe(s); });
  }

  /* ---------- footer year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- project screenshots: thumbnail strip + lightbox ---------- */
  (function () {
    var strips = document.querySelectorAll("[data-shots]");
    if (!strips.length) return;

    var lb, lbImg, lbCount, gallery = [], idx = 0;

    function build() {
      lb = document.createElement("div");
      lb.className = "lightbox";
      lb.setAttribute("aria-hidden", "true");
      lb.innerHTML =
        '<button class="lightbox__close" type="button" aria-label="Close">✕</button>' +
        '<button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Previous">‹</button>' +
        '<img class="lightbox__img" alt="" />' +
        '<button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Next">›</button>' +
        '<span class="lightbox__count"></span>';
      document.body.appendChild(lb);
      lbImg = lb.querySelector(".lightbox__img");
      lbCount = lb.querySelector(".lightbox__count");
      lb.querySelector(".lightbox__close").addEventListener("click", close);
      lb.querySelector(".lightbox__nav--prev").addEventListener("click", function (e) { e.stopPropagation(); step(-1); });
      lb.querySelector(".lightbox__nav--next").addEventListener("click", function (e) { e.stopPropagation(); step(1); });
      lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    }

    function render() {
      lbImg.src = gallery[idx];
      lbCount.textContent = (idx + 1) + " / " + gallery.length;
      lbCount.style.display = gallery.length > 1 ? "" : "none";
    }
    function open(g, i) {
      if (!lb) build();
      gallery = g; idx = i;
      lb.classList.add("is-open");
      lb.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      render();
    }
    function close() {
      if (!lb) return;
      lb.classList.remove("is-open");
      lb.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
    function step(d) {
      idx = (idx + d + gallery.length) % gallery.length;
      render();
    }

    Array.prototype.forEach.call(strips, function (strip) {
      var thumbs = Array.prototype.slice.call(strip.querySelectorAll(".shots__thumb"));
      var urls = thumbs.map(function (t) { return t.getAttribute("data-full"); });
      if (thumbs.length > 3) {
        strip.classList.add("shots--more");
        thumbs[2].setAttribute("data-more", "+" + (thumbs.length - 3));
      }
      thumbs.forEach(function (t, i) {
        t.addEventListener("click", function () { open(urls, i); });
      });
    });

    document.addEventListener("keydown", function (e) {
      if (!lb || !lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft") step(-1);
      else if (e.key === "ArrowRight") step(1);
    });
  })();
})();
