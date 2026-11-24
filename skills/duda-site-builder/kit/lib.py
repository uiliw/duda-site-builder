"""
Núcleo do builder do site Duda novo (alias <site>): API, conteúdo, imagens e helpers de widgets.

Princípios:
- O conteúdo vem dos mesmos arquivos do Next (src/lib/*.ts), exportados via Node.
- Tipografia e cores vêm do TEMA do site (h1–h6, parágrafo, cores color_1..): o editor muda tudo por lá.
  Widgets referenciam as cores do tema com var(--color_N); texto usa as tags h1–h6/p do tema e só
  recebe estilo inline quando foge da escala.
- Estilos nativos em props.style. O styles.css só guarda estrutura e movimento.
"""
import base64
import functools
import json
import time
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SITE = "<ALIAS>"  # alias do site Duda (ex.: <site>)
API = "https://api.duda.co/api"

# ---------- paleta (ids das cores no tema) ----------
AURORA, LAVANDA, NOITE, INDIGO, SOL, AMBAR, INDIGO_PROFUNDO, PESSEGO = (f"var(--color_{i})" for i in range(1, 9))
PALETTE = [
    ("color_1", "#FFF2E9", "Aurora (texto)"),
    ("color_2", "#ABA6D6", "Lavanda (texto de apoio)"),
    ("color_3", "#16132C", "Noite (fundo)"),
    ("color_4", "#312D60", "Índigo"),
    ("color_5", "#F56035", "Sol"),
    ("color_6", "#FFAB66", "Âmbar"),
    ("color_7", "#1E1A3D", "Índigo profundo"),
    ("color_8", "#FFC18F", "Pêssego"),
]
# Transparências não existem como variável de tema: ficam literais.
AURORA_85 = "rgba(255, 242, 233, 0.85)"
AURORA_75 = "rgba(255, 242, 233, 0.75)"
AURORA_25 = "rgba(255, 242, 233, 0.25)"
AURORA_15 = "rgba(255, 242, 233, 0.15)"
INDIGO_70 = "rgba(49, 45, 96, 0.7)"
CLEAR = "rgba(0, 0, 0, 0)"
SUN_GRADIENT = "linear-gradient(35deg, rgba(245, 96, 53, 1) 20%, rgba(255, 171, 102, 1) 95%, rgba(255, 193, 143, 1) 100%)"
DISPLAY = "Fraunces"
SANS = "'Hanken Grotesk'"  # entre aspas: sem elas a Duda grava "Hanken,Grotesk"


# ---------- API ----------

def _env():
    """Credenciais: ~/.config/duda/credentials.env (uma vez por máquina) e depois o .env do projeto (sobrescreve)."""
    import os
    out = {}
    for f in (pathlib.Path.home() / ".config/duda/credentials.env", REPO / ".env"):
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip("\"'")
    for k in ("DUDA_API_USER", "DUDA_API_PASS", "DUDA_TOKEN"):
        out[k] = os.environ.get(k) or out.get(k, "")
        if not out[k]:
            sys.exit(f"{k} ausente: preencha ~/.config/duda/credentials.env (veja .env.example do plugin)")
    return out


_E = _env()
_AUTH = "Basic " + base64.b64encode(f"{_E['DUDA_API_USER']}:{_E['DUDA_API_PASS']}".encode()).decode()


