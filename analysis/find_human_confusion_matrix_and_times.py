import extract_data_quantitative_human_experiments as quant
import analysis_utils as au
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score, matthews_corrcoef


def calculate_response_times(experiment, correct_id):
    match_found = False
    guess_time, fault_injection_time = 0.0, 0.0
    for i in range(len(experiment.guesses)):
        if experiment.guesses[i].robot_id == correct_id and not experiment.guesses[i].is_revoke:
            if type(experiment.guesses[i].timestamp) is float:
                guess_time = experiment.guesses[i].timestamp
                match_found = True
                break
            else:
                print(type(experiment.guesses[i].timestamp))
                print(f"WARNING: Match found in guesses, but the timestamp was not valid: {experiment.guesses[i].timestamp}, will try again to see if match exists later on")
                continue

    true_value_found = False
    if match_found:
        for i in range(len(experiment.true_values)):
            if experiment.true_values[i].robot_id == correct_id:
                true_value_found = True
                if type(experiment.true_values[i].timestamp) is float:
                    fault_injection_time = experiment.true_values[i].timestamp
                    break
                else:
                    print(type(experiment.true_values[i].timestamp))
                    raise ValueError(f"ERROR: Match found in true values, but the timestamp was not valid: {experiment.true_values[i].timestamp}")
    else:
        print(f"WARNING: No match found in calculate_response_times. This means there is an issue with the true positive that was detected")
        return None
                    
    if true_value_found:
        response_time = guess_time - fault_injection_time
        return response_time
    else:
        raise ValueError(f"No true value found in calculate_response_times.")


def populate_confusion_matrix(experiment):
    # Focus on the hypothesis first, then try to explain those results, not just going looking for some new interesting find.
    confusion_matrix = au.ConfusionMatrix()

    confusion_matrix.total_robots = experiment.metadata.num_robots

    actual_faulty_ids = []
    for faulty_robot in experiment.true_values:
        actual_faulty_ids.append(faulty_robot.robot_id)

    guess_faulty_ids = set()
    for guess_robot in experiment.guesses:
        guess_faulty_ids.add(guess_robot.robot_id)

    response_times = []
    for guess_id in guess_faulty_ids:
        if guess_id in actual_faulty_ids:
            time_from_faulty = calculate_response_times(experiment, guess_id)
            if time_from_faulty == None:
                confusion_matrix.true_positives += 1
            elif time_from_faulty < 0:
                confusion_matrix.false_positives += 1
                confusion_matrix.false_negatives += 1
            else:
                confusion_matrix.true_positives += 1
                response_times.append(time_from_faulty)
            
        else:
            confusion_matrix.false_positives += 1

    for actual_id in actual_faulty_ids:
        if actual_id not in guess_faulty_ids:
            confusion_matrix.false_negatives += 1

    num_total_robots = 64 if experiment.metadata.video_type % 2 == 0 else 16  # 64 for even, 16 for odd
    num_faulty_robots = len(experiment.true_values)
    confusion_matrix.true_negatives = (num_total_robots - num_faulty_robots) - confusion_matrix.false_positives

    if num_faulty_robots != (confusion_matrix.true_positives + confusion_matrix.false_negatives):
        raise ValueError("Cannot have a different number of faulty robots than the sum of true positives and false negatives")
    
    return confusion_matrix, response_times

def populate_cm_for_each_experiment(data):
    for i in range(len(data)):
        print(f"Populating user {data[i].user_number}")
        # Go through each video
        for j in range(len(data[i].video_experiments)):
            experiment = data[i].video_experiments[j]
            data[i].video_experiments[j].confusion_matrix, data[i].video_experiments[j].response_times  = populate_confusion_matrix(experiment)

    return data

def calculate_percentage_confusion_matrix_times(data):
    pass

def calc_accuracy(tp, tn, total):
    accuracy = (tp+tn)/total
    return accuracy

def calc_f1_score(tp, fp, fn):
    if tp == 0:
        print("tp equals zero!")
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score

def calc_matthews_coefficient(tp, fp, fn, tn):
    """Calculates the Matthews correlation coefficient (MCC).

    Args:
        tp (int): True positives.
        fp (int): False positives.
        tn (int): True negatives.
        fn (int): False negatives.

    Returns:
        float: The Matthews correlation coefficient.
    """

    numerator = (tp * tn) - (fp * fn)
    denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    if denominator == 0:
        print("WARNING: mc's denominator was zero")
        return 0

    mcc = numerator / denominator
    return mcc


def get_cm_metrics(cm):
    tp = cm.true_positives
    tn = cm.true_negatives
    fp = cm.false_positives
    fn = cm.false_negatives
    total = cm.total_robots

    accuracy = calc_accuracy(tp, tn, total)
    f1_score = calc_f1_score(tp, fp, fn)
    mcc = calc_matthews_coefficient(tp, fp, fn, tn)

    return accuracy, f1_score, mcc


def sum_confusion_matrices(cm1, cm2):
    total = au.ConfusionMatrix()
    total.true_positives = cm1.true_positives + cm2.true_positives
    total.true_negatives = cm1.true_negatives + cm2.true_negatives
    total.false_positives = cm1.false_positives + cm2.false_positives
    total.false_negatives = cm1.false_negatives + cm2.false_negatives
    total.revoked_true_positives = cm1.revoked_true_positives + cm2.revoked_true_positives
    total.revoked_false_positives = cm1.revoked_false_positives + cm2.revoked_false_positives
    total.total_robots = cm1.total_robots + cm2.total_robots
    return total

def get_grouped_data(data, video_types_requested):
    confusion_matrix = au.ConfusionMatrix()
    response_times = []
    for i in range(len(data)):
        for j in range(len(data[i].video_experiments)):
            if data[i].video_experiments[j].metadata.video_type in video_types_requested:
                response_times = response_times + data[i].video_experiments[j].response_times
                confusion_matrix = sum_confusion_matrices(confusion_matrix, data[i].video_experiments[j].confusion_matrix)

    return response_times, confusion_matrix

def main():
    LEDS_ON_VIDEO_TYPES = (1, 3, 5, 7, 9, 11)
    LEDS_OFF_VIDEO_TYPES = (2, 4, 6, 8, 10, 12)
    ALL = range(12)
    quant_filename = '../data/user_study_user_data/quantitative_raw_results.csv'
    quant_data = quant.extract_quant_data_from_csv(quant_filename)
    populated_data = populate_cm_for_each_experiment(quant_data)
    # print(populated_data)
    leds_on_rt, leds_on_cm = get_grouped_data(populated_data, LEDS_ON_VIDEO_TYPES)
    leds_off_rt, leds_off_cm = get_grouped_data(populated_data, LEDS_OFF_VIDEO_TYPES)
    grouped_response_times = [leds_on_rt, leds_off_rt]

    acc_leds_on, f1_leds_on, mcc_leds_on = get_cm_metrics(leds_on_cm)
    acc_leds_off, f1_leds_off, mcc_leds_off = get_cm_metrics(leds_off_cm)

    print(acc_leds_on, f1_leds_on, mcc_leds_on)
    print(acc_leds_off, f1_leds_off, mcc_leds_off)

    plt.boxplot(grouped_response_times)
    plt.title("Response Times (Human)")
    plt.xlabel("LED Status")
    plt.ylabel("time (s)")
    plt.xticks([1, 2], ["LEDs On", "LEDs Off"])
    plt.show()

    # Calculate true positive rate:



if __name__ == "__main__":
    main()