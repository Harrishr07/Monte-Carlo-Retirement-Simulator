import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MonteCarloRetirementSimulator:
    """
    A comprehensive Monte Carlo simulator for retirement planning
    """
    
    def __init__(self):
        self.results = None
        self.simulations_df = None
        
    def run_simulation(self, 
                      current_savings=50000,
                      monthly_contribution=1000,
                      years=30,
                      annual_return=7.0,
                      annual_volatility=15.0,
                      inflation_rate=2.5,
                      goal_amount=1500000,
                      n_simulations=10000):
        """
        Run Monte Carlo simulation for retirement planning
        
        Parameters:
        -----------
        current_savings : float
            Current retirement savings
        monthly_contribution : float
            Monthly contribution amount (assumes end-of-month)
        years : int
            Number of years until retirement
        annual_return : float
            Expected average annual return (percentage)
        annual_volatility : float
            Expected annual volatility (standard deviation, percentage)
        inflation_rate : float
            Expected annual inflation rate (percentage)
        goal_amount : float
            Target retirement amount (in today's dollars)
        n_simulations : int
            Number of Monte Carlo simulations to run
        
        Returns:
        --------
        dict: Simulation results and statistics
        """
        
        # Convert percentages to decimals
        annual_return = annual_return / 100
        annual_volatility = annual_volatility / 100
        inflation_rate = inflation_rate / 100
        
        # Adjust goal for inflation (future dollars)
        future_goal = goal_amount * (1 + inflation_rate) ** years
        
        # Pre-calculate monthly values
        months = years * 12
        monthly_return = (1 + annual_return) ** (1/12) - 1
        monthly_volatility = annual_volatility / np.sqrt(12)
        
        # Initialize results array
        results = np.zeros((months + 1, n_simulations))
        results[0] = current_savings
        
        # Run simulations
        print(f"Running {n_simulations} Monte Carlo simulations...")
        
        for month in range(1, months + 1):
            # Generate random returns for all simulations at once
            random_returns = np.random.normal(
                monthly_return, 
                monthly_volatility, 
                n_simulations
            )
            results[month] = results[month - 1] * (1 + random_returns)
            if month % 12 != 0:  # Add contribution every month
                results[month] += monthly_contribution
        
        # Store results
        self.results = results
        self.simulations_df = pd.DataFrame(results.T)
        
        # Calculate statistics
        final_values = results[-1]
        
        # Calculate success probability
        success_count = np.sum(final_values >= future_goal)
        success_probability = (success_count / n_simulations) * 100
        
        # Calculate percentiles
        percentiles = {
            '5th': np.percentile(final_values, 5),
            '25th': np.percentile(final_values, 25),
            '50th': np.percentile(final_values, 50),
            '75th': np.percentile(final_values, 75),
            '95th': np.percentile(final_values, 95)
        }
        
        # Calculate shortfall risk
        shortfall_amount = future_goal - final_values[final_values < future_goal]
        avg_shortfall = np.mean(shortfall_amount) if len(shortfall_amount) > 0 else 0
        
        # Prepare summary statistics
        summary = {
            'success_probability': success_probability,
            'future_goal': future_goal,
            'median_final_value': percentiles['50th'],
            'mean_final_value': np.mean(final_values),
            'std_final_value': np.std(final_values),
            'percentiles': percentiles,
            'avg_shortfall': avg_shortfall,
            'min_value': np.min(final_values),
            'max_value': np.max(final_values),
            'shortfall_probability': 100 - success_probability
        }
        
        print(f"✅ Simulation complete!")
        print(f"Probability of reaching goal: {success_probability:.1f}%")
        print(f"Median final value: ${percentiles['50th']:,.0f}")
        
        return summary
    
    def plot_results(self, summary, save_path=None):
        """
        Generate visualization plots for the simulation results
        
        Parameters:
        -----------
        summary : dict
            Simulation summary statistics
        save_path : str
            Path to save the plot (optional)
        """
        
        fig = plt.figure(figsize=(16, 10))
        
        # 1. Distribution of final values
        ax1 = plt.subplot(2, 2, 1)
        final_values = self.results[-1]
        
        plt.hist(final_values, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(x=summary['future_goal'], color='red', linestyle='--', 
                   linewidth=2, label=f"Goal: ${summary['future_goal']:,.0f}")
        plt.axvline(x=summary['median_final_value'], color='green', linestyle='--',
                   linewidth=2, label=f"Median: ${summary['median_final_value']:,.0f}")
        
        plt.title('Distribution of Final Portfolio Values', fontsize=14, fontweight='bold')
        plt.xlabel('Final Portfolio Value ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. Probability of success
        ax2 = plt.subplot(2, 2, 2)
        success_prob = summary['success_probability']
        failure_prob = 100 - success_prob
        
        colors = ['#4CAF50', '#F44336']
        plt.pie([success_prob, failure_prob], 
                labels=[f'Success\n{success_prob:.1f}%', f'Shortfall\n{failure_prob:.1f}%'],
                colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('Probability of Reaching Retirement Goal', fontsize=14, fontweight='bold')
        
        # 3. Percentile plot
        ax3 = plt.subplot(2, 2, 3)
        percentiles = summary['percentiles']
        labels = ['5th', '25th', '50th', '75th', '95th']
        values = [percentiles['5th'], percentiles['25th'], percentiles['50th'], 
                 percentiles['75th'], percentiles['95th']]
        
        bars = plt.bar(labels, values, color=['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2', '#073B4C'])
        plt.axhline(y=summary['future_goal'], color='red', linestyle='--', 
                   linewidth=2, label='Goal')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 10000,
                    f'${value:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.title('Portfolio Value at Different Percentiles', fontsize=14, fontweight='bold')
        plt.ylabel('Portfolio Value ($)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        # 4. Sample simulation paths
        ax4 = plt.subplot(2, 2, 4)
        years = self.results.shape[0] // 12
        
        # Plot 50 random simulation paths
        for i in range(min(50, self.results.shape[1])):
            plt.plot(np.arange(years + 1), self.results[:, i][::12] / 1000, 
                    alpha=0.1, color='blue')
        
        # Plot median path
        median_path = np.median(self.results[:, :50], axis=1)[::12]
        plt.plot(np.arange(years + 1), median_path / 1000, 
                color='red', linewidth=3, label='Median Path')
        
        plt.axhline(y=summary['future_goal'] / 1000, color='green', 
                   linestyle='--', linewidth=2, label='Goal')
        
        plt.title('Sample Simulation Paths (50 shown)', fontsize=14, fontweight='bold')
        plt.xlabel('Years', fontsize=12)
        plt.ylabel('Portfolio Value ($ thousands)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()
    
    def generate_report(self, summary, inputs):
        """
        Generate a detailed text report of the simulation
        
        Parameters:
        -----------
        summary : dict
            Simulation summary statistics
        inputs : dict
            Input parameters used for simulation
        """
        
        print("\n" + "="*60)
        print("MONTE CARLO RETIREMENT SIMULATION REPORT")
        print("="*60)
        
        print("\nINPUT PARAMETERS")
        print("-"*40)
        for key, value in inputs.items():
            if 'return' in key or 'volatility' in key or 'inflation' in key:
                print(f"{key.replace('_', ' ').title()}: {value}%")
            elif 'savings' in key or 'contribution' in key or 'goal' in key:
                print(f"{key.replace('_', ' ').title()}: ${value:,.0f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\nSIMULATION RESULTS")
        print("-"*40)
        print(f"Probability of Reaching Goal: {summary['success_probability']:.1f}%")
        print(f"Shortfall Probability: {summary['shortfall_probability']:.1f}%")
        print(f"Future Goal (inflation-adjusted): ${summary['future_goal']:,.0f}")
        print(f"\nFinal Portfolio Statistics:")
        print(f"  Mean: ${summary['mean_final_value']:,.0f}")
        print(f"  Median: ${summary['median_final_value']:,.0f}")
        print(f"  Standard Deviation: ${summary['std_final_value']:,.0f}")
        print(f"  Minimum: ${summary['min_value']:,.0f}")
        print(f"  Maximum: ${summary['max_value']:,.0f}")
        
        print(f"\nPERCENTILE ANALYSIS")
        print("-"*40)
        percentiles = summary['percentiles']
        for key, value in percentiles.items():
            print(f"{key} percentile: ${value:,.0f}")
        
        print(f"\nRISK ANALYSIS")
        print("-"*40)
        print(f"Average Shortfall (if goal not met): ${summary['avg_shortfall']:,.0f}")
        
        # Provide recommendations
        print(f"\nRECOMMENDATIONS")
        print("-"*40)
        
        if summary['success_probability'] >= 80:
            print("You're on track! Your current plan has a high probability of success.")
            print("Consider maintaining your strategy or potentially reducing risk.")
        elif summary['success_probability'] >= 60:
            print("Your plan has a moderate chance of success.")
            print("Consider:")
            print("  • Increasing monthly contributions by 10-20%")
            print("  • Extending retirement by 2-3 years")
            print("  • Reviewing investment strategy for better returns")
        else:
            print("Your current plan has a low probability of reaching your goal.")
            print("Immediate actions needed:")
            print("  • Increase monthly contributions significantly")
            print("  • Consider working longer (5+ years)")
            print("  • Consult a financial advisor")
            print("  • Review and potentially increase risk tolerance")
        
        print("\n" + "="*60)
        print("End of Report")
        print("="*60 + "\n")
    
    def sensitivity_analysis(self, base_inputs, variable_to_test, test_values):
        """
        Perform sensitivity analysis on a specific variable
        
        Parameters:
        -----------
        base_inputs : dict
            Base input parameters
        variable_to_test : str
            Variable to test sensitivity for
        test_values : list
            List of values to test
        
        Returns:
        --------
        DataFrame: Results of sensitivity analysis
        """
        
        results = []
        
        print(f"\nRunning Sensitivity Analysis on {variable_to_test}...")
        
        for value in test_values:
            # Create copy of inputs with modified value
            test_inputs = base_inputs.copy()
            test_inputs[variable_to_test] = value
            
            # Run simulation
            summary = self.run_simulation(**test_inputs)
            
            results.append({
                variable_to_test: value,
                'success_probability': summary['success_probability'],
                'median_value': summary['median_final_value']
            })
        
        # Convert to DataFrame
        sensitivity_df = pd.DataFrame(results)
        
        # Plot sensitivity
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(sensitivity_df[variable_to_test], sensitivity_df['success_probability'], 
                marker='o', linewidth=2, color='blue')
        ax1.set_xlabel(variable_to_test.replace('_', ' ').title())
        ax1.set_ylabel('Success Probability (%)')
        ax1.set_title(f'Impact of {variable_to_test} on Success Probability')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(sensitivity_df[variable_to_test], sensitivity_df['median_value'], 
                marker='s', linewidth=2, color='green')
        ax2.set_xlabel(variable_to_test.replace('_', ' ').title())
        ax2.set_ylabel('Median Final Value ($)')
        ax2.set_title(f'Impact of {variable_to_test} on Median Portfolio Value')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return sensitivity_df