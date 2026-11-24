"""Páginas do site: criação/renomeação, SEO, navegação e montagem do conteúdo."""
import importlib
import json

import lib

PAGES_FILE = lib.ROOT / "pages.json"

# Chave -> título, caminho, SEO (mesmos textos do metadata do Next).
PAGES = {
    "home": {"title": "Home", "path": "home", "template": "home",
             "seo": ("Agência Exemplo | Agência de Marketing Digital com Propósito",
                     "Criamos presenças digitais autênticas para negócios com propósito. Sites que convertem, branding visionário e estratégias de marketing personalizadas.")},
    "servicos": {"title": "Serviços", "path": "servicos", "template": "services",
                 "seo": ("Serviços | Agência Exemplo", "Sites, branding visionário, inteligência artificial e performance para negócios com propósito.")},
    "sites": {"title": "Sites e presença digital", "path": "sites-presenca-digital",
              "seo": ("Sites e presença digital | Agência Exemplo", "Criação de sites estratégicos para negócios com propósito: alta conversão, autonomia, SEO e AEO.")},
    "branding": {"title": "Branding visionário", "path": "branding-visionario",
                 "seo": ("Branding visionário | Agência Exemplo", "Brand manager, consultoria, reposicionamento, identidade e design de marca para negócios com propósito.")},
    "projetos": {"title": "Projetos", "path": "projetos",
                 "seo": ("Projetos | Agência Exemplo", "Sites e marcas criados pela Agência Exemplo para terapeutas, artistas e negócios com propósito.")},
    "segmentos": {"title": "Segmentos", "path": "segmentos",
                  "seo": ("Segmentos | Agência Exemplo", "Marketing digital, sites e branding para instrutores de yoga, terapeutas, astrólogos, DJs e outros negócios com propósito.")},
    "segmento": {"title": "Segmento", "path": "segmento", "collection": "Segmentos",
                 "seo": ("Segmento | Agência Exemplo", "Marketing digital com propósito para o seu segmento.")},
    "sobre": {"title": "Sobre", "path": "sobre", "template": "about",
              "seo": ("Sobre | Agência Exemplo", "Conheça a Agência Exemplo, agência de marketing com propósito dedicada a artistas, terapeutas e negócios de impacto.")},
    "contato": {"title": "Contato", "path": "contato", "template": "contact",
                "seo": ("Contato | Agência Exemplo", "Fale com a Agência Exemplo pelo WhatsApp, Instagram ou formulário e conte sobre o seu projeto de site, branding ou marketing.")},
}
# Ordem do menu (subitens entre parênteses são filhos de Serviços). Home e a página dinâmica ficam ocultas.
NAV = [("servicos", []), ("projetos", []), ("segmentos", []), ("sobre", []), ("contato", [])]
# Sites e Branding ficam fora do menu (sem submenu em Serviços), mas as páginas continuam no ar.
HIDDEN = ["home", "segmento", "sites", "branding"]


def uuids():
    return json.loads(PAGES_FILE.read_text()) if PAGES_FILE.exists() else {}


def _list_pages():
    res = lib.call("GET", f"/sites/multiscreen/{lib.SITE}/pages")
    return res.get("results", res) if isinstance(res, dict) else res


def setup():
    ids = uuids()
    current = {pg["path"]: pg["uuid"] for pg in _list_pages()}
    template_paths = {"home": "home", "services": "services", "about": "about", "contact": "contact"}

    for key, cfg in PAGES.items():
        seo_title, seo_desc = cfg["seo"]
        seo = {"title": seo_title, "description": seo_desc, "no_index": False, "og_image": lib.img("/images/cristais.webp")}
        uuid = ids.get(key) or current.get(cfg["path"]) or current.get(template_paths.get(cfg.get("template"), "∅"))
        if uuid:
            body = {"title": cfg["title"], "seo": seo, "draft_status": "STAGED_DRAFT"}
            if key != "home":
                body["path"] = cfg["path"]
            lib.call("PUT", f"/sites/multiscreen/{lib.SITE}/pages/{uuid}", body)
            print("página atualizada:", key, uuid)
        else:
            args = {"site_name": lib.SITE, "page_title": cfg["title"], "page_path": cfg["path"],
                    "seo": seo, "draft_status": "STAGED_DRAFT"}
            if cfg.get("collection"):
                args["collection_name"] = cfg["collection"]
            text = lib.mcp("create_page", args)
            uuid = json.loads(text[: text.rfind("}") + 1])["uuid"]
            print("página criada:", key, uuid)
        ids[key] = uuid
        PAGES_FILE.write_text(json.dumps(ids, indent=1))
    navigation()


def navigation():
    res = lib.call("GET", f"/sites/multiscreen/{lib.SITE}/navigation")["results"][0]
    lang, items = res["lang"], res["navigation"]
    flat = items + [c for it in items for c in it.get("sub_navigation") or []]
    by_url = {it["url"]: it["id"] for it in flat}

    def item_id(key):
        path = PAGES[key]["path"]
        return by_url.get("/" if key == "home" else f"/{path}")

    def patch(nid, body):
        lib.call("PATCH", f"/sites/multiscreen/{lib.SITE}/navigation/{lang}/items/{nid}", body)

    # Ordem de trás para frente: cada item aponta para o próximo que já está no lugar.
    order = [k for k, _ in NAV]
    for i in range(len(order) - 1, -1, -1):
        key, children = NAV[i]
        nid = item_id(key)
        if not nid:
            print("sem item de menu para", key)
            continue
        body = {"title": PAGES[key]["title"], "hidden": [], "parent_id": ""}
        body["next_sibling_id"] = item_id(order[i + 1]) if i + 1 < len(order) else ""
        patch(nid, body)
        for j in range(len(children) - 1, -1, -1):
            cid = item_id(children[j])
            if cid:
                nxt = item_id(children[j + 1]) if j + 1 < len(children) else ""
                patch(cid, {"title": PAGES[children[j]]["title"], "parent_id": nid, "next_sibling_id": nxt or "", "hidden": []})
    for key in HIDDEN:
        nid = item_id(key)
        if nid:
            patch(nid, {"hidden": ["DESKTOP", "TABLET", "MOBILE"], "parent_id": "", "next_sibling_id": ""})
    print("menu organizado")


# ---------- conteúdo ----------

def _base(key):
    return f"{lib.V2}/pages/{uuids()[key]}/elements"


def build_content(names):
    for key in names:
        mod = importlib.import_module(f"page_{key}")
        base = _base(key)
        for el in lib.call("GET", base)["results"]:
            lib.call("DELETE", f"{base}/{el['element_id']}")
        for sec in mod.sections():
            anchor = sec.get("_anchor")
            res = lib.call("POST", base, lib.strip_private(sec))
            if anchor:
                lib.call("POST", f"{base}/{res['element_id']}/anchor", {"anchor_id": anchor, "create_navigation_item": False})
        print("conteúdo montado:", key)
    push_head(names)


def push_head(names=None):
    html = lib.head_html()
    for key in names or uuids():
        lib.call("PUT", f"/sites/multiscreen/{lib.SITE}/pages/{uuids()[key]}", {"header_html": html})
    print("head atualizado:", ", ".join(names or uuids()))
