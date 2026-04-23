#!/bin/bash
# Le Proxy Français — Vérifier les crédits restants
curl -s https://prx.lv/usage -H "Authorization: Bearer ${LPF_API_KEY}" | python3 -m json.tool
