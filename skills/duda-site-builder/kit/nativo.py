"""Leva para as propriedades nativas dos widgets o que o styles.css forçava com !important
(pedido do cliente, 2026-10-22: tudo que o widget configura tem de ser ajustável no editor).

Cada item grava no widget o valor que aparecia na tela (o do CSS); depois a regra sai do styles.css.
GET antes e PUT com props completos (o PUT preserva o "Edit CSS" que o cliente colocar no editor).

  python3 nativo.py          # simula
  python3 nativo.py --apply  # grava
  python3 nativo.py --audit  # lista regras do styles.css com !important em propriedade que o editor configura

CHANGES abaixo é o exemplo do Projeto H: troque pelos widgets/classes do site. Rode depois de remontar
header ou páginas se o builder ainda gerar valores antigos.
"""
import copy
import json
import sys

import lib
import pages
from fontsizes import walk

APPLY = "--apply" in sys.argv
LT, OS = "LTSuperiorSerif-Regular", "OpenSans-Regular"


def caption(title, desc, sizes, padding="0px", position=None):
    """sizes = {breakpoint: (título, descrição)}"""
    def fn(st):
        cap = st.setdefault("caption", {}) or {}
        st["caption"] = cap
        cap["padding"] = padding
        if position:
            cap["position"] = position
        cap["title"] = dict(cap.get("title") or {}, **title)
        if desc:
            cap["description"] = dict(cap.get("description") or {}, **desc)
        bo = st.get("breakpoint_overrides") or {}
        st["breakpoint_overrides"] = bo
        for bp, (t, d) in sizes.items():
            slot = bo.get(bp) or {}
            bo[bp] = slot
            slot["caption"] = dict(slot.get("caption") or {}, title_text_font_size=t, description_text_font_size=d)
    return fn


def merge(patch):
    def fn(st):
        def deep(a, b):
            for k, v in b.items():
                if isinstance(v, dict) and isinstance(a.get(k), dict):
                    deep(a[k], v)
                else:
                    a[k] = copy.deepcopy(v)
        deep(st, patch)
    return fn


def bp(name, patch):
    return {"breakpoint_overrides": {name: patch}}


