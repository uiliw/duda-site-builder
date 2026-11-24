"""Header e footer globais do site (nativos). Leem o elemento atual e enviam props completos (PUT substitui tudo)."""
import copy

import lib
from lib import (AURORA, AURORA_85, CLEAR, DISPLAY, INDIGO, INDIGO_70, NOITE, SANS, SOL, button, column, image, inner, p, para, rte)

WHATSAPP = "https://wa.me/5500000000000?text=Ol%C3%A1!%20Vim%20pelo%20site%20da%20Agência Exemplo%20e%20quero%20come%C3%A7ar%20um%20projeto."
INSTAGRAM = "https://instagram.com/agencia.exemplo"


def _walk(els, out):
    for e in els:
        out[e["element_id"]] = e
        _walk(e.get("children") or [], out)
    return out


def _put(area, el, data=None, style=None, classes=None):
    props = copy.deepcopy(el.get("props") or {})
    if data is not None:
        props["data"] = data
    if style is not None:
        props["style"] = style
    body = {"element_type": el["element_type"], "props": props}
    if classes is not None:
        body["custom_class_names"] = classes
    lib.call("PUT", f"{lib.V2}/{area}/elements/{el['element_id']}", body)


def _style(el):
    return copy.deepcopy((el.get("props") or {}).get("style") or {})


def _nav_style(el, color, hover, size, font=SANS, weight="400"):
    st = _style(el)
    st["effect"] = "NONE"
    st.setdefault("all_pages", {})
    st["all_pages"]["link_text"] = {"font_family": font, "font_weight": weight, "font_style": None, "font_size": size,
                                    "color": color, "text_decoration": None, "text_transform": "none"}
    st["selected_page_and_hover"] = dict(st.get("selected_page_and_hover") or {}, color=hover)
    return st


def header():
    res = lib.call("GET", f"{lib.V2}/header/elements")
    els = _walk(res["results"] if isinstance(res, dict) else res, {})
    by_type = {}
    for e in els.values():
        by_type.setdefault(e["element_type"], []).append(e)

    hdr = by_type["HEADER"][0]
    st = _style(hdr)
    st["background"] = {"color": CLEAR, "image": None, "gradient": None}
    _put("header", hdr, style=st)

    main_section = hdr["children"][0]
    st = _style(main_section)
    st["spacing"] = dict(st.get("spacing") or {}, **lib.pad(0, 40, 0, 40))
    st["background"] = {"color": CLEAR}
    _put("header", main_section, style=st, classes=["ov-header"])

    logo = by_type["IMAGE"][0]
    st = _style(logo)
    st["size"] = dict(st.get("size") or {}, width="141px", height="auto")
    _put("header", logo, data=dict(logo["props"]["data"], src=lib.img("logo-claro"), alt="Agência Exemplo"), style=st)

    navs = by_type["NAVIGATION"]
    top_nav = next(n for n in navs if _style(n).get("orientation") == "HORIZONTAL")
    menu_nav = next(n for n in navs if n is not top_nav)
    _put("header", top_nav, style=_nav_style(top_nav, AURORA_85, AURORA, "15px"), classes=["ov-nav"])
    _put("header", menu_nav, style=_nav_style(menu_nav, AURORA, lib.AMBAR, "44px", font=DISPLAY), classes=["ov-menu-nav"])

    cta = by_type["BUTTON"][0]
    st = _style(cta)
    st.update({"button_style": "PRIMARY", "size": {"width": "auto", "height": "auto"}, "spacing": lib.pad(11, 22, 11, 22)})
    link = {"href": WHATSAPP, "target": "_blank", "rel": "noopener", "type": ""}
    _put("header", cta, data=dict(cta["props"]["data"], text="Começar projeto", link=link), style=st, classes=["ov-btn-primary", "ov-header-cta"])

    for ic in by_type.get("ICON", []):
        lib.call("DELETE", f"{lib.V2}/header/elements/{ic['element_id']}")

    for hb in by_type.get("HAMBURGER_BUTTON", []):
        st = _style(hb)
        st["icon"] = {"color": AURORA, "background_color": CLEAR}
        _put("header", hb, style=st)

    # Painel do menu no celular: fundo índigo, menu grande em Fraunces e contatos.
    menu = by_type["HAMBURGER_MENU"][0]
    for sec in menu["children"]:
        st = _style(sec)
        st["background"] = {"color": INDIGO}
        _put("header", sec, style=st)
    text = by_type["PARAGRAPH"][0]
    contacts = (p(f'<a href="{WHATSAPP}" target="_blank" type="url" style="color: {AURORA};">WhatsApp +55 00 00000-0000</a>')
                + p(f'<a href="{INSTAGRAM}" target="_blank" type="url" style="color: {AURORA};">Instagram @agencia.exemplo</a>'))
    _put("header", text, data={"content": contacts})
    print("header global configurado")


