"""Seções reutilizáveis (espelham os componentes do Next). Tipografia pelo tema: h1–h4 Fraunces, p Hanken."""
import json

import lib
from lib import (AMBAR, AURORA, AURORA_75, AURORA_85, CLEAR, DISPLAY, INDIGO, INDIGO_70, INDIGO_PROFUNDO, LAVANDA, NOITE,
                 accordion, bound_para, bullets, button, column, gallery, icon, image, inner, lead, p, para, rte, section)

WHATSAPP = "https://wa.me/5500000000000?text=Ol%C3%A1!%20Vim%20pelo%20site%20da%20Agência Exemplo%20e%20quero%20come%C3%A7ar%20um%20projeto."
INSTAGRAM = "https://instagram.com/agencia.exemplo"
ICONS = json.loads((lib.REPO / "duda/home-v2/icons.json").read_text())


def C():
    return lib.content()


def h(tag, text, **kw):
    return rte(tag, text, **kw)


def stat(value, label):
    return rte("p", value, 86, 70, 56, lh=1, color=AMBAR, font=DISPLAY, ls="-0.035em") + p(label, size=16, color="rgba(255, 242, 233, 0.7)")


def heading(text, tag="h2", cls="ov-h2 ov-reveal", max_width="900px"):
    return para(cls, h(tag, text), max_width=max_width)


def sub(text, margin_top=28, max_width="560px"):
    return para("ov-lead", lead(text), max_width=max_width, margin_top=margin_top)


# ---------- home ----------

def home_hero():
    return section("ov-hero", [
        column([
            image("ov-hero-media", lib.img("/images/cristais.webp"), "Pessoa caminhando entre cristais luminosos refletidos na água"),
            para("ov-hero-title", h("h1", "Presença digital.<br>Branding visionário.")),
            para("ov-hero-lead", lead("Marketing com propósito para terapeutas, artistas e negócios que vivem de uma missão.", color=AURORA_85), max_width="420px"),
            inner("ov-hero-ctas", [button("primary", "Começar projeto", WHATSAPP, new_tab=True), button("link", "Ver serviços ↘", "#servicos")],
                  direction="row", gap="20px", align="center"),
            inner("ov-manifesto", [
                para("ov-manifesto-text", h("h2", "Você não precisa virar especialista em marketing para crescer."), max_width="1000px"),
                inner("ov-manifesto-foot", [
                    para("ov-manifesto-lead", lead("Cuidamos da estratégia, do branding e da tecnologia. Você fica com o tempo livre para o que importa: manifestar sua missão.", color=AURORA_85), width="420px"),
                    para("ov-stat", stat("180+", "projetos entregues"), width="auto"),
                    para("ov-stat", stat("12+", "anos de experiência"), width="auto"),
                ], direction="row", gap="64px", align="flex-end", justify="space-between", wrap="wrap", width="100%"),
            ], gap="56px", justify="center"),
        ], cls="ov-hero-col"),
    ], pad_y=(0, 0))


def home_services():
    services = C()["content"]["services"]
    blocks = []
    for s in services:
        src = lib.img(s["image"])
        blocks.append(inner("ov-svc-block", [
            image("ov-svc-mimg", src, s["alt"], radius="24px"),
            icon("ov-svc-icon", ICONS[s["id"]]),
            para("ov-svc-title ov-reveal", h("h3", s["title"]), margin_top=32),
            para("ov-svc-lead", p(s["lead"], color=AURORA_75), max_width="520px", margin_top=24),
            para("ov-svc-items", bullets(s["items"]), max_width="520px", margin_top=40),
        ], justify="center", min_height="76vh"))
    return section("ov-services", [
        column([
            heading("Comunique sua essência e atraia os clientes certos."),
            sub("Estratégia, design e tecnologia trabalhando juntos para que sua marca seja encontrada, entendida e escolhida."),
            inner("ov-svc-grid", [
                inner("ov-svc-frame", [image("ov-svc-img", lib.img(s["image"]), s["alt"]) for s in services],
                      border={"radius": "32px", "width": "0px", "color": CLEAR}, background={"color": INDIGO}),
                inner("ov-svc-list", blocks),
            ], direction="row", gap="80px", margin_top="96px", width="100%"),
        ]),
    ], anchor="servicos")


