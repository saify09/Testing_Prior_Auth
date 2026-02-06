async function submitRequest() {
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultHeader = document.getElementById('result-header');
    const resultBody = document.getElementById('result-body');
    const resultContainer = document.getElementById('status-area');

    // Reset UI
    submitBtn.disabled = true;
    loading.classList.remove('hidden');
    resultContainer.style.display = 'none';
    results.className = 'result-box'; // reset classes

    const payload = {
        member_id: document.getElementById('memberId').value,
        provider_id: "PROV001",
        cpt_code: document.getElementById('cptCode').value,
        diagnosis_code: document.getElementById('diagnosisCode').value,
        clinical_notes: document.getElementById('clinicalNotes').value
    };

    try {
        // Use absolute URL to allow running from file:// or other origins
        const response = await fetch('http://localhost:8001/agent/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        // Hide loader
        loading.classList.add('hidden');
        resultContainer.style.display = 'block';

        if (data.final_explanation) {
            resultBody.innerText = data.final_explanation;
            
            // Determine result type based on text content (simple heuristic)
            if (data.final_explanation.includes("Approved")) {
                results.classList.add('success');
                resultHeader.innerText = "Authorization Approved";
            } else if (data.final_explanation.includes("ACTION REQUIRED") || data.final_explanation.includes("Missing")) {
                results.classList.add('warning');
                resultHeader.innerText = "Documentation Gap Detected";
            } else if (data.final_explanation.includes("Denied")) {
                results.classList.add('error');
                resultHeader.innerText = "Authorization Denied";
            } else {
                 results.classList.add('success'); // Default for info messages
                 resultHeader.innerText = "Status Update";
            }
        } else {
             results.classList.add('error');
             resultHeader.innerText = "System Error";
             resultBody.innerText = "No explanation returned from agent.";
        }

    } catch (error) {
        console.error('Error:', error);
        loading.classList.add('hidden');
        resultContainer.style.display = 'block';
        results.classList.add('error');
        resultHeader.innerText = "Connection Error";
        resultBody.innerText = "Failed to connect to the Agent API. Ensure the server is running.";
    } finally {
        submitBtn.disabled = false;
    }
}
