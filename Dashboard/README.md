# Fleet Watch — Predictive Maintenance Dashboard

## Files
- `index.html` — page structure
- `styles.css` — all styling (dark control-room theme)
- `data.js` — dataset summary + model comparison + feature importance, computed from `cleaned_predictive_maintenance_dataset.csv`
- `app.js` — charts, live feed simulation, risk scoring, emergency modal, fleet table logic

## Run it
No build step, no dependencies to install. Just open `index.html` in a browser
(or use the VS Code "Live Server" extension for auto-reload while editing).

## How the risk score works
`app.js` scores each simulated reading against this dataset's own percentile
bands (see `data.js` → `percentiles`), weighted by each feature's real
correlation with `failure` in the CSV (Vibration, Torque, and Current are the
strongest predictors here). A score ≥ 72 triggers the emergency popup. This is
a transparent rule-based stand-in — the trained `.pkl` model can't run
client-side in a browser, so it isn't wired in.

## Known approximations
- Model comparison numbers (`app.js` → `MODEL_COMPARISON` inside `data.js`)
  are read off the provided `model_comparison.png` chart, not an exact
  metrics table — the notebook only contained EDA.
- Feature importance values are similarly approximate reads from
  `feature_importance.png`.

## Customizing
- Change the critical threshold in `app.js` → `riskTier()`.
- Change simulation speed in `app.js` → `setPlaying()` (`1800` ms interval).
- Swap the color tokens at the top of `styles.css` (`:root { --bg ... }`) to retheme.
