# Phase 6 — purchase attribution bridge

OUTSIDE the pack by contract: "attribution ends at the purchase". The pack
records clicks and leads; the sale happens in the owner's store. This file
documents the two ways to close the loop. The wizard OFFERS this phase; it
never applies it silently — touching the owner's store code requires explicit
approval.

## Path A — same-domain cookie (recommended when a domain exists)

Run tracklink on a subdomain of the SAME registrable domain as the store
(e.g. `t.sualoja.com` for `sualoja.com`) and set the cookie's `Domain`
attribute to the registrable domain (`Domain=.sualoja.com`), not the subdomain
host. The first-party cookie written during the 302 is then readable by the
store at checkout. Requires DNS + TLS. Trade-off: strongest, one DNS entry,
same-domain only.

## Path B — lead matching (works cross-domain)

The lead row already stores `firstTrackingClickId` (camelCase). At purchase,
match the buyer's email/phone against the lead and copy the origin onto the
purchase. Pseudo-code for the store's purchase handler:

```
lead = leads.find_by(email: buyer.email) or leads.find_by(phone: buyer.phone)
if lead: purchase.origin = lead.firstTrackingClickId
```

Trade-off: no DNS requirement; accuracy depends on the buyer using the same
email/phone they gave the form.

## Wizard rules for this phase

- Present both paths with the trade-offs; let the owner choose (or skip).
- Deliverable: a documented snippet + where it goes in Lovable (TODO-VERIFY
  current custom-code flow). Never edit the owner's app without approval.
- The final report must state honestly which path was taken or that the
  bridge was skipped — purchases will not attribute until it exists.
