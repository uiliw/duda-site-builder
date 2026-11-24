---
name: duda-site-builder
description: "Metodologia para criar, refazer ou MODIFICAR sites na Duda: protótipo aprovado em Next.js (Tailwind, lucide, GSAP opcional) e site Duda via Partner API + MCP, com widgets nativos editáveis, tema, coleções, header/footer globais, SEO e movimento — sempre com as skills frontend-design, ui-ux-pro-max e impeccable. CARREGUE ANTES de qualquer pedido que mude algo que aparece num site Duda, mesmo sem a palavra Duda: página, seção, botão, texto, estilo/CSS/JS do site (styles.css, site*.js, mod/*.js, head), coleção, galeria, menu, header/footer, página dinâmica, SEO, publicar, ou dados/views que alimentam o site (ex.: Projeto A, pasta duda/, nativo.sql/schema.sql das views duda_*, coleções externas do Supabase). Também ao configurar tema/coleções/menu, comparar protótipo × site, ou corrigir algo visto no preview/publicado (duda.co, dudamobile, <editor-host>, alias de site)."
---

# Sites na Duda: protótipo → site nativo editável

Fluxo validado em projetos reais da Ohmline (nomes de clientes trocados por "Projeto A, B..." nas referências). `kit/` nesta skill é a cópia de um builder completo em funcionamento, para servir de ponto de partida (os dados de contato do kit são de exemplo).

**Antes de tudo (obrigatório):** as skills `frontend-design`, `ui-ux-pro-max` e `impeccable` precisam estar instaladas (o plugin as declara como dependências e o hook de início de sessão avisa se faltar alguma). Se alguma não estiver disponível, **pare** e peça ao dev para instalar (ver README do plugin) — não siga sem elas. Credenciais da Duda: `~/.config/duda/credentials.env` (uma vez por máquina) ou `.env` do projeto; rode `bash scripts/check-setup.sh` (na pasta desta skill) se algo falhar.

Leia antes de começar:
- `references/gotchas.md` — armadilhas da Duda (CSS, DOM, galerias, API). **Obrigatório** antes de escrever CSS/JS ou chamar a API.
- `references/api.md` — endpoints REST e ferramentas MCP.

## Princípios (combinados com o cliente)

1. **Nativo primeiro — PRIORIDADE MÁXIMA** (cliente, 2026-10-22: "qualquer ajuste como estilo, alinhamento, espaçamento, tamanho etc que são configuráveis no widget deve ser permitido configurar no widget e não forçado com CSS customizado"). Vale acima de fidelidade ao protótipo e de conveniência do builder. Sempre usar widgets e recursos da Duda (galerias ligadas a coleções, acordeão, formulário, menu, tema).
   - **Tudo que o editor configura vai na propriedade nativa do widget**: cor, fundo e **degradê** (`background.gradient`), fonte, tamanho por tela, alinhamento, espaçamento (padding/margin por breakpoint), largura/altura, cantos, borda, legendas de galeria (`caption.title/description` + `breakpoint_overrides.<bp>.caption.*_font_size`), menu (`all_pages.link_text`, `link_style.spacing`, `selected_page_and_hover`), colunas por tela (largura no tablet/celular), animação de entrada e **ligada à rolagem** (`style.animation`, `trigger: "viewport"`). Nunca `!important` no CSS sobre essas propriedades: o cliente mexe no editor e "não muda nada" (casos reais: degradê dos pilares, largura de parágrafo, coluna do logo com `width: auto !important`, `min-height` do header).
   - **Nunca `max_width` em px escondido**: o controle de largura do editor só mexe no `width`. Grave `width: <px>` + `max_width: 100%` (o `kit/lib.para` já faz).
   - **Valor nativo = valor da tela.** Se o CSS sobrescreve o nativo, o editor mostra um número e a página outro. Ao migrar, grave no widget o que aparece hoje (atenção a somas: padding nativo + padding do CSS em outro nó).
   - **CSS só para o que o editor não oferece**: estrutura/layout especial (galeria virando roda ou lista, header dividido), efeitos (céu, SVG), movimento sem equivalente nativo, entrelinha de legenda, hover de link de texto. Quando o CSS precisa ficar ajustável por widget, ele vai no **"Edit CSS" do widget** (`#<id>[data-css-edit] { … }`): a API não grava ali (ver gotchas), então gere um arquivo pronto para o usuário colar e só então tire do CSS geral.
   - **Antes de entregar**, audite o `styles.css`: nenhuma regra com `!important` em fonte/tamanho/cor/alinhamento/margem/padding/largura/fundo de widget que o editor configura (script de auditoria em `kit/nativo.py`, docstring). Comparar capturas antes/depois (movimento reduzido) a cada migração.
   **Evite o widget HTML** sempre que houver widget nativo que resolva (botão, parágrafo, imagem, galeria, ícone, formulário): o cliente edita no editor e o conteúdo sai no HTML do servidor. Widget HTML só para o que não existe nativo.
