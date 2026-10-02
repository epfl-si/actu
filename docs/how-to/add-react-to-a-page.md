# How to integrate React to a Django page

React is integrated as small "islands" inside the regular Django templates. A new
React component on an existing page needs exactly 5 pieces:

1. a mount `<div>` in the Django template. Convention want it to be have the "-root" particule in the name.
2. a React island entry in `src/assets/pages/<page-dir>/`
3. the component(s) in `src/assets/components/<feature>/`
4. one line in `vite.config.js` to register the entry
5. one `{% vite_asset %}` tag in the template where the `<div>` is mounted

Everything is compiled at build time into plain hashed JS in `src/static/` and
resolved by the Vite manifest — the server never runs Node.js and clients only
receive self-hosted static files.

Below are the detailed steps for the pieces:

## 1. How to load the data into the React component

Server data travels to React through a `json_script` payload. One per island.
Sample:

```html
{{ news_blocks_editor_props|json_script:"news-blocks-editor-props" }}
<div id="news-blocks-editor-root">
</div>
```

Conventions:

- name the mount id after the page and the component, e.g.
  `news-blocks-editor-root`
- the payload tag id follows `<page>-<component>-props`, e.g.
  `news-blocks-editor-props`; the mount id follows `<page>-<component>-root`.
  The entry looks both up
- the view owns the payload shape as a dict in the context (e.g.
  `news_blocks_editor_props = {"newsId": news.pk, "language": lang}`). JSON keeps
  real types (`null`, numbers, booleans), so no string coercion is needed on
  either side
- for internationalized strings, pass them inside the payload instead of
  adding a client-side i18n framework
- mind the language: `{% get_current_language %}` is the **UI/site language**,
  while e.g. `{{ form.language }}` is the **content language** of the page (the
  `lang` URL parameter). Pick the one your feature needs
- name components and islands after **what they do** (e.g. `NewsBlocksEditor`,
  `news_blocks_editor`), never generic names like `App`

## 2. React entry file

Create the island entry in the page directory,
e.g. `src/assets/pages/edit-news/news-blocks.editor.tsx`:

Notes:

- the `@vitejs/plugin-react/preamble` import **must be the first import**. It
  boots the Fast Refresh runtime, which stock `django-vite` templates cannot
  inject (Django renders the HTML, Vite never sees it). In production builds it
  resolves to an empty module — nothing refresh-related ships to the client

## 3. Components

Create the component in its own directory,
e.g. `src/assets/components/blocks-editor/NewsBlocksEditor.tsx`:

Conventions:

- components are declared as arrow functions assigned to `const`
- colocated styles go next to the component, `.scss` rules are transpiled and are 
  imported in the component (`import './news-blocks-editor.scss'`). Rolldown extracts
  them into a CSS chunk for the entry (`css/news_blocks_editor.css`, see the build output), and
  django-vite's `{% vite_asset %}` generates the matching
  `<link rel="stylesheet" />` automatically in production — no template change
  needed. In development Vite injects the styles through HMR instead
- SCSS partials in `src/assets/_variables.scss` (EPFL colors) are available
  via `@use 'variables';` and namespaced access (e.g. `variables.$leman`)
- **only export React components** from files under `src/assets/components/` —
  Fast Refresh invalidates the whole module otherwise (enforced by the
  `react-refresh/only-export-components` ESLint rule)
- the ESLint rewrites keep the project style: single quotes in JSX
  (`jsx-quotes`), space before function parentheses, trailing commas
  (`comma-dangle`), `react-hooks/rules-of-hooks` as error

## 4. Register the entry in `vite.config.js`

Add the entry to `rolldownOptions.input`, like this:

```js
input: {
  ...
  news_blocks_editor: './assets/pages/edit-news/news-blocks-editor.tsx',
},
```

- key names use snake_case and are named after the **island** (e.g.
  `news_blocks_editor`), not the page — the key determines the bundle and CSS
  chunk names (`news_blocks_editor-[hash].js`, `css/news_blocks_editor.css`);
  directory/file names use kebab-case
- TypeScript is transpiled by Vite; the `jsx`/`tsx` extensions are
  allowed

## 5. Include the entry in the template

In the template, load the tag library and add the script to
`{% block web2018_extra_js %}`, keeping `{{ block.super }}` so the HMR client
from `base.html` stays. e.g.:

```html
{% load django_vite %}
...

{% block web2018_extra_js %}
  {{ block.super }}
  {% vite_asset 'assets/pages/edit-news/news-blocks-editor.tsx' %}
{% endblock %}
```

## Verify

Local tooling:

```
npm run lint        # stylelint + eslint + typecheck (tsc --noEmit)
npm run build       # then check src/static/manifest.json has the new key
npm run dev         # Vite dev server on http://localhost:5173/static/
```

Docker tooling (same as CI):

```
make assets-build   # npm run build inside the assets container
make eslint
```

Checks:

- build output shows the new bundle, e.g. `<island>-[hash].js` and its CSS
  chunk `css/<island>.css`
- `src/static/manifest.json` contains the new entry with `"isEntry": true`
- with `DEBUG = True`, go to the page: the island renders and edits hot-reload
  without a full page reload

## Gotchas

- rewriting `{% block web2018_extra_js %}` without `{{ block.super }}` removes
  the HMR client in development
- `createRoot(...).render()` is used instead of `.mount()` — React 19 runtime
  has both, but the installed `@types/react-dom` does not type `.mount()` yet
