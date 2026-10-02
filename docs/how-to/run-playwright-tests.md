# How to run Playwright tests locally

## Start the required processes

Start your Playwright server and get the running address, e.g.: `ws://127.0.0.1:3651`.
Set the env var `REMOTE_PLAYWRIGHT_SERVER` with this value.

## Run the tests

By default, the tests are headless.
e.g.:
```bash
REMOTE_PLAYWRIGHT_SERVER="ws://127.0.0.1:3651" python src/manage.py test \
  homepages.tests.tests_playwright
```

## Watch the tests live

To watch it while the tests run, set `PLAYWRIGHT_HEADED=1`.
the Chromium window opens on the host's display.

Optionally set `PLAYWRIGHT_SLOW_MO=<milliseconds>` to slow the browser actions
down and make them easier to follow:

e.g.:
```bash
PLAYWRIGHT_HEADED=1 PLAYWRIGHT_SLOW_MO=450 python src/manage.py test \
  homepages.tests.tests_playwright
```

## Watch the tests live

The remote browser runs headless by default. To watch it while the tests run,
set `PLAYWRIGHT_HEADED=1` — the Chromium window opens on the host's display:

```bash
PLAYWRIGHT_HEADED=1 python src/manage.py test \
  news.tests.tests_playwright \
  homepages.tests.tests_playwright
```

Optionally set `PLAYWRIGHT_SLOW_MO=<milliseconds>` to slow the browser actions
down and make them easier to follow:

```bash
PLAYWRIGHT_HEADED=1 PLAYWRIGHT_SLOW_MO=450 python src/manage.py test \
  news.tests.tests_playwright \
  homepages.tests.tests_playwright
```

This requires the Playwright server to run on the same machine and display as
the tests (the devenv setup does this).

## How it works

- `REMOTE_PLAYWRIGHT_SERVER` var env tells Django where the Playwright server is.
  - e.g.: REMOTE_PLAYWRIGHT_SERVER = "ws://127.0.0.1:3651";
- the Django live server binds to `127.0.0.1` when the Playwright server is on
  localhost, and to the container's network IP when it is on another
  host (Docker/CI), so the remote browser can reach it.
