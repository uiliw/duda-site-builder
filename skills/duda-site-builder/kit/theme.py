"""Tema global do site: paleta, tipografia (h1–h6, parágrafo), botões, espaçamentos e fundo."""
from lib import PALETTE, SANS, SITE, SUN_GRADIENT, call

# Escala tipográfica (desktop, tablet, mobile). Fraunces nos títulos, Hanken Grotesk no texto.
TYPE = {
    "h1": ("Fraunces", 115, 80, 50, "1.2", "-0.035em"),
    "h2": ("Fraunces", 84, 64, 42, "1", "-0.035em"),
    "h3": ("Fraunces", 56, 44, 34, "1.05", "-0.03em"),
    "h4": ("Fraunces", 38, 32, 28, "1.1", "-0.03em"),
    "h5": ("Hanken Grotesk", 22, 20, 19, "1.4", "0"),
    "h6": ("Hanken Grotesk", 16, 16, 15, "1.4", "0"),
    "paragraph": ("Hanken Grotesk", 18, 17, 16, "1.6", "0"),
}


def text_style(font, d, t, m, lh, ls, color="var(--color_1)", weight="400"):
    return {
        "font_family": font,
        "color": color,
        "font_weight": weight,
        "font_style": "normal",
        "text_decoration": "none",
        "text_direction": "ltr",
        "line_height": lh,
        "letter_spacing": ls,
        "font_size": f"{d}px",
        "text_transform": None,
        "breakpoints": {"tablet": {"text": {"font_size": f"{t}px"}}, "mobile": {"text": {"font_size": f"{m}px"}}},
    }


def build_theme(current):
    colors = []
    ours = {cid: (hexv, label) for cid, hexv, label in PALETTE}
    for c in current["colors"]:
        if c["id"] in ours:
            colors.append({"id": c["id"], "value": ours[c["id"]][0], "label": ours[c["id"]][1]})
        else:
            colors.append({"id": c["id"], "value": None, "label": None})

    text = {k: text_style(*v) for k, v in TYPE.items()}
    text["h6"]["color"] = "var(--color_2)"
    text["default"] = text_style("Hanken Grotesk", 18, 17, 16, "1.6", "0")

    button_text = {"font_family": SANS.strip("'"), "font_size": "16px", "font_weight": "500", "text_decoration": "none",
                   "font_style": None, "text_align": "center", "direction": "ltr"}
    buttons = {
        # Primário: o gradiente do sol do logo.
        "primary": {
            "box_shadow": None,
            "background": {"color": "var(--color_5)", "gradient": SUN_GRADIENT, "image": None},
            "border": {"color": "rgba(0, 0, 0, 0)", "width": "0px", "radius": "999px"},
            "icon": {"color": "var(--color_3)"},
            "hover": {"background": {"color": "var(--color_6)"}, "border": {"color": "rgba(0, 0, 0, 0)"},
                      "text": {"color": "var(--color_3)", "font_weight": None, "text_decoration": None, "font_style": None}},
            "text": dict(button_text, color="var(--color_3)"),
            "breakpoints": {"mobile": {"text": {"font_size": "15px"}}, "tablet": {"text": {"font_size": "16px"}}},
        },
        # Secundário: contorno claro.
        "secondary": {
            "box_shadow": None,
            # Gradiente transparente explícito: com None o secundário herda o gradiente do primário.
            "background": {"color": "rgba(0, 0, 0, 0)", "gradient": "linear-gradient(0deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) 100%)", "image": None},
            "border": {"color": "rgba(255, 242, 233, 0.6)", "width": "1px", "radius": "999px"},
            "icon": {"color": "var(--color_1)"},
            "hover": {"background": {"color": "rgba(255, 171, 102, 0.08)", "gradient": "linear-gradient(0deg, rgba(255, 171, 102, 0.08) 0%, rgba(255, 171, 102, 0.08) 100%)"}, "border": {"color": "var(--color_6)"},
                      "text": {"color": "var(--color_6)", "font_weight": None, "text_decoration": None, "font_style": None}},
            "text": dict(button_text, color="var(--color_1)", font_weight="400"),
            "breakpoints": {"mobile": {"text": {"font_size": "15px"}}, "tablet": {"text": {"font_size": "16px"}}},
        },
    }
    sections = {
        "spacings": {"padding_top": "140px", "padding_bottom": "140px", "padding_left": "40px", "padding_right": "40px"},
        "content_width": {"default_max_width_constraint": "1440px", "default_content_mode": "constrained_width"},
        "breakpoints": {
            "tablet": {"spacing": {"padding_top": "112px", "padding_bottom": "112px", "padding_left": "32px", "padding_right": "32px"}},
            "mobile": {"spacing": {"padding_top": "96px", "padding_bottom": "96px", "padding_left": "20px", "padding_right": "20px"}},
        },
    }
    zero = {"padding_top": "0px", "padding_bottom": "0px", "padding_left": "0px", "padding_right": "0px"}
    return {
        "colors": colors,
        "text": text,
        "buttons": buttons,
        "sections": sections,
        "columns": {"spacings": zero, "breakpoints": None},
        "inner_columns": {"spacings": zero, "breakpoints": None},
        "background": {"color": "var(--color_3)", "gradient": None, "image": None, "breakpoints": None},
    }


def apply():
    current = call("GET", f"/sites/multiscreen/{SITE}/theme")
    theme = build_theme(current)
    call("PUT", f"/sites/multiscreen/{SITE}/theme", theme)
    print("tema aplicado:", len(theme["colors"]), "cores,", len(theme["text"]), "estilos de texto")
