#!/usr/bin/env python3
"""
Monta o site Duda novo (alias <site>) a partir do projeto Next.

  python3 duda/site/build.py --theme          # paleta, tipografia, botões, espaçamentos, fundo
  python3 duda/site/build.py --assets         # envia as imagens para a biblioteca do site (assets.json)
  python3 duda/site/build.py --collections    # coleções (projetos, Segmentos)
  python3 duda/site/build.py --pages          # cria/renomeia páginas, navegação e SEO
  python3 duda/site/build.py --settings       # SEO do site, favicon, dados do negócio
  python3 duda/site/build.py --header --footer
  python3 duda/site/build.py --content home servicos ...   # APAGA e recria as seções dessas páginas
  python3 duda/site/build.py --head           # atualiza só CSS/JS em todas as páginas (seguro)

--content e --header/--footer desfazem edições feitas no editor nessas áreas: use só com pedido explícito.
"""
import json
import sys

import lib


def upload_assets():
    sources = json.loads((lib.ROOT / "image-sources.json").read_text())
    done = lib.assets()
    todo = {k: v for k, v in sources.items() if k not in done}
    for i in range(0, len(todo), 10):
        batch = list(todo.items())[i:i + 10]
        body = [{"resource_type": "IMAGE", "src": src, "folder": "site"} for _, src in batch]
        res = lib.call("POST", f"/sites/multiscreen/resources/{lib.SITE}/upload", body)
        by_src = {r["original_url"]: r for r in res["uploaded_resources"]}
        for key, src in batch:
            r = by_src.get(src)
            if r and r.get("status") == "UPLOADED":
                done[key] = r["new_url"]
            else:
                print("falhou:", key, r)
        lib.ASSETS_FILE.write_text(json.dumps(done, indent=1))
    print("imagens no site:", len(done), "de", len(sources))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if "--theme" in args:
        import theme
        theme.apply()
    if "--assets" in args:
        upload_assets()
    if "--collections" in args:
        import collections_ as col
        col.apply()
    if "--settings" in args:
        import settings
        settings.apply()
    if "--pages" in args:
        import pages
        pages.setup()
    if "--header" in args or "--footer" in args:
        import chrome
        if "--header" in args:
            chrome.header()
        if "--footer" in args:
            chrome.footer()
    if "--content" in args:
        import pages
        names = [a for a in args[args.index("--content") + 1:] if not a.startswith("--")]
        pages.build_content(names)
    if "--head" in args:
        import pages
        pages.push_head()


if __name__ == "__main__":
    main()
