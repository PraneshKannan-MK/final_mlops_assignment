import pandas as pd
import numpy as np
from src.models.xgboost_model import XGBoostModel

def test_model_train_and_predict():
    X = pd.DataFrame(np.random.rand(50, 5))
    y = pd.Series(np.random.rand(50))

    model = XGBoostModel()
    model.train(X, y)
    preds = model.predict(X)

    assert len(preds) == len(X)