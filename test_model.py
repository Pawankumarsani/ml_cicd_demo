import joblib
import numpy as np

def test_model_accuracy():
    model = joblib.load('model.pkl')
    # Generate test data (different from training)
    X_test = np.random.rand(20, 1) * 10
    y_test = 2.5 * X_test + 1.2 + np.random.randn(20, 1) * 0.5
    score = model.score(X_test, y_test)
    assert score > 0.85, f"R² too low: {score:.3f}"
    print(f"Test passed with R² = {score:.3f}")