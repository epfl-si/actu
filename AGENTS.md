# AGENTS.md

Context for an AI agent (Claude Code, OpenCode, etc.) working on this project. It focuses on what's hard to infer just by reading the code — business intent, gotchas, and conventions.

For exact commands, read the `Makefile` directly rather than trusting a stale copy here. For human-oriented setup/release instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Project overview

EPFL news management app (Django, Python, PostgreSQL, Django REST Framework for the API, Vite for assets), split in 2 parts:

- **Backoffice**: editors (permissions checked via EPFL Entra) create, edit, and publish news and homepage.
- **Frontoffice**: public part where visitors read published news.

Site languages: French, English, German, Italian.

## Key business rules

- `News` = fields shared across languages (one per news item).
- `NewsTranslation` = language-specific fields (one per language, unique per `(news, language)`).
- Publication status belongs to `NewsTranslation`, never `News`.
- A translation can be published independently of the other languages.

## URL structure — frequent source of confusion

Backoffice URLs contain 2 languages:

- `/<lang_ui>/...` = UI language (interface labels)
- resource path language = translation being edited

Example: `/fr/news/<news_id>/en/edit/` = French UI + English translation.

Never confuse these two.

## Dev environment

- Everything runs via Docker (`docker-compose-dev.yml` for dev, `docker-compose.yml` for prod-like).
- Main containers: `local-django-actu` (backend), `local-assets-actu` (assets), `local-postgres-actu` (database).
- Lint and tests run **inside the containers**, not on the host — the dev stack must be up (`make local-up`) before linting, testing, or seeding.
- Run `make help` for the full, up-to-date command list. Frequent entry points: `local-up`, `lint`, `test`, `translation`, `db-seed`.
- Django settings modules live in `src/configs/`: `settings.py` (local dev), `ci.py` (tests/CI), `ocp.py` (OpenShift).
- Demo data: each app ships a `sample_data.json` fixture (`src/<app>/fixtures/`, e.g. `news`, `homepages`, `users`). `make db-seed` loads them all for a demo-ready site — beware, it may overwrite existing data. Human-oriented instructions: [docs/tutorial/load-some-sample-data.md](docs/tutorial/load-some-sample-data.md).

## Conventions

- Function-based views (no class-based views).
- Multi-model forms should receive the acting user explicitly.
- Use `_safe_int` / `_safe_int_set` for query-string integers.
- Follow existing `select_related` / `prefetch_related` patterns.
- New models should reuse the shared base classes: `AuditModelMixin` (audit/tracking fields) and `LabelModel` (translated labels fr/en/de/it).
- HTML content fields use TinyMCE (`HTMLField`).
- User-facing strings must be translatable (`gettext_lazy`), including model verbose names and choices.
- Update translation files with `make translation` when adding new strings.

## UI

- Prefer existing EPFL Elements components.
  - Docs: https://epfl-si.github.io/elements/#/
  - Repo: https://github.com/epfl-si/elements
- Introduce custom CSS/JS only if not available within Elements.
- Assets (SCSS/JS) live in `src/assets/`, built with Vite.

## Git

- Never commit unless explicitly asked.
- Never push to origin unless explicitly asked.
- Never force-push or rewrite history, and never skip hooks.
- Never commit secrets or credentials (Keybase files, `ACTU_*` env values).
