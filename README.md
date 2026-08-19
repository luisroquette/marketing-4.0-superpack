<p align="center">
  <img src="assets/logo.png" alt="CF Gauss" width="64" />
</p>

<h1 align="center">MARKETING 4.0</h1>

<p align="center">
  <strong>Digital Marketing in the Age of AI — monte seu ecossistema de marketing peça por peça, como LEGO.</strong><br>
  Um manual de montagem: cada peça tem um papel no funil, cada plug tem um contrato, e o conjunto fecha um sistema completo — da aquisição por SEO/GEO até a atribuição da venda.
</p>

<p align="center">
  <a href="https://github.com/luisroquette"><img alt="CF Gauss" src="https://img.shields.io/badge/CF_Gauss-Applied_AI_Systems-7B2FBE?style=for-the-badge&labelColor=1A1524"></a>
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-2E7D32?style=for-the-badge&labelColor=1A1524">
  <img alt="8 peças" src="https://img.shields.io/badge/peças-8-D5A62E?style=for-the-badge&labelColor=1A1524">
</p>

---

## 🗺️ O mapa do ecossistema

**[Abra o grafo interativo do funil](assets/grafo-marketing-4.0.html)** (baixe e abra no navegador) — 205 conceitos e ~420 conexões extraídas dos próprios contratos dos sistemas, organizadas por estágio do funil. O grafo é a fonte da verdade de como as peças se relacionam; este README é o manual de montagem.

O funil tem seis estágios. Cada peça encaixa em um deles:

```
ATRAIR ──────────► CONVERTER ─────► NUTRIR ──────► VENDER ──────► AMPLIFICAR
 (SEO/GEO)          (LP+tracking)   (e-mail)      (IA+propostas)  (social)
    │                    │              │              │              │
    └────────────────────┴──────────────┴──────────────┴──────────────┘
                                   MEDIR (o tempo todo)
```

---

## 🧱 As peças

Cada peça: o que faz, onde mora, como instalar, como plugar. **Instale só as peças do seu estágio — o contrato entre elas é que permite montar o conjunto inteiro depois.**

### Peça 1 — SEO/GEO (Atrair)
**O que faz:** audita e otimiza seu conteúdo para busca clássica e busca por IA, com falsificabilidade (cada recomendação responde "como saberíamos que falhou?").
- Repo: `AgriciDaniel/claude-seo` (MIT) — clone: `git clone https://github.com/AgriciDaniel/claude-seo.git`
- **Pluga em:** nada (é a porta de entrada). Alimenta o funil com tráfego orgânico.
- Gate em comum com o resto: gate de SEO (metaTitle/metaDescription/JSON-LD) — a LP usa o mesmo padrão.

### Peça 2 — Autoblog (Atrair)
**O que faz:** conteúdo editorial autônomo (artigos gerados de fontes reais, com compliance guard em runtime). Referência viva: `cfgauss-site` (`app/api/cron/generate-article`).
- **Pluga em:** ig-sentinel (monitora falhas do autoblog). Não usa tracking links por contrato — o blog atrai; quem converte é a LP.

### Peça 3 — LP Engine (Converter)
**O que faz:** páginas de venda a partir de brief ou URL, com 6 modelos, 4 gates e anti-fabricação como regra suprema.
- Repo: `luisroquette/My_LP_Makes_Neil_Proud` — clone: `git clone https://github.com/luisroquette/My_LP_Makes_Neil_Proud.git`
- **Pluga em:**
  - → **Tracklink** (obrigatório para CTAs): cada CTA da LP sai como link trackeado; o lead grava `firstTrackingClickId`.
  - → **MailMKT** (intake): a LP entrega o lead para o e-mail engine.

### Peça 4 — Tracklink UTM (Converter/Medir)
**O que faz:** o dono do contrato de tracking — criação, clique, atribuição first/last, saúde e métricas, com validator determinístico de 13 casos.
- Repo: `luisroquette/My_UTMs_Make_Me_Proud` — clone: `git clone https://github.com/luisroquette/My_UTMs_Make_Me_Proud.git`
- **Pluga em:** LP (produtora de links), MailMKT (todo CTA `mailmkt-<slug>`), dashboard unificada (métricas 7/30/90).

