# NexoraIQ REST API Specification

Base URL: `/api/v1`

---

## 1. Authentication (`/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register new user, organization & default workspace | No |
| `POST` | `/auth/login` | Authenticate user credentials and receive JWT | No |
| `GET` | `/auth/me` | Fetch active user profile, workspace & permissions | Yes (Bearer) |

---

## 2. Workspaces (`/workspaces`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/workspaces/` | List all workspaces in tenant organization | Yes |
| `POST` | `/workspaces/` | Create a new isolated workspace | Yes |

---

## 3. Datasets (`/datasets`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/datasets/?workspace_id={id}` | List all datasets in active workspace | Yes |
| `POST` | `/datasets/upload` | Upload CSV or Excel file with automated quality audit | Yes |
| `GET` | `/datasets/{dataset_id}` | Fetch metadata, data quality report & data preview | Yes |
| `POST` | `/datasets/{dataset_id}/mappings` | Override automatic semantic column mappings | Yes |
| `POST` | `/datasets/seed-demo-datasets` | Seed benchmark datasets into workspace | Yes |

---

## 4. Dashboard & Analytics (`/dashboard`, `/analytics`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/summary` | Aggregate executive KPIs, timeseries & cost breakdown | Yes |
| `GET` | `/analytics/profitability` | Contribution margin, break-even & dimensional breakdown | Yes |
| `GET` | `/analytics/inventory` | Inventory turnover, Days Inventory Outstanding & ABC analysis | Yes |
| `GET` | `/analytics/marketing` | Channel ROAS, CAC, conversion efficiency & attribution | Yes |
| `GET` | `/analytics/finance` | Cash runway months, burn rate & concentration risk | Yes |

---

## 5. Predictive Machine Learning (`/forecasting`, `/anomalies`, `/customers`, `/explainability`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/forecasting/run` | Execute walk-forward cross-validation & forecast forward | Yes |
| `GET` | `/forecasting/latest` | Retrieve latest forecast run metrics & comparison | Yes |
| `GET` | `/anomalies/` | Execute ensemble anomaly detection (IF, LOF, Z-score) | Yes |
| `GET` | `/customers/rfm-and-churn` | Compute RFM segmentation & evaluate churn classifiers | Yes |
| `GET` | `/explainability/attribution`| Compute SHAP feature attributions and business narrative | Yes |

---

## 6. AI Decision Advisor & Reports (`/advisor`, `/reports`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/advisor/recommendations` | Generate evidence-backed strategic recommendations | Yes |
| `POST` | `/advisor/chat` | Controlled tool-based natural language business analyst | Yes |
| `POST` | `/reports/generate` | Compile Excel (.xlsx) workbook or ReportLab PDF brief | Yes |
| `GET` | `/reports/download/{fn}` | Download generated report document | No (Direct link) |

