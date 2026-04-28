"""
One-time script to register existing trained model into Docker MLflow.
Run while docker-compose is up.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import mlflow
import mlflow.xgboost
import joblib
import json
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

# Point to Docker MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("demand-forecasting")

print("Connected to MLflow at http://localhost:5000")

# Load feature data
df = pd.read_csv("data/features/sales_features.csv", parse_dates=["date"])
print(f"Loaded {len(df)} rows")

# Feature columns — must match exactly what was used in training
feature_cols = [
    "year", "month", "day_of_week", "day_of_year", "week_of_year",
    "quarter", "is_weekend", "is_month_start", "is_month_end",
    "price", "price_lag_7", "price_pct_change", "price_rolling_mean_7",
    "sales_lag_1", "sales_lag_7", "sales_lag_14", "sales_lag_28",
    "sales_rolling_mean_7", "sales_rolling_mean_14", "sales_rolling_mean_28",
    "sales_rolling_std_7", "sales_rolling_std_14", "sales_rolling_std_28",
    "sin_1", "cos_1", "sin_2", "cos_2", "sin_3", "cos_3",
    "discount_effect", "low_stock_flag", "price_diff",
    "is_promo", "is_rainy", "seasonality_index", "epidemic_flag",
]

target_col = "sales_qty"

# Keep only rows that have all feature columns
available_features = [c for c in feature_cols if c in df.columns]
print(f"Using {len(available_features)} features")

df_model = df[available_features + [target_col]].dropna()
X = df_model[available_features]
y = df_model[target_col]

print(f"Training on {len(X)} samples")

# Train XGBoost
import xgboost as xgb

params = {
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "objective": "reg:squarederror",
    "n_jobs": -1,
    "random_state": 42,
}

with mlflow.start_run() as run:
    run_id = run.info.run_id
    print(f"MLflow run: {run_id}")

    # Log params
    for k, v in params.items():
        mlflow.log_param(k, v)
    mlflow.log_param("n_samples", len(X))
    mlflow.log_param("n_features", len(available_features))
    mlflow.log_param("model_type", "xgboost")

    # TimeSeriesSplit CV
    tscv = TimeSeriesSplit(n_splits=5)
    mae_list, rmse_list = [], []

    for fold, (tr_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]

        m = xgb.XGBRegressor(**params)
        m.fit(X_tr, y_tr, verbose=False)
        preds = np.maximum(m.predict(X_val), 0)

        mae = float(np.mean(np.abs(y_val.values - preds)))
        rmse = float(np.sqrt(np.mean((y_val.values - preds) ** 2)))
        mae_list.append(mae)
        rmse_list.append(rmse)

        mlflow.log_metric(f"fold_{fold}_mae", mae)
        mlflow.log_metric(f"fold_{fold}_rmse", rmse)
        print(f"  Fold {fold}: MAE={mae:.2f}, RMSE={rmse:.2f}")

    mlflow.log_metric("cv_mean_mae", float(np.mean(mae_list)))
    mlflow.log_metric("cv_mean_rmse", float(np.mean(rmse_list)))

    # Final model on all data
    final_model = xgb.XGBRegressor(**params)
    final_model.fit(X, y, verbose=100)

    final_preds = np.maximum(final_model.predict(X), 0)
    final_mae = float(np.mean(np.abs(y.values - final_preds)))
    final_rmse = float(np.sqrt(np.mean((y.values - final_preds) ** 2)))
    mlflow.log_metric("mae", final_mae)
    mlflow.log_metric("rmse", final_rmse)
    print(f"Final MAE={final_mae:.2f}, RMSE={final_rmse:.2f}")

    # Log feature importances
    imp = final_model.get_booster().get_fscore()
    with open("feature_importances.json", "w") as f:
        json.dump(imp, f, indent=2)
    mlflow.log_artifact("feature_importances.json")
    os.remove("feature_importances.json")

    # Save model with joblib
    joblib.dump(final_model, "model.joblib")
    mlflow.log_artifact("model.joblib", artifact_path="model")
    os.remove("model.joblib")

    # Register in MLflow registry
    client = mlflow.MlflowClient()
    try:
        client.create_registered_model("demand_forecaster")
        print("Created registered model: demand_forecaster")
    except Exception:
        print("Model already exists in registry")

    model_uri = f"runs:/{run_id}/model"
    mv = client.create_model_version(
        name="demand_forecaster",
        source=model_uri,
        run_id=run_id,
    )
    print(f"Created model version {mv.version}")

    # Promote to Production
    client.transition_model_version_stage(
        name="demand_forecaster",
        version=mv.version,
        stage="Production",
    )
    print(f"Version {mv.version} promoted to Production")
    print(f"Done. Check http://localhost:5000/#/models")