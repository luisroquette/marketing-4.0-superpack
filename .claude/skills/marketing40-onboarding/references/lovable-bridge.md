# Lovable bridge (mechanics for Lovable-built stores)

The pack speaks repos and contracts; the owner speaks Lovable. This file is
the translation layer. Items marked TODO-VERIFY must be confirmed against the
current Lovable UI before the wizard claims them — if unverified, instruct by
goal ("open your project settings and look for the database section"), never
by invented clicks.

| The owner needs | Reality in Lovable |
|---|---|
| Supabase credentials | Lovable provisions a Supabase project per app. TODO-VERIFY: current settings path to Database → connection string + anon key. |
| Stripe customer export (for the leads CSV) | Stripe Dashboard → Customers → Export. TODO-VERIFY: applies to Lovable-managed checkout. |
| Custom domain for the LP | Lovable Settings → Domains; requires a CNAME at the DNS provider. TODO-VERIFY: exact flow. |
| Adding the LP page to the store | Option 1: deploy the LP repo to Vercel (tracklink plug is native there). Option 2: TODO-VERIFY — whether the LP emits pasteable standalone HTML for a Lovable page; if it does, tracking becomes custom code (see `attribution-bridge.md`). |

## The honest gaps (say these aloud to the owner)

- Purchase attribution is NOT in the pack — it ends at the click. Closing the
  loop requires a small bridge in the store (`attribution-bridge.md`).
- The unified dashboard is a roadmap item. Until it ships, the owner keeps
  their spreadsheet; the metrics contract (7/30/90, absence ≠ zero) is the
  shape the export will use.
