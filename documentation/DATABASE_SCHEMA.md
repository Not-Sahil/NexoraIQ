# NexoraIQ Database Schema & Data Dictionary

Schema definitions and migration scripts are located in `database/migrations/001_initial_schema.sql`.

## 1. Relational Entity Overview
```
+---------------+        1:N        +---------------+
| organizations |-------------------|  workspaces   |
+---------------+                   +---------------+
        |                                   |
        | 1:N                               | 1:N
        v                                   v
+---------------+                   +---------------+
|  org_members  |                   |   datasets    |
+---------------+                   +---------------+
        |                                   |
        | N:1                               | 1:N
        v                                   v
+---------------+                   +---------------+
|   profiles    |                   | forecasts,    |
+---------------+                   | anomalies,    |
                                    | metrics, etc. |
                                    +---------------+
```

## 2. Table Specifications
1. **`profiles`**: User identities synchronized with Supabase Auth (`id UUID`, `email`, `full_name`, `avatar_url`, `created_at`).
2. **`organizations`**: Multi-tenant organizations (`id UUID`, `name`, `slug`, `billing_plan`, `industry`).
3. **`organization_members`**: RBAC permissions (`id UUID`, `organization_id`, `user_id`, `role: owner/admin/analyst`).
4. **`workspaces`**: Isolated data domains (`id UUID`, `organization_id`, `name`, `description`, `domain_type`).
5. **`datasets`**: Uploaded datasets (`id UUID`, `workspace_id`, `name`, `filename`, `file_path`, `row_count`, `col_count`, `quality_score`).
6. **`dataset_columns`**: Column metadata and semantic roles (`id UUID`, `dataset_id`, `column_name`, `inferred_type`, `mapped_semantic_role`).
7. **`data_quality_reports`**: Audit scores (`completeness_score`, `validity_score`, `uniqueness_score`, `consistency_score`, `issues_json`).
8. **`business_metrics`**: Aggregated performance metrics (`total_revenue`, `gross_profit`, `net_profit`, `cac`, `clv`, `conversion_rate`).
9. **`forecasts`**: Model runs (`target_column`, `best_model_name`, `val_mape`, `val_rmse`, `test_rmse`, `model_comparison_json`).
10. **`forecast_predictions`**: Future projection points (`forecast_date`, `predicted_value`, `lower_bound`, `upper_bound`).
11. **`anomaly_events`**: Detected deviations (`event_date`, `metric_name`, `actual_value`, `expected_value`, `deviation_pct`, `severity`, `method`, `root_cause`).
12. **`customer_segments`**: RFM classifications (`customer_identifier`, `recency_days`, `frequency_orders`, `monetary_total`, `rfm_score`, `segment_label`).
13. **`churn_predictions`**: Churn risks (`customer_identifier`, `churn_probability`, `risk_tier`, `top_churn_factors`).
14. **`business_recommendations`**: Strategic advice (`category`, `problem_statement`, `supporting_evidence`, `recommended_action`, `expected_impact`, `priority`, `confidence`).
15. **`audit_logs`**: Tenant audit trail (`action`, `resource_type`, `resource_id`, `ip_address`, `details`).

