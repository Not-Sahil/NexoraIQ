"""
NexoraIQ: Production Forecasting Engine
Implements:
- Chronological splitting (70% train, 15% val, 15% test)
- Benchmarks: Naive baseline, Seasonal Naive, Ridge/Linear, Random Forest, XGBoost, LightGBM, ARIMA
- Multi-metric evaluation: MAE, RMSE, MAPE, sMAPE, R2
- Model selection based on validation set performance
- Final evaluation on untouched test set
- Recursive multi-step out-of-sample forecasting with confidence intervals
"""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

# Try importing gradient boosted trees
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except Exception:
    HAS_LIGHTGBM = False

from ml_engine.feature_engineering.pipeline import TimeSeriesFeatureEngineer

class BusinessForecastingEngine:
    def __init__(
        self,
        date_col: str = "date",
        target_col: str = "revenue",
        forecast_horizon: int = 30
    ):
        self.date_col = date_col
        self.target_col = target_col
        self.forecast_horizon = forecast_horizon
        self.feature_engineer = TimeSeriesFeatureEngineer(date_col=date_col, target_col=target_col)
        
        self.trained_models: Dict[str, Any] = {}
        self.validation_metrics: Dict[str, Dict[str, float]] = {}
        self.test_metrics: Dict[str, Dict[str, float]] = {}
        self.best_model_name: Optional[str] = None
        self.best_model: Optional[Any] = None

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculates MAE, RMSE, MAPE, sMAPE, and R2 with zero-division protection."""
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)
        
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        
        # MAPE with non-zero filter
        non_zero = y_true != 0
        if np.any(non_zero):
            mape = float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100.0)
        else:
            mape = 0.0
            
        # sMAPE
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
        non_zero_denom = denominator != 0
        if np.any(non_zero_denom):
            smape = float(np.mean(np.abs(y_pred[non_zero_denom] - y_true[non_zero_denom]) / denominator[non_zero_denom]) * 100.0)
        else:
            smape = 0.0
            
        r2 = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else 1.0
        
        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "smape": round(smape, 2),
            "r2": round(r2, 4)
        }

    def partition_chronological(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Chronological split strictly: 70% Train, 15% Validation, 15% Testing."""
        data = df.sort_values(by=self.date_col).reset_index(drop=True)
        n = len(data)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = data.iloc[:train_idx].copy()
        val_df = data.iloc[train_idx:val_idx].copy()
        test_df = data.iloc[val_idx:].copy()
        
        return train_df, val_df, test_df

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Full Training, Tuning, Validation, and Model Selection Workflow:
        1. Chronological splitting (Train 70%, Val 15%, Test 15%)
        2. Feature Engineering fitted on Train only
        3. Train Candidate Models (Naive, Seasonal Naive, Ridge, RF, XGBoost, LightGBM, ARIMA)
        4. Validate on untouched Validation partition
        5. Select Winner model with lowest Validation RMSE
        6. Evaluate Winner model on untouched Test partition
        """
        train_df, val_df, test_df = self.partition_chronological(df)
        
        # Fit Feature Engineer strictly on Train
        train_feat, feature_cols = self.feature_engineer.fit_transform(train_df)
        val_feat = self.feature_engineer.transform(val_df)
        test_feat = self.feature_engineer.transform(test_df)
        
        X_train, y_train = train_feat[feature_cols].fillna(0), train_feat[self.target_col].values
        X_val, y_val = val_feat[feature_cols].fillna(0), val_feat[self.target_col].values
        X_test, y_test = test_feat[feature_cols].fillna(0), test_feat[self.target_col].values
        
        candidates: Dict[str, Any] = {
            "Naive Baseline": "baseline_naive",
            "Seasonal Naive (7D)": "baseline_seasonal_7",
            "Ridge Regression": Ridge(alpha=1.0, random_state=42),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        }
        
        if HAS_XGBOOST:
            candidates["XGBoost Regressor"] = xgb.XGBRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42, verbosity=0
            )
        if HAS_LIGHTGBM:
            candidates["LightGBM Regressor"] = lgb.LGBMRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42, verbose=-1
            )
            
        model_comparison = []
        
        for name, model in candidates.items():
            try:
                if name == "Naive Baseline":
                    # Last known value in training set
                    val_pred = np.full(len(y_val), y_train[-1])
                    val_metrics = self.calculate_metrics(y_val, val_pred)
                elif name == "Seasonal Naive (7D)":
                    period = 7 if len(y_train) >= 7 else 1
                    val_pred = []
                    combined = np.concatenate([y_train, y_val])
                    for i in range(len(y_val)):
                        val_pred.append(combined[len(y_train) + i - period])
                    val_pred = np.array(val_pred)
                    val_metrics = self.calculate_metrics(y_val, val_pred)
                else:
                    model.fit(X_train, y_train)
                    val_pred = model.predict(X_val)
                    val_metrics = self.calculate_metrics(y_val, val_pred)
                    self.trained_models[name] = model

                self.validation_metrics[name] = val_metrics
                model_comparison.append({
                    "model_name": name,
                    "val_mae": val_metrics["mae"],
                    "val_rmse": val_metrics["rmse"],
                    "val_mape": val_metrics["mape"],
                    "val_smape": val_metrics["smape"],
                    "val_r2": val_metrics["r2"]
                })
            except Exception as e:
                warnings.warn(f"Failed training {name}: {e}")
                
        # Fit ARIMA candidate
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                arima = ARIMA(y_train, order=(2, 1, 1))
                arima_fit = arima.fit()
                arima_val_pred = arima_fit.forecast(steps=len(y_val))
                arima_val_metrics = self.calculate_metrics(y_val, arima_val_pred)
                self.validation_metrics["ARIMA (2,1,1)"] = arima_val_metrics
                self.trained_models["ARIMA (2,1,1)"] = arima_fit
                model_comparison.append({
                    "model_name": "ARIMA (2,1,1)",
                    "val_mae": arima_val_metrics["mae"],
                    "val_rmse": arima_val_metrics["rmse"],
                    "val_mape": arima_val_metrics["mape"],
                    "val_smape": arima_val_metrics["smape"],
                    "val_r2": arima_val_metrics["r2"]
                })
        except Exception as e:
            warnings.warn(f"Failed ARIMA: {e}")

        # Model selection: Lowest validation RMSE among ML models
        valid_candidates = [m for m in model_comparison if m["model_name"] in self.trained_models]
        if not valid_candidates:
            valid_candidates = model_comparison
            
        best = min(valid_candidates, key=lambda x: x["val_rmse"])
        self.best_model_name = best["model_name"]
        self.best_model = self.trained_models.get(self.best_model_name)
        
        # Evaluate Best Model on UNTOUCHED Test Data
        if self.best_model is not None:
            if "ARIMA" in self.best_model_name:
                test_pred = self.best_model.forecast(steps=len(y_test))
            else:
                test_pred = self.best_model.predict(X_test)
            test_metrics = self.calculate_metrics(y_test, test_pred)
        else:
            test_pred = np.full(len(y_test), y_train[-1])
            test_metrics = self.calculate_metrics(y_test, test_pred)
            
        self.test_metrics[self.best_model_name] = test_metrics

        # Generate future forecast points
        future_forecast = self.generate_future_forecast(df, steps=self.forecast_horizon)
        
        # Historical actuals vs validation predictions for chart comparison
        history_points = []
        for idx, row in df.tail(60).iterrows():
            history_points.append({
                "date": str(row[self.date_col])[:10],
                "actual": float(row[self.target_col]),
                "type": "historical"
            })
            
        return {
            "best_model_name": self.best_model_name,
            "validation_metrics": self.validation_metrics[self.best_model_name],
            "test_metrics": test_metrics,
            "model_comparison": model_comparison,
            "future_forecast": future_forecast,
            "history_tail": history_points,
            "features_used": feature_cols
        }

    def generate_future_forecast(self, full_df: pd.DataFrame, steps: int = 30) -> List[Dict[str, Any]]:
        """
        Recursive multi-step forward projection:
        Generates genuine future dates, recursively advances lag features,
        and computes confidence interval envelopes (+- 1.96 * residual std).
        """
        data = full_df.sort_values(by=self.date_col).reset_index(drop=True)
        last_date = pd.to_datetime(data[self.date_col].iloc[-1])
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq="D")
        
        # Standard error estimation from validation residuals
        best_val_rmse = self.validation_metrics.get(self.best_model_name, {}).get("rmse", 500.0)
        
        predictions = []
        current_data = data.copy()
        
        if "ARIMA" in str(self.best_model_name):
            try:
                arima = ARIMA(data[self.target_col].values, order=(2, 1, 1))
                fit = arima.fit()
                fc = fit.get_forecast(steps=steps)
                predicted_vals = fc.predicted_mean
                conf_int = fc.conf_int()
                
                for i, f_date in enumerate(future_dates):
                    pred_val = max(0.0, float(predicted_vals[i]))
                    lower = max(0.0, float(conf_int[i, 0]))
                    upper = float(conf_int[i, 1])
                    predictions.append({
                        "date": f_date.strftime("%Y-%m-%d"),
                        "predicted_value": round(pred_val, 2),
                        "lower_bound": round(lower, 2),
                        "upper_bound": round(upper, 2),
                        "confidence_level": 0.95
                    })
                return predictions
            except Exception:
                pass

        # For Tree / Linear ML Models: Recursive Step-by-Step
        for step_idx, f_date in enumerate(future_dates):
            # Transform current data buffer
            feat_df = self.feature_engineer.transform(current_data)
            latest_row = feat_df.iloc[-1:][self.feature_engineer.feature_columns].fillna(0)
            
            if self.best_model is not None and hasattr(self.best_model, "predict"):
                pred_val = float(self.best_model.predict(latest_row)[0])
            else:
                pred_val = float(current_data[self.target_col].iloc[-1])
                
            pred_val = max(0.0, round(pred_val, 2))
            
            # Uncertainty expands moderately over future horizon
            horizon_spread = 1.0 + (step_idx * 0.025)
            margin = best_val_rmse * 1.96 * horizon_spread
            lower_bound = max(0.0, round(pred_val - margin, 2))
            upper_bound = round(pred_val + margin, 2)
            
            predictions.append({
                "date": f_date.strftime("%Y-%m-%d"),
                "predicted_value": pred_val,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence_level": 0.95
            })
            
            # Append synthesized row to buffer for recursive next step
            new_row = {col: 0 for col in current_data.columns}
            new_row[self.date_col] = f_date
            new_row[self.target_col] = pred_val
            current_data = pd.concat([current_data, pd.DataFrame([new_row])], ignore_index=True)

        return predictions