PROJECT_ITEM = {
    "src": {"source": "COLLECTION_ITEM", "field": "Imagem"},
    "alt": {"source": "COLLECTION_ITEM", "field": "Nome"},
    "title": {"title": {"source": "COLLECTION_ITEM", "field": "Nome"}},
    "description": {"description": {"source": "COLLECTION_ITEM", "field": "Resumo"}},
    "button": {"text": {"source": "COLLECTION_ITEM", "field": "Area"}, "link": {"source": "COLLECTION_ITEM", "field": "Link"}},
}


def home_projects():
    return section("ov-projects", [
        column([
            inner("ov-proj-track", [
                inner("ov-proj-intro", [heading("Trabalhos selecionados."),
                                        sub("Marcas que já saíram da dependência das redes e ganharam uma casa digital à altura do que entregam.")]),
                gallery("ov-proj-gallery", "projetos", PROJECT_ITEM, full_image=True, columns=4,
                        query={"filters": [{"field": "Destaque", "operator": "GREATER_OR_EQUAL", "values": ["1"]}]}),
                inner("ov-proj-end", [
                    para("ov-proj-end-title", h("h3", "Seu projeto pode ser o próximo.")),
                    button("primary", "Conversar sobre meu projeto", WHATSAPP, new_tab=True),
                    button("link", "Ver todos os projetos ↘", "/projetos"),
                ], gap="20px"),
            ], direction="row"),
        ]),
    ], bg=INDIGO, pad_y=(0, 0), anchor="projetos")


def segments_gallery(cls="ov-seg-gallery", details=False):
    """`details`: página Segmentos — frase da chamada (cta_titulo) ao lado do nome e seta à direita."""
    uuid = json.loads((lib.ROOT / "pages.json").read_text())["segmento"]
    item = {
        "src": {"source": "COLLECTION_ITEM", "field": "imagem"},
        "alt": {"source": "COLLECTION_ITEM", "field": "segmento"},
        "title": {"title": {"source": "COLLECTION_ITEM", "field": "segmento"}},
        "button": {"link": {"source": "COLLECTION_ITEM", "field": f"dpfield#_{uuid}"}},
    }
    if details:
        item["description"] = {"description": {"source": "COLLECTION_ITEM", "field": "cta_titulo"}}
        cls += " ov-seg-gallery--details"
    return gallery(cls, "Segmentos", item, columns=1, title_color=AURORA_85, desc_color=LAVANDA)


def home_segments():
    return section("ov-segments", [
        column([
            inner("ov-seg-head", [
                heading("Feito para quem trabalha com propósito.", max_width="820px"),
                para("ov-lead", lead("Conhecemos a linguagem, o público e o ritmo de quem cuida, cria e conduz. Seu marketing fala como você."), width="384px"),
            ], direction="row", justify="space-between", align="flex-end", gap="48px", wrap="wrap", width="100%"),
            segments_gallery(),
        ]),
    ], anchor="segmentos")


def values(title="Construindo marcas com propósito verdadeiro."):
    return section("ov-values", [
        column([
            inner("ov-values-head", [
                heading(title, max_width="820px"),
                # Símbolo da marca (recorte quadrado do logotipo): gira devagar com a rolagem.
                image("ov-values-mark", lib.img("logo-indigo"), "", fit="cover", width="112px", height="112px"),
            ], direction="row", justify="space-between", align="flex-start", gap="40px", width="100%"),
            inner("ov-values-grid", [para("ov-value", h("h4", v["name"]) + p(v["text"], color=LAVANDA), width="30%") for v in C()["content"]["values"]],
                  direction="row", wrap="wrap", gap="56px", margin_top="96px", width="100%"),
        ]),
    ], bg=INDIGO, anchor="valores")