2. **Tema centraliza a identidade.** Paleta em `color_1..N` do tema; widgets usam `var(--color_N)`. h1–h6, parágrafo, botões primário/secundário e espaçamento de seções no tema.
   **Fonte personalizada (fora da lista da Duda) é ENVIADA pelo usuário no editor (Tema › Fontes), NUNCA forçada pelo CSS** (pedido do usuário, 2026-11-10, reforçado no Projeto C: "preciso enviar, não forçar no css"): nem `@font-face` embutido como ponte, nem woff2 no CDN citado pelo styles.css. Gere os arquivos (uma instância estática por peso/largura/itálico usado, subconjunto latino, `fontes_tema.py`), entregue a pasta ao usuário e **peça o envio antes de montar/publicar**; o tema e os widgets citam os nomes registrados (cada arquivo = família de peso 400). Não publique enquanto as fontes não estiverem no tema (o site cairia na fonte reserva). Ver gotchas (Projeto B 2026-11-09, Projeto A 2026-11-10, Projeto C 2026-11-10).
3. **Conteúdo tem uma fonte só.** Os textos vivem no protótipo (`src/lib/*.ts`) e o builder lê de lá (`node --experimental-strip-types`). Itens repetidos (portfólio, segmentos) viram **coleções** com página dinâmica.
4. **Nunca publicar** o site, nem mexer em site de produção, tema, header ou footer globais de outro site sem pedido explícito. Construir num **site novo (alias próprio)**; o cliente republica.
5. **Segredos só em `~/.config/duda/credentials.env` ou no `.env` do projeto** (gitignored): `DUDA_TOKEN` (MCP), `DUDA_API_USER`, `DUDA_API_PASS`. Nunca imprimir, nunca commitar, nunca colar em issue/PR/chat.
5b. **Textos literais.** Em redesign, todo texto visível vem literal do site atual (qualquer página) ou de material oficial do cliente. Pode **mover** texto (ex.: frase de página interna vira CTA na home); **não pode criar, reescrever nem "melhorar"**. No levantamento, extraia o inventário literal de todas as páginas e comente a fonte de cada texto no arquivo de conteúdo. Exceção: o próprio cliente pede texto novo — aí reescreva marcando `// RASCUNHO`, e resultados/depoimentos só na voz literal dos depoimentos reais.
5c. **Fontes da marca ficam.** Se o site atual usa fontes do manual de identidade (MIV), o redesign mantém as famílias (extraia família e pesos do CSS/font-face); o conceito exclusivo vem de cor, composição, motivo e movimento.
6. **Cada site é exclusivo.** A metodologia (protótipo → Duda nativa, conteúdo em `src/lib`, builder) se repete; o **design e a estrutura não**. Nada de copiar componentes, seções, header, footer, chamada final, tipografia ou padrões de interação de um site anterior (ex.: Agência Exemplo). Parta do conteúdo e do universo do cliente para inventar um conceito próprio, inovador e impactante: estrutura de páginas, navegação, tipografia, motivo visual, botões e animações pensados para aquele conteúdo. Reaproveite só infraestrutura invisível (registro do GSAP, scroll suave, `NavLink`, builder).
7. **Movimento: GSAP não é obrigatório — surpreenda sempre.** Escolha a ferramenta pelo efeito: recursos nativos da Duda (animações de entrada e de rolagem dos widgets, parallax de fundo, hover, efeitos de seção, editáveis pelo cliente no editor), CSS puro (`@keyframes`, `animation-timeline: view()/scroll()` com `@supports`, transições, SVG animado), e GSAP só quando o efeito exigir (pin, scrub coordenado, SplitText). Nativo e CSS pesam menos (PageSpeed) e o cliente consegue editar. Cada site precisa de pelo menos um momento de movimento memorável e inédito, nascido do universo do cliente — nunca repetir o repertório de sites anteriores.
7b. **Slide, nunca rolagem horizontal** (pedido do usuário, 2026-10-07): itens lado a lado (depoimentos, linha do tempo, cartões) ficam num slide com setas ≥ 44 px, pontos (ou contador "3 de 11" quando há muitas posições), arrastar no toque e teclado, sem troca automática (só com pedido explícito, e então com botão de pausa: ver gotchas, Projeto A 2026-10-23). Nada de trilha com `overflow-x`/scroll-snap. Na Duda: slider nativo de conteúdo.
8. **Sempre junto com as skills `frontend-design`, `ui-ux-pro-max` e `impeccable`.** Papéis diferentes: `frontend-design` dá o conceito e a direção estética exclusiva (paleta, tipografia, composição, o momento memorável); `ui-ux-pro-max` garante a qualidade de UX (acessibilidade e contraste, toque ≥ 44 px, navegação, responsivo, formulários, desempenho/CLS, movimento reduzido) e fornece o checklist de entrega (`references/pro-rules.md`); `impeccable` dá o vocabulário de refino e crítica (`/impeccable critique`, `audit`, `polish`, `bolder`) e o detector de "AI slop" (`npx impeccable detect`). Carregue as três no início do protótipo; antes de mostrar cada página ao usuário, rode o checklist do `ui-ux-pro-max` e uma passada `impeccable` (critique/audit + detect na URL local) e corrija o que aparecer. Paletas, estilos e pares de fontes prontos do `ui-ux-pro-max` são consulta, nunca molde: o design continua nascendo do universo do cliente (princípio 6).
9. **URLs: preservar o SEO.** Ao refazer um site publicado, cada página, post do blog e item de coleção mantém **exatamente a mesma URL** do site atual (levante todas antes: menu, `list_pages`, `list_blog_posts`, sitemap.xml, coleções). Use os mesmos caminhos já no protótipo (rotas do Next = paths da Duda) e defina os slugs das coleções (`page_item_url`) iguais aos antigos. Só mude uma URL com motivo forte e, nesse caso, crie o 301 (`create_url_rule`) da antiga para a nova. Em **site novo do zero** (sem URLs indexadas), recomende e use a melhor URL a partir do título: curta, em minúsculas, sem acentos nem stopwords desnecessárias, com a palavra-chave principal (ex.: "Musicoterapia para pessoas autistas" → `/musicoterapia-autismo`).
10. **Trilha (breadcrumb) sempre nativa** (pedido do usuário): ele insere o widget numa página pelo editor; o builder duplica essa página para as outras e move o widget ao remontar (ver gotchas). Subpáginas ficam aninhadas (ocultas) no menu para a trilha mostrar a hierarquia.
11. **Ações destrutivas:** remontar conteúdo (`--content`), header ou footer apaga edições feitas no editor. Prefira edições pontuais (GET → alterar → PUT completo) quando só um texto/estilo muda; ao remontar, avise o usuário no resumo.

