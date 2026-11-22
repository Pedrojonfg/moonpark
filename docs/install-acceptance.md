# Install acceptance (D-a91c)

Workflow: **Desktop installers** (`.github/workflows/desktop-release.yml`), job **Install acceptance smoke**.

Per OS matrix leg (linux, windows, macos), after `deploy/build-desktop.sh`:

1. Bundled `moonpark-api` starts on loopback port 8765.
2. `GET /health` succeeds.
3. `GET /session-memory` returns budget fields.
4. `GET /site?mock=1&local_search=1` returns a non-empty leaderboard.
5. `POST /deep-search` with `"mock": true` returns non-empty `export_rows`.

**Platform claims:** README and release notes may call Linux or Windows *supported* only when the matching leg is green on the release tag. **macOS:** the installer may ship when the macOS build is green; do **not** claim maintainer-tested Mac hardware — CI build + engine smoke on `macos-latest` is not the same as a user Mac walkthrough (`D-a91c`).

Heavy S12 validation uses marker `validation_full` and workflow **Validation full** (`.github/workflows/validation-full.yml`); default CI excludes those tests (`D-b591`).