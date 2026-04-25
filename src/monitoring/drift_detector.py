"""
Data drift detection using Kolmogorov-Smirnov test.
Compares live inference data distributions against training baseline.
Triggers retraining alerts when enough features have drifted.
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
from src.utils.config import config
from src.utils.logger import get_logger
from src.monitoring.metrics_exporter import FEATURE_DRIFT_SCORE, DRIFT_ALERT

log = get_logger("drift_detector")


class DriftDetector:
    """Detects distributional shift between baseline and live data."""

    def __init__(self, baseline_path: str = "data/processed/baseline_stats.json"):
        self.baseline_path = baseline_path
        self.baseline: dict = {}
        self._load_baseline()

    def _load_baseline(self) -> None:
        try:
            with open(self.baseline_path) as f:
                self.baseline = json.load(f)
            log.info(f"Loaded baseline stats for {len(self.baseline)} features")
        except FileNotFoundError:
            log.warning(f"Baseline not found at {self.baseline_path}. Drift detection disabled.")

    def detect(self, live_data: pd.DataFrame) -> dict:
        """Run KS test drift detection on a batch of live data.

        Args:
            live_data: DataFrame of current inference features.

        Returns:
            dict mapping feature name to drift score and alert flag.
        """
        if not self.baseline:
            return {}

        results = {}
        for feature, stats_dict in self.baseline.items():
            if feature not in live_data.columns:
                continue
            live_values = live_data[feature].dropna().values
            if len(live_values) < 30:
                continue

            # Reconstruct baseline sample from stored statistics
            baseline_sample = np.random.normal(
                loc=stats_dict["mean"],
                scale=max(stats_dict["std"], 1e-6),
                size=1000,
            )
            baseline_sample = np.clip(baseline_sample, stats_dict["min"], stats_dict["max"])

            ks_stat, p_value = stats.ks_2samp(baseline_sample, live_values)
            is_drifted = p_value < config.drift_threshold

            results[feature] = {
                "ks_stat": float(ks_stat),
                "p_value": float(p_value),
                "is_drifted": is_drifted,
            }

            # Update Prometheus metrics
            FEATURE_DRIFT_SCORE.labels(feature_name=feature).set(ks_stat)
            if is_drifted:
                DRIFT_ALERT.labels(feature_name=feature).inc()
                log.warning(f"DRIFT DETECTED: {feature} | KS={ks_stat:.4f}, p={p_value:.4f}")

        drifted = [f for f, r in results.items() if r["is_drifted"]]
        if drifted:
            log.warning(f"Drift in {len(drifted)} features: {drifted}")
        else:
            log.info("No drift detected in this batch")

        return results

    def should_retrain(self, drift_results: dict) -> bool:
        """Return True if 3 or more features have drifted — triggers retraining."""
        drifted_count = sum(1 for r in drift_results.values() if r.get("is_drifted"))
        return drifted_count >= 3