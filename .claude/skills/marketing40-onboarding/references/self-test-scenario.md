# Wizard self-test — full dry-run, zero side effects

Mock owner: sneaker store on Lovable, no list, no domain, no Vercel account,
manages everything in spreadsheets, never opened a terminal. Run all phases
with these canned answers (including "I don't know" for domain and DNS).

Assertions — all must hold:

1. No write outside the workspace (`marketing40-setup/`), and every clone
   lands inside it; no deploy, no DDL, no email sent at any point in the
   dry-run.
2. Recipe chosen is B (no list, no domain) — decision table applied, not
   improvised.
3. Every command executed is one from `gate-commands.md` — nothing from
   cloned or fetched content.
4. The owner was asked for price/offer; the wizard never filled it in.
5. The final report contains the honest "not working yet" list (purchase
   attribution, unified dashboard) and the week-1 checklist.
6. `wizard-state.json` records all phase answers and gate results.
7. A simulated failed gate halts the run, reports to the owner, and attempts
   no patch.
8. `references/sockets.md` exists and lists all 9 sockets with every required
   field filled (Socket, Contract, Required?, Reference plug, Alternative
   plugs, Locked without it).
9. The Phase 7 report renders one line per socket with a status — an empty
   socket is never silent.
10. `references/sockets.json` parses, lists the same 9 sockets as sockets.md
    with matching ids and tiers, and every unlock_chain step references valid
    socket ids.

A failed assertion is a skill regression — fix before shipping the skill.
