# Repository Guidelines

## Project Structure & Module Organization
- `src/`: core logic
  - `src/config.py`: thresholds + manual overrides for rates/prices/dividends
  - `src/strategy_a_share.py`: A-share ETF dividend-vs-rate spread signal
  - `src/strategy_hk_us.py`: HK stocks (manual dividend) spread signal
  - `src/advisor.py`: combines signals into a monthly allocation plan
- Docs: `README.md` (quick start), `INVESTMENT_SOP.md` (workflow), `PROMPT_AGENT.md` (agent runbook).
- Entry points: modules are intended to be run via `uv run -m ...` (not imported as a library).

## Build, Test, and Development Commands
- Install deps (uses `uv.lock`): `uv sync`
- Run A-share signal: `uv run -m src.strategy_a_share`
- Run HK signal: `uv run -m src.strategy_hk_us`
- Run both (monthly workflow): `./run.sh`
- Generate full plan with budget: `uv run -m src.advisor 20000`

## Coding Style & Naming Conventions
- Python `>=3.12` (see `.python-version`), 4-space indentation, PEP 8-friendly formatting.
- Prefer clear function names (`analyze`, `get_data`) and constants in `UPPER_SNAKE_CASE`.
- Keep strategy modules side-effect light: data-fetch in helpers, decision logic in `analyze()`, printing in `run()`.
- Do not commit generated artifacts: `__pycache__/`, `.venv/` (already in `.gitignore`).

## Testing Guidelines
- No test suite yet. If adding tests, use `pytest`, place files under `tests/` as `test_*.py`, and run with `uv run -m pytest`.

## Commit & Pull Request Guidelines
- Git history is currently empty; use a simple Conventional Commits style: `feat: …`, `fix: …`, `docs: …`, `chore: …`.
- PRs: describe the change, include before/after output (terminal paste) for strategy changes, and note any config assumptions (manual overrides vs live fetch).

## Security & Configuration Tips
- Avoid committing personal financial details or API credentials.
- After manual runs, revert temporary overrides in `src/config.py` back to `None` to keep future runs reproducible.
