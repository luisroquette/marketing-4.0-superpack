# Cost sheet — present at Phase 2, repeat before every external action

| Item | Cost | Note |
|---|---|---|
| Licenses | Zero | All MIT |
| Supabase | Free tier usually enough | Can share the project Lovable already provisioned |
| Vercel (LP deploy) | Owner's plan: Pro $20/mo + usage; each deploy burns build minutes | ALWAYS alert before creating a project or deploying |
| MailMKT cron host | Vercel cron (project cost) or Railway (usage-based) | Decision made with the cost on the table |
| Resend | Free tier: 3,000 emails/month (100/day), 1 custom domain | Verified 20/08/2026 |
| Claude Code session | Owner's plan | ~30–60 min for the whole wizard |

## Approval gates (hard stops)

1. Before creating any Vercel project or running any deploy.
2. Before applying database changes (tables/migrations) to the owner's Supabase.
3. Before the first real email send (dry mode comes first).
4. One deploy per piece, after local validation — never iterative redeploys.
