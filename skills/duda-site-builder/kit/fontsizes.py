"""Troca pontual dos tamanhos de título (pedido do cliente, 2026-10-20: fontes grandes demais).

Percorre páginas, header e footer, troca as classes de tamanho inline (size-N t-size-N m-size-N) e os
tamanhos nativos dos parágrafos ligados à coleção, e faz PUT só dos elementos alterados (GET antes,
props completos), sem apagar o que foi editado no editor. Os mesmos valores já estão em blocks.py/page_*.py.

  python3 fontsizes.py          # simula
  python3 fontsizes.py --apply  # grava
"""
import re
import sys

import lib
import pages

# (desktop, tablet, celular) antigo -> novo
MAP = {
    (96, 68, 44): (72, 56, 40),
    (80, 60, 42): (60, 48, 36),
    (72, 56, 36): (56, 46, 34),
    (54, 44, 29): (44, 36, 27),
    (76, 60, 38): (60, 48, 36),
    (38, 32, 26): (32, 28, 24),
    (72, 56, 40): (56, 46, 36),
    (60, 48, 38): (48, 40, 34),
    (48, 40, 34): (40, 36, 30),
    (56, 48, 38): (46, 40, 34),
    (29, 26, 22): (25, 23, 20),
}
BOUND = {(128, 84, 52): (80, 60, 40)}
APPLY = "--apply" in sys.argv


def fix_html(html):
    def block(m):
        old = tuple(int(x) for x in m.groups())
        new = MAP.get(old)
        return m.group(0) if not new else "size-%d t-size-%d m-size-%d" % new
    def span(m):
        old = tuple(int(x) for x in m.groups())
        new = MAP.get(old)
        return m.group(0) if not new else "font-size-%d t-font-size-%d m-font-size-%d" % new
    html = re.sub(r"(?<![-\w])size-(\d+) t-size-(\d+) m-size-(\d+)", block, html)
    return re.sub(r"(?<![-\w])font-size-(\d+) t-font-size-(\d+) m-font-size-(\d+)", span, html)


def fix_bound(style):
    try:
        old = (int(style["text"]["font_size"][:-2]),
               int(style["breakpoint_overrides"]["tablet"]["text"]["font_size"][:-2]),
               int(style["breakpoint_overrides"]["mobile"]["text"]["font_size"][:-2]))
    except (KeyError, TypeError, ValueError):
        return False
    new = BOUND.get(old)
    if not new:
        return False
    style["text"]["font_size"] = f"{new[0]}px"
    style["breakpoint_overrides"]["tablet"]["text"]["font_size"] = f"{new[1]}px"
    style["breakpoint_overrides"]["mobile"]["text"]["font_size"] = f"{new[2]}px"
    return True


def walk(els):
    for e in els:
        yield e
        yield from walk(e.get("children") or [])


def run(area_base, label):
    n = 0
    for e in walk(lib.call("GET", area_base)["results"]):
        if e["element_type"] != "PARAGRAPH":
            continue
        props = e["props"] or {}
        data, style = props.get("data") or {}, props.get("style") or {}
        changed = False
        html = data.get("content")
        if isinstance(html, str):
            new = fix_html(html)
            if new != html:
                data["content"] = new
                changed = True
        if fix_bound(style):
            changed = True
        if not changed:
            continue
        n += 1
        print(f"  {label}: {e['element_id']} {' '.join(e.get('custom_class_names') or [])}")
        if APPLY:
            body = {"element_type": e["element_type"], "props": {"data": data, "style": style}}
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
