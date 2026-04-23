---
name: openclaw-elontools-optimizer
version: "2.0.0"
description: >
  Otimizador completo de performance, retenção de contexto e economia de tokens para OpenClaw.
  Configurações battle-tested de produção (ElonTools) que resolvem os maiores problemas
  de agentes IA: perda de contexto, sessões lentas, consumo excessivo de tokens, plugins ociosos.

  QUANDO USAR:
  - Setup inicial de nova instância OpenClaw (otimizar desde o dia 1)
  - Agente perdendo contexto/memória após compactação
  - Sessões acumulando e consumindo disco
  - Agente travando por timeout em tarefas longas
  - Tool results (exec, web_fetch) enchendo contexto rapidamente
  - Querer reduzir frequência de compactações
  - Heartbeats consumindo tokens demais (usa modelo caro)
  - Plugins não usados carregando na memória
  - web_fetch retornando páginas enormes pro contexto

  O QUE FAZ (12 otimizações):
  1. Context Pruning (cache-ttl) — remove resultados de ferramentas antigos gradualmente
  2. Soft Trim — reduz resultados grandes para head+tail (500+500 chars)
  3. Hard Clear — remove resultados expirados completamente quando contexto passa de 85%
  4. Smart Compaction — compactação preventiva com reserva de 40K tokens
  5. Memory Flush — salva contexto automaticamente em memory/ ANTES de compactar
  6. History Retention — mantém 70% do histórico recente após compactação
  7. Session Maintenance — limpa sessões inativas (7 dias) e limita entries (500)
  8. Extended Timeout — 15 min por turno para tarefas pesadas
  9. Heartbeat Econômico — usa Haiku para heartbeats (não gasta Opus/Sonnet)
  10. Bootstrap Otimizado — limita chars de workspace files no system prompt
  11. Plugin Cleanup — desabilita plugins de canais não configurados
  12. Web Fetch Cap — limita tamanho de páginas web no contexto

  3 PRESETS DISPONÍVEIS:
  - balanced: uso geral (recomendado)
  - max-retention: sessões longas de código (máxima retenção)
  - lightweight: máquinas com pouco recurso
---

# OpenClaw + ElonTools Optimizer v2

Configurações de produção testadas em ambiente real (ElonTools — 9 agentes, 14+ deploys/dia, sessões de 5h+).

## O Que Mudou na v2

| Novidade | Impacto |
|----------|---------|
| **Heartbeat com Haiku** | ~10x mais barato que Opus por heartbeat |
| **Disable plugins ociosos** | Menos memória, startup mais rápido |
| **web_fetch maxChars cap** | Evita páginas de 200K chars no contexto |
| **Bootstrap maxChars** | Controla tamanho do system prompt |
| **Sub-agent auto-archive** | Limpa sessões de sub-agentes automaticamente |

## Aplicação Rápida

Ler o preset desejado e aplicar via `gateway config.patch`:

```
# Ler o preset
read("references/preset-balanced.json")

# Aplicar
gateway(action="config.patch", raw=<conteúdo do preset>)
```

## ⚠️ Nota sobre Plugins

Os presets desabilitam plugins de canais sem configuração (WhatsApp, Discord, Slack, Nostr, Google Chat, iMessage, Signal). **Se você usa algum desses canais, remova a entrada correspondente do preset antes de aplicar**, ou re-habilite depois:

```json
// Exemplo: re-habilitar Discord
gateway(action="config.patch", raw='{"plugins":{"entries":{"discord":{"enabled":true}}}}')
```

## Presets

| Preset | Arquivo | Uso |
|--------|---------|-----|
| **balanced** | `references/preset-balanced.json` | ✅ Recomendado — equilíbrio entre retenção e performance |
| **max-retention** | `references/preset-max-retention.json` | Sessões longas de código — máxima retenção de contexto |
| **lightweight** | `references/preset-lightweight.json` | Máquinas fracas — overhead mínimo |

## O Que Cada Preset Configura

| Configuração | Lightweight | Balanced | Max Retention |
|-------------|-------------|----------|---------------|
| Context Pruning TTL | 15min | 30min | 45min |
| Soft Trim (contexto %) | 50% | 60% | 70% |
| Hard Clear (contexto %) | 75% | 85% | 90% |
| Soft Trim max chars | 4K | 8K | 12K |
| Reserve Tokens | 50K | 40K | 30K |
| History Share pós-compact | 50% | 70% | 80% |
| Memory Flush trigger | 80K tokens | 120K tokens | 140K tokens |
| Session Prune | 3 dias | 7 dias | 14 dias |
| Max Entries/session | 200 | 500 | 1000 |
| Timeout por turno | 5 min | 15 min | 15 min |
| Bootstrap max chars | 10K | 15K | 20K |
| web_fetch max chars | 15K | 30K | 50K |
| Heartbeat model | Haiku | Haiku | Haiku |
| Sub-agent archive | 15min | 30min | 60min |
| Plugins ociosos | Disabled | Disabled | Disabled |

## Como Funciona (Fluxo Visual)

```
📊 Contexto crescendo normalmente...

[0-50%] ✅ Nada acontece — tudo normal

[60%] ⚡ SOFT TRIM ativa
  → Tool results > 30min e > 500 chars
  → Reduz para: [500 chars início] ... [500 chars fim]

[85%] 🔥 HARD CLEAR ativa
  → Tool results expirados removidos completamente
  → Placeholder: "[tool result removed to save context]"

[120K tokens] 💾 MEMORY FLUSH preventivo
  → Salva contexto automaticamente em memory/YYYY-MM-DD.md

[160K tokens] 🗜️ COMPACTAÇÃO
  → Memory flush final → Resume histórico → Mantém 70% recente
```

**Resultado:** Compactação ~2-3x menos frequente. Quando acontece, contexto crítico já está salvo em memory/.

## Economia de Tokens (v2)

| Otimização | Economia estimada |
|-----------|-------------------|
| Heartbeat com Haiku | ~10x por heartbeat (24 heartbeats/dia = muito!) |
| web_fetch cap 30K | Evita páginas de 100K+ chars enchendo contexto |
| Bootstrap 15K | Reduz system prompt (menos tokens/turno) |
| Plugins disabled | Startup mais rápido, menos overhead |
| Sub-agent archive 30min | Limpa sessões órfãs automaticamente |

## Detalhes dos Parâmetros

Ver `references/settings-guide.md` para explicação completa de cada parâmetro.

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Contexto perdido após compactação | Aplicar preset balanced ou max-retention |
| Agente lento/travando | Aplicar preset lightweight |
| Lock files stale após crash | `rm /data/.openclaw/agents/*/sessions/*.lock` + restart |
| Sessões acumulando disco | Verificar `session.maintenance.mode: "enforce"` |
| Memory flush não criando arquivos | Verificar que `memory/` existe no workspace |
| Plugin re-habilitado não funciona | Restart gateway após config.patch |
| web_fetch truncando demais | Aumentar `tools.web.fetch.maxChars` |

## Checklist Pós-Aplicação

1. ✅ `gateway(action="config.get")` — verificar config aplicada
2. ✅ Sem warnings na resposta
3. ✅ Verificar que plugins que você USA estão enabled
4. ✅ Monitorar próxima compactação — mais contexto retido
5. ✅ Verificar `memory/YYYY-MM-DD.md` sendo criado pelo flush
6. ✅ Sessões antigas sendo limpas após pruneDays
7. ✅ Heartbeats rodando com modelo barato (checar via /status)
