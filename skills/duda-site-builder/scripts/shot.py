"""Capturas do preview da Duda para conferir o resultado (Playwright).

Uso:
  python3 shot.py <host> <alias> <auth_file> <path> <largura> "<seletores>" ['<js>']

  host       domínio do editor (ex.: <editor-host> ou www.dudamobile.com)
  alias      alias do site (ex.: <site>)
  auth_file  arquivo com o preview_membership_auth (vem do MCP get_site_details)
  path       caminho da página (home, contato, segmento/<slug>...)
  seletores  lista separada por vírgula; "@800" rola para y=800; vazio = só roda o JS
  js         expressão avaliada na página; o resultado é impresso (medir, inspecionar DOM)

Salva shot_0.png, shot_1.png... no diretório atual.
"""
import asyncio
import sys
import urllib.parse

from playwright.async_api import async_playwright

host, site, auth_file, path, width, sels = sys.argv[1:7]
js = sys.argv[7] if len(sys.argv) > 7 else None
width = int(width)
auth = urllib.parse.quote(open(auth_file).read().strip(), safe="")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": 900 if width > 800 else 844})
        await page.goto(f"https://{host}/site/{site}/{path}?preview=true&preview_membership_auth={auth}",
                        wait_until="networkidle", timeout=120000)
        await page.wait_for_timeout(3000)
        if js:
            print(await page.evaluate(js))
        for i, sel in enumerate(s for s in sels.split(",") if s):
            if sel.startswith("@"):
                await page.evaluate(f"window.scrollTo(0,{sel[1:]})")
            else:
                await page.evaluate(f"(()=>{{const e=document.querySelector('{sel}');window.scrollTo(0,e.getBoundingClientRect().top+scrollY)}})()")
            await page.wait_for_timeout(2500)
            await page.screenshot(path=f"shot_{i}.png")
        await browser.close()


asyncio.run(main())
