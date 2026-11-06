# NexoraIQ Machine Learning & Analytical Methodology

## 1. Principles of Predictive Integrity
1. **Never Randomly Shuffle Time-Series:** Chronological ordering is preserved strictly. Training (first 70%), Validation (subsequent 15%), and Testing (final untouched 15%).
2. **Strict Leakage Prevention:** Feature transformations, rolling windows, and normalizations are fitted strictly on the training partition and transformed out-of-sample.
3. **No Fabricated Predictions or Metrics:** All reported evaluation metrics (MAE, RMSE, MAPE, sMAPE, R², ROC-AUC, Precision, Recall, F1) are calculated from actual predictions on validation/test partitions.
4. **Benchmark Comparison Against Naive Baselines:** Every complex model is benchmarked against Naive (last observed value) and Seasonal Naive (7-day periodic lag) baselines.

---

## 2. Forecasting Engine Architecture
- **Algorithms:**
  - `Naive Baseline` (Zero-variance baseline)
  - `Seasonal Naive` (7-day lag autoregressive persistence)
  - `Ridge Regression` ($L_2$ regularized linear model)
  - `Random Forest Regressor` (100 estimators, max depth 10)
  - `XGBoost Regressor` (Gradient boosted trees with early stopping)
  - `LightGBM Regressor` (Leaf-wise histogram boosted decision trees)
  - `ARIMA(2,1,1)` (Autoregressive integrated moving average)
- **Model Selection Protocol:** The algorithm demonstrating the lowest root mean squared error (RMSE) on the validation set is selected as the winning model.
- **Recursive Multi-Step Forward Projections:** Unlike naive extrapolation that repeats the last day's features, NexoraIQ dynamically recalculates autoregressive lags and rolling statistics step-by-step into future calendar horizons.
- **Uncertainty Quantification:** Prediction intervals are computed as:
  $$\hat{y}_{t+h} \pm 1.96 \cdot \hat{\sigma}_{\text{residuals}} \cdot (1 + 0.025 \cdot h)$$
  where $h$ is the forecast step horizon, capturing compounding forecast uncertainty.

---

## 3. Multi-Method Anomaly Detection
An ensemble approach isolates true operational events from statistical noise:
1. **Isolation Forest:** Builds randomized isolation trees on multivariate features to flag observations with short average path lengths.
2. **Local Outlier Factor (LOF):** Measures local density of an observation relative to its $k$-nearest neighbors.
3. **Rolling Z-Score (3-Sigma Rule):** Measures deviations relative to a 14-day rolling median and interquartile deviation:
   $$Z_t = \frac{|y_t - \text{median}_{14}(y)|}{\text{std}_{14}(y)}$$
4. **Severity Stratification:**
   - Critical: Absolute deviation $> 150\%$ or $Z > 4.5$
   - High: Absolute deviation $> 75\%$ or $Z > 3.0$
   - Medium: Absolute deviation $> 35\%$ or $Z > 2.0$
   - Low: Minor deviations

---

## 4. Customer Churn & RFM Segmentation
- **RFM Stratification:** Recency (1-5), Frequency (1-5), Monetary (1-5).
  - *Champions*: $R \ge 4, F \ge 4$
  - *Loyal Customers*: $R \ge 3, F \ge 3$
  - *Recent Buyers*: $R \ge 4, F \le 2$
  - *At Risk*: $R \le 2, F \ge 3$
  - *Lost Customers*: $R = 1, F \le 2$
- **Supervised Churn Classifiers:** Random Forest, Gradient Boosting, Logistic Regression with balanced class weights. Evaluated via Precision, Recall, F1, PR-AUC, ROC-AUC, and Confusion Matrix.

---

## 5. Explainable AI (XAI)
Integrates `shap.TreeExplainer` to calculate Shapley values across predictive features:
- Global feature importance: $\frac{1}{N} \sum_{i=1}^N |\phi_j^{(i)}|$
- Directional sample contribution: $\phi_j^{(t)}$ indicating upward (+) or downward (-) push on predicted revenue.
- Automated transformation into human-readable executive narratives.

