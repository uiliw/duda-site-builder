# Duda: API e MCP usados pelo kit

Base REST: `https://api.duda.co/api` · Basic auth `DUDA_API_USER:DUDA_API_PASS` (do `.env`).
`V2 = /sites/multiscreen/v2/{SITE}`.

## Conteúdo (Page Elements v2)
| Ação | Método e caminho |
|---|---|
| Listar elementos da página | `GET {V2}/pages/{page_uuid}/elements` |
| Criar seção | `POST {V2}/pages/{page_uuid}/elements` (árvore SECTION > COLUMN > widgets) |
| Âncora numa seção | `POST {V2}/pages/{page_uuid}/elements/{id}/anchor` `{anchor_id, create_navigation_item:false}` |
| Apagar elemento | `DELETE {V2}/pages/{page_uuid}/elements/{id}` |
| Header/footer globais | `GET/POST {V2}/header/elements`, `{V2}/footer/elements`; `PUT/DELETE .../{id}` |
| Atualizar elemento | `PUT {V2}/{area}/elements/{id}` com `{element_type, props:{data, style}, custom_class_names}` completos |

Inserir num lugar exato: `POST {V2}/pages/{uuid}/elements` com `parent_id` + `next_sibling_id` (antes do irmão).
Mover (inclusive widget UNKNOWN, ex.: trilha nativa): `POST {V2}/pages/{uuid}/elements/{id}/move` `{parent_id, next_sibling_id}`.
Duplicar página (copia widgets que a API não cria): `POST /sites/multiscreen/{SITE}/pages/{uuid}/duplicate` `{title, path, seo}`.

Tipos usados: SECTION, COLUMN, INNER_COLUMN (grupo), PARAGRAPH, IMAGE, BUTTON, ICON, ACCORDION, PHOTO_GALLERY, NAVIGATION, SOCIAL_ICONS, FORM_ELEMENT (FORM_STEP, TEXT_INPUT, CHOICE, FORM_BUTTONS_CONTAINER, FORM_BUTTON), HEADER, HAMBURGER_BUTTON, HAMBURGER_MENU.

Ligação a coleção (`connected_data`):
- Galeria: `{"data": {"images": {"source": "COLLECTION", "collection": nome, "item": {src,alt,title,description,button}, "query": {"filters": [...]}}}}`
- Página dinâmica: `{"data": {"content": {"source": "DYNAMIC_PAGE", "field": campo}}}`; fundo da seção: `{"style": {"background": {"image": {"source": "DYNAMIC_PAGE", "field": campo}}}}`
- Imagem ligada: `{"data": {"src": {"source": "DYNAMIC_PAGE", "field": campo}, "alt": {...}}}`; botão: `{"data": {"link": {...}}}`. VIDEO não aceita.
- Filtros de galeria: só numéricos (`GREATER_OR_EQUAL`, `LESS_OR_EQUAL`); `sort` com vários campos funciona.
- Galeria ligada a lista do item (coleção interna) na página dinâmica: `{"data": {"images": {"source": "DYNAMIC_PAGE", "field": campo, "item": {...COLLECTION_ITEM...}}}}`; campo criado com `{"name", "type": "collection", "inner_collection_fields": [{name,type}]}`.
- Texto do site (biblioteca de conteúdo): `{"data": {"content": {"source": "SITE_TEXT", "field": "about_us"|"overview"|"services"}}}`; dados do negócio: `{"source": "CONTENT_LIBRARY", "field": "business_data.name"}` (só name/logo_url, location_data.*, additional_locations).
- Widget customizado: `CUSTOM_WIDGET` com `props.data = {widget_id, widget_version, widget_config}` (o widget é criado no Widget Builder, não pela API).
- Link para a página dinâmica do item: `{"source": "COLLECTION_ITEM", "field": "dpfield#_<uuid da página dinâmica>"}`

## Site, tema, páginas, navegação
| Ação | Método e caminho |
|---|---|
| Tema (cores, textos, botões, seções) | `GET/PUT /sites/multiscreen/{SITE}/theme` (dá para mandar só uma chave, ex. `{"buttons": {...}}`) |
| Configurações (lang, favicon, SEO do site) | `POST /sites/multiscreen/update/{SITE}` |
| Páginas | `GET /sites/multiscreen/{SITE}/pages`; `PUT /sites/multiscreen/{SITE}/pages/{uuid}` (`title`, `path`, `seo`, `header_html`, `draft_status`) |
| Menu | `GET /sites/multiscreen/{SITE}/navigation`; `PATCH /sites/multiscreen/{SITE}/navigation/{lang}/items/{id}` |
| Imagens | `POST /sites/multiscreen/resources/{SITE}/upload` `[{resource_type:"IMAGE", src:<URL pública>, folder}]` |
| Campos / revalidar coleção | `POST /sites/multiscreen/{SITE}/collection/{nome}/field` `[{name,type}]`; `POST .../collection/{nome}/revalidate` |
| Noindex de página | `PUT /sites/multiscreen/{SITE}/pages/{uuid}` `{"seo": {"no_index": true}}` |
| Biblioteca de conteúdo | `GET/POST /sites/multiscreen/{SITE}/content` (`site_texts`, `business_data`, `location_data`) |
| Linhas de coleção | `PUT /sites/multiscreen/{SITE}/collection/{nome}/row` `[{id, page_item_url, data}]` |

## MCP (https://mcp.duda.co/mcp, header Authorization: DUDA_TOKEN)
Usado para: `get_site_details` (preview auth), `create_page` (inclusive dinâmica com `collection_name`), `create_collection`, `create_collection_rows`, `get_collections`, `update_content_library` (telefone, endereço, logo, textos do negócio), `list_pages`, `publish_site` (**nunca sem pedido explícito**).
Não faz: upload de arquivo, conteúdo de página (use a REST).
