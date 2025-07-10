import os
import re
import pandas as pd
import numpy as np
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC





app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "Health Assistant API is running."

# Load datasets
base_path = r'C:\Users\HP\OneDrive\Desktop\minor\minor'
training = pd.read_csv(os.path.join(base_path, 'Data', 'Training.csv'))
testing = pd.read_csv(os.path.join(base_path, 'Data', 'Testing.csv'))

cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

# Mapping strings to numbers
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

# Splitting the data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

# Initialize classifiers
clf1 = DecisionTreeClassifier()
clf = clf1.fit(x_train, y_train)
model = SVC()
model.fit(x_train, y_train)

severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {symptom: index for index, symptom in enumerate(cols)}

# Function to get severity dictionary
def getSeverityDict():
    global severityDictionary
    with open(os.path.join(base_path, 'MasterData', 'Symptom_severity.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) >= 2:
                severityDictionary[row[0]] = int(row[1])

# Function to get description list
def getDescription():
    global description_list
    with open(os.path.join(base_path, 'MasterData', 'symptom_Description.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            description_list[row[0]] = row[1]

# Function to get precaution dictionary
def getprecautionDict():
    global precautionDictionary
    with open(os.path.join(base_path, 'MasterData', 'symptom_precaution.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    symptoms = data.get('symptoms', [])
    days = data.get('days', 0)

    # Validate input
    if not symptoms or not isinstance(days, (int, float)):
        return jsonify({'error': 'Invalid input data.'}), 400

    # Check if there are fewer than 4 symptoms provided
    if len(symptoms) < 3:
        return jsonify({'message': 'Please provide more symptoms for a more accurate prediction.'}), 400

    # Input vector for prediction
    input_vector = np.zeros(len(cols))
    for symptom in symptoms:
        if symptom in symptoms_dict:
            input_vector[symptoms_dict[symptom]] = 1

    # Predicting disease
    predicted_disease = clf.predict([input_vector])[0]
    predicted_disease_name = le.inverse_transform([predicted_disease])[0]
    
    # Getting description and precautions
    description = description_list.get(predicted_disease_name, "No description available.")
    precautions = precautionDictionary.get(predicted_disease_name, ["No precautions available."])

    # Calculate condition
    severity_score = sum(severityDictionary.get(symptom, 0) for symptom in symptoms)
    if (severity_score * days) / (len(symptoms) + 1) > 13:
        advice = "You should take the consultation from a doctor."
    else:
        advice = "It might not be that bad but you should take precautions."

    response = {
        'disease': predicted_disease_name,
        'description': description,
        'precautions': precautions,
        'advice': advice
    }

    return jsonify(response)


if __name__ == '__main__':
    getSeverityDict()
    getDescription()
    getprecautionDict()
    app.run(debug=True)
