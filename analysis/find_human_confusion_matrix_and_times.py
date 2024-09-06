import extract_data_quantitative_human_experiments as quant
from dataclasses import dataclass


@dataclass
class ConfusionMatrix:
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


def populate_confusion_matrix(data):
    pass

def calculate_response_times(data):
    pass

def calculate_percentage_confusion_matrix_times(data):
    pass


def main():
    quant_filename = '../data/user_study_user_data/quantitative_raw_results.csv'
    quant_data = quant.extract_quant_data_from_csv(quant_filename)


if __name__ == "__main__":
    main()