## Equipe de agentes (pedido do usuário, 2026-10-03)

Em site novo ou redesenho grande, divida o protótipo entre subagentes (Agent tool, em paralelo, em segundo plano), com você como **diretor de arte/integrador**:
1. Escreva antes um `BRIEF.md` na raiz do projeto (posicionamento, público, conceito, tom, tokens, rotas, fatos reais, onde está o conteúdo antigo) e um `src/lib/types.ts` com o formato dos dados. Os agentes leem os dois; isso mantém tudo coerente.
2. **Redator + SEO/AEO** → escreve só `src/lib/content.ts` (tipado), marca `// RASCUNHO` no que o cliente precisa confirmar, sem números inventados.
3. **Identidade visual** → logo/símbolo em SVG (`public/brand/`), `Logo.tsx`, favicon; confere renderizando PNG em 512 e 32 px.
4. **Você** → design/estrutura e componentes contra os tipos, em paralelo; integra quando os agentes terminam.
5. **Auditor UX/a11y** (depois de pronto) → `ux-audit.py`, capturas 1440/390, contraste, foco, movimento reduzido; devolve lista priorizada, você corrige.
Cada agente recebe arquivos exclusivos (nunca dois no mesmo arquivo) e responde com resumo curto. Workflow (orquestração grande) só se o usuário pedir.

