"""
NexoraIQ: Explainable AI (XAI) Engine
Integrates SHAP (SHapley Additive exPlanations) & Feature Contribution Attribution
Transforms technical mathematical feature impacts into human-readable business narratives.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import shap

class BusinessExplainabilityEngine:
    def explain_model_predictions(
        self,
        model: Any,
        feature_data: pd.DataFrame,
        feature_names: List[str],
        max_samples: int = 50
    ) -> Dict[str, Any]:
        """
        Computes SHAP values and feature impacts.
        Provides both global feature importance and sample-level directional contributions.
        """
        X = feature_data[feature_names].fillna(0)
        sample = X.tail(max_samples)
        
        feature_impacts = []
        narratives = []
        
        try:
            # TreeExplainer for Tree-based models (RandomForest, XGBoost, LightGBM)
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(sample)
            
            # Handle multi-output or single-output
            if isinstance(shap_values, list):
                shap_matrix = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            else:
                shap_matrix = shap_values
                
            mean_abs_shap = np.mean(np.abs(shap_matrix), axis=0)
            
            # Most recent observation's directional contribution
            latest_shap = shap_matrix[-1]
            latest_features = sample.iloc[-1].to_dict()
            
            for i, feat in enumerate(feature_names):
                impact_mag = float(mean_abs_shap[i])
                directional_val = float(latest_shap[i])
                
                direction = "positive" if directional_val > 0 else "negative"
                feature_impacts.append({
                    "feature": feat,
                    "global_importance": round(impact_mag, 4),
                    "latest_value": round(float(latest_features[feat]), 2),
                    "directional_impact": round(directional_val, 4),
                    "direction": direction
                })
                
            feature_impacts.sort(key=lambda x: x["global_importance"], reverse=True)
            
            # Construct Business Language Narrative
            top_positive = [f["feature"] for f in feature_impacts if f["direction"] == "positive"][:2]
            top_negative = [f["feature"] for f in feature_impacts if f["direction"] == "negative"][:2]
            
            narrative = "Model prediction analysis: "
            if top_positive:
                narrative += f"Upward performance is supported primarily by strength in {', '.join(top_positive)}. "
            if top_negative:
                narrative += f"Downward pressure is exerted by {', '.join(top_negative)}. "
                
            return {
                "status": "success",
                "method": "SHAP TreeExplainer",
                "feature_impacts": feature_impacts[:12],
                "business_narrative": narrative
            }

        except Exception as e:
            # Fallback to model feature_importances_ or coefficients
            warnings.warn(f"SHAP explanation fallback triggered: {e}")
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                for feat, imp in zip(feature_names, importances):
                    feature_impacts.append({
                        "feature": feat,
                        "global_importance": round(float(imp), 4),
                        "latest_value": round(float(sample[feat].iloc[-1]), 2),
                        "directional_impact": 0.0,
                        "direction": "neutral"
                    })
                feature_impacts.sort(key=lambda x: x["global_importance"], reverse=True)
                top_3 = [f["feature"] for f in feature_impacts[:3]]
                narrative = f"Prediction is most heavily influenced by variations in {', '.join(top_3)}."
                return {
                    "status": "fallback",
                    "method": "Tree Feature Importances",
                    "feature_impacts": feature_impacts[:12],
                    "business_narrative": narrative
                }
            return {
                "status": "unavailable",
                "method": "None",
                "feature_impacts": [],
                "business_narrative": "Detailed feature attribution is not supported for this model class."
            }