def faq(items=None, title="Todos os detalhes, explicados."):
    items = items or [(f["q"], f["a"]) for f in C()["content"]["faq"]]
    return section("ov-faq", [
        column([heading(title, max_width="560px"), sub("Não encontrou sua dúvida? A gente responde pessoalmente."),
                button("secondary", "Fazer uma pergunta", WHATSAPP, new_tab=True)], cls="ov-faq-aside", gap="28px", width="40%"),
        column([accordion("ov-faq-acc", items)], cls="ov-faq-list", width="54%"),
    ], direction="row", gap="6%", anchor="duvidas")


def sunrise(title="Tem uma visão? Vamos torná-la realidade.", text=None, bound=False):
    title_el = (bound_para("ov-sunrise-title", "cta_titulo", tag="h2", max_width="1000px") if bound
                else para("ov-sunrise-title", h("h2", title, align="center"), max_width="1000px"))
    cta = [button("indigo", "Conversar no WhatsApp", WHATSAPP, new_tab=True),
           para("ov-sunrise-note", p(f'ou mande um direct no <a href="{INSTAGRAM}" target="_blank" type="url" style="color: {INDIGO};">Instagram</a>', size=16, color=INDIGO_70, align="center"))]
    if bound:
        cta.insert(0, bound_para("ov-sunrise-text", "cta_texto", max_width="620px"))
    elif text:
        cta.insert(0, para("ov-sunrise-text", p(text, color=INDIGO, align="center"), max_width="620px"))
    return section("ov-sunrise", [column([title_el, inner("ov-sunrise-cta", cta, gap="20px", align="center")], cls="ov-sunrise-col", align="center")],
                   pad_y=(0, 0), anchor="contato")


# ---------- páginas internas ----------

def page_hero(title, text, img_key, alt, next_href=None, next_label=None):
    ctas = [button("primary", "Começar projeto", WHATSAPP, new_tab=True)]
    if next_href:
        ctas.append(button("link", f"{next_label} ↘", next_href))
    return section("ov-phero", [
        column([
            image("ov-phero-media", lib.img(img_key), alt),
            para("ov-phero-title", h("h1", title), max_width="1100px"),
            inner("ov-phero-sub", [para("ov-phero-lead", lead(text, color=AURORA_85), max_width="460px"),
                                   inner("ov-phero-ctas", ctas, direction="row", gap="20px", align="center")],
                  direction="row", justify="space-between", align="flex-end", wrap="wrap", gap="32px", width="100%", margin_top="32px"),
        ], cls="ov-phero-col"),
    ], pad_y=(0, 0))


def statement(title, text, extra=None, side=False):
    """`side`: o extra (ex.: índice de serviços) fica à direita do texto, alinhado embaixo."""
    children = [para("ov-st-title", h("h1", title), max_width="1100px")]
    if extra and side:
        children.append(inner("ov-st-sub", [para("ov-st-lead", lead(text), width="448px"), extra],
                              direction="row", justify="space-between", align="flex-end", gap="48px", wrap="wrap", width="100%", margin_top="48px"))
    else:
        children.append(para("ov-st-lead", lead(text), max_width="560px", margin_top=48))
        if extra:
            children.append(extra)
    return section("ov-statement", [column(children)], pad_y=(200, 150))


def intro(title, text, img_key, alt, anchor=None, bg=NOITE):
    return section("ov-intro", [
        column([heading(title), para("ov-intro-text", lead(text), max_width="600px", margin_top=40)], width="52%"),
        column([image("ov-intro-arch", lib.img(img_key), alt)], cls="ov-intro-media", width="40%", align="center"),
    ], bg=bg, direction="row", gap="8%", anchor=anchor)