## Fases

### 1. Protótipo em Next.js (aprovação)
- Next.js App Router + Tailwind v4 + lucide; GSAP (`@gsap/react`, ScrollTrigger, SplitText) só se o movimento pedir (princípio 7). Carregue as skills `frontend-design`, `ui-ux-pro-max` e `impeccable` antes de desenhar e passe o checklist do `ui-ux-pro-max` + a passada `impeccable` antes de mostrar (princípio 8). No protótipo, anote em cada animação se vira **nativo da Duda**, **CSS** ou **GSAP** na migração.
- **Comece do zero no design** (princípio 6): levante o conteúdo do site antigo, defina um conceito exclusivo derivado do tema do cliente (ex.: astrologia → roda do zodíaco, fases da lua, dados de nascimento) e só então desenhe as seções. Antes de mostrar, compare com os sites já feitos: se lembrar algum (layout do header, lista com foto seguindo o cursor, título grande + texto ao lado, chamada final pinada, botões pílula), refaça.
- Estruture o conteúdo em `src/lib/*.ts` (exportações simples: arrays/objetos) — é o que o builder vai ler.
- Antes de mostrar cada página: `python3 scripts/ux-audit.py http://localhost:<porta>/<página>` (toque ≥ 44 px, sem rolagem horizontal no celular, alt, texto ≥ 12 px) + capturas em 1440 e 390 px.
- Cada seção = um componente; anote no `CLAUDE.md` do projeto regras e armadilhas de GSAP.
- Só migrar depois da aprovação do usuário, página por página.

### 2. Preparar a Duda
- `.mcp.json` → `scripts/duda-mcp.sh` (copie de `scripts/`), lendo `DUDA_TOKEN` do `.env`.
- Peça o **alias do site novo** (criado pelo usuário a partir de um template). As credenciais da Partner API já estão em `~/.config/duda/credentials.env` (ou no `.env`); se faltar, peça ao dev master — nunca peça para colar no chat.
- `get_site_details` (MCP) dá o `preview_membership_auth` para o preview: salve num arquivo fora do repositório.
- **FONTES — PASSO OBRIGATÓRIO, ANTES DE MONTAR** (falha repetida no Projeto K, 2026-11-24: Plus Jakarta Sans ficou de fora e o usuário teve de cobrar "cadê as fontes"). Para **cada** família do protótipo, confira se está na lista nativa da Duda (no preview, `document.fonts.check('16px "<Nome>"')` com a fonte citada num widget, ou ver se cai na reserva). Toda família que **não** estiver: copie `kit/fontes_tema.py` para `duda/site/`, ajuste `ORIGEM`/`FACES` (uma instância estática por peso/itálico realmente usado: confira `font-semibold`, `font-bold`, `<strong>`, `<em>` no protótipo), rode, e **entregue já no início** o caminho absoluto de `duda/site/fontes-tema/` com a lista de `.ttf` para o usuário enviar em Tema › Fontes. Nunca apague o gerador nem a pasta porque "uma das fontes é nativa": trate família por família. "Adicione a fonte no editor" sem entregar os arquivos **não serve**. Depois do envio, troque o nome no tema e nos widgets pelos nomes registrados (`PlusJakartaSans-SemiBold` etc., cada arquivo = família de peso 400) e confira no preview.

