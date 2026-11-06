"""
NexoraIQ: Universal Data Ingestion & Quality Scoring Engine
Supports CSV and Excel uploads, automatic schema detection,
semantic role mapping, outlier identification, and data quality grading (0-100%).
"""

import os
import re
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class UniversalDataIngestionEngine:
    # Semantic mapping heuristics
    SEMANTIC_PATTERNS = {
        "date": [r"date", r"time", r"period", r"timestamp", r"day", r"month", r"year"],
        "revenue": [r"revenue", r"sales", r"sale_amount", r"amount", r"turnover", r"gross_sales", r"mrr", r"arr"],
        "cost": [r"cost", r"cogs", r"expense", r"expenditure", r"spend", r"operating_cost"],
        "profit": [r"profit", r"net_profit", r"gross_profit", r"margin", r"earnings"],
        "units_sold": [r"unit", r"quantity", r"qty", r"volume", r"orders_count", r"items"],
        "customer_id": [r"customer", r"client", r"buyer", r"user", r"account_id", r"customer_id", r"client_id"],
        "marketing_spend": [r"marketing", r"ad_spend", r"campaign_spend", r"acquisition_spend", r"advertising"],
        "website_visitors": [r"visitor", r"traffic", r"sessions", r"page_views", r"impressions", r"clicks"],
        "conversion_rate": [r"conversion", r"cvr", r"conv_rate"],
        "inventory": [r"inventory", r"stock", r"units_in_stock", r"warehouse_qty", r"holding"],
        "product": [r"product", r"sku", r"item", r"merchandise", r"product_name"],
        "category": [r"category", r"dept", r"department", r"segment", r"class"],
        "region": [r"region", r"country", r"territory", r"state", r"market", r"location"],
        "channel": [r"channel", r"source", r"medium", r"utm_source", r"sales_channel"]
    }

    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """Loads dataset from CSV or Excel file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".csv", ".txt"]:
            # Auto-detect encoding and separator
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only CSV and Excel (.xlsx, .xls) are supported.")
            
        return df

    def infer_column_type(self, series: pd.Series) -> str:
        """Infers the data type of a column accurately."""
        # Drop NAs for type inspection
        valid_series = series.dropna()
        if len(valid_series) == 0:
            return "empty"
            
        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
            
        # Try converting string series to datetime if samples match dates
        if series.dtype == "object":
            sample = valid_series.head(50).astype(str)
            date_matches = 0
            for val in sample:
                val_clean = val.strip()
                # Matches YYYY-MM-DD, DD/MM/YYYY, etc.
                if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", val_clean) or \
                   re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", val_clean):
                    date_matches += 1
            if date_matches / len(sample) >= 0.70:
                try:
                    pd.to_datetime(valid_series.head(20))
                    return "datetime"
                except Exception:
                    pass

        # Check numeric
        if pd.api.types.is_numeric_dtype(series):
            # Check boolean disguised as int
            unique_vals = set(valid_series.unique()[:5])
            if unique_vals.issubset({0, 1}) and len(valid_series.unique()) <= 2:
                return "boolean"
            return "numeric"
            
        # Check boolean
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
            
        # Check categorical vs text (low cardinality = categorical)
        unique_ratio = len(valid_series.unique()) / len(valid_series)
        if unique_ratio < 0.20 or len(valid_series.unique()) <= 30:
            return "categorical"
            
        return "text"

    def map_semantic_role(self, col_name: str, col_type: str) -> Optional[str]:
        """Maps a column name to a standard business semantic role using regex heuristics."""
        clean_name = re.sub(r"[_\s\-]+", " ", col_name.lower()).strip()
        
        # If inferred as datetime, give strong preference to 'date'
        if col_type == "datetime":
            return "date"
            
        for role, patterns in self.SEMANTIC_PATTERNS.items():
            for pat in patterns:
                if re.search(r"\b" + pat, clean_name):
                    return role
        return None

    def profile_columns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Profiles each column with metadata, types, and stats."""
        columns_meta = []
        for col in df.columns:
            series = df[col]
            inferred_type = self.infer_column_type(series)
            semantic_role = self.map_semantic_role(str(col), inferred_type)
            
            null_count = int(series.isnull().sum())
            null_pct = round(float((null_count / len(df)) * 100), 2)
            distinct_count = int(series.nunique())
            
            meta: Dict[str, Any] = {
                "column_name": str(col),
                "inferred_type": inferred_type,
                "mapped_semantic_role": semantic_role,
                "null_count": null_count,
                "null_percentage": null_pct,
                "distinct_count": distinct_count,
                "min_value": None,
                "max_value": None,
                "mean_value": None,
                "std_value": None
            }
            
            if inferred_type == "numeric":
                valid_num = pd.to_numeric(series, errors="coerce").dropna()
                if len(valid_num) > 0:
                    meta["min_value"] = float(valid_num.min())
                    meta["max_value"] = float(valid_num.max())
                    meta["mean_value"] = round(float(valid_num.mean()), 4)
                    meta["std_value"] = round(float(valid_num.std()) if len(valid_num) > 1 else 0.0, 4)
            elif inferred_type == "datetime":
                try:
                    valid_dt = pd.to_datetime(series, errors="coerce").dropna()
                    if len(valid_dt) > 0:
                        meta["min_value"] = valid_dt.min().strftime("%Y-%m-%d")
                        meta["max_value"] = valid_dt.max().strftime("%Y-%m-%d")
                except Exception:
                    pass
            columns_meta.append(meta)
            
        return columns_meta

    def assess_data_quality(self, df: pd.DataFrame, columns_meta: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assesses data quality across 4 core dimensions:
        1. Completeness: Ratio of non-null cells
        2. Uniqueness: Ratio of non-duplicate rows
        3. Validity: Adherence to business domain constraints (e.g. positive revenues, valid dates)
        4. Consistency: Low extreme outlier pollution
        Returns an overall score (0 - 100) and actionable issues list.
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = max(1, total_rows * total_cols)
        
        # 1. Completeness
        missing_cells = int(df.isnull().sum().sum())
        completeness_score = round(max(0.0, 100.0 - ((missing_cells / total_cells) * 100.0)), 2)
        
        # 2. Uniqueness
        duplicate_rows = int(df.duplicated().sum())
        uniqueness_score = round(max(0.0, 100.0 - ((duplicate_rows / max(1, total_rows)) * 100.0)), 2)
        
        # 3. Validity & Outliers
        issues: List[Dict[str, Any]] = []
        outlier_count = 0
        invalid_cells = 0
        
        if duplicate_rows > 0:
            issues.append({
                "severity": "medium",
                "type": "duplicate_rows",
                "message": f"Found {duplicate_rows} duplicate rows in dataset.",
                "remedy": "Deduplicate before running predictive models."
            })
            
        # Check column-specific validity
        has_date_col = False
        has_revenue_col = False
        
        for col_info in columns_meta:
            col_name = col_info["column_name"]
            col_type = col_info["inferred_type"]
            role = col_info["mapped_semantic_role"]
            series = df[col_name]
            
            if role == "date" or col_type == "datetime":
                has_date_col = True
                
            if role in ["revenue", "sales_amount"]:
                has_revenue_col = True
                # Check for negative revenues
                valid_num = pd.to_numeric(series, errors="coerce").dropna()
                negatives = int((valid_num < 0).sum())
                if negatives > 0:
                    invalid_cells += negatives
                    issues.append({
                        "severity": "high",
                        "type": "negative_revenue",
                        "column": col_name,
                        "message": f"Found {negatives} negative values in revenue column '{col_name}'.",
                        "remedy": "Examine if returns/refunds are mixed with gross sales."
                    })
                    
            if col_type == "numeric":
                valid_num = pd.to_numeric(series, errors="coerce").dropna()
                if len(valid_num) > 10:
                    q25 = valid_num.quantile(0.25)
                    q75 = valid_num.quantile(0.75)
                    iqr = q75 - q25
                    lower_bound = q25 - (3.0 * iqr)
                    upper_bound = q75 + (3.0 * iqr)
                    col_outliers = int(((valid_num < lower_bound) | (valid_num > upper_bound)).sum())
                    if col_outliers > 0:
                        outlier_count += col_outliers
                        if col_outliers / len(valid_num) > 0.05:
                            issues.append({
                                "severity": "medium",
                                "type": "high_outlier_density",
                                "column": col_name,
                                "message": f"{col_outliers} statistical outliers detected in '{col_name}'.",
                                "remedy": "Robust scaling or anomaly isolation recommended."
                            })

        if not has_date_col:
            issues.append({
                "severity": "high",
                "type": "missing_temporal_dimension",
                "message": "No temporal (Date/Time) column detected. Time-series forecasting will require an index.",
                "remedy": "Map a sequential index or upload a dataset with timestamp."
            })
            
        if not has_revenue_col:
            issues.append({
                "severity": "low",
                "type": "unmapped_target",
                "message": "No primary revenue/target column mapped by default.",
                "remedy": "Manually designate target column in settings."
            })
            
        validity_score = round(max(0.0, 100.0 - ((invalid_cells / max(1, total_rows)) * 50.0)), 2)
        consistency_score = round(max(0.0, 100.0 - ((outlier_count / max(1, total_cells)) * 100.0)), 2)
        
        # Weighted Overall Score
        overall_score = round(
            (completeness_score * 0.35) +
            (validity_score * 0.30) +
            (uniqueness_score * 0.20) +
            (consistency_score * 0.15),
            2
        )
        
        return {
            "overall_score": overall_score,
            "completeness_score": completeness_score,
            "validity_score": validity_score,
            "uniqueness_score": uniqueness_score,
            "consistency_score": consistency_score,
            "total_rows": total_rows,
            "total_columns": total_cols,
            "duplicate_rows": duplicate_rows,
            "missing_cells": missing_cells,
            "outlier_count": outlier_count,
            "issues": issues,
            "grade": "A+" if overall_score >= 90 else ("A" if overall_score >= 80 else ("B" if overall_score >= 70 else ("C" if overall_score >= 60 else "D")))
        }

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Full pipeline: load, profile, evaluate quality, and generate preview."""
        df = self.load_dataset(file_path)
        columns_meta = self.profile_columns(df)
        quality_report = self.assess_data_quality(df, columns_meta)
        
        # Generate clean preview (first 15 rows)
        preview_data = df.head(15).replace({np.nan: None}).to_dict(orient="records")
        
        return {
            "row_count": len(df),
            "col_count": len(df.columns),
            "columns": columns_meta,
            "quality_report": quality_report,
            "preview": preview_data
        }

