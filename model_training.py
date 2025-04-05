import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the VPN test results
with open('updated_vpn_results.json', 'r') as file:
    vpn_results = json.load(file)

# Prepare the feature set (X) and labels (y)
X = []
y = []

# Initialize LabelEncoder for country encoding
le = LabelEncoder()

for result in vpn_results:
    # Features: latency and success status (1 for success, 0 for failure)
    latency = result['latency'] if result['latency'] != 'No Latency Data' else 0
    success = 1 if result['status'] == 'connected' else 0
    
    # We will also include country as a categorical feature (using integer encoding)
    country = result['filename'].split('_')[-1].replace(".ovpn", "")
    
    # Encode the country using LabelEncoder
    encoded_country = le.fit_transform([country])[0]

    # Append feature vector and target label
    X.append([latency, success, encoded_country])
    y.append(success)  # Predicting success/failure of VPN connection

# Convert lists to numpy arrays
X = np.array(X)
y = np.array(y)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize KNN model
knn = KNeighborsClassifier(n_neighbors=3)

# Train the model
knn.fit(X_train, y_train)

# Test the model
y_pred = knn.predict(X_test)

# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the trained model
joblib.dump(knn, 'vpn_recommendation_model.pkl')