def detail_rows(title, details, bg=INDIGO):
    rows = []
    for i, d in enumerate(details):
        text = "".join(p(t, color=AURORA_85 if k == 0 else LAVANDA) for k, t in enumerate(d["text"]))
        tags = para("ov-tags", "<ul>" + "".join(f"<li><span>{t}</span></li>" for t in d["tags"]) + "</ul>", margin_top=24)
        body = inner("ov-detail-body", [para("ov-detail-title ov-reveal", h("h3", d["title"])), para("ov-detail-text", text, max_width="600px", margin_top=24), tags],
                     width="48%" if d.get("image") else "55%")
        if d.get("image"):
            media = inner("ov-detail-media", [image("ov-detail-img", lib.img(d["image"]), d.get("alt", ""))], width="45%")
            kids = [media, body] if i % 2 == 0 else [body, media]
            rows.append(inner("ov-detail-row ov-detail-row--img", kids, direction="row", justify="space-between", align="center", width="100%", wrap="wrap", gap="48px"))
        else:
            rows.append(inner("ov-detail-row", [para("ov-detail-title ov-reveal", h("h3", d["title"]), width="40%"),
                                                inner("ov-detail-body", [para("ov-detail-text", text), tags], width="55%")],
                              direction="row", justify="space-between", width="100%", wrap="wrap", gap="32px"))
    return section("ov-details", [column([heading(title), inner("ov-detail-list", rows, width="100%", margin_top="80px"),
                                          button("primary", "Vamos conversar", WHATSAPP, new_tab=True)], gap="0px")], bg=bg)


def process(title, steps):
    items = [para("ov-step", rte("p", f"{i + 1:02d}", 52, 44, 38, lh=1, color="rgba(255, 242, 233, 0.4)", font=DISPLAY) + h("h5", s["title"]) + p(s["text"], color=LAVANDA))
             for i, s in enumerate(steps)]
    return section("ov-process", [
        column([heading(title, max_width="560px")], cls="ov-process-aside", width="40%"),
        column([inner("ov-process-list", items, width="100%")], width="54%"),
    ], direction="row", gap="6%")


def features(title, feats):
    cards = [inner("ov-feature", [image("ov-feature-img", lib.img(f["image"]), "", radius="24px"),
                                  para("ov-feature-text", h("h4", f["title"]) + p(f["lead"], color=AURORA) + p(f["text"], color=LAVANDA), margin_top=24)],
                   width="31%") for f in feats]
    return section("ov-features", [column([heading(title), inner("ov-feature-grid", cards, direction="row", wrap="wrap", gap="48px", width="100%", margin_top="80px")])],
                   bg=INDIGO)


def stack(services):
    cards = []
    for i, s in enumerate(services):
        # Botão fantasma (contorno claro; âmbar no hover): página do serviço ou WhatsApp.
        btn = button("secondary", s["cta"], s["href"], cls="ov-stack-btn") if s.get("href") else button("secondary", s["cta"], WHATSAPP, new_tab=True, cls="ov-stack-btn")
        cards.append(section("ov-stack-card", [
            column([heading(s["title"], max_width="640px"), para("ov-stack-lead", p(s["lead"], color=AURORA_85), max_width="520px", margin_top=24),
                    para("ov-svc-items", bullets(s["items"]), max_width="520px", margin_top=32), btn], cls="ov-stack-copy", gap="0px", width="48%"),
            column([image("ov-stack-img", lib.img(s["image"]), s["alt"], radius="28px")], cls="ov-stack-media", width="46%"),
        ], bg=INDIGO if i % 2 else INDIGO_PROFUNDO, direction="row", gap="6%", anchor=s["id"]))
    return cards


def about_story():
    a = C()["about"]["aboutPage"]
    j = a["journey"]
    story = section("ov-story", [
        column([image("ov-story-arch", lib.img(j["image"]), j["alt"])], cls="ov-story-media", width="38%", align="center"),
        column([para("ov-story-label", h("h6", j["title"])), para("ov-story-statement", h("h3", j["statement"]), margin_top=24),
                para("ov-story-text", "".join(p(t, color=LAVANDA) for t in j["text"]), max_width="600px", margin_top=48)], width="54%"),
    ], bg=INDIGO, direction="row", gap="8%")
    pillars = section("ov-pillars", [
        column([para("ov-pillar", h("h6", pl["label"]) + h("h4", pl["title"]) + p(pl["text"], color=LAVANDA))], width="46%")
        for pl in a["pillars"]
    ], direction="row", gap="8%")
    return [story, pillars]