### 2b. Importar o conteúdo do CRM (quando houver)
Quando o cliente (ou o lead) preencheu o que o site precisa na aba **Conteúdos** do CRM, importe em vez de pedir de novo ou copiar e colar. Cabe ao passo 2 antes e ao 3 depois; nada aqui publica.
0. **Quem acessa o CRM é só o dev master.** Os demais devs não têm acesso ao servidor do CRM: recebem do dev master a pasta `crm-import/conteudos-<negócio>-<AAAAMMDD>/` (por canal privado, nunca num repositório público) e seguem do passo 2. Sem a pasta, partem do site atual + `BRIEF.md`.
1. (Dev master) No repositório do CRM: `bash scripts/servidor/conteudos-exportar.sh <lead|cliente> <id|nome> ./crm-import [--so-aprovados]` (ssh no servidor do CRM; nome com mais de um resultado mostra os ids e termina: rode de novo com o id). Sem `--so-aprovados` vem tudo, cada grupo com o status; use a flag quando só o aprovado pela equipe puder entrar. Cria `crm-import/conteudos-<negócio>-<AAAAMMDD>/`. Antes do deploy da fase, rode local: `npx tsx scripts/conteudos-exportar.ts <lead|cliente> <id|nome> --saida ./crm-import`. A pasta tem dados pessoais do cliente: mantenha fora do git e apague ao terminar.
2. `BRIEF.md` da pasta é o ponto de partida do `BRIEF.md` do projeto (negócio, contato, redes, público, tom de voz, cores e referências, sites que gosta, domínio e lista dos conteúdos). O diretor de arte acrescenta conceito, tokens e rotas. Campo "(não informado)" não se inventa: pergunte ou deixe `// RASCUNHO`.
3. `conteudo.json` (manifesto, `versao` 1) e `grupos/*.md` são a matéria-prima do **redator**, que escreve `src/lib/content.ts`: usa o texto do cliente, marca `// RASCUNHO` no que ele precisa confirmar (todo grupo que não está `aprovado` traz o aviso no topo) e **não inventa fatos**. O `destinoDuda` de cada grupo diz onde o CRM mandaria o texto na Biblioteca de Conteúdo.
4. `arquivos/` vai para `public/images/crm/` do protótipo (nomes `NN-grupo-MM.ext`; o logo é `briefing-logo.ext`). O `alt` de cada imagem está no manifesto.
5. **As imagens já estão no site Duda de destino** (o CRM as enviou ao site do projeto): mescle `assets.seed.json` (chave `/images/crm/<arquivo>` → URL do CDN) em `duda/site/assets.json`, pule o envio dessas imagens no `build.py --assets` e use `SITE = "<site.alias do manifesto>"` em `lib.py`. Imagem com `cdnUrl: null` não está no site: suba normalmente.
6. **AVISO — não sobrescreva a Biblioteca de Conteúdo.** Se o manifesto tem `ultimoEnvioDuda` (o CRM já enviou textos, telefones, e-mails e imagens ao site), o `kit/settings.py` **não pode** rodar `update_content_library` com valores fixos: `phones` e `emails` são substituídos por inteiro e `site_texts` mesclam por campo, então o que o CRM enviou (e o que a equipe editou na Duda) se perde. Faça `GET` da biblioteca e mescle, ou tire essa chamada para esse site.
7. Nada é publicado. Armadilhas desse caminho em `references/gotchas.md` ("Conteúdo vindo do CRM").

