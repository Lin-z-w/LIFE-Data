# ICNP 2026 Camera-Ready Data Record

## Scope

This repository preserves the compact experiment data associated with the LIFE paper. The ICNP 2026 camera-ready revision added Linux kernel baselines, updated LIFE v11 runs, LeoCC results, and revised fairness experiments.

## Tracked additions

The camera-ready data commit adds the manageable LeoCC results used by the updated evaluation:

- `origin_data/standard/LeoCC/`
- `origin_data/throughput/congest/LeoCC/`
- `origin_data/throughput/rain/LeoCC/`
- `origin_data/throughput/random_loss/LeoCC/`
- `origin_data/throughput/reconfig&hadover/LeoCC/`
- `origin_data/intra-protocol/2flow/LeoCC/`
- `origin_data/inter-protocol/LIFE+LeoCC/`

## Large local archive

The full camera-ready rerun tree is retained locally under `camera_ready/`. It contains raw logs, build directories, repeated runs, seed searches, diagnostic plots, and intermediate candidates totaling approximately 52 GB. The sensitivity archive under `origin_data/sensitivity/` is approximately 1.3 GB. These directories are intentionally excluded from normal Git commits.

The final paper repository stores the selected figures and the plotting scripts used for the submitted camera-ready version. Large raw archives should be transferred with an artifact or object-storage workflow if they need to be published later; they should not be added to this Git repository wholesale.

## Version

- Data branch: `main`
- Camera-ready tag: `icnp-2026-camera-ready-data`
- Finalization date: 2026-08-25
