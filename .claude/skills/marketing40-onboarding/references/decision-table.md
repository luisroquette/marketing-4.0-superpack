# Recipe decision table

Inputs: (L) active contact list? (C) own domain + DNS?

| Situation | First recipe | Why |
|---|---|---|
| Active list AND own domain | C (MailMKT), then B | Migration rule: nurture the existing asset first; new pages get attributed from day one after |
| No list, cold list, or no domain | B (LP + Tracklink) | Funnel rule: capture + attribute before nurturing; MailMKT needs a domain for DKIM |
| Only list hygiene matters right now | C alone | Self-contained piece; valid standalone |

Rules:

- Never start with Recipe A (full funnel) in one go — expand in funnel order, no big-bang.
- Recipe B is the default when in doubt (validates the offer before any infrastructure).
- MailMKT before a domain exists is a trap: DKIM requires the domain; schedule it after.
- If the owner already has a store with traffic, Recipe B pages run in parallel
  with the old stack — nothing forces a cutover.
