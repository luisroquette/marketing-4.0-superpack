# Credentials protocol

## Supabase (Tracklink + MailMKT)

- NEED: `DATABASE_URL` (connection string, ports 5432/6543) + the `anon` /
  publishable key.
- NEVER ask for, accept or store the `service_role` key. If the owner pastes
  one: stop, explain what it unlocks, recommend rotating it.
- Lovable projects already ship a Supabase — where to find its keys:
  `lovable-bridge.md`.

## Resend (MailMKT sender)

- NEED: one API key, stored the same way.

## Where secrets live

- ONLY in `<workspace>/marketing40-setup/.env`, created in Phase 0 and
  gitignored. The owner pastes values directly into this file (the wizard
  creates it empty); secrets never enter the chat. Never in repo files, never
  in commits, never in docs, never in chat artifacts.
- If a secret was pasted into the chat, say so plainly and recommend rotation.

## Wiring the pieces

- The single `<workspace>/.env` is the source of truth. At assembly time
  (Phase 5), the wizard copies the relevant variables into each piece's own
  gitignored env file, as documented by that piece. Neither file is ever
  committed.

## Where the owner never touches

- The owner never edits repo code to store credentials. The wizard writes
  `.env` once; nothing else moves it.
