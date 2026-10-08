# AGENTS.md

Context for an AI agent (Claude Code, OpenCode, etc.) working on this project. It focuses on what's hard to infer just by reading the code — business intent, gotchas, and conventions.

For exact commands, read the `Makefile` directly rather than trusting a stale copy here. For human-oriented setup/release instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Communication

- Reply in the language the user writes the prompt in.
- Code, code comments, docs, and commit messages are always in English. Exception: translation files and user-facing strings (fr/en/de/it).
- Human-facing text (comments, commit messages, replies): fewest words possible. Pick each word deliberately. Less is more.
- Applies to prose replies and comments. Not to docs or docstrings, which stay complete.
- No praise, no superlatives. No "you're absolutely right". State the facts, including unwelcome ones.
- Ask when a business rule is ambiguous. Don't guess.
- Before changes spanning several layers or models, propose a plan first.
- Final reply: list changed files and commands to run.

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
- News pages need a good SEO score and are cached — keep the
  public frontoffice server-rendered; dynamic client content like React is not
  welcome there.

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

## Documentation

Docs live in `docs/` and follow the [Diátaxis](https://diataxis.fr/) framework —
organized by reader's need, not project structure. Start from [docs/index.md](docs/index.md).

- `docs/tutorial/` — guided learning experiences for newcomers.
- `docs/how-to/` — recipes for a specific task (dev workflows, debugging). Title pages "How to …".
- `docs/reference/` — precise technical lookups (API, settings).
- `docs/explanation/` — concepts, architecture, decisions (the "why").

- One topic per page, kebab-case filenames (e.g. `debug-on-intellij.md`).
- Keep commands consistent with the Makefile; link, don't copy whole command lists.
- If a change makes an existing doc stale, suggest the update to the user instead of
  doing it unasked (e.g. new test env var → `docs/how-to/run-playwright-tests.md`).
- When introducing a non-obvious workflow, tool, or env var, suggest a new page;
  write it only if the user confirms.
- Don't duplicate AGENTS.md content: AGENTS.md is agent-oriented (rules, gotchas);
  `docs/` is human-oriented.

## Implementation

- Function-based views (no class-based views).
- Multi-model forms should receive the acting user explicitly.
- Use `_safe_int` / `_safe_int_set` for query-string integers.
- Follow existing `select_related` / `prefetch_related` patterns.
- New models should reuse the shared base classes: `AuditModelMixin` (audit/tracking fields) and `LabelModel` (translated labels fr/en/de/it).
- HTML content fields use TinyMCE (`HTMLField`).
- User-facing strings must be translatable (`gettext_lazy`), including model verbose names and choices.
- Update translation files with `make translation` when adding new strings.
- One migration per change. Never mix data and schema migrations.
- Follow `.editorconfig` and at the repo root.
- Python: `black` and `isort` (profile black), line length 79. `flake8` for linting. Config in `pyproject.toml` and `.flake8`.
- JS: `eslint`. SCSS: `stylelint`. Dockerfiles: `hadolint`.
- Extract recurring or domain-specific values into constants or enums; keep self-explanatory one-off values inline. Use framework constants for standard values such as HTTP status codes where available.
- OnceAndOnlyOnce: no duplication. Extract shared logic.
- Prefer concise, descriptive function names; do not impose a fixed length limit.
- Use booleans for genuinely binary options and enums for meaningful multi-state values.
- Separate logical blocks with blank lines. Add comments only when they clarify non-obvious intent.
- Don't touch code unrelated to the feature. No comments on code you didn't create or modify. Minimize changed lines.
- No opportunistic refactoring.
- No `print`. Use `logging`.

## Architecture

- Follow the 12-factor methodology: https://12factor.net/
- In OpenShift, Ansible reads secrets from Keybase, creates a Kubernetes Secret, and exposes its values to the container as environment variables via `envFrom.secretRef`.
- Django reads secrets and deployment-specific configuration from environment variables. Stable application defaults may be defined in Django settings; do not hardcode secrets or deployment-specific values in application logic.

## Boundaries

Ask before:

- Adding a dependency (pip/npm).
- Editing `docker-compose*.yml`, CI config, or `src/configs/`.

Never:

- Edit an existing migration. Create a new one.
- Edit generated files (compiled `.mo`, Vite build output).

## Testing

- Framework: Django test runner (`python src/manage.py test`, `configs.ci` settings). Use `make test`, never run it on the host.
- `make test` runs `make lint` and `make assets-build` first. Run it before declaring a task done.
- Use `make coverage` to check coverage of new code.
- Never delete, skip, or weaken a test to make it pass.

## UI

- Prefer existing EPFL Elements components.
  - Docs: https://epfl-si.github.io/elements/#/
  - Repo: https://github.com/epfl-si/elements
- Introduce custom CSS/JS only if not available within Elements.
- React may be used, but keep it for highly interactive user experiences (e.g. the block
  editor) — it needs intense API interaction and may shadow Django features, like 
  Forms. So don't use it for simple screens.
- React ships as small islands inside Django templates, not an SPA: components
  live in `src/assets/components/<feature>/`, island entries in
  `src/assets/pages/<page-dir>/`; TypeScript is recommended. Recipe:
  [docs/how-to/add-react-to-a-page.md](docs/how-to/add-react-to-a-page.md).
- Assets (SCSS/JS) live in `src/assets/`, built with Vite.
- If the style guide lacks a needed element, create `TODO-styleguide.md` at the repo root. One line per missing element: component and page concerned.
- Design source: Penpot, team ISA-FSD, project Actu: https://ait-penpot.epfl.ch/#/dashboard/files?team-id=0ba4abe3-fd81-816f-8008-a5c241a4a1fe&project-id=79de8261-3fae-80f8-8008-a8641ea9184f
- Before changing anything in Penpot, save a version first (Penpot's version history). Never edit without a restore point.

## Git

- Never commit unless explicitly asked.
- Never push to origin unless explicitly asked.
- Never force-push or rewrite history, and never skip hooks.
- Never commit secrets or credentials (Keybase files, `ACTU_*` env values).
- Commit subjects and bodies are always in English, whatever language the user writes in.
- Commit messages follow these rules:
  - Subject prefixed with a tag: `[bump]` (dependency/version update), `[doc]`, `[feature]`, `[fix]`, `[hotfix]` (urgent production fix), `[refactor]`, `[unfeature]` (feature removal).
  - Single blank line between subject and body.
  - Subject: 50 characters max (72 hard limit).
  - Capitalize the first letter after the tag.
  - No period at the end of the subject.
  - Imperative mood. Test: "If applied, this commit will [subject]". Example: `[fix] Correct null check`.
  - Wrap body at 72 characters.
  - Body explains what and why, not how.
