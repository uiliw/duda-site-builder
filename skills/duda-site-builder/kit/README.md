# Kit do builder (cópia do projeto Agência Exemplo)

Ponto de partida, não biblioteca: copie para `duda/site/` do novo projeto e adapte.

- Troque `SITE = "<ALIAS>"` em `lib.py`.
- `lib.content()` lê `src/lib/*.ts` do projeto Next — ajuste os módulos e chaves.
- `blocks.py`, `page_*.py`, `styles.css` e `motion.js` são **exemplos do Agência Exemplo** (seções, classes `ov-*`, animações). Reaproveite a estrutura e os padrões; reescreva o desenho do novo cliente.
- `reference/` deve receber o JSON do formulário nativo copiado do site antigo (se houver).
- Arquivos gerados na execução: `assets.json`, `pages.json` (não copie de outro projeto).
- `nativo.py` — leva para as propriedades nativas o que o CSS forçava (lista `CHANGES` por classe; GET → PUT completo, preserva o "Edit CSS" do editor) e `--audit` lista as regras do `styles.css` com `!important` em propriedade editável. Prioridade máxima (SKILL.md, princípio 1).
- `maxwidth.py` — troca `max_width` px escondido por `width` px + `max_width` 100% em todos os widgets já montados.
