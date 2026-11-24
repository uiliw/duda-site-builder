"""Contato: formulário nativo da Duda (mesma estrutura e destinatários do site atual)."""
import json

import blocks as b
import lib
from lib import AURORA, LAVANDA, column, image, inner, p, para, section

OLD_CONTACT = lib.ROOT / "reference/contato-form.json"


def _clean(el):
    out = {k: el[k] for k in ("element_type", "props", "custom_class_names") if el.get(k) is not None}
    if el.get("children"):
        out["children"] = [_clean(c) for c in el["children"]]
    return out


FONT = "'Hanken Grotesk'"
FIELD_TEXT = {"font_family": FONT, "font_weight": "400", "font_size": "16px", "color": "var(--color_1)"}
PLACEHOLDER = dict(FIELD_TEXT, color="rgba(255, 242, 233, 0.45)")
FIELD_BOX = {"background_color": "rgba(22, 19, 44, 0.4)",
             "border": {"color": "rgba(255, 242, 233, 0.2)", "width": "1px 1px 1px 1px", "radius": "16px 16px 16px 16px"}}
NO_PAD = {"padding_top": "0px", "padding_right": "0px", "padding_bottom": "0px", "padding_left": "0px"}


def _walk(el, fn):
    fn(el)
    for c in el.get("children") or []:
        _walk(c, fn)


def _style_form(form):
    """Estilo do protótipo nas propriedades nativas do formulário (editáveis no editor)."""
    def fix(el):
        st = el.setdefault("props", {}).setdefault("style", {}) or {}
        el["props"]["style"] = st
        t = el["element_type"]
        if t == "TEXT_INPUT":
            st.update({"label": FIELD_TEXT, "input_text": FIELD_TEXT, "placeholder_text": PLACEHOLDER, "field": FIELD_BOX})
            st["size"] = dict(st.get("size") or {}, width="100%", max_width="100%")
            st["spacing"] = dict(st.get("spacing") or {}, margin_top="0px", margin_bottom="0px")
        elif t == "CHOICE":
            st.update({"label": dict(FIELD_TEXT), "text": dict(FIELD_TEXT, color="rgba(255, 242, 233, 0.85)")})
            st["check_box"] = {"background_color": "rgba(22, 19, 44, 0.4)",
                               "border": {"color": "rgba(255, 242, 233, 0.35)", "width": "1px 1px 1px 1px", "radius": "6px 6px 6px 6px"},
                               "selected_background_color": "var(--color_5)",
                               "selected_border": {"color": "var(--color_5)", "width": "1px 1px 1px 1px", "radius": "6px 6px 6px 6px"},
                               "checkmark_color": "var(--color_1)"}
            st["size"] = dict(st.get("size") or {}, width="100%", max_width="100%")
        elif t in ("FORM_ELEMENT", "FORM_STEP", "INNER_COLUMN", "FORM_BUTTONS_CONTAINER"):
            st["spacing"] = dict(st.get("spacing") or {}, **NO_PAD)
            st["size"] = dict(st.get("size") or {}, min_height="0px")
            st["row_gap"] = "20px"
            if t == "FORM_BUTTONS_CONTAINER":
                st["spacing"]["margin_top"] = "16px"
        elif t == "FORM_BUTTON" and st.get("button_style") == "SECONDARY":
            # Enviar: botão primário do tema (gradiente do sol).
            st.update({"button_style": "PRIMARY", "size": dict(st.get("size") or {}, width="auto"),
                       "spacing": dict(st.get("spacing") or {}, padding_top="16px", padding_right="32px", padding_bottom="16px", padding_left="32px")})
    _walk(form, fix)
    # E-mail e WhatsApp lado a lado (no celular a coluna volta a empilhar).
    fields = form["children"][0]["children"][0]
    kids = fields["children"]
    inputs = [k for k in kids if k["element_type"] == "TEXT_INPUT"]
    email, phone = inputs[1], inputs[2]
    for f in (email, phone):
        st = f["props"]["style"]
        st["size"] = dict(st["size"], width="48%")
        bo = st.setdefault("breakpoint_overrides", {}) or {}
        st["breakpoint_overrides"] = bo
        bo["mobile"] = dict(bo.get("mobile") or {}, size={"width": "100%", "max_width": "100%"})
    row = {"element_type": "INNER_COLUMN", "props": {"style": {
        "flex_direction": "row", "justify_content": "space-between", "align_items": "flex-start", "column_gap": "4%", "row_gap": "20px",
        "size": {"width": "100%", "min_height": "0px"}, "spacing": dict(NO_PAD),
        "breakpoint_overrides": {"mobile": {"flex_direction": "column"}}}},
        "children": [email, phone]}
    i = kids.index(email)
    kids[i:i + 2] = [row]
    return form


def sections():
    form = _style_form(_clean(json.loads(OLD_CONTACT.read_text())))
    form["custom_class_names"] = ["ov-form"]
    links = (p(f'<a href="{b.WHATSAPP}" target="_blank" type="url" style="color: {AURORA};">WhatsApp +55 00 00000-0000</a>')
             + p(f'<a href="{b.INSTAGRAM}" target="_blank" type="url" style="color: {AURORA};">Instagram @agencia.exemplo</a>')
             + p("Florianópolis, Santa Catarina. Atendemos todo o Brasil.", color=LAVANDA))
    contact = section("ov-contact", [
        column([image("ov-contact-arch", lib.img("/images/contato-portal.webp"), "Mulher diante de um anel de luz suave em tons de lilás"),
                para("ov-contact-links", p("Prefere falar direto?", size=20, color=AURORA) + links, margin_top=40)], cls="ov-contact-aside", width="38%"),
        column([form], cls="ov-contact-form", width="56%"),
    ], direction="row", gap="6%", pad_y=(0, 120))
    return [b.statement("Vamos conversar.", "Seja um novo projeto ou uma pergunta rápida, estamos aqui para você. Conte sua ideia e vamos transformá-la em impacto duradouro."),
            contact, b.faq()]