def footer():
    res = lib.call("GET", f"{lib.V2}/footer/elements")
    root = (res["results"] if isinstance(res, dict) else res)[0]
    st = _style(root)
    st["background"] = {"color": AURORA, "image": None, "gradient": None}
    _put("footer", root, style=st)
    for sec in root.get("children") or []:
        lib.call("DELETE", f"{lib.V2}/footer/elements/{sec['element_id']}")

    label = lambda t: para("ov-footer-label", p(t, size=14, color=INDIGO_70))
    contacts = (p(f'<a href="{WHATSAPP}" target="_blank" type="url" style="color: {INDIGO};">WhatsApp +55 00 00000-0000</a>', color=INDIGO)
                + p(f'<a href="{INSTAGRAM}" target="_blank" type="url" style="color: {INDIGO};">Instagram @agencia.exemplo</a>', color=INDIGO))
    nav = {
        "element_type": "NAVIGATION", "custom_class_names": ["ov-footer-nav"],
        "props": {"data": {"navigation_type": "SITE_PAGES"}, "style": {
            "orientation": "VERTICAL", "main_layout": "VERTICAL_NAV_LAYOUT_1", "effect": "NONE",
            "all_pages": {"link_text": {"color": INDIGO, "font_family": SANS, "font_size": "16px", "font_weight": "400", "text_transform": "none"},
                          # Itens próximos, sem divisória (como no protótipo).
                          "link_style": {"divider": "NONE", "spacing": {"padding_top": "4px", "padding_right": "0px", "padding_bottom": "4px", "padding_left": "0px"}}},
            "selected_page_and_hover": {"color": SOL},
        }},
    }
    social = {"element_type": "SOCIAL_ICONS", "custom_class_names": ["ov-footer-social"],
              "props": {"data": {"networks": [{"platform": "instagram", "url": INSTAGRAM}, {"platform": "whatsapp", "url": WHATSAPP}]}}}
    section = lib.section("ov-footer", [
        column([
            inner("ov-footer-top", [
                para("ov-footer-tagline", rte("p", "Presença digital e branding visionário para negócios com propósito.", 44, 36, 30, lh=1.05, color=INDIGO, font=DISPLAY, ls="-0.03em"), width="40%"),
                inner("ov-footer-col", [label("Navegue"), nav], gap="16px", width="25%"),
                inner("ov-footer-col", [label("Fale com a gente"), para("ov-footer-contact", contacts), social], gap="16px", width="25%"),
            ], direction="row", gap="48px", justify="space-between", width="100%"),
            inner("ov-footer-brand", [
                image("ov-footer-logo", lib.img("logo-indigo"), "Agência Exemplo", width="100%"),
                inner("ov-footer-bottom", [
                    para("ov-footer-legal", p("© 2020–2026 Agência Exemplo", size=14, color=INDIGO_70), width="auto"),
                    para("ov-footer-legal", p("Marketing com propósito", size=14, color=INDIGO_70), width="auto"),
                ], direction="row", justify="space-between", width="100%"),
            ], gap="20px", width="100%"),
        ], gap="96px"),
    ], bg=AURORA, pad_y=(110, 80))
    # O nascer do sol (chamada para contato) abre o footer em todas as páginas.
    import blocks
    lib.call("POST", f"{lib.V2}/footer/elements", lib.strip_private(blocks.sunrise()))
    lib.call("POST", f"{lib.V2}/footer/elements", lib.strip_private(section))
    print("footer global configurado (nascer do sol + rodapé)")
