# How the pieces communicate

The full communication flow of the MARKETING 4.0 ecosystem — the map of who
talks to whom, and through which physical mechanism. Companion to the main
README and to the interactive graph (`assets/grafo-marketing-4.0.html`).

```mermaid
flowchart LR
    SEO["claude-seo<br/>ATTRACT"] -->|"audited content pattern"| BLOG["Autoblog<br/>ATTRACT"]
    BLOG -->|"traffic, no tracking links"| LP["LP Engine<br/>CONVERT"]
    LP -->|"publishes CTA"| TK["Tracklink<br/>CONVERT / MEASURE"]
    TK -->|"302 redirect + xmax=0 click"| LP
    LP -->|"lead intake (3 fields)"| MK["MailMKT<br/>NURTURE"]
    MK -->|"every CTA = mailmkt-&lt;slug&gt;"| TK
    TK -->|"cookie: last-click on purchase"| PURCHASE(("Purchase"))
    TK -->|"7/30/90 calendar-filled metrics"| DASH["Unified dashboard"]
    MK -->|"cockpit queries"| DASH
```

> GitHub renders the Mermaid block above as a live diagram. The same flow as
> machine-readable JSON: [`ecosystem-flow.json`](ecosystem-flow.json).

## How each connection actually works

| Connection | Real mechanism |
|---|---|
| **LP → Tracklink** | At publication, the LP creates the tracked link for the CTA. When the visitor converts, the LP records `firstTrackingClickId` on the lead (camelCase). |
| **Tracklink → destination** | 302 redirect. The click is recorded transactionally (`RETURNING (xmax = 0)`) and the visitor continues — analytics never blocks delivery. |
| **LP → MailMKT** | Intake contract: the 3-field lead (bedrock clause) enters the 25-day sequence. It is a data shape, not a code call. |
| **MailMKT → Tracklink** | Every email CTA goes out as a `mailmkt-<slug>` link — nurture also attributes origin. |
| **Tracklink → purchase** | Attribution ends at the purchase: the tracklink **cookie** records the origin (last-click, snake_case on the purchase). Whatever checkout you use is outside the pack. |
| **autoblog → LP** | Traffic only. By contract, the blog does **not** emit tracking links — the LP converts, and the boundary is explicit in the graph. |
| **claude-seo → the rest** | No direct call. The link is the pattern: the LP's SEO gate (metaTitle/description/JSON-LD) follows the same methodology, and the audited content is what the autoblog publishes. |
| **Tracklink → Dashboard** | 7/30/90 calendar-filled metrics — absence ≠ zero. |
| **MailMKT → Dashboard** | Documented cockpit queries (sends per motor, throttle state, outbox health). |

## The three principles that make this work

1. **Contracts, not SDKs** — no piece imports another's code. Every contract has a
   declared owner; when two disagree, the owner wins. It is prose readable by
   humans and agents, plus a deterministic validator.
2. **The physical communication is the data** — columns (`firstTrackingClickId`),
   redirects (302) and cookies (attribution). Nothing calls anything through
   internal APIs.
3. **Absences are contracts too** — the graph records what does NOT connect (the
   autoblog does not emit tracking links), so you never go looking for an
   integration that does not exist.

The interactive graph (`assets/grafo-marketing-4.0.html`) is this same view with
204 nodes, where every edge carries a source sentence from the repos' documents.
