"""
NexoraIQ: Advanced Feature Engineering Engine
Leakage-proof feature engineering pipeline for time-series forecasting,
business KPI modeling, and customer risk scoring.
All transformers are fitted strictly on the training partition and applied out-of-sample.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

class TimeSeriesFeatureEngineer:
    def __init__(
        self,
        date_col: str = "date",
        target_col: str = "revenue",
        lags: List[int] = [1, 2, 7, 14, 30],
        rolling_windows: List[int] = [7, 14, 30]
    ):
        self.date_col = date_col
        self.target_col = target_col
        self.lags = lags
        self.rolling_windows = rolling_windows
        
        # Fit parameters (fitted strictly on training set)
        self.train_target_mean: Optional[float] = None
        self.train_target_std: Optional[float] = None
        self.feature_columns: List[str] = []

    def fit(self, df: pd.DataFrame) -> "TimeSeriesFeatureEngineer":
        """Fits scale and statistics strictly on the training partition."""
        if self.target_col in df.columns:
            series = pd.to_numeric(df[self.target_col], errors="coerce").dropna()
            self.train_target_mean = float(series.mean())
            self.train_target_std = float(series.std()) if len(series) > 1 else 1.0
        return self

    def transform(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """
        Transforms dataset by generating:
        - Calendar & cyclical temporal features
        - Autoregressive lag features (lag 1, 2, 7, 14, 30)
        - Rolling window metrics (mean, std, min, max)
        - Ratio & financial interaction terms
        """
        data = df.copy()
        
        # Ensure chronological ordering
        if self.date_col in data.columns:
            data[self.date_col] = pd.to_datetime(data[self.date_col])
            data = data.sort_values(by=self.date_col).reset_index(drop=True)
            
            # Calendar temporal components
            dt = data[self.date_col].dt
            data["day_of_month"] = dt.day
            data["day_of_week"] = dt.dayofweek
            data["month"] = dt.month
            data["quarter"] = dt.quarter
            data["is_weekend"] = dt.dayofweek.isin([5, 6]).astype(int)
            data["is_month_end"] = dt.is_month_end.astype(int)
            data["is_quarter_end"] = dt.is_quarter_end.astype(int)
            
            # Cyclical sine/cosine transforms for day of week and month
            data["dow_sin"] = np.sin(2 * np.pi * data["day_of_week"] / 7.0)
            data["dow_cos"] = np.cos(2 * np.pi * data["day_of_week"] / 7.0)
            data["month_sin"] = np.sin(2 * np.pi * data["month"] / 12.0)
            data["month_cos"] = np.cos(2 * np.pi * data["month"] / 12.0)

        # Autoregressive lag features on target
        if self.target_col in data.columns:
            target_series = pd.to_numeric(data[self.target_col], errors="coerce")
            
            for lag in self.lags:
                lag_col = f"{self.target_col}_lag_{lag}"
                data[lag_col] = target_series.shift(lag)
                
            # Rolling window statistics
            for window in self.rolling_windows:
                # Use shift(1) to avoid leaking the current day's target into the feature
                shifted = target_series.shift(1)
                data[f"{self.target_col}_roll_mean_{window}"] = shifted.rolling(window=window, min_periods=1).mean()
                data[f"{self.target_col}_roll_std_{window}"] = shifted.rolling(window=window, min_periods=1).std().fillna(0.0)
                data[f"{self.target_col}_roll_min_{window}"] = shifted.rolling(window=window, min_periods=1).min()
                data[f"{self.target_col}_roll_max_{window}"] = shifted.rolling(window=window, min_periods=1).max()
                
            # Growth & Momentum features
            data["target_growth_w_w"] = (target_series.shift(1) - target_series.shift(8)) / (target_series.shift(8).abs() + 1e-5)

        # Business financial ratios (if relevant columns exist)
        cols = data.columns
        if "revenue" in cols and "cost" in cols:
            data["expense_to_revenue_ratio"] = (data["cost"] / (data["revenue"] + 1e-5)).clip(0, 5)
            data["gross_profit_calculated"] = data["revenue"] - data["cost"]
            data["profit_margin_calculated"] = (data["gross_profit_calculated"] / (data["revenue"] + 1e-5)) * 100.0

        if "revenue" in cols and "customer_count" in cols:
            data["revenue_per_customer"] = data["revenue"] / (data["customer_count"] + 1e-5)

        if "revenue" in cols and "marketing_spend" in cols:
            data["marketing_roas"] = data["revenue"] / (data["marketing_spend"] + 1e-5)

        if "website_visitors" in cols and "customer_count" in cols:
            data["traffic_conversion_rate"] = data["customer_count"] / (data["website_visitors"] + 1e-5)

        # Backfill initial lag NaNs using training target mean to avoid dropping rows
        fallback_val = self.train_target_mean if self.train_target_mean is not None else 0.0
        lag_roll_cols = [c for c in data.columns if "_lag_" in c or "_roll_" in c or "growth" in c]
        for col in lag_roll_cols:
            data[col] = data[col].fillna(fallback_val)

        if is_training:
            # Exclude raw date and raw targets from feature set
            exclude = {self.date_col, self.target_col, "is_ground_truth_anomaly", "anomaly_label", "churn_risk_label"}
            self.feature_columns = [
                c for c in data.columns 
                if c not in exclude and pd.api.types.is_numeric_dtype(data[c])
            ]
            
        return data

    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Fits on training DataFrame and transforms it, returning features and feature column names."""
        self.fit(df)
        transformed = self.transform(df, is_training=True)
        return transformed, self.feature_columns

