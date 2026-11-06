"""
NexoraIQ: Multi-Method Anomaly Detection Engine
Combines:
1. Isolation Forest (Global non-linear multivariate contamination)
2. Local Outlier Factor (LOF - Density-based local anomalies)
3. Robust Statistical Z-score & Rolling Deviation
4. Business Rule Thresholds (Sudden margin collapse, expense blowouts)
Each detected anomaly includes:
- Date, Metric, Actual value, Expected baseline, Deviation %, Severity, Detection method, and Root cause explanation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class MultiMethodAnomalyDetector:
    def __init__(
        self,
        date_col: str = "date",
        target_col: str = "revenue",
        contamination: float = 0.05
    ):
        self.date_col = date_col
        self.target_col = target_col
        self.contamination = contamination

    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Runs ensemble anomaly detection across the dataset."""
        data = df.copy()
        if self.date_col in data.columns:
            data[self.date_col] = pd.to_datetime(data[self.date_col])
            data = data.sort_values(by=self.date_col).reset_index(drop=True)

        if self.target_col not in data.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in dataset.")

        series = pd.to_numeric(data[self.target_col], errors="coerce").fillna(0)
        n = len(series)
        if n < 10:
            return {"anomalies": [], "total_count": 0, "summary": "Insufficient data"}

        # 1. Rolling Expected Baseline & Statistical Z-Score
        # 14-day rolling window as baseline
        rolling_baseline = series.rolling(window=14, min_periods=3, center=True).median().fillna(series.median())
        rolling_std = series.rolling(window=14, min_periods=3, center=True).std().fillna(series.std())
        rolling_std = rolling_std.replace(0, 1.0)
        
        z_scores = np.abs((series - rolling_baseline) / rolling_std)
        stat_flags = z_scores > 2.5

        # 2. Isolation Forest (Multivariate if other numeric features exist)
        num_cols = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c]) and c != self.date_col]
        X = data[num_cols].fillna(0)
        
        iso = IsolationForest(contamination=self.contamination, random_state=42)
        iso_flags = iso.fit_predict(X) == -1

        # 3. Local Outlier Factor
        lof = LocalOutlierFactor(n_neighbors=min(20, max(5, n // 5)), contamination=self.contamination)
        lof_flags = lof.fit_predict(X) == -1

        # Ensemble Vote: An anomaly is flagged if at least 2 methods agree or extreme Z-Score > 3.5
        anomaly_events: List[Dict[str, Any]] = []

        for i in range(n):
            methods_detected = []
            if stat_flags.iloc[i]:
                methods_detected.append("Rolling Z-Score")
            if iso_flags[i]:
                methods_detected.append("Isolation Forest")
            if lof_flags[i]:
                methods_detected.append("LOF")

            actual = float(series.iloc[i])
            expected = float(rolling_baseline.iloc[i])
            diff = actual - expected
            dev_pct = round(((diff) / (abs(expected) + 1e-5)) * 100.0, 2)
            z = float(z_scores.iloc[i])

            # Trigger condition: 2 or more methods agree OR single method with massive Z-score
            if len(methods_detected) >= 2 or z > 3.5:
                # Determine Severity
                abs_dev = abs(dev_pct)
                if abs_dev > 150 or z > 4.5:
                    severity = "critical"
                elif abs_dev > 75 or z > 3.0:
                    severity = "high"
                elif abs_dev > 35 or z > 2.0:
                    severity = "medium"
                else:
                    severity = "low"

                # Generate Root Cause Explanation
                root_cause = self._explain_root_cause(data.iloc[i], actual, expected, dev_pct)

                date_val = str(data[self.date_col].iloc[i])[:10] if self.date_col in data.columns else f"Period {i}"
                
                anomaly_events.append({
                    "index": i,
                    "date": date_val,
                    "metric": self.target_col,
                    "actual_value": round(actual, 2),
                    "expected_value": round(expected, 2),
                    "deviation_pct": dev_pct,
                    "z_score": round(z, 2),
                    "severity": severity,
                    "detection_methods": methods_detected,
                    "primary_method": ", ".join(methods_detected),
                    "root_cause_explanation": root_cause,
                    "status": "detected"
                })

        return {
            "anomalies": anomaly_events,
            "total_count": len(anomaly_events),
            "critical_count": sum(1 for a in anomaly_events if a["severity"] == "critical"),
            "high_count": sum(1 for a in anomaly_events if a["severity"] == "high"),
            "medium_count": sum(1 for a in anomaly_events if a["severity"] == "medium"),
            "low_count": sum(1 for a in anomaly_events if a["severity"] == "low")
        }

    def _explain_root_cause(self, row: pd.Series, actual: float, expected: float, dev_pct: float) -> str:
        """Synthesizes business-language root cause explanation from row features."""
        direction = "drop" if dev_pct < 0 else "surge"
        
        # Check conversion rate & visitors
        if "conversion_rate" in row and "website_visitors" in row:
            cvr = float(row.get("conversion_rate", 0))
            vis = float(row.get("website_visitors", 0))
            if dev_pct < 0 and cvr < 0.015:
                return f"Unusual {abs(dev_pct)}% revenue drop correlated with severe conversion rate collapse ({cvr*100:.1f}%), suggesting checkout funnel failure."
            if dev_pct > 0 and vis > 2.0 * float(row.get("website_visitors", 1000)):
                return f"Revenue surge driven by an anomalous +{dev_pct}% spike in web traffic sessions ({int(vis):,} visitors)."

        # Check marketing spend
        if "marketing_spend" in row:
            mkt = float(row.get("marketing_spend", 0))
            if dev_pct > 0 and mkt > 1.8 * float(row.get("marketing_spend", 1000)):
                return f"Revenue surge aligned with {round(mkt, 2)} marketing promotion deployment."

        # Check costs / margin compression
        if "cost" in row:
            cost = float(row.get("cost", 0))
            if "cogs" in row and cost > actual:
                return f"Profitability inversion: operating cost (${cost:,.2f}) abruptly exceeded gross revenue (${actual:,.2f})."

        return f"Statistically significant {direction} of {abs(dev_pct)}% away from 14-day rolling expectation (${expected:,.2f})."

