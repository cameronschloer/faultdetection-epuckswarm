import extract_data_qualitative_human_experiments as qual
import extract_data_quantitative_human_experiments as quant
import analyze_swarm_feedback as sf

def main():
    qual_filename = '../data/user_study_user_data/qualitative_raw_results.csv'
    quant_filename = '../data/user_study_user_data/quantitative_raw_results.csv'

    qual_data = qual.extract_qual_data_from_csv(qual_filename)
    quant_data = quant.extract_quant_data_from_csv(quant_filename)

    # Create accuracy and time measurements for all three cases, swarm only, human only, combined
    

    # Visualize the data to start with

if __name__ == "__main__":
    main()