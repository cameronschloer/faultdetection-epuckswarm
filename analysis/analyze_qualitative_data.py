from extract_data_qualitative_human_experiments import extract_qual_data_from_csv

filename = '../data/user_study_user_data/qualitative_raw_results.csv'
data = extract_qual_data_from_csv(filename)
print(data)