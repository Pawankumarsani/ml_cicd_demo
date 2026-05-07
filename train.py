import numpy as np
import joblib
from sklearn.linear_model import LinearRegression

# Generate synthetic data
np.random.seed(42)
X = np.random.rand(100, 1) * 10
y = 2.5 * X + 1.2 + np.random.randn(100, 1) * 0.5

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, 'model.pkl')
print(f"Model trained. R² on training data: {model.score(X, y):.3f}")