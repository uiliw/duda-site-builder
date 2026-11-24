#!/usr/bin/env python3
"""Fontes do TEMA do Projeto K: Plus Jakarta Sans (texto; fonte do site atual) NÃO está na lista da Duda. A Duda registra
CADA ARQUIVO como uma família de peso 400, então cada peso usado vira um arquivo estático com nome PostScript = família.
Hedvig Letters Serif (títulos) já é nativa: não precisa de arquivo.

  python3 duda/site/fontes_tema.py    # gera duda/site/fontes-tema/<Nome>.ttf e .woff2

O usuário envia os .ttf no editor (Tema › Fontes); depois o builder troca 'Plus Jakarta Sans' pelos nomes registrados
(PlusJakartaSans-Regular / -SemiBold / -Bold). Origem: fonte variável do google/fonts (OFL).
"""
import io
import sys
import tempfile
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

PASTA = Path(__file__).resolve().parent / "fontes-tema"
GF = "https://github.com/google/fonts/raw/main/ofl/"
ORIGEM = {"jakarta": GF + "plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf"}
# Português + Latin Extended-A + pontuação tipográfica, €, ™, setas, menos, ♥
UNICODES = ("U+0020-007E,U+00A0-017F,U+0218-021B,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2018-201A,U+201C-201E,U+2022,"
            "U+2026,U+2039-203A,U+20AC,U+2122,U+2190-2193,U+2212,U+2665,U+FE0E")
# nome PostScript (= família na Duda) -> (origem, eixos fixos, família, estilo)
FACES = {
    "PlusJakartaSans-Regular": ("jakarta", {"wght": 400}, "Plus Jakarta Sans", "Regular"),
    "PlusJakartaSans-SemiBold": ("jakarta", {"wght": 600}, "Plus Jakarta Sans", "SemiBold"),  # botões, rótulos, dados
    "PlusJakartaSans-Bold": ("jakarta", {"wght": 700}, "Plus Jakarta Sans", "Bold"),  # <strong>, telefones
}


def _nomes(f, ps, familia, estilo):
    """Família própria por arquivo (é assim que a Duda registra): nome = PostScript, estilo Regular."""
    tab = f["name"]
    completo = f"{familia} {estilo}"
    for nid in (16, 17, 21, 22, 25):
        tab.removeNames(nameID=nid)
    tab.setName(ps, 1, 3, 1, 0x409)
    tab.setName("Regular", 2, 3, 1, 0x409)
    tab.setName(f"{ps};cliente", 3, 3, 1, 0x409)
    tab.setName(completo, 4, 3, 1, 0x409)
    tab.setName(ps, 6, 3, 1, 0x409)
    tab.removeNames(platformID=1)
    f["OS/2"].usWeightClass = 400
    f["OS/2"].fsSelection = (f["OS/2"].fsSelection & ~0b1100001) | 0b1000000  # REGULAR, sem bold/italic
    f["head"].macStyle = 0


def gerar():
    PASTA.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="fontes-gf-"))
    cache = {}
    for ps, (orig, eixos, familia, estilo) in FACES.items():
        if orig not in cache:
            alvo = tmp / f"{orig}.ttf"
            alvo.write_bytes(urllib.request.urlopen(ORIGEM[orig], timeout=120).read())
            cache[orig] = alvo
        f = instancer.instantiateVariableFont(TTFont(cache[orig]), eixos, updateFontNames=False)
        b = io.BytesIO()
        f.save(b)
        b.seek(0)
        f = TTFont(b, lazy=False)  # recarrega: o subsetter falha com tabelas preguiçosas depois do instancer
        o = subset.Options()
        o.layout_features = ["*"]
        o.name_IDs = ["*"]
        o.notdef_outline = True
        s = subset.Subsetter(o)
        s.populate(unicodes=subset.parse_unicodes(UNICODES))
        s.subset(f)
        _nomes(f, ps, familia, estilo)
        f.flavor = None
        f.save(PASTA / f"{ps}.ttf")
        f.flavor = "woff2"
        f.save(PASTA / f"{ps}.woff2")
        print(f"{ps:34} ttf {(PASTA / f'{ps}.ttf').stat().st_size // 1024:3} KB  woff2 {(PASTA / f'{ps}.woff2').stat().st_size // 1024:3} KB")


if __name__ == "__main__":
    gerar() if len(sys.argv) == 1 else print(__doc__)
