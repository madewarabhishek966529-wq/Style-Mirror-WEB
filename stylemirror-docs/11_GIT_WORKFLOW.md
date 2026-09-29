# 11 — Git & Auto-Push Workflow

## Rule (mandatory for AI coding assistants)
Whenever you **create a new folder or new files in ANY language or format** and the code is in a working state, **commit and push to GitHub automatically**, without waiting to be asked.

**Applies to all languages and file types**, for example:
- Dart / Flutter: `.dart`, `pubspec.yaml`
- Python: `.py`, `requirements.txt`, `pyproject.toml`
- JavaScript / TypeScript: `.js`, `.ts`
- Web: `.html`, `.css`, `.scss`
- SQL / migrations: `.sql`
- Kotlin / Java / Swift / Objective-C (native Android/iOS code)
- Shell / YAML / JSON / TOML / config files
- Docs and assets: `.md`, `.svg`, `.png`, `.jpg` (style thumbnails only)

This applies to every part of the repo: `apps/web`, `apps/api`, `apps/mobile`, `scripts`, `assets`, docs.

## Auto-Push Procedure
Run after each logical unit (new folder, new feature file set, finished task):

```bash
git add -A
git status --short              # sanity check: no secrets, no build output
git commit -m "<type>(<scope>): <short summary>"
git push origin HEAD
```

If the branch has no upstream yet:
```bash
git push -u origin HEAD
```

## Commit Message Format (Conventional Commits)
`feat(api): add /uploads endpoint`
`feat(web): add styleGrid.js module`
`feat(mobile): add lib/features/tryon/ folder with dart files
feat(api): add services/ folder with python files
feat(web): add js/ modules and css/ files`
`docs: update API spec`
`chore: add .gitignore`

## Branching
- `main` — stable, deployable. Do not push half-broken code here.
- `dev` — default working branch; auto-push here.
- `feat/<name>` — larger features; open a PR into `dev`.

## Safety Rules (never skip)
1. **Never commit secrets:** `.env`, AI provider API keys, service-account JSON, keystores. Only `.env.example`.
2. Confirm `.gitignore` exists **before the first push**.
3. **No force push** (`--force`) unless the user explicitly asks.
4. Do not push if tests/lint/analyze fail — fix first.
5. Do not commit user photos, generated outputs, `storage/`, the SQLite `.db` file, `.venv`, `build/`, `.dart_tool/`.
6. If `git push` fails (auth, conflict, no remote): stop, report the exact error, do not retry destructively. Use `git pull --rebase origin <branch>` for simple divergence.

## One-Time Setup
```bash
git init
git branch -M main
git remote add origin https://github.com/<username>/stylemirror.git
git checkout -b dev
git add -A && git commit -m "chore: initial project docs and structure"
git push -u origin dev
```
Authenticate with a GitHub PAT or SSH key stored in your OS credential manager — never in the repo.

## Recommended `.gitignore`
```gitignore
# env & secrets
.env
.env.*
!.env.example
*.pem
*.jks
*.keystore
service-account*.json
google-services.json.local

# python
__pycache__/
*.db
stylemirror.db
.venv/
*.pyc
.pytest_cache/

# node / next
node_modules/
.next/
out/

# flutter / dart
.dart_tool/
.packages
build/
.flutter-plugins
.flutter-plugins-dependencies
*.iml
.idea/

# app data
storage/
tmp/
*.log
.DS_Store
```

## Pre-Push Checks
| Area | Command |
|---|---|
| Dart/Flutter | `dart format . && flutter analyze && flutter test` |
| Python | `ruff check . && ruff format --check . && pytest -q` |
| HTML/CSS/JS | `npx eslint frontend/js` and `npx htmlhint frontend/*.html` (if configured) |
| SQL | run migrations on a local/test DB |
| Kotlin/Java (Android) | `./gradlew lint test` |
| Swift (iOS) | `xcodebuild test` |
| Shell | `shellcheck *.sh` |
| YAML/JSON | validate syntax (`python -m json.tool`, `yamllint`) |
| Docs/other | no check; ensure no secrets |

If a language has no configured checker yet, skip the check but still verify `git status` shows no secrets or build output before pushing.

Optional: enforce with a `pre-push` git hook or GitHub Actions CI.
