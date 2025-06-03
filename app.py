from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import os
import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

app = Flask(__name__)

def create_dummy_model():
    """Buat dummy model jika tidak ada model yang tersedia"""
    print("📝 Creating dummy model for demo purposes...")
    # Buat data dummy untuk training
    np.random.seed(42)
    X_dummy = np.random.rand(100, 7)  # 7 features
    y_dummy = np.random.randint(0, 2, 100)  # Binary classification
    
    # Train simple model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_dummy, y_dummy)
    
    return model

def load_latest_model():
    """Load model terbaru berdasarkan timestamp"""
    try:
        print("🔍 Looking for trained models...")
        
        # Buat direktori jika belum ada
        os.makedirs("Model/model", exist_ok=True)
        
        # Cari model terbaru dengan berbagai pattern
        model_patterns = [
            "Model/model/*_deployed_*.pkl",
            "Model/model/*.pkl",
            "models/*.pkl",
            "*.pkl"
        ]
        
        model_files = []
        for pattern in model_patterns:
            files = glob.glob(pattern)
            if files:
                model_files.extend(files)
                print(f"✅ Found models with pattern {pattern}: {files}")
                break
        
        if model_files:
            # Ambil file terbaru
            latest_model = max(model_files, key=os.path.getctime)
            print(f"📊 Loading model: {latest_model}")
            return joblib.load(latest_model)
        else:
            print("⚠️ No trained model found, creating dummy model...")
            return create_dummy_model()
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("🔄 Falling back to dummy model...")
        return create_dummy_model()

# Load model saat startup
print("🚀 Initializing MLOps Application...")
model = load_latest_model()
print(f"✅ Model loaded successfully: {type(model).__name__}")

@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

@app.route("/predict", methods=["POST"])
def predict():
    """Prediction endpoint"""
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500
            
        # Ambil data dari form atau JSON
        if request.is_json:
            input_data = request.get_json()
        else:
            input_data = request.form.to_dict()
            
        print(f"📥 Received input: {input_data}")
        
        # Convert string values to float untuk numerik input
        numeric_data = {}
        expected_features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
        
        for feature in expected_features:
            if feature in input_data:
                try:
                    numeric_data[feature] = float(input_data[feature])
                except:
                    numeric_data[feature] = 0.0
            else:
                numeric_data[feature] = 0.0
        
        # Convert ke array untuk prediksi
        feature_array = np.array([[
            numeric_data['Pclass'],
            numeric_data['Sex'], 
            numeric_data['Age'],
            numeric_data['SibSp'],
            numeric_data['Parch'],
            numeric_data['Fare'],
            numeric_data['Embarked']
        ]])
        
        print(f"🔢 Feature array: {feature_array}")
        
        # Lakukan prediksi
        prediction = model.predict(feature_array)[0]
        probability = None
        
        # Jika model support predict_proba
        try:
            proba = model.predict_proba(feature_array)[0]
            probability = {
                "class_0": float(proba[0]),
                "class_1": float(proba[1])
            }
        except Exception as prob_error:
            print(f"⚠️ Probability calculation failed: {prob_error}")
            
        response = {
            "prediction": int(prediction),
            "prediction_text": "Survived" if prediction == 1 else "Did not survive",
            "input_data": numeric_data
        }
        
        if probability:
            response["probability"] = probability
            
        print(f"📤 Response: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/model-info")
def model_info():
    """Endpoint untuk informasi model"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
        
    try:
        info = {
            "model_type": str(type(model).__name__),
            "features": getattr(model, 'feature_names_in_', 'Not available'),
            "n_features": getattr(model, 'n_features_in_', 'Not available')
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting MLOps Flask Application...")
    print(f"📊 Model loaded: {'✅' if model else '❌'}")
    print("🌐 Access the application at: http://localhost:3000")
    
    # Perbaiki syntax error: __name__ bukan **name**
    app.run(host="0.0.0.0", port=3000, debug=False)
