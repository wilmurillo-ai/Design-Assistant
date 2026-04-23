# lpf_proxy — Le Proxy Français

Skill OpenClaw pour utiliser les proxy français Le Proxy Français avec vos agents IA.

## Installation

```bash
# Depuis ClawHub
/install lpf-proxy

# Ou manuellement
curl -sL https://leproxyfrancais.cloud/skill.md -o ~/.openclaw/skills/lpf-proxy/SKILL.md --create-dirs
```

## Configuration

```json5
// ~/.openclaw/openclaw.json
{
  "skills": {
    "entries": {
      "lpf_proxy": {
        "enabled": true,
        "env": { "LPF_API_KEY": "lpf_votre_cle_api" }
      }
    }
  }
}
```

Récupérez votre clé API sur https://leproxyfrancais.cloud/app (Clés API > Révéler).

## 3 Types de Proxy

| Type | Endpoint | Protocole | Prix |
|------|----------|-----------|------|
| Mutualisé | `mut.prx.lv:1080` | SOCKS5 | 3 crédits/Go |
| Dédié | `ded.prx.lv:1081` | SOCKS5 | 8 crédits/Go |
| Navigateur | `nav.prx.lv:80` | WebSocket (Playwright) | 10 crédits/Go |

Le navigateur est utilisé par défaut. Les crédits se déduisent automatiquement au Go consommé.

## Liens

- Dashboard : https://leproxyfrancais.cloud/app
- Documentation API : https://leproxyfrancais.cloud/documentation
- Skill complet : https://leproxyfrancais.cloud/skill.md