### 3. Builder (`duda/site/`, a partir de `kit/`)
Copie `kit/` para `duda/site/` e adapte:
- `lib.py`: `SITE`, `content()` (quais arquivos `src/lib/*.ts` ler), `FONTS`, constantes de paleta, helpers (`section/column/inner/para/image/button/icon/accordion/gallery/bound_para`, `rte/p/lead/bullets` no formato do editor), `call()` com retentativa.
- `theme.py` (tema), `settings.py` (idioma, favicon, SEO do site, biblioteca de conteúdo), `collections_.py` (coleções, linhas, slugs), `pages.py` (páginas, SEO, menu, montagem, head), `chrome.py` (header/footer globais), `blocks.py` (seções reutilizáveis), `page_<chave>.py` (seções de cada página), `styles.css` + `motion.js` + `head.html` (CSS/JS injetados em base64).
- `build.py` flags: `--theme --assets --collections --settings --pages --header --footer --content <páginas> --head`. `--head` é seguro (só CSS/JS); `--content/--header/--footer` apagam e recriam.
- Imagens: `image-sources.json` (chave local → URL pública de origem) e `assets.json` (chave → URL no CDN do site novo). **Confira visualmente** o mapa depois do upload (houve troca de fotos no Agência Exemplo).

Ordem num site novo: `--theme --assets --collections --settings --pages --header --footer --content <todas> --head`.

### 4. Verificar sempre no preview
- `scripts/shot.py` (Playwright): captura seções em 1440 e 390 px e roda JS de inspeção (medidas, estilos computados, DOM). Use antes de corrigir (entender a causa) e depois (provar a correção).
- Compare com o protótipo local lado a lado (capture as duas e junte com PIL) quando o pedido for "igual ao protótipo".
- Cheque desktop **e** celular, hover/clique quando houver interação (filtro, acordeão, menu).

### 5. Ciclos de ajuste
Para cada item pedido: reproduza no preview → ache a causa no DOM/estilo computado → corrija no lugar certo (propriedade nativa > tema > CSS estrutural) → aplique pelo builder → verifique com captura → registre armadilha nova em `references/gotchas.md` desta skill e no `CLAUDE.md` do projeto.

**Tudo que aprender sobre a Duda volta para esta skill na mesma hora** (pedido do usuário): armadilha em `references/gotchas.md`, endpoint/formato em `references/api.md`, helper reutilizável no `kit/`. Inclui correções de algo que esta skill dizia errado.


### Entrega ao dev master (trabalho em equipe)
Cada projeto de cliente vive num **repositório Git privado** (um por cliente, criado/compartilhado pelo dev master). O dev:
1. Trabalha no repositório do projeto: protótipo Next.js, `BRIEF.md`, `src/lib/*.ts` (conteúdo), `duda/site/` (builder, `assets.json`, `image-sources.json`), relatórios.
2. **Nunca commita** `.env`, `crm-import/`, arquivos de preview auth nem respostas de formulário (confira o `.gitignore` antes do primeiro commit).
3. Monta o site Duda **só no alias de trabalho** indicado pelo dev master; **não publica** nem mexe em site de produção (princípio 4).
4. Ao terminar cada fase, faz push numa branch e abre PR com: o que mudou, alias usado, comandos do builder rodados (`build.py --...`), pendências (`// RASCUNHO`, fontes a enviar em Tema › Fontes, imagens com `cdnUrl: null`).
5. O dev master baixa a versão, revisa, envia o que for preciso ao CRM e à Duda e publica.
Aprendizado novo sobre a Duda entra no PR **deste plugin** (`references/gotchas.md`, `references/api.md`, `kit/`), sem nome de cliente, ID de site nem dados pessoais (use "Projeto X" e `<site>`).

