"""Configurações gerais: SEO do site, favicon, idioma e dados do negócio (biblioteca de conteúdo)."""
import lib

FAVICON = "https://irp.cdn-website.com/<site>/site_favicon_16_1764099393000.ico"


def apply():
    c = lib.content()
    lib.call("POST", f"/sites/multiscreen/update/{lib.SITE}", {
        "lang": "pt",
        "fav_icon": FAVICON,
        "site_seo": {
            "title": "Agência Exemplo | Agência de Marketing Digital com Propósito",
            "description": "Criamos presenças digitais autênticas para negócios com propósito. Sites que convertem, branding visionário e estratégias de marketing personalizadas.",
            "og_image": lib.img("/images/cristais.webp"),
            "no_index": False,
        },
    })
    # Mesmo endereço já cadastrado no site atual (<site>).
    lib.mcp("update_content_library", {
        "site_name": lib.SITE,
        "location_data": {
            "phones": [{"phoneNumber": "+55 00 00000-0000", "label": "WhatsApp"}],
            "social_accounts": {"instagram": "agencia.exemplo", "whatsapp": "5500000000000"},
            "address": {"streetAddress": "Rua Exemplo, 100", "postalCode": "00000-000", "city": "Florianópolis",
                        "region": "Santa Catarina", "country": "BR"},
            "logo_url": lib.img("logo-claro"),
        },
        "business_data": {
            "name": "Agência Exemplo | Marketing com Propósito",
            "logo_url": lib.img("logo-claro"),
            "description": "Agência de marketing digital com propósito: sites, branding visionário, inteligência artificial e performance para terapeutas, artistas e negócios de impacto.",
        },
        "site_texts": {
            "overview": "Presença digital e branding visionário para negócios com propósito.",
            "about_us": c["about"]["aboutPage"]["lead"],
            "services": "Sites e presença digital, branding visionário, soluções em inteligência artificial, performance e automação.",
        },
    })
    print("configurações do site aplicadas")