def call(method, path, body=None, ok_404=False, tries=5):
    # A Duda às vezes bloqueia rajadas de requisições com 403 do nginx (página HTML, não JSON)
    # ou 429: espera e tenta de novo antes de desistir.
    for attempt in range(tries):
        req = urllib.request.Request(
            API + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Authorization": _AUTH, "Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw.strip() else None
        except urllib.error.HTTPError as e:
            if ok_404 and e.code == 404:
                return None
            text = e.read().decode()
            throttled = e.code == 429 or e.code >= 500 or (e.code == 403 and "nginx" in text)
            if throttled and attempt < tries - 1:
                time.sleep(15 * (attempt + 1))
                continue
            sys.exit(f"{method} {path} -> {e.code}: {text[:2000]}")


def mcp(tool, args):
    """Chama uma ferramenta do MCP da Duda (usa DUDA_TOKEN)."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args}}).encode()
    req = urllib.request.Request(
        "https://mcp.duda.co/mcp", data=body, method="POST",
        headers={"Authorization": _E["DUDA_TOKEN"], "Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
    )
    raw = urllib.request.urlopen(req, timeout=180).read().decode()
    data = next((json.loads(l[5:]) for l in raw.splitlines() if l.startswith("data:")), None) or json.loads(raw)
    res = data.get("result", {})
    text = "".join(c.get("text", "") for c in res.get("content", []))
    if res.get("isError"):
        sys.exit(f"MCP {tool}: {text[:2000]}")
    return text


V2 = f"/sites/multiscreen/v2/{SITE}"


# ---------- conteúdo (fonte única: src/lib/*.ts) ----------

@functools.lru_cache
def content():
    script = (
        "Promise.all(['content','services','projects','segments','about'].map(n=>import('"
        + str(REPO / "src/lib/")
        + "/'+n+'.ts').then(m=>[n,m]))).then(r=>console.log(JSON.stringify(Object.fromEntries(r))))"
    )
    out = subprocess.run(["node", "--experimental-strip-types", "--no-warnings", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ---------- imagens (enviadas para a biblioteca do site novo) ----------

ASSETS_FILE = ROOT / "assets.json"


def assets():
    return json.loads(ASSETS_FILE.read_text()) if ASSETS_FILE.exists() else {}


def img(key):
    """Caminho local do Next (/images/...) ou chave (logo-claro) -> URL no CDN do site novo."""
    url = assets().get(key)
    if not url:
        sys.exit(f"imagem sem upload: {key} (rode build.py --assets)")
    return url


# ---------- texto (formato que o editor grava) ----------

def rte(tag, text, size=None, tablet=None, mobile=None, lh=None, color=None, font=None, ls=None, weight=None, align=None):
    """Bloco de texto. Sem argumentos usa o estilo do tema para a tag; com argumentos, sobrescreve inline."""
    cls = ["rteBlock"]
    if size:
        tablet = tablet or size
        mobile = mobile or tablet
        cls += [f"size-{size}", f"t-size-{tablet}", f"m-size-{mobile}"]
    if align:
        cls.append(f"text-align-{align}")
    block_style = f' style="line-height: {lh};"' if lh else ""
    span_cls = f' class="font-size-{size} t-font-size-{tablet} m-font-size-{mobile}"' if size else ""
    styles = ["display: initial"]
    if font:
        styles.append(f"font-family: {font}")
    if color:
        styles.append(f"color: {color}")
    if ls:
        styles.append(f"letter-spacing: {ls}")
    if weight:
        styles.append(f"font-weight: {weight}")
    return f'<{tag} class="{" ".join(cls)}"{block_style}><span{span_cls} style="{"; ".join(styles)};">{text}</span></{tag}>'


def p(text, **kw):
    return rte("p", text, **kw)


def lead(text, color=LAVANDA):
    """Texto de apoio maior (20/19/17)."""
    return rte("p", text, 20, 19, 17, lh=1.6, color=color)


def bullets(items, color=AURORA_85):
    li = "".join(f'<li><span style="display: initial; color: {color};">{i}</span></li>' for i in items)
    return f'<ul class="defaultList bullet">{li}</ul>'


# ---------- estrutura ----------

def pad(t=0, r=0, b=0, l=0):
    return {"padding_top": f"{t}px", "padding_right": f"{r}px", "padding_bottom": f"{b}px", "padding_left": f"{l}px"}


def section(cls, children, bg=NOITE, pad_y=(140, 96), direction=None, gap=None, min_height=None, anchor=None):
    desk, mob = pad_y
    style = {
        "background": {"color": bg},
        "spacing": pad(desk, 40, desk, 40),
        "breakpoint_overrides": {"mobile": {"spacing": pad(mob, 20, mob, 20)}},
        "size": {"min_height": min_height or "0px"},
    }
    if direction:
        style["flex_direction"] = direction
        style["align_items"] = "flex-start"
    if gap:
        style["column_gap"] = gap
    el = {"element_type": "SECTION", "custom_class_names": cls.split(), "props": {"style": style}, "children": children}
    if anchor:
        el["_anchor"] = anchor
    return el


def column(children, cls=None, gap="0px", width="100%", align="flex-start"):
    style = {"spacing": pad(), "row_gap": gap, "align_items": align, "justify_content": "flex-start", "size": {"width": width}}
    el = {"element_type": "COLUMN", "children": children, "props": {"style": style}}
    if cls:
        el["custom_class_names"] = cls.split()
    return el


def inner(cls, children, direction="column", gap="0px", align="flex-start", justify="flex-start", wrap=None,
          width=None, min_height=None, margin_top=None, **extra):
    style = {"flex_direction": direction, "spacing": pad(), "row_gap": gap, "column_gap": gap, "align_items": align, "justify_content": justify}
    if wrap:
        style["flex_wrap"] = wrap
    size = {k: v for k, v in (("width", width), ("min_height", min_height)) if v}
    if size:
        style["size"] = size
    if margin_top:
        style["spacing"] = dict(style["spacing"], margin_top=margin_top)
    style.update(extra)
    return {"element_type": "INNER_COLUMN", "custom_class_names": cls.split(), "props": {"style": style}, "children": children}


def para(cls, html, width="100%", max_width=None, margin_top=None):
    # max_width em px vira largura do widget (teto 100%): o controle de largura do editor só mexe no width,
    # um max_width escondido trava o ajuste (cliente, 2026-10-22).
    if max_width and max_width != "100%" and width in ("100%", None):
        width, max_width = max_width, None
    style = {"size": {"width": width, "max_width": max_width or "100%"}}
    if margin_top is not None:
        style["spacing"] = {"margin_top": f"{margin_top}px"}
    return {"element_type": "PARAGRAPH", "custom_class_names": cls.split(), "props": {"data": {"content": html}, "style": style}}


def image(cls, src, alt, radius=None, fit="cover", width=None, height=None):
    style = {"object_fit": fit}
    if radius:
        style["border"] = {"radius": radius, "width": "0px", "color": CLEAR}
    if width or height:
        style["size"] = {k: v for k, v in (("width", width), ("height", height)) if v}
    return {"element_type": "IMAGE", "custom_class_names": cls.split(), "props": {"data": {"src": src, "alt": alt}, "style": style}}


def button(kind, text, href, new_tab=False, cls=""):
    """kind: primary/secondary usam o estilo de botão do tema; link/indigo sobrescrevem."""
    link = {"href": href, "target": "_blank" if new_tab else "", "rel": "noopener" if new_tab else "", "type": ""}
    style = {"size": {"width": "auto"}, "alignment": "LEFT"}
    if kind in ("primary", "secondary"):
        style["button_style"] = kind.upper()
        style["spacing"] = pad(15, 28, 15, 28)
    if kind == "secondary":
        # Gradiente transparente explícito: sem ele o secundário herda o gradiente do primário.
        style["background"] = {"color": CLEAR, "gradient": "linear-gradient(0deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) 100%)"}
    elif kind == "link":
        style.update({
            "button_style": "SECONDARY",
            # Gradiente transparente explícito: senão herda o gradiente do botão primário do tema.
            "background": {"color": CLEAR, "gradient": "linear-gradient(0deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) 100%)"},
            "border": {"radius": "999px", "width": "0px", "color": CLEAR},
            "text": {"color": AURORA_85, "font_family": SANS, "font_size": "16px", "font_weight": "400"},
            "hover": {"background": {"color": CLEAR}, "text": {"color": AURORA}},
            "spacing": pad(14, 6, 14, 6),
        })
    elif kind == "indigo":
        style.update({
            "button_style": "PRIMARY",
            "background": {"color": INDIGO, "gradient": "linear-gradient(0deg, var(--color_4) 0%, var(--color_4) 100%)"},
            "text": {"color": AURORA, "font_family": SANS, "font_size": "18px", "font_weight": "500"},
            "hover": {"background": {"color": NOITE}, "text": {"color": AURORA}},
            "spacing": pad(18, 36, 18, 36),
        })
    return {"element_type": "BUTTON", "custom_class_names": [f"ov-btn-{kind}"] + cls.split(),
            "props": {"data": {"text": text, "link": link}, "style": style}}


def icon(cls, svg, alt="", size="28px"):
    return {"element_type": "ICON", "custom_class_names": cls.split(),
            "props": {"data": {"icon": svg, "alt": alt}, "style": {"size": {"width": size, "height": size}}}}


def accordion(cls, items, title_color=AURORA, desc_color=AURORA_75):
    return {
        "element_type": "ACCORDION",
        "custom_class_names": cls.split(),
        "props": {
            "data": {
                "first_expanded": True, "close_others": True, "add_schema_markup": True,
                "items_data": [{"title": q, "desc": p(a, color=desc_color), "show_button": False, "show_media": False} for q, a in items],
            },
            "style": {
                "title_tag": "h3",
                "item": {
                    "title": {"color": title_color, "font_family": SANS, "font_size": "20px", "font_weight": "400", "gap": "24px"},
                    "title_wrapper": {"background": {"color": CLEAR}},
                    "description": {"background": {"color": CLEAR}},
                    "arrow_wrapper": {"color": title_color, "background": {"color": CLEAR}},
                },
                "description": {"color": desc_color, "font_family": SANS, "font_size": "17px"},
            },
        },
    }


def gallery(cls, collection, item, query=None, columns=3, title_color=AURORA, desc_color=AURORA_75, full_image=False, source="COLLECTION"):
    binding = {"source": source, "collection": collection, "item": item}
    if query:
        binding["query"] = query
    style = {
        "layout": "SQUARE", "columns": columns, "corner_radius": "24px 24px 24px 24px",
        "caption": {
            "display": "BELOW", "position": "bottom left",
            "title": {"color": title_color, "font_family": DISPLAY, "font_weight": "400"},
            "description": {"color": desc_color, "font_family": SANS, "font_weight": "400"},
        },
    }
    if full_image:
        style["image"] = {"size": "contain"}
        style["breakpoint_overrides"] = {
            "desktop": {"image_style": {"padding": "0px", "height": "0px"}},
            "tablet": {"image_style": {"padding": "0px", "height": "100%"}},
            "mobile": {"image_style": {"padding": "0px", "height": "100%"}},
        }
    return {"element_type": "PHOTO_GALLERY", "custom_class_names": cls.split(), "props": {"style": style},
            "connected_data": {"data": {"images": binding}}}


def bound_para(cls, field, tag="p", width="100%", max_width=None, text=None, sizes=None):
    """Parágrafo ligado a um campo da página dinâmica (coleção).
    `text`: estilo nativo (fonte, cor, peso); `sizes`: (desktop, tablet, mobile) em px."""
    el = para(cls, rte(tag, "&nbsp;"), width=width, max_width=max_width)
    el["connected_data"] = {"data": {"content": {"source": "DYNAMIC_PAGE", "field": field}}}
    if text or sizes:
        st = el["props"]["style"]
        st["text"] = dict(text or {})
        if sizes:
            d, t, m = sizes
            st["text"]["font_size"] = f"{d}px"
            st["breakpoint_overrides"] = {"tablet": {"text": {"font_size": f"{t}px"}}, "mobile": {"text": {"font_size": f"{m}px"}}}
    return el


DISPLAY_TEXT = {"font_family": "Fraunces", "font_weight": "400", "color": "var(--color_1)"}
BODY_TEXT = {"font_family": "'Hanken Grotesk'", "font_weight": "400", "color": "rgba(255, 242, 233, 0.85)"}


# ---------- head (CSS/JS de estrutura e movimento, igual em todas as páginas) ----------

FONTS = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..600,0..100,0..1&family=Hanken+Grotesk:wght@400;500;600&display=swap"


def _b64(text):
    return base64.b64encode(text.encode()).decode()


def head_html():
    html = (
        (ROOT / "head.html").read_text()
        .replace("/*FONTS*/", _b64(FONTS))
        .replace("/*STYLES*/", _b64((ROOT / "styles.css").read_text()))
        .replace("/*MOTION*/", _b64((ROOT / "motion.js").read_text()))
    )
    body = "".join(part.split(">", 1)[-1] for part in html.split("<"))
    assert not any(ch in body for ch in "<>&"), "head_html contém caractere que a Duda escapa"
    return html


def strip_private(el):
    """Remove chaves internas (_anchor) antes de enviar para a API."""
    el = {k: v for k, v in el.items() if not k.startswith("_")}
    if "children" in el:
        el["children"] = [strip_private(c) for c in el["children"]]
    return el


# ---------------------------------------------------------------- widgets ligados e troca pontual (aprendido no Projeto A, 2026-09)
def bound_image(cls, field, alt_field="Nome", placeholder="", radius=None, fit="cover"):
    """Imagem ligada a um campo de imagem da página dinâmica. Ligue a um campo com a URL já reduzida
    (.../dms3rep/multi/opt/<nome>-480w.<ext>): a Duda serve a versão 1920w do campo original."""
    el = image(cls, placeholder, "", radius=radius, fit=fit)
    el["connected_data"] = {"data": {"src": {"source": "DYNAMIC_PAGE", "field": field},
                                     "alt": {"source": "DYNAMIC_PAGE", "field": alt_field}}}
    return el


def campo(cls, field, **kw):
    """Parágrafo ligado a um campo com HTML pronto (montado no banco/view). Resete no CSS os estilos de
    parágrafo da Duda dentro de .campo (marcador de li, recuo, cor de link)."""
    return bound_para(f"campo {cls}".strip(), field, **kw)


def galeria_lista(cls, field, columns=3):
    """Galeria na página dinâmica ligada a um campo de coleção interna do item ([{Img, Nome, Link, Sub}]).
    Lista vazia = a Duda não desenha a galeria (esconda o bloco/título com :has no CSS)."""
    ci = lambda f: {"source": "COLLECTION_ITEM", "field": f}
    item = {"src": ci("Img"), "alt": ci("Nome"), "title": {"title": ci("Nome")}, "description": {"description": ci("Sub")}, "button": {"link": ci("Link")}}
    g = gallery(cls, None, item, columns=columns)
    g["connected_data"] = {"data": {"images": {"source": "DYNAMIC_PAGE", "field": field, "item": item}}}
    return g


def texto_site(el, field="about_us"):
    """Liga um parágrafo a um texto da biblioteca de conteúdo (about_us, overview, services). O HTML de `el` fica como
    estilo/reserva; o texto vem de site_texts (POST /sites/multiscreen/{site}/content)."""
    el["connected_data"] = {"data": {"content": {"source": "SITE_TEXT", "field": field}}}
    return el


def trocar(page_uuid, cls, novos, dry=False, match=None):
    """Troca pontual: acha os elementos com a classe `cls` (e `match(e)`, se dado) e insere `novos` no mesmo lugar
    (POST com parent_id + next_sibling_id), depois apaga o antigo. Não remonta a página nem desfaz edições do editor.
    `novos` pode ser uma função (elemento antigo -> lista de novos)."""
    base = f"{V2}/pages/{page_uuid}/elements"
    achados = []

    def andar(els):
        for e in els:
            if cls in (e.get("custom_class_names") or []) and (match is None or match(e)):
                achados.append(e)
            andar(e.get("children") or [])
    andar(call("GET", base)["results"])
    for e in achados:
        if dry:
            print("trocaria", e["element_id"], e["element_type"], "em", e.get("parent_id"))
            continue
        for n in (novos(e) if callable(novos) else novos):
            call("POST", base, dict(strip_private(n), parent_id=e["parent_id"], next_sibling_id=e["element_id"]))
        call("DELETE", f"{base}/{e['element_id']}")
    return len(achados)


def recriar_secao(page_uuid, element_id, nova):
    """Recria uma seção no mesmo lugar (nova antes da antiga, depois apaga a antiga). Único jeito de limpar os widgets
    apagados pela API que a Duda deixa escondidos no .flex-widgets-container da seção (PUT e publicar não limpam).
    Desfaz edições do editor dentro da seção: compare antes com o builder."""
    base = f"{V2}/pages/{page_uuid}/elements"
    res = call("POST", base, dict(strip_private(nova), next_sibling_id=element_id))
    call("DELETE", f"{base}/{element_id}")
    return res["element_id"]


# ---------------------------------------------------------------- texto pelo tema, botão-link e fio nativo (Projeto G, 2026-10)
# Escala do tema por tag: (desktop, tablet, celular, entrelinha). Preencha com os mesmos valores do theme.py.
THEME_SIZES = {}  # ex.: {"h2": (50, 44, 36, "1.08"), "p": (17, 17, 17, "1.65")}
DEFAULT_TEXT_COLOR = None  # ex.: "var(--color_1)"


def native_text(tag, text, sizes=(None, None, None), lh=None, color=None, font=None, align=None):
    """Bloco no formato do editor escrevendo inline SÓ o que foge do tema (tamanho, entrelinha, cor, fonte).
    Igual ao tema = `<h2 class="rteBlock">…</h2>`: o editor muda título/parágrafo pelo tema, sem estilo preso no texto."""
    base = THEME_SIZES.get(tag)
    if base and tuple(sizes) == tuple(base[:3]):
        sizes = (None, None, None)
    if base and lh == base[3]:
        lh = None
    if color == DEFAULT_TEXT_COLOR:
        color = None
    if not any((*sizes, lh, color, font)):
        cls = "rteBlock" + (f" text-align-{align}" if align else "")
        return f'<{tag} class="{cls}">{text}</{tag}>'
    return rte(tag, text, *sizes, lh=lh, color=color, font=font, align=align)


def link_button(text, href, color=None, new_tab=False, margin_top=None, cls="link-btn"):
    """Link de chamada ("Saiba mais") como BOTÃO nativo no estilo secundário do tema (fundo e borda transparentes,
    alinhado à esquerda): texto e destino editáveis no editor. `color` vale só para este botão (seção escura).
    O CSS só desenha o detalhe do link (sublinhado etc.) em `.<cls> .dmButtonLink .text` e esconde `.iconBg`.
    Padding 12px vertical = alvo de toque ≥ 44 px."""
    link = {"href": href, "target": "_blank" if new_tab else "", "rel": "noopener" if new_tab else "", "type": ""}
    style = {"size": {"width": "auto"}, "alignment": "LEFT", "button_style": "SECONDARY", "spacing": pad(12, 0, 12, 0)}
    if margin_top is not None:
        style["spacing"]["margin_top"] = f"{margin_top}px"
    if color:
        style["text"] = {"color": color}
        style["hover"] = {"text": {"color": color}}
    return {"element_type": "BUTTON", "custom_class_names": cls.split(),
            "props": {"data": {"text": text, "link": link}, "style": style}}


def top_rule(color, clear="rgba(0, 0, 0, 0)"):
    """Fio só no topo como borda nativa (seção, parágrafo, coluna): largura/cor por lado em topo, direita, base, esquerda."""
    return {"width": "1px 0px 0px 0px", "color": f"{color} {clear} {clear} {clear}", "radius": None}
