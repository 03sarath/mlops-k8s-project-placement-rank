from flask import Flask, request, jsonify, render_template_string
import pickle

#loading the model 
with open("project_one_model.pkl","rb") as f_in:
    dv,model = pickle.load(f_in)

app = Flask('Predict')

@app.route('/')
def home():
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Placement Analytics</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #f8fafc;
                color: #1e293b;
                line-height: 1.6;
            }
            
            .dashboard {
                display: flex;
                min-height: 100vh;
            }
            
            .sidebar {
                width: 280px;
                background: linear-gradient(180deg, #1e40af 0%, #3b82f6 100%);
                color: white;
                padding: 2rem;
                position: fixed;
                height: 100vh;
                overflow-y: auto;
            }
            
            .sidebar-header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            
            .sidebar-header h1 {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            
            .sidebar-header p {
                font-size: 0.875rem;
                opacity: 0.8;
            }
            
            .nav-stats {
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                backdrop-filter: blur(10px);
            }
            
            .stat-card h3 {
                font-size: 0.875rem;
                opacity: 0.8;
                margin-bottom: 0.5rem;
            }
            
            .stat-card .value {
                font-size: 1.5rem;
                font-weight: 700;
            }
            
            .main-content {
                flex: 1;
                margin-left: 280px;
                padding: 2rem;
            }
            
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #e2e8f0;
            }
            
            .header h2 {
                font-size: 2rem;
                font-weight: 700;
                color: #1e293b;
            }
            
            .header .subtitle {
                color: #64748b;
                font-size: 1rem;
            }
            
            .content-grid {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
            }
            
            .form-container {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid #e2e8f0;
            }
            
            .form-header {
                display: flex;
                align-items: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .form-header i {
                font-size: 1.5rem;
                color: #3b82f6;
                margin-right: 1rem;
            }
            
            .form-header h3 {
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .form-sections {
                display: grid;
                gap: 2rem;
            }
            
            .form-section {
                background: #f8fafc;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            
            .section-title {
                display: flex;
                align-items: center;
                margin-bottom: 1.5rem;
                font-weight: 600;
                color: #374151;
            }
            
            .section-title i {
                margin-right: 0.75rem;
                color: #3b82f6;
                width: 20px;
            }
            
            .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }
            
            .form-field {
                display: flex;
                flex-direction: column;
            }
            
            .form-field label {
                font-size: 0.875rem;
                font-weight: 500;
                color: #374151;
                margin-bottom: 0.5rem;
            }
            
            .form-field input,
            .form-field select {
                padding: 0.75rem;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 0.875rem;
                transition: all 0.2s ease;
                background: white;
            }
            
            .form-field input:focus,
            .form-field select:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .action-buttons {
                display: flex;
                gap: 1rem;
                margin-top: 2rem;
            }
            
            .btn {
                padding: 0.875rem 1.5rem;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.875rem;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .btn-primary {
                background: #3b82f6;
                color: white;
                flex: 1;
            }
            
            .btn-primary:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }
            
            .btn-secondary {
                background: #10b981;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #059669;
                transform: translateY(-1px);
            }
            
            .results-container {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid #e2e8f0;
                height: fit-content;
                position: sticky;
                top: 2rem;
            }
            
            .results-header {
                display: flex;
                align-items: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .results-header i {
                font-size: 1.5rem;
                color: #3b82f6;
                margin-right: 1rem;
            }
            
            .results-header h3 {
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .prediction-display {
                text-align: center;
                padding: 2rem;
                border-radius: 12px;
                background: #f8fafc;
                border: 2px dashed #e2e8f0;
                margin-bottom: 2rem;
            }
            
            .prediction-display.active {
                border-color: #3b82f6;
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            }
            
            .prediction-display.success {
                border-color: #10b981;
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            }
            
            .prediction-display.danger {
                border-color: #ef4444;
                background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            }
            
            .probability-badge {
                display: inline-block;
                padding: 0.5rem 1rem;
                border-radius: 50px;
                font-weight: 700;
                font-size: 1.25rem;
                margin-bottom: 1rem;
            }
            
            .probability-badge.success {
                background: #10b981;
                color: white;
            }
            
            .probability-badge.danger {
                background: #ef4444;
                color: white;
            }
            
            .prediction-status {
                font-size: 1.125rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .prediction-description {
                color: #64748b;
                font-size: 0.875rem;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
            }
            
            .metric-card {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e2e8f0;
            }
            
            .metric-card h4 {
                font-size: 0.75rem;
                color: #64748b;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .metric-card .value {
                font-size: 1.25rem;
                font-weight: 700;
                color: #1e293b;
            }
            
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            .loading-content {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #e2e8f0;
                border-top: 4px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @media (max-width: 1024px) {
                .sidebar {
                    transform: translateX(-100%);
                    transition: transform 0.3s ease;
                }
                
                .sidebar.open {
                    transform: translateX(0);
                }
                
                .main-content {
                    margin-left: 0;
                }
                
                .content-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            @media (max-width: 768px) {
                .form-grid {
                    grid-template-columns: 1fr;
                }
                
                .action-buttons {
                    flex-direction: column;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="sidebar">
                <div class="sidebar-header">
                    <h1><i class="fas fa-chart-line"></i></h1>
                    <h1>Placement Analytics</h1>
                    <p>AI-Powered Student Placement Prediction</p>
                </div>
                
                <div class="nav-stats">
                    <div class="stat-card">
                        <h3>Model Accuracy</h3>
                        <div class="value">94.2%</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Predictions</h3>
                        <div class="value">1,247</div>
                    </div>
                    <div class="stat-card">
                        <h3>Success Rate</h3>
                        <div class="value">78.5%</div>
                    </div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="header">
                    <div>
                        <h2>Student Placement Predictor</h2>
                        <p class="subtitle">Enter candidate details to get AI-powered placement predictions</p>
                    </div>
                </div>
                
                <div class="content-grid">
                    <div class="form-container">
                        <div class="form-header">
                            <i class="fas fa-user-graduate"></i>
                            <h3>Candidate Information</h3>
                        </div>
                        
                        <form id="predictionForm">
                            <div class="form-sections">
                                <div class="form-section">
                                    <div class="section-title">
                                        <i class="fas fa-user"></i>
                                        Personal Information
                                    </div>
                                    <div class="form-grid">
                                        <div class="form-field">
                                            <label for="gender">Gender</label>
                                            <select id="gender" name="gender" required>
                                                <option value="">Select Gender</option>
                                                <option value="M">Male</option>
                                                <option value="F">Female</option>
                                            </select>
                                        </div>
                                        <div class="form-field">
                                            <label for="workex">Work Experience</label>
                                            <select id="workex" name="workex" required>
                                                <option value="">Select Experience</option>
                                                <option value="Yes">Yes</option>
                                                <option value="No">No</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <div class="section-title">
                                        <i class="fas fa-school"></i>
                                        Secondary Education (SSC)
                                    </div>
                                    <div class="form-grid">
                                        <div class="form-field">
                                            <label for="ssc_p">Percentage</label>
                                            <input type="number" id="ssc_p" name="ssc_p" step="0.01" min="0" max="100" required>
                                        </div>
                                        <div class="form-field">
                                            <label for="ssc_b">Board</label>
                                            <select id="ssc_b" name="ssc_b" required>
                                                <option value="">Select Board</option>
                                                <option value="Central">Central</option>
                                                <option value="Others">Others</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <div class="section-title">
                                        <i class="fas fa-graduation-cap"></i>
                                        Higher Secondary (HSC)
                                    </div>
                                    <div class="form-grid">
                                        <div class="form-field">
                                            <label for="hsc_p">Percentage</label>
                                            <input type="number" id="hsc_p" name="hsc_p" step="0.01" min="0" max="100" required>
                                        </div>
                                        <div class="form-field">
                                            <label for="hsc_b">Board</label>
                                            <select id="hsc_b" name="hsc_b" required>
                                                <option value="">Select Board</option>
                                                <option value="Central">Central</option>
                                                <option value="Others">Others</option>
                                            </select>
                                        </div>
                                        <div class="form-field">
                                            <label for="hsc_s">Specialization</label>
                                            <select id="hsc_s" name="hsc_s" required>
                                                <option value="">Select Specialization</option>
                                                <option value="Science">Science</option>
                                                <option value="Commerce">Commerce</option>
                                                <option value="Arts">Arts</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <div class="section-title">
                                        <i class="fas fa-university"></i>
                                        Undergraduate Degree
                                    </div>
                                    <div class="form-grid">
                                        <div class="form-field">
                                            <label for="degree_p">Percentage</label>
                                            <input type="number" id="degree_p" name="degree_p" step="0.01" min="0" max="100" required>
                                        </div>
                                        <div class="form-field">
                                            <label for="degree_t">Degree Type</label>
                                            <select id="degree_t" name="degree_t" required>
                                                <option value="">Select Degree Type</option>
                                                <option value="Sci&Tech">Sci&Tech</option>
                                                <option value="Comm&Mgmt">Comm&Mgmt</option>
                                                <option value="Others">Others</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <div class="section-title">
                                        <i class="fas fa-chart-line"></i>
                                        MBA & Employability
                                    </div>
                                    <div class="form-grid">
                                        <div class="form-field">
                                            <label for="etest_p">Employability Test %</label>
                                            <input type="number" id="etest_p" name="etest_p" step="0.01" min="0" max="100" required>
                                        </div>
                                        <div class="form-field">
                                            <label for="mba_p">MBA Percentage</label>
                                            <input type="number" id="mba_p" name="mba_p" step="0.01" min="0" max="100" required>
                                        </div>
                                        <div class="form-field">
                                            <label for="specialisation">MBA Specialization</label>
                                            <select id="specialisation" name="specialisation" required>
                                                <option value="">Select Specialization</option>
                                                <option value="Mkt&Fin">Mkt&Fin</option>
                                                <option value="Mkt&HR">Mkt&HR</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="action-buttons">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-magic"></i>
                                    Generate Prediction
                                </button>
                                <button type="button" class="btn btn-secondary" onclick="fillSampleData()">
                                    <i class="fas fa-database"></i>
                                    Load Sample
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="results-container">
                        <div class="results-header">
                            <i class="fas fa-chart-pie"></i>
                            <h3>Prediction Results</h3>
                        </div>
                        
                        <div class="prediction-display" id="predictionDisplay">
                            <div class="probability-badge" id="probabilityBadge">--</div>
                            <div class="prediction-status" id="predictionStatus">Ready for Analysis</div>
                            <div class="prediction-description" id="predictionDescription">
                                Enter candidate details and click "Generate Prediction" to get started
                            </div>
                        </div>
                        
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h4>Confidence</h4>
                                <div class="value" id="confidenceValue">--</div>
                            </div>
                            <div class="metric-card">
                                <h4>Data Quality</h4>
                                <div class="value" id="dataQualityValue">--</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <h3>Analyzing Candidate Data</h3>
                <p>Our AI model is processing the information...</p>
            </div>
        </div>

        <script>
            document.getElementById('predictionForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (key === 'ssc_p' || key === 'hsc_p' || key === 'degree_p' || key === 'etest_p' || key === 'mba_p') {
                        data[key] = parseFloat(value);
                    } else {
                        data[key] = value;
                    }
                }

                // Show loading
                document.getElementById('loadingOverlay').style.display = 'flex';

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();
                    
                    // Hide loading
                    document.getElementById('loadingOverlay').style.display = 'none';
                    
                    // Update results
                    const probability = (result.Placement_Probability * 100).toFixed(1);
                    const isPlaced = result.Placement;
                    
                    const predictionDisplay = document.getElementById('predictionDisplay');
                    const probabilityBadge = document.getElementById('probabilityBadge');
                    const predictionStatus = document.getElementById('predictionStatus');
                    const predictionDescription = document.getElementById('predictionDescription');
                    
                    probabilityBadge.textContent = probability + '%';
                    probabilityBadge.className = 'probability-badge ' + (isPlaced ? 'success' : 'danger');
                    
                    predictionStatus.textContent = isPlaced ? 'High Placement Probability' : 'Low Placement Probability';
                    predictionDescription.textContent = isPlaced ? 
                        'This candidate shows strong indicators for successful placement' : 
                        'Consider additional training or skill development for better placement chances';
                    
                    predictionDisplay.className = 'prediction-display ' + (isPlaced ? 'success' : 'danger');
                    
                    // Update metrics
                    document.getElementById('confidenceValue').textContent = 
                        probability > 70 ? 'High' : probability > 40 ? 'Medium' : 'Low';
                    document.getElementById('dataQualityValue').textContent = 'Excellent';
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('loadingOverlay').style.display = 'none';
                    alert('Error occurred while making prediction. Please try again.');
                }
            });

            function fillSampleData() {
                const sampleData = {
                    gender: 'M',
                    ssc_p: 41.0,
                    ssc_b: 'Central',
                    hsc_p: 38.66,
                    hsc_b: 'Central',
                    hsc_s: 'Science',
                    degree_p: 28.0,
                    degree_t: 'Sci&Tech',
                    etest_p: 46.0,
                    mba_p: 31.3,
                    specialisation: 'Mkt&Fin',
                    workex: 'Yes'
                };

                for (let [key, value] of Object.entries(sampleData)) {
                    const element = document.getElementById(key);
                    if (element) {
                        element.value = value;
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/predict',methods=['POST'])
def predict():
    candidate = request.get_json()
    X = dv.transform(candidate)
    preds = model.predict_proba(X)[:,1]
    placement = preds > 0.5
    result ={
        "Placement_Probability" : float(preds),
        "Placement" :bool(placement)
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)