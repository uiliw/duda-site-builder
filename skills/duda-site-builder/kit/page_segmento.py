"""Página dinâmica: cada seção lê os campos do item da coleção Segmentos."""
import blocks as b
import lib
from lib import AURORA_85, BODY_TEXT, DISPLAY_TEXT, LAVANDA, NOITE, INDIGO, bound_para, button, column, image, inner, para, section


def sections():
    hero = section("ov-phero ov-phero--bound", [
        column([
            bound_para("ov-phero-title", "segmento", tag="h1", max_width="1100px", text=DISPLAY_TEXT, sizes=(115, 80, 50)),
            inner("ov-phero-sub", [bound_para("ov-phero-lead", "chamada", max_width="460px", text=BODY_TEXT, sizes=(20, 19, 17)),
                                   inner("ov-phero-ctas", [button("primary", "Começar projeto", b.WHATSAPP, new_tab=True),
                                                           button("link", "Ver como ajudamos ↘", "#o-que-fazemos")], direction="row", gap="20px", align="center")],
                  direction="row", justify="space-between", align="flex-end", wrap="wrap", gap="32px", width="100%", margin_top="32px"),
        ], cls="ov-phero-col"),
    ], pad_y=(0, 0))
    hero["connected_data"] = {"style": {"background": {"image": {"source": "DYNAMIC_PAGE", "field": "hero"}}}}

    pic = image("ov-intro-arch", lib.img("/images/cristais.webp"), "")
    pic["connected_data"] = {"data": {"src": {"source": "DYNAMIC_PAGE", "field": "imagem"}}}
    intro = section("ov-intro", [
        column([b.heading("Como fortalecemos a sua presença."), bound_para("ov-intro-text", "descricao", max_width="600px", text=dict(BODY_TEXT, color="var(--color_2)"), sizes=(20, 19, 17))], width="52%"),
        column([pic], cls="ov-intro-media", width="40%", align="center"),
    ], direction="row", gap="8%", anchor="o-que-fazemos")

    highlights = section("ov-highlights", [
        column([b.heading("O que entra no seu projeto.", max_width="520px")], width="40%"),
        column([bound_para("ov-highlights-list", "diferenciais", text=DISPLAY_TEXT, sizes=(40, 32, 24))], width="54%"),
    ], bg=INDIGO, direction="row", gap="6%")

    faq = section("ov-faq ov-faq--bound", [
        column([b.heading("Perguntas frequentes.", max_width="520px"), b.sub("Não encontrou sua dúvida? A gente responde pessoalmente."),
                button("secondary", "Fazer uma pergunta", b.WHATSAPP, new_tab=True)], cls="ov-faq-aside", gap="28px", width="40%"),
        column([bound_para("ov-faq-bound", "perguntas", text=BODY_TEXT, sizes=(18, 17, 16))], cls="ov-faq-list", width="54%"),
    ], direction="row", gap="6%")

    others = section("ov-segments ov-segments--others", [column([para("ov-others-label", lib.rte("h6", "Outros segmentos")), b.segments_gallery()])], pad_y=(0, 96))
    return [hero, intro, highlights, faq, others]
