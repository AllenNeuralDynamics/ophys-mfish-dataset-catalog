This repository stores canonical JSON metadata records for ophys-mFISH mice, including round-level assets, derived outputs, and specimen annotations.

## Example Record

```json
{
  "schema_version": "1.0.0",
  "mouse_id": "782149",
  "rounds": {
    "R1": "HCR_782149_2025-11-05_13-00-00_processed_2025-11-10_20-37-29",
    "R2": "HCR_782149_2025-11-12_13-00-00_processed_2025-11-13_22-04-32",
    "R3": "HCR_782149_2025-11-19_13-00-00_processed_2025-11-21_01-27-24",
    "R4": "HCR_782149_2025-12-04_13-00-00_processed_2025-12-05_22-31-35",
    "R5": "HCR_782149_2025-12-11_13-00-00_processed_2025-12-12_23-45-26"
  },
  "mouse_metadata": {
    "species": "mouse",
    "nickname": "Lemongrass"
  },
  "derived_assets": {
    "roi_shape_metrics": "HCR_782149_2025-11-05_13-00-00_roi-shape-metrics",
    "cell_typing": "HCR_782149_cell-typing_2026-03-09_12-00-00"
  },
  "notes": [
    "This collection is for pre laser changes on 2026-03-12.",
    "Sample is missing a gene."
  ]
}
```