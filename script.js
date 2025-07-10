document.getElementById('symptomForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting in the traditional way

    const symptomsInput = document.getElementById('symptoms').value;
    const daysInput = document.getElementById('days').value;

    // Prepare data for the POST request
    const symptoms = symptomsInput.split(',').map(symptom => symptom.trim());

    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symptoms, days: parseInt(daysInput) })
        });

        const data = await response.json();
        displayResponse(data);
    } catch (error) {
        console.error('Error:', error);
    }
});

function displayResponse(data) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = `
        <h2>Prediction Result</h2>
        <p><strong>Disease:</strong> ${data.disease}</p>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Precautions:</strong> ${data.precautions.join(', ')}</p>
        <p><strong>Advice:</strong> ${data.advice}</p>
    `;
}