# (área, classe do widget, função que altera o style)
CHANGES = [
    # céu da home: a coluna começa abaixo do header (96px) e não tem respiro embaixo (todas as telas)
    ("home", "es-sky", merge({"spacing": {"padding_top": "96px", "padding_bottom": "0px"},
                              "breakpoint_overrides": {"mobile": {"spacing": {"padding_top": "96px", "padding_bottom": "0px"}}}})),
    # aberturas das internas: respiro embaixo para a roda nascer no horizonte
    # (somava o nativo 200/150px com o clamp(160px, 24vw, 320px) do CSS)
    ("*", "es-horizon", merge({"spacing": {"padding_bottom": "520px"},
                               "breakpoint_overrides": {"tablet": {"spacing": {"padding_bottom": "440px"}},
                                                        "mobile": {"spacing": {"padding_bottom": "310px"}}}})),
    # pilares: 2 por linha no tablet, 1 no celular
    ("home", "es-pillar", merge({"breakpoint_overrides": {"tablet": {"size": {"width": "46%"}, "spacing": {"margin_bottom": "56px"}},
                                                          "mobile": {"size": {"width": "100%"}, "spacing": {"margin_bottom": "56px"}}}})),
    # fotos redondas: largura no widget (antes 100% + max-width escondido no CSS)
    ("atendimento", "es-reading-photo", merge({"size": {"width": "520px", "max_width": "100%"}, "border": {"radius": "999px"}})),
    ("sobre", "es-tl-photo", merge({"size": {"width": "420px", "max_width": "100%"}, "border": {"radius": "999px"}})),
    ("home", "es-hello-face", merge({"border": {"radius": "999px", "width": "0px"}, "spacing": {"padding_top": "0px", "padding_right": "0px", "padding_bottom": "0px", "padding_left": "0px"}})),
    # linhas da ficha do atendimento
    ("atendimento", "es-row", merge({"spacing": {"padding_top": "72px", "padding_bottom": "72px", "padding_left": "0px", "padding_right": "0px"},
                                     "breakpoint_overrides": {"mobile": {"spacing": {"padding_top": "48px", "padding_bottom": "48px"}}}})),
    # header: logo de 150px no tablet (o celular já tinha 110px nativo)
    ("header", "es-logo", merge({"spacing": {"margin_top": "0px", "margin_right": "0px", "margin_bottom": "0px", "margin_left": "0px"},
                                 "breakpoint_overrides": {"tablet": {"size": {"width": "150px"}}, "mobile": {"size": {"width": "110px"}}}})),
    # menu do celular: itens de 34px, 14px de respiro, página atual dourada
    ("header", "es-menu-nav", merge({"all_pages": {"link_text": {"font_size": "34px", "color": "var(--color_1)"},
                                                   "link_style": {"spacing": {"padding_top": "14px", "padding_bottom": "14px", "padding_left": "0px", "padding_right": "0px"}}},
                                     "selected_page_and_hover": {"color": "var(--color_6)"},
                                     "breakpoint_overrides": {"tablet": {"link_text": {"font_size": "34px"}}, "mobile": {"link_text": {"font_size": "34px"}}}})),
    # legendas das galerias (fonte, cor, tamanho por tela, sem respiro)
    ("header", "es-drop-gallery", caption({"font_family": LT, "font_weight": "400", "color": "var(--color_1)"},
                                          {"font_family": OS, "font_weight": "400", "color": "var(--color_2)"},
                                          {"desktop": ("16px", "15px"), "tablet": ("16px", "15px"), "mobile": ("16px", "15px")}, position="top left")),
    ("header", "es-menu-atend", caption({"font_family": OS, "font_weight": "400", "color": "var(--color_2)"}, None,
                                        {"desktop": ("16px", "15px"), "tablet": ("16px", "15px"), "mobile": ("16px", "15px")}, padding="4px 0px")),
    ("*", "es-orbit-gallery", caption({"font_family": LT, "font_weight": "400", "color": "var(--color_1)"},
                                      {"font_family": OS, "font_weight": "400", "color": "var(--color_2)"},
                                      {"desktop": ("28px", "16px"), "tablet": ("28px", "16px"), "mobile": ("28px", "16px")})),
]


def areas():
    for k in pages.uuids():
        yield k, pages._base(k)
    yield "header", f"{lib.V2}/header/elements"
    yield "footer", f"{lib.V2}/footer/elements"


def audit(path="styles.css"):
    import re
    s = re.sub(r"/\*.*?\*/", "", open(path).read(), flags=re.S)
    edit = r"(font-size|font|color|text-align|margin(-\w+)?|padding(-\w+)?|width|max-width|min-height|height|line-height|letter-spacing|font-family|font-weight|background(-color|-image)?|border-radius)"
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", s):
        hits = [d.strip() for d in m.group(2).split(";") if "!important" in d and re.match(r"\s*" + edit + r"\s*:", d)]
        if hits:
            print(f"{m.group(1).strip()[:110]} || {'; '.join(hits)[:200]}")


if __name__ == "__main__":
    if "--audit" in sys.argv:
        audit()
        sys.exit()
    n = 0
    for label, base in areas():
        todo = [c for c in CHANGES if c[0] in (label, "*")]
        if not todo:
            continue
        for e in walk(lib.call("GET", base)["results"]):
            cc = e.get("custom_class_names") or []
            for _, cls, fn in todo:
                if cls not in cc:
                    continue
                props = e.get("props") or {}
                style = copy.deepcopy(props.get("style") or {})
                fn(style)
                if style == (props.get("style") or {}):
                    continue
                n += 1
                print(f"  {label}: {e['element_id']} {e['element_type']} {cls}")
                if APPLY:
                    body = {"element_type": e["element_type"], "props": {"data": props.get("data") or {}, "style": style}}
                    body["custom_class_names"] = cc
                    lib.call("PUT", f"{base}/{e['element_id']}", body)
    print(("gravados" if APPLY else "a alterar"), n)
