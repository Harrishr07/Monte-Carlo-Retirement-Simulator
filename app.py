"""
MONTE CARLO SIMULATOR - SIMPLE BUT MODERN
Only 100 lines of effective CSS improvements
"""

from flask import Flask, render_template_string, request, jsonify
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# ============================================================================
# MONTE CARLO SIMULATOR (Same as before)
# ============================================================================
class MonteCarloRetirementSimulator:
    def __init__(self):
        self.results = None
    
    def run_simulation(self, 
                      current_savings=50000,
                      monthly_contribution=1000,
                      years=30,
                      annual_return=7.0,
                      annual_volatility=15.0,
                      inflation_rate=2.5,
                      goal_amount=1500000,
                      n_simulations=5000):
        
        # Convert percentages
        annual_return /= 100.0
        annual_volatility /= 100.0
        inflation_rate /= 100.0
        
        # Calculate future goal
        future_goal = goal_amount * ((1 + inflation_rate) ** years)
        
        # Monthly calculations
        months = years * 12
        monthly_return = (1 + annual_return) ** (1/12.0) - 1
        monthly_volatility = annual_volatility / np.sqrt(12)
        
        # Initialize results
        results = np.zeros((months + 1, n_simulations))
        results[0, :] = current_savings
        
        # Run simulations
        for month in range(1, months + 1):
            random_returns = np.random.normal(monthly_return, monthly_volatility, n_simulations)
            results[month] = results[month - 1] * (1 + random_returns)
            results[month] += monthly_contribution
        
        self.results = results
        
        # Calculate statistics
        final_values = results[-1]
        success_count = np.sum(final_values >= future_goal)
        success_probability = (success_count / n_simulations) * 100.0
        
        # Percentiles
        percentiles = {
            '5th': float(np.percentile(final_values, 5)),
            '25th': float(np.percentile(final_values, 25)),
            '50th': float(np.percentile(final_values, 50)),
            '75th': float(np.percentile(final_values, 75)),
            '95th': float(np.percentile(final_values, 95))
        }
        
        # Summary
        summary = {
            'success_probability': float(success_probability),
            'future_goal': float(future_goal),
            'median_final_value': float(percentiles['50th']),
            'mean_final_value': float(np.mean(final_values)),
            'std_final_value': float(np.std(final_values)),
            'min_value': float(np.min(final_values)),
            'max_value': float(np.max(final_values)),
            'percentiles': percentiles,
            'n_simulations': n_simulations
        }
        
        return summary
    
    def create_plot(self, summary):
        """Create simple plot"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            
            final_values = self.results[-1]
            years = self.results.shape[0] // 12
            
            # 1. Histogram
            axes[0, 0].hist(final_values, bins=40, alpha=0.7, color='#3498db', edgecolor='white')
            axes[0, 0].axvline(x=summary['future_goal'], color='red', linestyle='--', linewidth=2)
            axes[0, 0].set_title('Portfolio Value Distribution')
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Success probability
            success_prob = summary['success_probability']
            failure_prob = 100 - success_prob
            axes[0, 1].pie([success_prob, failure_prob],
                          labels=[f'Success\n{success_prob:.1f}%', f'Shortfall\n{failure_prob:.1f}%'],
                          colors=['#2ecc71', '#e74c3c'], autopct='%1.1f%%')
            axes[0, 1].set_title('Success Probability')
            
            # 3. Percentile analysis
            percentiles = summary['percentiles']
            labels = ['5th', '25th', '50th', '75th', '95th']
            values = [percentiles['5th'], percentiles['25th'], percentiles['50th'],
                     percentiles['75th'], percentiles['95th']]
            colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']
            axes[1, 0].bar(labels, values, color=colors)
            axes[1, 0].set_title('Percentile Analysis')
            axes[1, 0].set_ylabel('Value ($)')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            
            # 4. Sample paths
            for i in range(min(10, self.results.shape[1])):
                axes[1, 1].plot(range(years + 1), self.results[:, i][::12] / 1000, alpha=0.2, color='blue')
            
            axes[1, 1].axhline(y=summary['future_goal'] / 1000, color='red', linestyle='--', linewidth=2)
            axes[1, 1].set_title('Simulation Paths')
            axes[1, 1].set_xlabel('Years')
            axes[1, 1].set_ylabel('Value ($K)')
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return plot_data
            
        except Exception as e:
            print(f"Error creating plot: {e}")
            return None

# ============================================================================
# SIMPLE BUT MODERN HTML/CSS
# ============================================================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Monte Carlo Simulator</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* === MODERN CSS IMPROVEMENTS === */
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            margin: 10px 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            display: flex;
            flex-wrap: wrap;
            padding: 30px;
            gap: 30px;
        }
        
        .input-section {
            flex: 1;
            min-width: 300px;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        .results-section {
            flex: 1.5;
            min-width: 300px;
        }
        
        /* Form improvements */
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input[type="number"]:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        /* Slider improvements */
        input[type="range"] {
            width: 100%;
            height: 8px;
            -webkit-appearance: none;
            background: linear-gradient(to right, #667eea, #764ba2);
            border-radius: 4px;
            margin: 10px 0;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 22px;
            height: 22px;
            background: white;
            border-radius: 50%;
            border: 3px solid #667eea;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .slider-value {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        /* Button improvements */
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        /* Loading spinner */
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Results improvements */
        .probability-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .probability-value {
            font-size: 3.5rem;
            font-weight: 800;
            margin: 10px 0;
        }
        
        .high { color: #2ecc71; }
        .medium { color: #f39c12; }
        .low { color: #e74c3c; }
        
        /* Stats grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 10px 0;
        }
        
        /* Plot container */
        .plot-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-top: 20px;
            text-align: center;
        }
        
        .plot-img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .content {
                flex-direction: column;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .probability-value {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Monte Carlo Retirement Simulator</h1>
            <p>Visualize your financial future with Monte Carlo simulations</p>
        </div>
        
        <div class="content">
            <!-- Input Section -->
            <div class="input-section">
                <h2 style="color: #2c3e50; margin-bottom: 25px;">Simulation Parameters</h2>
                
                <div class="form-group">
                    <label>Current Savings ($)</label>
                    <input type="number" id="currentSavings" value="50000" min="0" step="1000">
                </div>
                
                <div class="form-group">
                    <label>Monthly Contribution ($)</label>
                    <input type="number" id="monthlyContribution" value="1000" min="0" step="100">
                </div>
                
                <div class="form-group">
                    <label>Years Until Retirement</label>
                    <input type="number" id="years" value="30" min="5" max="60">
                </div>
                
                <div class="form-group">
                    <label>Target Amount ($)</label>
                    <input type="number" id="goalAmount" value="1500000" min="0" step="10000">
                </div>
                
                <div class="form-group">
                    <label>Expected Return: <span class="slider-value" id="returnValue">7%</span></label>
                    <input type="range" id="annualReturn" min="2" max="15" step="0.1" value="7" 
                           oninput="document.getElementById('returnValue').textContent = this.value + '%'">
                </div>
                
                <div class="form-group">
                    <label>Volatility: <span class="slider-value" id="volatilityValue">15%</span></label>
                    <input type="range" id="annualVolatility" min="5" max="30" step="0.1" value="15"
                           oninput="document.getElementById('volatilityValue').textContent = this.value + '%'">
                </div>
                
                <div class="form-group">
                    <label>Inflation Rate: <span class="slider-value" id="inflationValue">2.5%</span></label>
                    <input type="range" id="inflationRate" min="1" max="6" step="0.1" value="2.5"
                           oninput="document.getElementById('inflationValue').textContent = this.value + '%'">
                </div>
                
                <div class="form-group">
                    <label>Simulations: <span class="slider-value" id="simulationsValue">5000</span></label>
                    <input type="range" id="nSimulations" min="1000" max="20000" step="1000" value="5000"
                           oninput="document.getElementById('simulationsValue').textContent = this.value">
                </div>
                <div style="margin-top: 30px; text-align: center;">
                    <button onclick="runSimulation()">Run Simulation</button>
                    <button onclick="resetForm()" style="background: #95a5a6;">Reset</button>
                </div>
            </div>
            
            <!-- Results Section -->
            <div class="results-section">
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <h3>Running Simulations...</h3>
                    <p>Analyzing <span id="simCount">5000</span> market scenarios</p>
                </div>
                
                <div id="results" style="display: none;">
                    <!-- Probability Card -->
                    <div class="probability-card">
                        <h2 style="margin: 0 0 10px 0; font-size: 1.3rem;">Probability of Success</h2>
                        <div id="probability" class="probability-value">--%</div>
                        <p>Based on <span id="totalSims">5000</span> simulations</p>
                    </div>
                    
                    <!-- Statistics -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div style="color: #7f8c8d; font-size: 0.9rem;">Median Value</div>
                            <div id="medianValue" class="stat-value">--</div>
                        </div>
                        <div class="stat-card">
                            <div style="color: #7f8c8d; font-size: 0.9rem;">Target (Future)</div>
                            <div id="futureGoal" class="stat-value">--</div>
                        </div>
                        <div class="stat-card">
                            <div style="color: #7f8c8d; font-size: 0.9rem;">Average Value</div>
                            <div id="meanValue" class="stat-value">--</div>
                        </div>
                        <div class="stat-card">
                            <div style="color: #7f8c8d; font-size: 0.9rem;">Std Deviation</div>
                            <div id="stdValue" class="stat-value">--</div>
                        </div>
                    </div>
                    
                    <!-- Plot -->
                    <div class="plot-container">
                        <h3 style="margin: 0 0 15px 0; color: #2c3e50;">Simulation Results</h3>
                        <img id="plotImage" class="plot-img" src="" alt="Results">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Format currency
        function formatCurrency(value) {
            if (value >= 1000000) {
                return '$' + (value / 1000000).toFixed(2) + 'M';
            } else if (value >= 1000) {
                return '$' + (value / 1000).toFixed(0) + 'K';
            }
            return '$' + Math.round(value).toLocaleString();
        }
        
        // Run simulation
        async function runSimulation() {
            // Show loading, hide results
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            // Get parameters
            const params = {
                current_savings: parseFloat(document.getElementById('currentSavings').value) || 50000,
                monthly_contribution: parseFloat(document.getElementById('monthlyContribution').value) || 1000,
                years: parseInt(document.getElementById('years').value) || 30,
                annual_return: parseFloat(document.getElementById('annualReturn').value) || 7.0,
                annual_volatility: parseFloat(document.getElementById('annualVolatility').value) || 15.0,
                inflation_rate: parseFloat(document.getElementById('inflationRate').value) || 2.5,  // <-- GET FROM INPUT
                goal_amount: parseFloat(document.getElementById('goalAmount').value) || 1500000,
                n_simulations: parseInt(document.getElementById('nSimulations').value) || 5000
            };
            // Update loading text
            document.getElementById('simCount').textContent = params.n_simulations;
            
            try {
                const response = await fetch('/simulate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                });
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    // Display results
                    const summary = data.summary;
                    
                    // Update probability
                    const probElement = document.getElementById('probability');
                    const prob = summary.success_probability;
                    probElement.textContent = prob.toFixed(1) + '%';
                    
                    // Color coding
                    probElement.className = 'probability-value';
                    if (prob >= 80) probElement.classList.add('high');
                    else if (prob >= 60) probElement.classList.add('medium');
                    else probElement.classList.add('low');
                    
                    // Update simulation count
                    document.getElementById('totalSims').textContent = summary.n_simulations;
                    
                    // Update statistics
                    document.getElementById('medianValue').textContent = formatCurrency(summary.median_final_value);
                    document.getElementById('futureGoal').textContent = formatCurrency(summary.future_goal);
                    document.getElementById('meanValue').textContent = formatCurrency(summary.mean_final_value);
                    document.getElementById('stdValue').textContent = formatCurrency(summary.std_final_value);
                    
                    // Update plot
                    if (data.plot) {
                        document.getElementById('plotImage').src = 'data:image/png;base64,' + data.plot;
                    }
                    
                    // Show results
                    document.getElementById('results').style.display = 'block';
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // Reset form
        function resetForm() {
            document.getElementById('currentSavings').value = 50000;
            document.getElementById('monthlyContribution').value = 1000;
            document.getElementById('years').value = 30;
            document.getElementById('goalAmount').value = 1500000;
            document.getElementById('annualReturn').value = 7;
            document.getElementById('annualVolatility').value = 15;
            document.getElementById('inflationRate').value = 2.5;  // <-- ADD THIS LINE
            document.getElementById('nSimulations').value = 5000;
            
            // Reset display values
            document.getElementById('returnValue').textContent = '7%';
            document.getElementById('volatilityValue').textContent = '15%';
            document.getElementById('inflationValue').textContent = '2.5%';  // <-- ADD THIS LINE
            document.getElementById('simulationsValue').textContent = '5000';
            
            document.getElementById('results').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
        }
    </script>
</body>
</html>
'''

# ============================================================================
# FLASK ROUTES
# ============================================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        
        params = {
            'current_savings': float(data.get('current_savings', 50000)),
            'monthly_contribution': float(data.get('monthly_contribution', 1000)),
            'years': int(data.get('years', 30)),
            'annual_return': float(data.get('annual_return', 7.0)),
            'annual_volatility': float(data.get('annual_volatility', 15.0)),
            'inflation_rate': float(data.get('inflation_rate', 2.5)),
            'goal_amount': float(data.get('goal_amount', 1500000)),
            'n_simulations': int(data.get('n_simulations', 5000))
        }
        
        simulator = MonteCarloRetirementSimulator()
        summary = simulator.run_simulation(**params)
        plot_data = simulator.create_plot(summary)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'plot': plot_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("Monte Carlo Simulator - Modern Design")
    print("="*60)
    print("Starting server...")
    print("Open: http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, port=5000, use_reloader=False)