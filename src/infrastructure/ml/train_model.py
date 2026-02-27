
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# 1. Generate Synthetic Data
def generate_data(num_samples=1000):
    np.random.seed(42)
    
    # Features:
    # - Payer: 0=UHC, 1=Cigna, 2=Aetna
    # - Procedure Code Risk: 0=Low, 1=Med, 2=High
    # - Diagnosis Match: 0=No, 1=Yes
    # - Documentation Score: 0-100
    
    payers = np.random.randint(0, 3, num_samples)
    proc_risk = np.random.randint(0, 3, num_samples) 
    diag_match = np.random.randint(0, 2, num_samples)
    doc_score = np.random.randint(50, 100, num_samples)
    
    # Target: 0=Approved, 1=Denied
    # Logic: High risk proc + low doc score = Denied
    denied = []
    for i in range(num_samples):
        risk = 0.1
        if proc_risk[i] == 2: risk += 0.4
        if diag_match[i] == 0: risk += 0.3
        if doc_score[i] < 70: risk += 0.3
        
        if np.random.random() < risk:
            denied.append(1)
        else:
            denied.append(0)
            
    df = pd.DataFrame({
        'payer_id': payers,
        'procedure_risk': proc_risk,
        'diagnosis_match': diag_match,
        'doc_score': doc_score,
        'denied': denied
    })
    return df

# 2. Train Model
def train():
    print("Generating synthetic data...")
    df = generate_data()
    
    X = df.drop('denied', axis=1)
    y = df['denied']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model Accuracy: {acc:.2f}")
    
    # Save Model
    output_path = "src/agents/denial_prediction_agent/model.pkl"
    with open(output_path, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train()
