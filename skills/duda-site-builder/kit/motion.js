/* Agência Exemplo Home v2 — movimento (GSAP + ScrollTrigger + SplitText) sobre widgets nativos da Duda. */
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // As galerias ligadas a coleções são montadas pelo JS da Duda depois do carregamento.
  function whenPresent(selector, cb) {
    var el = $(selector);
    if (el) return cb(el);
    var obs = new MutationObserver(function () {
      var found = $(selector);
      if (!found) return;
      obs.disconnect();
      cb(found);
      ScrollTrigger.refresh();
    });
    // No site publicado a galeria só é montada quando chega perto da tela: observa sem prazo.
    obs.observe(document.body, { childList: true, subtree: true });
  }

  function header() {
    // Header global: fundo depois do topo; some ao descer e volta ao subir.
    var bar = $("#flex-header");
    if (!bar) return;
    var lastY = 0;
    addEventListener("scroll", function () {
      var y = scrollY;
      bar.classList.toggle("is-scrolled", y > 40);
      if (!reduce && window.gsap) {
        gsap.to(bar, { yPercent: y > lastY && y > 200 ? -110 : 0, duration: 0.6, ease: "power3.out", overwrite: "auto" });
      }
      lastY = y;
    }, { passive: true });
  }

  // Entrada do header: logo, itens do menu e botão chegam em sequência.
  function headerIntro() {
    var bar = $("#flex-header .ov-header");
    if (!bar) return;
    var items = $$(".ov-nav .unifiednav__container > .unifiednav__item-wrap", bar).filter(function (li) { return li.offsetParent; });
    gsap.set(bar, { visibility: "visible" });
    gsap.timeline({ defaults: { ease: "expo.out", duration: 1.1 }, delay: 0.3 })
      .from($$(".imageWidget, .dmImageWidget", bar).slice(0, 1), { y: -24, autoAlpha: 0 })
      .from(items, { y: -18, autoAlpha: 0, stagger: 0.08 }, 0.25)
      .from($$(".ov-header-cta, [class*='hamburger'], .hamburgerButton", bar), { y: -18, autoAlpha: 0 }, 0.6);
  }

  // Acordeão nativo: marca o item aberto (a Duda só gira a seta) para o ícone "+" do desenho.
  function faqIcons() {
    $$(".ov-faq-acc").forEach(function (acc) {
      var sync = function () {
        $$("[data-grab='accordion-item-container']", acc).forEach(function (it) {
          // Aberto = a resposta ocupa altura além do título.
          var head = $("[data-grab='accordion-item-title-wrapper']", it);
          var open = head && it.getBoundingClientRect().height - head.getBoundingClientRect().height > 24 ? "1" : "0";
          if (it.getAttribute("data-ov-open") !== open) it.setAttribute("data-ov-open", open);
        });
      };
      // A seta muda por classe (styled-components) quando a Duda abre/fecha ou termina de montar.
      var queued = false;
      new MutationObserver(function () {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () { queued = false; sync(); });
      }).observe(acc, { subtree: true, childList: true, attributes: true, attributeFilter: ["class"] });
      // Abrir/fechar muda a altura da lista (inclusive a primeira resposta aberta ao montar).
      if (window.ResizeObserver) new ResizeObserver(function () { sync(); }).observe(acc);
      // Mostra o estado novo já no clique; confere de novo quando a animação da Duda termina.
      acc.addEventListener("click", function (e) {
        var it = e.target.closest("[data-grab='accordion-item-container']");
        if (it && e.target.closest("[data-grab='accordion-item-title-wrapper']")) {
          var willOpen = it.getAttribute("data-ov-open") !== "1";
          $$("[data-grab='accordion-item-container']", acc).forEach(function (x) { x.setAttribute("data-ov-open", x === it && willOpen ? "1" : "0"); });
        }
        setTimeout(sync, 700);
      });
      sync();
    });
  }

  // Favicon com o símbolo da marca.
  function favicon() {
    $$("link[rel~='icon']").forEach(function (l) { l.parentNode.removeChild(l); });
    var link = document.createElement("link");
    link.rel = "icon";
    link.type = "image/svg+xml";
    link.href = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNzQuNjIgMTc0LjYxIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSI1NS44MiIgeTE9IjE2OC43NCIgeDI9IjExOC44IiB5Mj0iNS44NyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIG9mZnNldD0iLjIxIiBzdG9wLWNvbG9yPSIjZjU2MDM1Ii8+PHN0b3Agb2Zmc2V0PSIuOTgiIHN0b3AtY29sb3I9IiNmZmFiNjYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNmZmMxOGYiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cGF0aCBkPSJNODcuMzEsMEMzOS4xNywwLDAsMzkuMTcsMCw4Ny4zMXMzOS4xNyw4Ny4zLDg3LjMxLDg3LjMsODcuMzEtMzkuMTYsODcuMzEtODcuM1MxMzUuNDUsMCw4Ny4zMSwwWiIgZmlsbD0idXJsKCNnKSIvPjxwYXRoIGQ9Ik0xMzYuMjksMTA2LjIxYy0uMTMuMTItLjI4LjIyLS40Mi4zMS0yLjk4LDEuOTctNS45MSw0LjAyLTkuMDcsNS43Mi02LjUsMy40OS0xMy4zMSw2LjE0LTIwLjU4LDcuNy00LjY0Ljk5LTkuMzEsMS40Mi0xMy4xOCwxLjUyLTQuNzctLjAzLTguNjUtLjM0LTEyLjQ4LTEuMDQtNi41OC0xLjIxLTEyLjkzLTMuMTMtMTguODgtNi4yMS02Ljg5LTMuNTctMTIuNy04LjM1LTE3LjEzLTE0LjY2LTMuMTctNC41My01LjUtOS40LTYuNTEtMTQuODMtLjQyLTIuMjgtLjUxLTQuNTgtLjQ3LTYuODkuMDItMS4zOC4xNi0yLjc2LjI4LTQuMTQuMDUtLjQ1LjE0LS45Mi4zMy0xLjM0LjYxLTEuNCwyLjMyLTEuNjIsMy4zLS40Mi4yNS4zMS40My42OC42MSwxLjA1LDEuNTMsMy4xMiwzLjMyLDYuMSw1LjUxLDguODQsMy42Nyw0LjYyLDguMTIsOC4zMywxMy40OCwxMC45Nyw3LjQxLDMuNjUsMTUuMjksNS4zMywyMy41Niw1LjM2LDQuOTcuMDEsOS43Mi0xLjA5LDE0LjMxLTIuODcsNS44Ni0yLjI4LDExLjE2LTUuNDgsMTUuOTctOS40Ni40OS0uNDEuOTgtLjg0LDEuNTItMS4xOCwxLjY3LTEuMDYsMy4zOS0uOTEsNC44NS40My4zOS4zNS43My43NiwxLjA2LDEuMTYsNC40Nyw1LjM3LDguOTMsMTAuNzMsMTMuNCwxNi4xLjI5LjM2LjYuNzEuODYsMS4xLjcsMS4wMi41OCwxLjk2LS4zMiwyLjc4WiIgZmlsbD0iI2ZmZjJlOSIvPjxwYXRoIGQ9Ik0xMDgsNzJjLS4yOC41Ni0uNjUsMS4xLTEuMTEsMS41My0xLjM1LDEuMjktMi43NSwyLjUyLTQuMTYsMy43NS0zLjk5LDMuNTEtNy45OSw3LTExLjk3LDEwLjUyLS45Ny44NS0yLjA0LDEuMzYtMy40MSwxLjM0LTEuMTkuMDMtMi4yMi0uNDYtMy4xNi0xLjIzLTIuMTEtMS43NS00LjI1LTMuNDgtNi4zNi01LjIzLTMuMjktMi43Mi02LjU2LTUuNDUtOS44NC04LjE4LS40LS4zMy0uODEtLjY4LTEuMTUtMS4wNy0uNjQtLjcyLS42NC0xLjYxLS4wMS0yLjM1LjI5LS4zNi42NC0uNjguOTktLjk5LDUuNzctNS4xOSwxMS41NS0xMC4zNywxNy4zMy0xNS41Ni4zLS4yNy42MS0uNTQuOTMtLjc5LDEuMDQtLjc4LDEuOC0uNzcsMi44OSwwLC4yNC4xNy40Ni4zNy42OC41NSw1LjY3LDQuNzksMTEuMzQsOS41NywxNywxNC4zNi4yNy4yMy41NC40NS44LjY4Ljg3Ljc2LDEuMDMsMS42OS41NSwyLjY3WiIgZmlsbD0iI2ZmZjJlOSIvPjwvc3ZnPg==";
    document.head.appendChild(link);
  }

  function revealLines(scope) {
    $$(".ov-reveal h2, .ov-reveal h3, .ov-h2 h2", scope).forEach(function (el) {
      SplitText.create(el, {
        type: "lines",
        mask: "lines",
        autoSplit: true,
        onSplit: function (self) {
          return gsap.from(self.lines, { yPercent: 110, duration: 1.3, stagger: 0.1, ease: "expo.out", scrollTrigger: { trigger: el, start: "top 88%" } });
        },
      });
    });
    [".ov-stagger ul", ".ov-values-grid", ".ov-faq-acc [data-grab='accordion-container']"].forEach(function (sel) {
      $$(sel, scope).forEach(function (list) {
        gsap.from(list.children, { y: 28, autoAlpha: 0, duration: 1, stagger: 0.07, ease: "expo.out", scrollTrigger: { trigger: list, start: "top 88%" } });
      });
    });
  }

  function hero(mm) {
    var root = $(".ov-hero");
    if (!root) return;
    var media = $(".ov-hero-media", root);
    var img = $("img", media);
    // Entrada e scroll animam elementos diferentes: se dividirem o mesmo alvo, o scroll grava
    // o estado inicial da entrada (imagem ampliada, textos invisíveis) e volta para ele.
    var imgWrap = $(".imageWidget", media) || img;
    var lead = $(".ov-hero-lead", root), ctas = $(".ov-hero-ctas", root);

    mm.add({ desktop: "(min-width: 768px)", mobile: "(max-width: 767px)" }, function (ctx) {
      var desktop = ctx.conditions.desktop;
      var arch = getComputedStyle(root).getPropertyValue("--arch").trim();
      var title = SplitText.create($(".ov-hero-title h1", root), { type: "lines", mask: "lines" });
      gsap.set([$(".ov-hero-title", root), $(".ov-hero-lead", root), $(".ov-hero-ctas", root)], { visibility: "visible" });

      // Entrada: a imagem nasce dentro do arco, o título sobe da máscara.
      gsap.timeline({ defaults: { ease: "expo.out" } })
        .from(img, { yPercent: 100, duration: 1.8, ease: "expo.inOut" })
        .from(img, { scale: 1.5, duration: 2.4 }, "<0.2")
        .from(title.lines, { yPercent: 105, duration: 1.4, stagger: 0.12 }, "-=1.9")
        .from([$(".dmNewParagraph", lead)].concat(Array.prototype.slice.call(ctas.children)), { y: 24, autoAlpha: 0, duration: 1, stagger: 0.08 }, "-=1");

      // Scroll: o arco abre, o título sai, o manifesto acende palavra por palavra.
      var words = SplitText.create($(".ov-manifesto-text h2", root), { type: "words" });
      gsap.set(words.words, { opacity: 0.14 });
      var stats = $$(".ov-stat p:first-child span", root);

      var tl = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: { trigger: root, start: "top top", end: desktop ? "+=260%" : "+=220%", scrub: 1, pin: true, anticipatePin: 1 },
      });
      tl.fromTo(media, { clipPath: arch }, { clipPath: "inset(0svh 0vw 0svh 0vw round 0vw 0vw 0vw 0vw)", duration: 1, ease: "power2.inOut" })
        .fromTo(imgWrap, { scale: 1 }, { scale: 1.08, duration: 1, ease: "power2.inOut" }, 0)
        .fromTo($(".ov-hero-title", root), { yPercent: 0, autoAlpha: 1 }, { yPercent: -40, autoAlpha: 0, duration: 0.6 }, 0)
        .fromTo([lead, ctas], { y: 0, autoAlpha: 1 }, { y: -60, autoAlpha: 0, duration: 0.4 }, 0)
        .fromTo(root, { "--veil": 0 }, { "--veil": 1, duration: 0.6 }, 0.55)
        .fromTo($(".ov-manifesto", root), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 0.9)
        .to(words.words, { opacity: 1, duration: 0.2, stagger: 0.06 }, 1)
        .addLabel("foot")
        .from($$(".ov-manifesto-foot > *", root), { y: 40, autoAlpha: 0, duration: 0.35, stagger: 0.1 }, "foot");

      stats.forEach(function (el) {
        var m = el.textContent.match(/(\d+)(.*)/);
        if (!m) return;
        var target = +m[1], suffix = m[2], obj = { v: 0 };
        tl.to(obj, { v: target, duration: 0.5, onUpdate: function () { el.textContent = Math.round(obj.v) + suffix; } }, "foot");
      });
      tl.to({}, { duration: 0.4 });

      return function () { title.revert(); words.revert(); };
    });
  }

  function services(mm) {
    var root = $(".ov-services");
    if (!root) return;
    mm.add("(min-width: 1024px)", function () {
      var frame = $(".ov-svc-frame", root);
      var frames = $$(".ov-svc-img", frame);
      var blocks = $$(".ov-svc-block", root);
      // Quadro fixo enquanto a lista passa.
      ScrollTrigger.create({ trigger: frame, start: "top 12%", endTrigger: $(".ov-svc-list", root), end: "bottom 88%", pin: true, pinSpacing: false });
      // Cada serviço faz a próxima imagem nascer de baixo para cima.
      frames.forEach(function (f, i) {
        if (!i) return;
        gsap.timeline({ defaults: { ease: "none" }, scrollTrigger: { trigger: blocks[i], start: "top 95%", end: "top 35%", scrub: true } })
          .fromTo(f, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)" })
          .fromTo($("img", f), { scale: 1.35 }, { scale: 1 }, 0)
          .fromTo($("img", frames[i - 1]), { scale: 1, yPercent: 0 }, { scale: 0.92, yPercent: -6 }, 0);
      });
    });
  }

  function projects(mm) {
    var root = $(".ov-projects");
    if (!root) return;
    // Desktop: a seção trava e a trilha inteira (introdução, projetos, fechamento) passa na horizontal.
    mm.add("(min-width: 1024px)", function () {
      var track = $(".ov-proj-track", root);
      if (!track) return;
      var dist = function () { return Math.max(0, track.scrollWidth - innerWidth); };
      gsap.to(track, {
        x: function () { return -dist(); },
        ease: "none",
        scrollTrigger: { trigger: root, start: "top top", end: function () { return "+=" + dist(); }, scrub: 1, pin: true, anticipatePin: 1, invalidateOnRefresh: true },
      });
      whenPresent(".ov-proj-gallery .photogallery-column", function () {
        eagerGalleries();
        // Sem entradas animadas dentro da trilha: no site publicado a Duda redesenha a galeria
        // depois do carregamento e os gatilhos ficariam presos a elementos que já não existem.
        ScrollTrigger.refresh();
      });
    });
  }

  // Legenda de cada projeto entra quando ele chega na tela. Lê a posição a cada rolagem e guarda os
  // índices vistos na raiz da galeria: a Duda pode redesenhar os itens, a classe é reaplicada.
  function projectCaptions() {
    var root = $(".ov-proj-gallery");
    if (!root || root.__ovCaptions) return;
    root.__ovCaptions = true;
    var seen = {}, ticking = false;
    function check() {
      ticking = false;
      $$(".photoGalleryThumbs", root).forEach(function (t, i) {
        var r = t.getBoundingClientRect();
        if (!seen[i] && r.left < innerWidth * 0.75 && r.top < innerHeight * 0.85 && r.bottom > 0) seen[i] = true;
        t.classList.toggle("is-in", !!seen[i]);
      });
    }
    addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(check); } }, { passive: true });
    new MutationObserver(function () { if (!ticking) { ticking = true; requestAnimationFrame(check); } }).observe(root, { childList: true, subtree: true });
    check();
  }

  function values() {
    var mark = $(".ov-values-mark");
    if (!mark) return;
    gsap.fromTo(mark, { rotation: -40 }, { rotation: 40, ease: "none", scrollTrigger: { trigger: ".ov-values", start: "top bottom", end: "bottom top", scrub: true } });
  }

  function segments(mm) {
    if (!$(".ov-seg-gallery")) return;
    whenPresent(".ov-seg-gallery .photoGalleryThumbs", function () { segmentsList(mm, $(".ov-seg-gallery")); });
  }

  function segmentsList(mm, root) {
    eagerGalleries();
    // Portal com a foto do segmento que acompanha o cursor. Os eventos ficam na galeria e as linhas
    // são lidas a cada hover: no site publicado a Duda redesenha a galeria depois de carregar.
    mm.add("(hover: hover) and (min-width: 1024px)", function () {
      var cursor = document.createElement("div");
      cursor.className = "ov-seg-cursor";
      cursor.setAttribute("aria-hidden", "true");
      var photo = document.createElement("img");
      photo.alt = "";
      cursor.appendChild(photo);
      root.appendChild(cursor);
      gsap.set(cursor, { xPercent: -50, yPercent: -50, scale: 0, autoAlpha: 0 });
      var xTo = gsap.quickTo(cursor, "x", { duration: 0.7, ease: "power3" });
      var yTo = gsap.quickTo(cursor, "y", { duration: 0.7, ease: "power3" });
      var rTo = gsap.quickTo(cursor, "rotation", { duration: 0.9, ease: "power3" });
      var lastX = 0, currentRow = null;

      function srcOf(row) {
        var img = $("img", row);
        if (img) return img.getAttribute("src") || img.getAttribute("data-src") || "";
        var a = $(".image-container a", row);
        var m = a && a.style.backgroundImage.match(/url\(["']?(.*?)["']?\)/);
        return m ? m[1] : "";
      }
      function move(e) {
        var r = root.getBoundingClientRect(), x = e.clientX - r.left;
        xTo(x); yTo(e.clientY - r.top); rTo(gsap.utils.clamp(-12, 12, (x - lastX) * 0.6)); lastX = x;
        var row = e.target.closest && e.target.closest(".photoGalleryThumbs");
        if (!row || row === currentRow) return;
        currentRow = row;
        photo.src = srcOf(row);
        gsap.fromTo(photo, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.7, ease: "expo.out", overwrite: true });
        gsap.to(cursor, { scale: 1, autoAlpha: 1, duration: 0.6, ease: "expo.out" });
      }
      function hide() {
        currentRow = null;
        gsap.to(cursor, { scale: 0, autoAlpha: 0, duration: 0.5, ease: "power3.in" });
      }
      root.addEventListener("pointermove", move);
      root.addEventListener("pointerleave", hide);
      return function () {
        root.removeEventListener("pointermove", move);
        root.removeEventListener("pointerleave", hide);
        cursor.remove();
      };
    });
  }

  function faq(mm) {
    var root = $(".ov-faq");
    if (!root) return;
    mm.add("(min-width: 1024px)", function () {
      var aside = $(".ov-faq-aside", root);
      ScrollTrigger.create({
        trigger: aside, start: "top 128px", endTrigger: $(".ov-faq-list", root),
        end: function () { return "bottom " + (128 + aside.offsetHeight) + "px"; },
        pin: true, pinSpacing: false, invalidateOnRefresh: true,
      });
    });
    // O acordeão muda de altura: recalcula os gatilhos seguintes.
    root.addEventListener("click", function () { setTimeout(function () { ScrollTrigger.refresh(); }, 650); });
  }

  function sunrise() {
    var root = $(".ov-sunrise");
    if (!root) return;
    var title = SplitText.create($(".ov-sunrise-title h2", root), { type: "words", mask: "words" });
    gsap.from(title.words, { yPercent: 110, duration: 1.2, stagger: 0.05, ease: "expo.out", scrollTrigger: { trigger: root, start: "top 55%" } });
    gsap.timeline({
      defaults: { ease: "none" },
      scrollTrigger: { trigger: root, start: "top top", end: "+=160%", scrub: 1, pin: true, anticipatePin: 1 },
    })
      .fromTo(root, { "--dawn": 0.2 }, { "--dawn": 1, duration: 1 })
      .fromTo(root, { "--sun": 0 }, { "--sun": 1, duration: 1.2, ease: "power1.out" }, 0)
      .fromTo(root, { "--glow": 0 }, { "--glow": 1, duration: 1.2 }, 0)
      .fromTo(root, { "--line": 0 }, { "--line": 1, duration: 0.6 }, 0)
      .fromTo(root, { "--ground": 0 }, { "--ground": 1, duration: 0.9, ease: "power2.inOut" }, 0.15)
      .from($$(".ov-sunrise-cta > *", root), { y: 40, autoAlpha: 0, duration: 0.3, stagger: 0.08 }, 0.9)
      .to({}, { duration: 0.3 });
  }

  // ================= páginas internas =================

  function splitReveal(el, delay) {
    if (!el) return;
    var split = SplitText.create(el, { type: "lines", mask: "lines" });
    gsap.from(split.lines, { yPercent: 110, duration: 1.4, stagger: 0.1, ease: "expo.out", delay: delay || 0.2 });
  }

  function pageHero(mm) {
    var root = $(".ov-phero");
    if (!root) return;
    var media = $(".ov-phero-media", root);
    gsap.set([$(".ov-phero-title", root), $(".ov-phero-sub", root)], { visibility: "visible" });
    mm.add({ desktop: "(min-width: 768px)", mobile: "(max-width: 767px)" }, function (ctx) {
      var arch = ctx.conditions.desktop ? "inset(18svh 34vw 0svh 34vw round 16vw 16vw 0vw 0vw)" : "inset(30svh 14vw 0svh 14vw round 36vw 36vw 0vw 0vw)";
      // A página dinâmica usa o fundo da própria seção: o arco abre sobre ela.
      var target = media || $(":scope > section", root);
      gsap.timeline({ defaults: { ease: "expo.inOut" } })
        .fromTo(target, { clipPath: arch }, { clipPath: "inset(0svh 0vw 0svh 0vw round 0vw 0vw 0vw 0vw)", duration: 2 })
        .from($(".ov-phero-title", root), { yPercent: 30, autoAlpha: 0, duration: 1.3, ease: "expo.out" }, 1.1)
        .from($(".ov-phero-sub", root), { y: 24, autoAlpha: 0, duration: 1, ease: "expo.out" }, 1.5);
      if (media) {
        gsap.to($("img", media), { yPercent: 12, ease: "none", scrollTrigger: { trigger: root, start: "top top", end: "bottom top", scrub: true } });
      }
      gsap.fromTo([$(".ov-phero-title", root), $(".ov-phero-sub", root)], { yPercent: 0, autoAlpha: 1 }, {
        yPercent: -30, autoAlpha: 0, ease: "none", immediateRender: false,
        scrollTrigger: { trigger: root, start: "top top", end: "70% top", scrub: true },
      });
    });
  }

  function statementHero() {
    var root = $(".ov-statement");
    if (!root) return;
    gsap.set([$(".ov-st-title", root), $(".ov-st-lead", root)], { visibility: "visible" });
    splitReveal($(".ov-st-title h1", root), 0.2);
    gsap.from([$(".ov-st-lead", root), $(".ov-hub-index", root), $(".ov-filter", root)].filter(Boolean), { y: 24, autoAlpha: 0, duration: 1, stagger: 0.08, ease: "expo.out", delay: 0.8 });
  }

  function arches() {
    $$(".ov-intro-arch, .ov-story-arch, .ov-contact-arch").forEach(function (el) {
      gsap.fromTo(el, { clipPath: "inset(100% 0% 0% 0% round 999px 999px 0px 0px)" }, {
        clipPath: "inset(0% 0% 0% 0% round 999px 999px 0px 0px)", duration: 1.8, ease: "expo.inOut",
        scrollTrigger: { trigger: el, start: "top 80%" },
      });
      gsap.fromTo($("img", el), { scale: 1.12 }, { scale: 1, ease: "none", scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: true } });
    });
  }

  function details() {
    $$(".ov-detail-row").forEach(function (row) {
      gsap.from($$(".ov-detail-text, .ov-tags", row), { y: 28, autoAlpha: 0, duration: 1, stagger: 0.07, ease: "expo.out", scrollTrigger: { trigger: row, start: "top 80%" } });
      var frame = $(".ov-detail-media", row);
      if (frame) {
        gsap.timeline({ defaults: { ease: "none" }, scrollTrigger: { trigger: row, start: "top 90%", end: "top 30%", scrub: true } })
          .fromTo(frame, { clipPath: "inset(100% 0% 0% 0% round 28px)" }, { clipPath: "inset(0% 0% 0% 0% round 28px)" })
          .fromTo($("img", frame), { scale: 1.3 }, { scale: 1 }, 0);
      }
    });
  }

  function processLight(mm) {
    var list = $(".ov-process-list");
    if (!list) return;
    gsap.fromTo(list, { "--light": 0 }, { "--light": 1, ease: "none", scrollTrigger: { trigger: list, start: "top 60%", end: "bottom 60%", scrub: true } });
    $$(".ov-step", list).forEach(function (step) {
      ScrollTrigger.create({ trigger: step, start: "top 60%", onEnter: function () { step.classList.add("is-lit"); }, onLeaveBack: function () { step.classList.remove("is-lit"); } });
    });
    mm.add("(min-width: 1024px)", function () {
      var aside = $(".ov-process-aside");
      ScrollTrigger.create({ trigger: aside, start: "top 128px", endTrigger: list, end: function () { return "bottom " + (128 + aside.offsetHeight) + "px"; }, pin: true, pinSpacing: false, invalidateOnRefresh: true });
    });
  }

  function features() {
    var grid = $(".ov-feature-grid");
    if (!grid) return;
    gsap.from($$(".ov-feature", grid), { y: 60, autoAlpha: 0, duration: 1.2, stagger: 0.1, ease: "expo.out", scrollTrigger: { trigger: grid, start: "top 80%" } });
  }

  function stackCards(mm) {
    var cards = $$(".ov-stack-card");
    if (cards.length < 2) return;
    mm.add("(min-width: 1024px)", function () {
      cards.forEach(function (card, i) {
        card.style.zIndex = i + 1;
        if (i === cards.length - 1) return;
        // Só o conteúdo encolhe e apaga: o fundo do cartão continua cobrindo a tela inteira,
        // senão o cartão anterior aparece pelas bordas.
        gsap.to($(":scope > section > .grid > .group", card), { scale: 0.9, autoAlpha: 0.35, transformOrigin: "50% 0%", ease: "none", scrollTrigger: { trigger: cards[i + 1], start: "top bottom", end: "top top", scrub: true } });
        ScrollTrigger.create({ trigger: card, start: "top top", endTrigger: cards[i + 1], end: "top top", pin: true, pinSpacing: false });
      });
    });
  }

  function portfolioFilter() {
    var bar = $(".ov-filter");
    if (!bar) return;
    var current = "todos";
    var norm = function (t) { return (t || "").trim().toLowerCase(); };
    function apply() {
      $$(".ov-portfolio-gallery .photoGalleryThumbs").forEach(function (item) {
        var cat = norm(($(".caption-button .text", item) || {}).textContent);
        item.classList.toggle("is-hidden", current !== "todos" && cat !== current);
      });
      $$("a", bar).forEach(function (a) { a.classList.toggle("is-active", norm(a.textContent) === current); });
      ScrollTrigger.refresh();
    }
    bar.addEventListener("click", function (e) {
      var a = e.target.closest("a");
      if (!a) return;
      e.preventDefault();
      e.stopPropagation();
      current = norm(a.textContent);
      apply();
      // Os projetos que ficam entram de novo, já nas posições reorganizadas.
      if (!reduce) {
        var shown = $$(".ov-portfolio-gallery .photogallery-column").filter(function (c) { return !$(".is-hidden", c); });
        gsap.fromTo(shown, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.9, stagger: 0.08, ease: "expo.out", overwrite: true, clearProps: "transform,opacity,visibility" });
      }
    }, true);
    apply();
    // A Duda pode redesenhar a galeria: reaplica o filtro quando os itens mudam.
    new MutationObserver(function () { apply(); }).observe($(".ov-portfolio-gallery") || document.body, { childList: true, subtree: true });
  }

  function faqBound() {
    var box = $(".ov-faq-bound .dmNewParagraph") || $(".ov-faq-bound");
    if (!box || $(".ov-qa", box)) return;
    var heads = $$("h3", box);
    if (!heads.length) return;
    heads.forEach(function (h3, i) {
      var answer = h3.nextElementSibling;
      var item = document.createElement("div");
      item.className = "ov-qa" + (i === 0 ? " is-open" : "");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "ov-qa-q";
      btn.id = "ov-qa-q" + i;
      btn.setAttribute("aria-expanded", String(i === 0));
      btn.setAttribute("aria-controls", "ov-qa-a" + i);
      btn.textContent = h3.textContent;
      var panel = document.createElement("div");
      panel.className = "ov-qa-a";
      panel.id = "ov-qa-a" + i;
      panel.setAttribute("role", "region");
      panel.setAttribute("aria-labelledby", btn.id);
      var inner = document.createElement("div");
      if (answer && answer.tagName === "P") inner.appendChild(answer);
      panel.appendChild(inner);
      var heading = document.createElement("h3");
      heading.style.margin = "0";
      heading.appendChild(btn);
      item.appendChild(heading);
      item.appendChild(panel);
      h3.replaceWith(item);
      btn.addEventListener("click", function () {
        var open = !item.classList.contains("is-open");
        $$(".ov-qa", box).forEach(function (o) { o.classList.remove("is-open"); $(".ov-qa-q", o).setAttribute("aria-expanded", "false"); });
        item.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", String(open));
        setTimeout(function () { ScrollTrigger.refresh(); }, 650);
      });
    });
  }

  function storyWords() {
    var el = $(".ov-story-statement h3");
    if (!el) return;
    var words = SplitText.create(el, { type: "words" });
    gsap.fromTo(words.words, { opacity: 0.15 }, { opacity: 1, stagger: 0.1, ease: "none", scrollTrigger: { trigger: el, start: "top 80%", end: "bottom 45%", scrub: true } });
    $$(".ov-pillar").forEach(function (pl) {
      gsap.from(pl, { y: 36, autoAlpha: 0, duration: 1.1, ease: "expo.out", scrollTrigger: { trigger: pl, start: "top 82%" } });
    });
  }

  function anchors() {
    // Rolagem suave para as âncoras desta página (links da navegação e botões).
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href*='#']");
      if (!a) return;
      var id = a.getAttribute("href").split("#")[1];
      var target = id && document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
    });
  }

  function eagerGalleries() {
    // As galerias carregam imagens sob demanda; na trilha horizontal isso falha, então carrega tudo.
    $$(".ov-proj-gallery img[data-src], .ov-seg-gallery img[data-src], .ov-portfolio-gallery img[data-src]").forEach(function (img) {
      if (!img.getAttribute("src")) img.setAttribute("src", img.getAttribute("data-src"));
    });
  }

  function init() {
    eagerGalleries();
    header();
    anchors();
    favicon();
    faqIcons();
    if (reduce || !window.gsap || !window.ScrollTrigger || !window.SplitText) {
      document.documentElement.classList.remove("ov-anim");
      return;
    }
    window.__ovready = true;
    gsap.registerPlugin(ScrollTrigger, SplitText);
    headerIntro();
    ScrollTrigger.config({ ignoreMobileResize: true });

    function start() {
      var mm = gsap.matchMedia();
      hero(mm);
      pageHero(mm);
      statementHero();
      arches();
      details();
      processLight(mm);
      features();
      stackCards(mm);
      portfolioFilter();
      whenPresent(".ov-portfolio-gallery .photoGalleryThumbs", eagerGalleries);
      whenPresent(".ov-faq-bound h3", faqBound);
      storyWords();
      services(mm);
      projects(mm);
      whenPresent(".ov-proj-gallery .photoGalleryThumbs", projectCaptions);
      revealLines(document);
      segments(mm);
      values();
      faq(mm);
      sunrise();
      // Galerias e imagens chegam depois e mudam a altura da página: recalcula os gatilhos.
      addEventListener("load", function () { ScrollTrigger.refresh(); });
      var lastH = 0, pending;
      new ResizeObserver(function () {
        var h = document.body.scrollHeight;
        if (Math.abs(h - lastH) < 2) return;
        lastH = h;
        clearTimeout(pending);
        pending = setTimeout(function () { ScrollTrigger.refresh(); }, 200);
      }).observe($("#dm_content") || document.body);
    }
    // SplitText mede as linhas: espera as fontes (com limite de tempo).
    var fonts = document.fonts ? document.fonts.ready : Promise.resolve();
    Promise.race([fonts, new Promise(function (r) { setTimeout(r, 1500); })]).then(start);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
