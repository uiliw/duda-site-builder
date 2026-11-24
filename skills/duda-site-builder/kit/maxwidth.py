"""Libera a largura dos widgets no editor (pedido do cliente, 2026-10-22: "largura travada" no contato).

O builder gravava width 100% + max_width em px: o controle de largura do editor mexe só no width e o
max_width (que o editor não mostra) continuava limitando. Troca por width = aquele px + max_width 100%:
mesmo resultado na tela, e a largura volta a ser ajustável no widget. GET antes e PUT com props
completos, só dos elementos nessa situação (edições feitas no editor ficam).

  python3 maxwidth.py          # simula
  python3 maxwidth.py --apply  # grava
"""
import re
import sys

import lib
import pages
from fontsizes import walk

APPLY = "--apply" in sys.argv
PX = re.compile(r"^\d+(\.\d+)?px$")


def fix(style):
    size = style.get("size") or {}
    mw, w = size.get("max_width"), size.get("width")
    if not (isinstance(mw, str) and PX.match(mw)):
        return False
    # largura já mudada no editor (ex.: 51.80%): fica a escolha do cliente, só sai o limite escondido
    style["size"] = dict(size, width=mw if w in (None, "", "100%", "auto") else w, max_width="100%")
    return True


def run(area_base, label):
    n = 0
    for e in walk(lib.call("GET", area_base)["results"]):
        props = e.get("props") or {}
        style = props.get("style") or {}
        before = (style.get("size") or {}).get("max_width")
        if not fix(style):
            continue
        n += 1
        print(f"  {label}: {e['element_id']} {e['element_type']} {' '.join(e.get('custom_class_names') or [])} ({before})")
        if APPLY:
            body = {"element_type": e["element_type"], "props": {"data": props.get("data") or {}, "style": style}}
            if e.get("custom_class_names") is not None:
                body["custom_class_names"] = e["custom_class_names"]
            lib.call("PUT", f"{area_base}/{e['element_id']}", body)
    return n


if __name__ == "__main__":
    total = 0
    for key in pages.uuids():
        total += run(pages._base(key), key)
    total += run(f"{lib.V2}/header/elements", "header")
    total += run(f"{lib.V2}/footer/elements", "footer")
    print(("gravados" if APPLY else "a alterar"), total)
