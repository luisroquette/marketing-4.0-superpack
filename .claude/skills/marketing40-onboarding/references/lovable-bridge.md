# Lovable bridge (mechanics for Lovable-built stores)

The pack speaks repos and contracts; the owner speaks Lovable. This file is
the translation layer. Everything below was verified against Lovable and
Stripe documentation on 19/08. If a platform path is ever unverified again,
mark it TODO-VERIFY, instruct by goal ("open your project settings and look
for the database section"), never by invented clicks.

| The owner needs | Reality in Lovable |
|---|---|
| Supabase credentials | Lovable connects to Supabase credential-free (pick the project → Connect; migrations and types are handled from chat). The pack's pieces need direct access: open the Supabase dashboard via the Lovable Cloud view ("Jump to the Supabase dashboard") and copy the connection string + anon key from the project's API settings. Never the `service_role` key. (Verified against Lovable docs, 19/08.) |
| Stripe customer export (for the leads CSV) | Stripe Dashboard → Customers → Export → CSV (date range, timezone and columns are selectable). Lovable-managed checkout IS Stripe (chat-driven integration; Stripe holds the customer records, Supabase holds users/subscriptions/payments) — so the export covers Lovable stores. (Verified against Stripe and Lovable docs, 19/08.) |
| Custom domain for the LP | Project → Settings → Domains (or Publish dialog → Add domain). Requires a paid plan and a published project. DNS: an A record to Lovable's edge IP `185.158.133.1` + a TXT record on host `_lovable` (value starting with `lovable_verify=`); Entri automates it or the owner adds the records manually; propagation can take up to 72 h; add `www` separately. (Verified against Lovable docs, 19/08.) |
| Adding the LP page to the store | Option 1: deploy the LP repo to Vercel (tracklink plug is native there). Option 2: NOT supported today — verified 19/08: the LP is a Claude Code/Codex skill whose output is a blueprint (draft → audit → publish); it does not emit a standalone HTML file to paste into Lovable. |

## The honest gaps (say these aloud to the owner)

- Purchase attribution is NOT in the pack — it ends at the click. Closing the
  loop requires a small bridge in the store (`attribution-bridge.md`).
- The unified dashboard is the 6th piece (My_Dashboard_Makes_Me_Proud),
  read-only by contract: it never writes to the owner's database. Until it
  is plugged, the owner keeps their spreadsheet; the metrics contract
  (7/30/90, absence ≠ zero) is the shape the export will use.