### Peça 5 — MailMKT (Nutrir)
**O que faz:** o cockpit de e-mail — throttle 1 e-mail/lead/dia, um cron só, outbox durável, dashboard demo. 107 testes.
- Repo: `luisroquette/My_MailMKT_makes_Neil_Proud` — clone: `git clone https://github.com/luisroquette/My_MailMKT_makes_Neil_Proud.git`
- **Pluga em:** LP (intake de leads), Tracklink (CTAs rastreados), ig-sentinel (não hoje — sem menção cruzada nos docs; o monitor é do blog/social).

### Peça 6 — Vendas com IA (Vender)
**O que faz:** marIA (vendas por WhatsApp) + Motor Empiricus (esteira evergreen + campanhas de lançamento com gate de compliance) + Sistema de Propostas.
- Referência viva: `cfgauss-site` (`lib/maria`, `lib/propostas`, motor Empiricus).
- **Pluga em:** plataforma de cursos própria. Obs.: o agente de vendas não nomeia LP/tracking nos docs — a venda acontece na conversa, a atribuição vem do cookie da Peça 4.

### Peça 7 — Amplificação Social (Amplificar)
**O que faz:** automação de Instagram (reels, stories, planejamento editorial) — Social Machine V3.1.
- **Pluga em:** ig-sentinel (monitora o IG). Produz alcance; o funil converte nas peças 3-5.

### Peça 8 — ig-sentinel (Medir)
**O que faz:** observabilidade do ecossistema — um cron lê 4 bancos Supabase e manda UM e-mail diário unificado; Doctor corrige automaticamente.
- **Pluga em:** autoblog (conta falhas por janela), V3.1/SWEN/CF Gauss (estado do IG).

---

## 🔌 Os contratos que fazem o encaixe (a parte LEGO de verdade)

As peças não se chamam por código — se referenciam por **contratos em Markdown**:

| Contrato | Dono | Consumidores |
|---|---|---|
| O que é um clique, um lead e uma compra | Tracklink (`references/nucleo/`) | LP, MailMKT, dashboard |
| Formulário de captura (3 campos — cláusula pétrea) | LP | MailMKT (intake) |
| Slug `mailmkt-<slug>` + UTMs | Tracklink (integração mailmkt) | MailMKT (todo CTA) |
| Métricas 7/30/90 calendar-filled | Tracklink (`metricas.md`) | Dashboard unificada |
| Gate de publicação nunca contornado | LP | — |
| Piso de copy no salvar E no enviar | MailMKT (`piso.ts`) | — |
| Ausência ≠ zero | os três repos | todos os dashboards |

**Regra de ouro:** quando dois contratos discordam, o dono vence (ex.: o tracklink define o que é um clique — a LP referencia, não redefine).

---

## 🧩 Receitas — fluxos prontos

### Receita A — Funil completo (o ecossistema inteiro)
1. **Atrair:** clone claude-seo + rode a auditoria no seu site; autoblog publica conteúdo contínuo
2. **Converter:** clone LP + Tracklink → crie a página, plugue o tracking, publique
3. **Nutrir:** clone MailMKT → aponte o intake para os leads da LP
4. **Vender:** marIA/Empiricus no WhatsApp e nas campanhas
5. **Amplificar:** V3.1 publica reels/stories
6. **Medir:** ig-sentinel + dashboard unificada (contratos do tracklink + queries do cockpit)

### Receita B — Só conversão (LP + tracking)
2 peças, 30 minutos: LP engine + Tracklink. A página captura o lead E atribui a origem.

### Receita C — Só nutrição (e-mail)
1 peça, self-contained: MailMKT com throttle, outbox e dashboard demo.

---

## 📊 O que o grafo revela (os princípios transversais)

- **"Ausência nunca é zero"** aparece nos 3 repos — é o contrato familiar do ecossistema.
- **"Analytics nunca bloqueia entrega"** atravessa tracking e e-mail.
- **O incidente é a arquitetura** — o throttle do MailMKT nasceu de 3 e-mails em 1 hora para um lead real.
- **Gates em cascata** — o gate de compliance do Empiricus é o mesmo padrão dos gates da LP.

---

<p align="center">
  <sub>CF Gauss · MARKETING 4.0 — Digital Marketing in the Age of AI · monte peça por peça</sub>
</p>