### 6. SEO e AEO (depois do trabalho, obrigatório)
Quando o site estiver montado na Duda (e antes de o cliente republicar), rode uma análise completa de **SEO** e de **AEO** (Answer Engine Optimization: aparecer como resposta em Google AI Overviews, ChatGPT, Perplexity, Gemini e Copilot) e entregue um relatório com correções priorizadas. Use as skills de SEO instaladas:
- `seo-audit` no preview/domínio: rastreamento, indexação, saúde geral (delegação para especialistas).
- `seo-technical`: robots.txt, sitemap (`seo-sitemap`), canônicas, redirecionamentos 301 das URLs antigas (manter slugs ou criar regras com `create_url_rule` no MCP), HTTPS, Core Web Vitals (`seo-google` / PageSpeed, celular).
- `seo-page` nas páginas principais: título, meta description, H1 único, hierarquia de títulos, alt das imagens (`seo-images`), links internos.
- `seo-content`: E-E-A-T (autor real, credenciais, experiência, local), conteúdo raso, legibilidade.
- `seo-schema`: JSON-LD adequado ao negócio (`LocalBusiness`/`ProfessionalService`, `Person`, `Service`, `FAQPage`, `BreadcrumbList`, `Article` no blog), injetado pelo head/SEO de página da Duda.
- `seo-local` quando houver atendimento presencial: Perfil da Empresa no Google, NAP consistente, página de contato com endereço/região.
- `seo-geo` (AEO/GEO): acesso de crawlers de IA no robots.txt, `llms.txt`, trechos citáveis (respostas curtas e diretas no início das seções, perguntas frequentes reais), sinais de marca/menções, dados estruturados que respondem "quem, o quê, onde, quanto tempo".
- `seo-hreflang` se o site tiver versões em outros idiomas.

Entrega: relatório (Artifact ou arquivo em `duda/site/seo-report.md`) com nota por área, problemas por severidade e correção de cada um; aplicar pela Partner API/MCP o que for seguro (metadados, SEO de página, schema, alt, regras de URL) e listar o que depende do cliente (Perfil da Empresa, conteúdo novo, republicar). Registrar aqui armadilhas novas.

## Padrões que funcionaram
- **Crédito no rodapé de todo site** (pedido do usuário, 2026-11-10): "Dev com ♥ pela Ohmline", com link para https://www.ohmline.com.br/ (nova aba), na linha do copyright; coração na cor de destaque do site. No protótipo e no footer global da Duda (parágrafo nativo; ex.: `lubellafestas.local/duda/site/chrome.py`).
- **Header global** fixo, transparente no topo e com fundo ao rolar (classe via JS), esconde ao descer; entrada em sequência (logo, itens, botão). Menu sem submenus quando pedido: páginas extras ficam ocultas no menu, não apagadas.
- **Footer global** com a chamada final (seção de CTA/"nascer do sol") + rodapé — aparece em todas as páginas.
- **Galerias de coleção** transformadas por CSS (trilha horizontal, lista tipográfica com foto seguindo o cursor, grade com filtro) — sempre com eventos delegados.
- **Página dinâmica** para itens da coleção: parágrafos ligados a campos (`bound_para`), fundo do hero ligado a campo de imagem, perguntas frequentes em HTML num campo TEXT viram acordeão via JS.
- **Nada de listagem/cartão montado por JS.** Com banco externo (Supabase/Postgres), as views devolvem campos com HTML pronto (tags, trilha, relacionados, JSON-LD, imagem já reduzida) e a Duda só exibe: parágrafos e imagens ligados na página dinâmica; galerias ligadas (descrição com HTML do cartão) nas listas. Sai no HTML do servidor (SEO/AEO) e sem CLS. JS só para interação (filtro que esconde itens, mapa, som). Para listagens complexas, proponha um **widget customizado** (Widget Builder, Handlebars no servidor) escrito por nós e colado pelo usuário; a API só o insere. Ver "Nativo em vez de HTML montado por JS" em `references/gotchas.md`.
- **Mudar tamanhos de texto sem remontar** (`kit/fontsizes.py`): percorre páginas/header/footer, troca as classes `size-N t-size-N m-size-N` (e `font-size-*` do span) e o `font_size` nativo dos parágrafos ligados, por mapa (antigo → novo), e faz PUT só do que mudou. Atualize também os mesmos números no builder.
- **Troca pontual** (`lib.trocar`: insere no mesmo lugar com `parent_id`/`next_sibling_id` e apaga o antigo) em páginas que o cliente já editou; remontar só páginas que são 100% do builder (ex.: moldes dinâmicos).
- **Formulário:** reutilize o formulário nativo (cópia JSON do site antigo) e estilize pelas propriedades nativas dos campos.
- **Entrega ao usuário:** resumo curto em português do que mudou, o que foi remontado (edições perdidas), o que não foi possível e por quê, e que nada foi publicado.
