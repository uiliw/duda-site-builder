"""Coleções do site: projetos (portfólio) e Segmentos (página dinâmica /segmento/<item>)."""
import json

import lib

COLLECTIONS = {
    "projetos": [
        {"name": "Nome", "type": "PLAIN_TEXT"},
        # Resumo + lista de entregas: a lista vira as etiquetas abaixo da descrição na galeria.
        {"name": "Resumo", "type": "TEXT"},
        {"name": "Categoria", "type": "MULTI_SELECT", "multi_select_options": ["Terapeutas", "Artistas", "Corporativo"]},
        {"name": "Entregas", "type": "MULTI_SELECT", "multi_select_options": ["Site", "SEO", "Branding", "Estratégia"]},
        {"name": "Imagem", "type": "IMAGE"},
        {"name": "Link", "type": "LINK"},
        {"name": "Destaque", "type": "NUMBER"},
        # Texto simples com a categoria: a galeria só liga campos de texto (usado pelo filtro da página Projetos).
        {"name": "Area", "type": "PLAIN_TEXT"},
    ],
    "Segmentos": [
        {"name": "segmento", "type": "PLAIN_TEXT"},
        {"name": "chamada", "type": "TEXT"},
        {"name": "descricao", "type": "TEXT"},
        {"name": "diferenciais", "type": "TEXT"},
        {"name": "cta_titulo", "type": "PLAIN_TEXT"},
        {"name": "cta_texto", "type": "TEXT"},
        {"name": "imagem", "type": "IMAGE"},
        {"name": "hero", "type": "IMAGE"},
        {"name": "seo_title", "type": "PLAIN_TEXT"},
        {"name": "seo_description", "type": "TEXT"},
        {"name": "perguntas", "type": "TEXT"},
    ],
}


def _html_list(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def _faq_html(faq):
    # Pares pergunta/resposta; o motion.js transforma em acordeão na página.
    return "".join(f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in faq)


def rows():
    c = lib.content()
    projects = [
        {"data": {
            "Nome": pr["name"], "Resumo": f"<p>{pr['summary']}</p>" + _html_list(pr["deliverables"]), "Categoria": [pr["category"]],
            "Entregas": [d for d in pr["deliverables"] if d in ("Site", "SEO", "Branding", "Estratégia")], "Imagem": lib.img(pr["image"]), "Link": pr.get("url", ""), "Destaque": 1 if pr["featured"] else 0, "Area": pr["category"],
        }}
        for pr in sorted(c["projects"]["projects"], key=lambda x: not x["featured"])
    ]
    segments = [
        {"data": {
            "segmento": s["name"], "chamada": f"<p>{s['lead']}</p>", "descricao": f"<p>{s['description']}</p>",
            "diferenciais": _html_list(s["highlights"]), "cta_titulo": s["ctaTitle"], "cta_texto": f"<p>{s['ctaText']}</p>",
            "imagem": lib.img(s["image"]), "hero": lib.img(s["heroImage"]), "seo_title": s["seoTitle"],
            "seo_description": f"<p>{s['seoDescription']}</p>", "perguntas": _faq_html(s["faq"]),
        }}
        for s in c["segments"]["segments"]
    ]
    return {"projetos": projects, "Segmentos": segments}


def set_slugs():
    """Define o endereço de cada item (/segmento/<slug>) a partir do conteúdo do Next."""
    c = lib.content()
    wanted = {
        "Segmentos": ("segmento", {x["name"]: x["slug"] for x in c["segments"]["segments"]}),
        "projetos": ("Nome", {x["name"]: x["slug"] for x in c["projects"]["projects"]}),
    }
    for name, (field, slugs) in wanted.items():
        col = json.loads(lib.mcp("get_collections", {"site_name": lib.SITE, "collection_name": name}))
        col = col[0] if isinstance(col, list) else col
        body = [
            {"id": v["id"], "page_item_url": slugs[v["data"][field]], "data": v["data"]}
            for v in col["values"]
            if slugs.get(v["data"][field]) and v.get("page_item_url") != slugs[v["data"][field]]
        ]
        if body:
            lib.call("PUT", f"/sites/multiscreen/{lib.SITE}/collection/{name}/row", body)
        print("slugs:", name, len(body), "atualizados")


def sync(name="projetos"):
    """Atualiza linhas existentes (pelo nome) e cria as que faltam, a partir do conteúdo do Next."""
    key = {"projetos": "Nome", "Segmentos": "segmento"}[name]
    wanted = {r["data"][key]: r["data"] for r in rows()[name]}
    col = json.loads(lib.mcp("get_collections", {"site_name": lib.SITE, "collection_name": name}))
    col = col[0] if isinstance(col, list) else col
    have = {v["data"][key]: v for v in col["values"]}
    updates = [{"id": v["id"], "page_item_url": v.get("page_item_url"), "data": dict(v["data"], **wanted[n])} for n, v in have.items() if n in wanted]
    if updates:
        lib.call("PUT", f"/sites/multiscreen/{lib.SITE}/collection/{name}/row", updates)
    missing = [{"data": d} for n, d in wanted.items() if n not in have]
    if missing:
        lib.mcp("create_collection_rows", {"site_name": lib.SITE, "collection_name": name, "rows": missing})
    print("sincronizado:", name, len(updates), "atualizados,", len(missing), "novos")
    set_slugs()


def apply():
    existing = json.loads(lib.mcp("get_collections", {"site_name": lib.SITE}) or "[]")
    names = {x["name"] for x in existing} if isinstance(existing, list) else set()
    data = rows()
    for name, fields in COLLECTIONS.items():
        if name in names:
            print("coleção já existe, pulando:", name)
            continue
        lib.mcp("create_collection", {"site_name": lib.SITE, "name": name, "fields": fields, "static_page_bindable": True})
        lib.mcp("create_collection_rows", {"site_name": lib.SITE, "collection_name": name, "rows": data[name]})
        print("coleção criada:", name, len(data[name]), "linhas")
    set_slugs()
