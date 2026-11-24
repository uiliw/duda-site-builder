# duda-site-builder

Plugin do Claude Code com a metodologia da Ohmline para **redesign de sites de clientes na Duda**:
protótipo aprovado em Next.js (Tailwind, lucide, GSAP opcional) → site Duda nativo e editável, montado pela
Partner API + MCP da Duda (tema, coleções, header/footer globais, SEO/AEO e movimento).

## 1. Instalar

No Claude Code:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add uiliw/duda-site-builder
/plugin install duda-site-builder@ohmline
```

O primeiro comando só é necessário se o marketplace oficial ainda não estiver adicionado (sem ele,
`frontend-design` não instala e o plugin não carrega — de propósito).

As skills **obrigatórias** vêm como dependências e são instaladas junto:

| Skill | Origem |
|---|---|
| `frontend-design` | `claude-plugins-official` (Anthropic) |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |

Se alguma não instalar sozinha, instale à mão:

```
/plugin install frontend-design@claude-plugins-official
/plugin install ui-ux-pro-max@ohmline
/plugin install impeccable@ohmline
```

Reinicie o Claude Code depois de instalar. A skill não trabalha sem as três.

Ferramentas da máquina: `git`, `python3`, `node`/`npx` e Playwright para as capturas
(`pip install playwright && python3 -m playwright install chromium`).

## 2. Credenciais da Duda

As credenciais são da conta da agência e **não estão neste repositório**. Peça ao dev master pelo
gerenciador de senhas e grave uma vez por máquina:

```bash
mkdir -p ~/.config/duda
curl -fsSL https://raw.githubusercontent.com/uiliw/duda-site-builder/main/.env.example > ~/.config/duda/credentials.env
chmod 600 ~/.config/duda/credentials.env
# edite e preencha DUDA_API_USER, DUDA_API_PASS e DUDA_TOKEN
```

Um `.env` na raiz do projeto do cliente sobrescreve esses valores, se precisar.

Para conferir tudo (skills, ferramentas, credenciais e acesso à API):

```bash
bash ~/.claude/plugins/cache/ohmline/duda-site-builder/*/skills/duda-site-builder/scripts/check-setup.sh --api
```

Ao abrir o Claude Code, um hook avisa se faltar alguma skill ou credencial.

**Regras de segurança:**
- Nunca commite `.env` ou `credentials.env`, nem cole token/senha em chat, issue ou PR.
- Não publique site e não mexa em site de produção. Trabalhe só no alias indicado pelo dev master.
- Quando alguém sai da equipe, o dev master gera credenciais novas no painel da Duda e redistribui.

## 3. Usar

Num projeto de cliente, peça normalmente ("refazer o site do cliente X na Duda", "ajustar o header do site Y").
A skill carrega sozinha. Para chamar direto: `/duda-site-builder:duda-site-builder`.

Fluxo: levantamento do site atual (textos **literais**, fontes da marca) → protótipo Next.js → aprovação →
builder (`duda/site/`, a partir do `kit/`) → verificação no preview → SEO/AEO. Detalhes em
[`skills/duda-site-builder/SKILL.md`](skills/duda-site-builder/SKILL.md).

## 4. Entrega ao dev master

1. Cada cliente tem um **repositório privado** próprio (o dev master cria e convida).
2. O dev trabalha nele (protótipo, `BRIEF.md`, `src/lib`, `duda/site/`), monta no alias de trabalho e **não publica**.
3. Ao fim de cada fase: push numa branch + PR com o que mudou, alias, comandos do builder rodados e pendências.
4. O dev master baixa, revisa, envia ao CRM e à Duda e publica.

Conteúdo vindo do CRM (`crm-import/`) tem dados pessoais do cliente: o dev master envia por canal privado e
ele nunca entra no git.

## 5. Contribuir com a skill

Aprendeu uma armadilha nova da Duda? Abra PR aqui em `references/gotchas.md`, `references/api.md` ou `kit/`.
Este repositório é **público**: sem nome de cliente, ID de site, contato ou dados pessoais (use "Projeto X" e `<site>`).
