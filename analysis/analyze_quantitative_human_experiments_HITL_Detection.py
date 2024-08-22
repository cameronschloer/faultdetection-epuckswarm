import pandas as pd

# Read the CSV file into a DataFrame
# df = pd.read_csv('../data/user_study_user_data/quantitative_raw_results.csv')

filename = '../data/user_study_user_data/quantitative_raw_results.csv'
# Read the CSV file into a DataFrame
# df = pd.read_csv('../data/user_study_user_data/qualitative_raw_results.csv')
# print(df.info())

try:
    df = pd.read_csv(filename)
except UnicodeDecodeError:
    # Try different encodings
    print("failed first pass")
    for encoding in ['utf-8', 'latin1', 'cp1252']:
        try:
            print(f"trying {encoding}")
            df = pd.read_csv(filename, encoding=encoding)
            break
        except UnicodeDecodeError:
            pass

    if df is None:
        print("all failed")
        # If all attempts fail, try ignoring errors
        df = pd.read_csv(filename, errors='ignore')

print(df)