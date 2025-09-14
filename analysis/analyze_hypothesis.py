import extract_data_qualitative_human_experiments as qual
import extract_data_quantitative_human_experiments as quant
import analyze_swarm_feedback as sf
import matplotlib.pyplot as plt
from enum import Enum


def create_plot_from_qualitative_data(data, in_prequestionnaire, data_to_plot):
    pass
    """
    Parses a list of custom objects and plots the data.

    Args:
        object_list (list): A list of objects, where each object has
                            'name' and 'score' attributes.
    """
    
    # 1. Initialize lists to store the extracted data
    names = []
    scores = []
    
    # 2. Loop through the list of objects and extract the values
    #    You'll need to modify this part to match your object attributes
    for obj in data:
        names.append(obj.name)
        scores.append(obj.score)
        
    # 3. Create a pandas DataFrame from the extracted lists
    #    This step is highly recommended as it simplifies plotting and analysis
    data_df = pd.DataFrame({
        'Names': names,
        'Scores': scores
    })
    
    print("DataFrame created from parsed data:")
    print(data_df)
    
    # 4. Create the plot using matplotlib
    plt.figure(figsize=(10, 6))  # Set the figure size for better readability
    
    # Create a bar chart
    plt.bar(data_df['Names'], data_df['Scores'], color='skyblue')
    
    # Add titles and labels for clarity
    plt.title('Scores by Person', fontsize=16)
    plt.xlabel('Names', fontsize=12)
    plt.ylabel('Scores', fontsize=12)
    
    # Add a grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ensure a tight layout
    plt.tight_layout()
    
    # Save the plot to a file
    plt.savefig('scores_bar_chart.png')
    
    print("\nPlot saved as scores_bar_chart.png")

def main():
    qual_filename = '../data/user_study_user_data/qualitative_raw_results.csv'
    quant_filename = '../data/user_study_user_data/quantitative_raw_results.csv'

    qual_data = qual.extract_qual_data_from_csv(qual_filename)
    quant_data = quant.extract_quant_data_from_csv(quant_filename, False)

    # Create accuracy and time measurements for all three cases, swarm only, human only, combined
    

    # Visualize the data to start with


if __name__ == "__main__":
    main()