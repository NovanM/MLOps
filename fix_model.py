import joblib
import os
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Buat direktori
os.makedirs("Model/model", exist_ok=True)

# Generate dummy data
np.random.seed(42)
X_dummy = np.random.rand(100, 7)  # 7 features sesuai Titanic
y_dummy = np.random.randint(0, 2, 100)  # Binary classification

# Train model
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_dummy, y_dummy)

# Save model
model_path = "Model/model/RandomForestClassifier_deployed_20250602_120000.pkl"
joblib.dump(model, model_path)

print(f"✅ Dummy model saved to: {model_path}")
