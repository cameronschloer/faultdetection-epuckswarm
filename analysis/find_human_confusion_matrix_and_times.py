import extract_data_quantitative_human_experiments as quant
import extract_data_qualitative_human_experiments as qual
import analysis_utils as au
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
from dataclasses import dataclass
import scipy.stats as stats


MISSING_USER_NUM = 18

class DataGroupingType(Enum):
    BY_USER = 0
    BY_WATCH_ORDER = 1
    BY_VIDEO_TYPE = 2
    BY_USER_THEN_VIDEO_TYPE = 3

    
@dataclass
class ListsOfGroupings():
    type_lists: list[list] = None
    user_lists: list[list] = None
    watch_order_lists: list[list] = None

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

def calculate_balanced_accuracy(tp, tn, fp, fn):
    """Calculates balanced accuracy.

    Args:
        tp: True positives.
        tn: True negatives.
        fp: False positives.
        fn: False negatives.

    Returns:
        Balanced accuracy.
    """

    try:
        sensitivity = tp / (tp + fn)
        specificity = tn / (tn + fp)

        balanced_accuracy = (sensitivity + specificity) / 2

        return balanced_accuracy

    except ZeroDivisionError:
        print("WARNING: No balanced accuracy could be found, division by Zero")
        return None

def calc_accuracy(tp, tn, total):
    try:
        accuracy = (tp+tn)/total
        return accuracy
    except ZeroDivisionError:
        print("WARNING: No accuracy could be found, division by Zero")
        return None

def calc_f1_score(tp, fp, fn):
    if tp == 0:
        print("WARNING: tp equals zero!")
    
    try:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score
    except ZeroDivisionError:
        print("WARNING: No F-Score could be found, division by Zero")
        return None
    

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
        return None

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
    bal_acc = calculate_balanced_accuracy(tp, tn, fp, fn)

    return accuracy, f1_score, mcc, bal_acc


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

def find_index_from_user_num(user_num):
    
    if user_num < MISSING_USER_NUM:
        index = user_num - 1  # Because index starts at 0

    elif user_num == MISSING_USER_NUM:
        index = None
        print(f"WARNING: Got missing user number in \"find_index_from_user_num\", {MISSING_USER_NUM}")
    else:
        index = user_num - 2  # Because of the skipped user

    return index

def get_grouped_data(data:quant.UserQuantData, data_grouping_type:DataGroupingType, first_grouping:list, second_grouping:list = None):
    confusion_matrix = au.ConfusionMatrix()
    response_times = []
    if data_grouping_type == DataGroupingType.BY_VIDEO_TYPE:
        for i in range(len(data)):
            for j in range(len(data[i].video_experiments)):
                if data[i].video_experiments[j].metadata.video_type in first_grouping:
                    response_times = response_times + data[i].video_experiments[j].response_times
                    confusion_matrix = sum_confusion_matrices(confusion_matrix, data[i].video_experiments[j].confusion_matrix)
    
    elif data_grouping_type == DataGroupingType.BY_USER:
        for user_num in first_grouping:
            user_index = find_index_from_user_num(user_num)
            if user_index == None and len(first_grouping) == 1:
                return None, None
            elif user_index == None:
                continue
            for experiment in data[user_index].video_experiments:
                response_times = response_times + experiment.response_times
                confusion_matrix = sum_confusion_matrices(confusion_matrix, experiment.confusion_matrix)

    elif data_grouping_type == DataGroupingType.BY_WATCH_ORDER:
        for i in range(len(data)):
            for j in range(len(data[i].video_experiments)):
                if data[i].video_experiments[j].metadata.user_watch_order in first_grouping:
                    response_times = response_times + experiment.response_times
                    confusion_matrix = sum_confusion_matrices(confusion_matrix, experiment.confusion_matrix)

    elif data_grouping_type == DataGroupingType.BY_USER_THEN_VIDEO_TYPE:
        # NOTE: first_grouping should be user, second_grouping type
        for user_num in first_grouping:
            user_index = find_index_from_user_num(user_num)
            if user_index == None and len(first_grouping) == 1:
                return None, None
            elif user_index == None:
                continue
            for j in range(len(data[user_index].video_experiments)):
                if data[user_index].video_experiments[j].metadata.video_type in second_grouping:
                    response_times = response_times + data[user_index].video_experiments[j].response_times
                    confusion_matrix = sum_confusion_matrices(confusion_matrix, data[user_index].video_experiments[j].confusion_matrix)

    return response_times, confusion_matrix

def get_append_and_print_grouped_data(data, data_grouping_type, grouped_resp_times_for_plotting, grouped_cms, first_grouping, second_grouping=None):
    response_times, confustion_matrix = get_grouped_data(data, data_grouping_type, first_grouping, second_grouping)
    if response_times != None and confustion_matrix != None:
        print(f"Recording group to lists, user {data[find_index_from_user_num(first_grouping[0])].user_number}")
        grouped_resp_times_for_plotting.append(response_times)
        grouped_cms.append(confustion_matrix)
        # print(confustion_matrix)
    return grouped_resp_times_for_plotting, grouped_cms

def gather_response_times_and_summed_cms(data:quant.UserQuantData, data_grouping_type:DataGroupingType, head_list:ListsOfGroupings):
    grouped_resp_times_for_plotting = []
    grouped_cms = []

    print("Raw Confusion Matrices:")
    
    if data_grouping_type == DataGroupingType.BY_USER_THEN_VIDEO_TYPE:
        for user_list in head_list.user_lists:
            print(user_list)
            for type_list in head_list.type_lists:
                grouped_resp_times_for_plotting, grouped_cms = get_append_and_print_grouped_data(data, data_grouping_type, grouped_resp_times_for_plotting, grouped_cms, user_list, type_list)

    elif data_grouping_type == DataGroupingType.BY_VIDEO_TYPE:
        for type_list in head_list.type_lists:
            grouped_resp_times_for_plotting, grouped_cms = get_append_and_print_grouped_data(data, data_grouping_type, grouped_resp_times_for_plotting, grouped_cms, type_list)
    
    elif data_grouping_type == DataGroupingType.BY_USER:
        for user_list in head_list.user_lists:
            grouped_resp_times_for_plotting, grouped_cms = get_append_and_print_grouped_data(data, data_grouping_type, grouped_resp_times_for_plotting, grouped_cms, user_list)

    elif data_grouping_type == DataGroupingType.BY_WATCH_ORDER:
        for watch_order_list in head_list.watch_order_lists:
            grouped_resp_times_for_plotting, grouped_cms = get_append_and_print_grouped_data(data, data_grouping_type, grouped_resp_times_for_plotting, grouped_cms, watch_order_list)

    return grouped_resp_times_for_plotting, grouped_cms


def gather_data_and_visualize_multiple_groups_of_data(data:quant.UserQuantData, data_grouping_type:DataGroupingType, head_list:ListsOfGroupings):
    grouped_resp_times_for_plotting, grouped_cms = gather_response_times_and_summed_cms(data, data_grouping_type, head_list)

    print("Metrics From Confusion Matrices")
    for i in range(len(grouped_cms)):   
        accuracy, f1_score, mcc, bal_acc = get_cm_metrics(grouped_cms[i])
        print(f"group {i}: ", accuracy, f1_score, mcc, bal_acc)

    group_num_list = range(1, len(grouped_resp_times_for_plotting)+1)
    plt.boxplot(grouped_resp_times_for_plotting)
    plt.title("Response Times (Human)")
    plt.xlabel("LED Status")
    plt.ylabel("time (s)")
    plt.xticks(group_num_list, [f"Group {i}" for i in group_num_list])
    plt.show()


def analyze_individual_cms_from_two_groups(data:quant.UserQuantData, data_grouping_type:DataGroupingType, group_one_head_list:ListsOfGroupings, group_two_head_list:ListsOfGroupings):
    grouped_resp_times1, grouped_cms1 = gather_response_times_and_summed_cms(data, data_grouping_type, group_one_head_list)
    grouped_resp_times2, grouped_cms2 = gather_response_times_and_summed_cms(data, data_grouping_type, group_two_head_list)

    print(len(grouped_cms1))

    if len(grouped_cms1) != len(grouped_cms2):
        raise ValueError("ERROR: Confusion matrices groups should be even in \"analyze_individual_cms_from_two_groups\"")
    
    if len(grouped_resp_times1) != len(grouped_resp_times2):
        raise ValueError("ERROR: Response times groups should be even in \"analyze_individual_cms_from_two_groups\"")

    differences_between_accs, differences_between_mccs = [], []
    accs1, accs2 = [], []
    mccs1, mccs2 = [], []
    for i in range(len(grouped_cms1)):   
        print(f"Calculating group {i}")
        accuracy1, f1_score1, mcc1, bal_acc1 = get_cm_metrics(grouped_cms1[i])
        accs1.append(bal_acc1)
        mccs1.append(mccs1)
        print("Now group 2")
        accuracy2, f1_score2, mcc2, bal_acc2 = get_cm_metrics(grouped_cms2[i])
        accs2.append(bal_acc2)
        mccs2.append(mccs2)
        difference_acc = bal_acc1 - bal_acc2
        difference_mcc = mcc1 - mcc2
        differences_between_accs.append(difference_acc)
        differences_between_mccs.append(difference_mcc)

    differences_times, times1, times2 = [], [], []
    for i in range(len(grouped_resp_times1)):
        if len(grouped_resp_times1[i]) != 0 and len(grouped_resp_times2[i]) != 0:
            average1 = sum(grouped_resp_times1[i])/len(grouped_resp_times1[i])
            times1.append(average1)
            average2 = sum(grouped_resp_times2[i])/len(grouped_resp_times2[i])
            times2.append(average2)
            difference = average1 - average2
            differences_times.append(difference)
    
    # Perform the Wilcoxon Signed-Rank Test
    statistic_mcc, pvalue_mcc = stats.wilcoxon(differences_between_mccs)
    statistic_acc, pvalue_acc = stats.wilcoxon(differences_between_accs)
    statistic_times, pvalue_times = stats.wilcoxon(differences_times)


    print("Mcc Test statistic:", statistic_mcc, "P-value:", pvalue_mcc)
    print("Acc Test statistic:", statistic_acc, "P-value:", pvalue_acc)
    print("Times Test statistic:", statistic_times, "P-value:", pvalue_times)

    group_num_list = range(1, 3)
    plt.boxplot([accs1, accs2])
    plt.title("Balanced Accuracy Values vs LED Status")
    plt.xlabel("LED Status")
    plt.ylabel("Balanced Accuracy")
    plt.xticks(group_num_list, [f"Group {i}" for i in group_num_list])
    plt.show()

    plt.boxplot([differences_between_accs])
    plt.title("Balanced Accuracy Values vs LED Status")
    plt.xlabel("LED Status")
    plt.ylabel("Balanced Accuracy")
    # plt.xticks(1, "Difference Between Paired Balanced Accuracies")
    plt.show()

    group_num_list = range(1, 3)
    plt.boxplot([times1, times2])
    plt.title("Response Times vs LED Status")
    plt.xlabel("LED Status")
    plt.ylabel("time (s)")
    plt.xticks(group_num_list, [f"Group {i}" for i in group_num_list])
    plt.show()

    return statistic_acc, pvalue_acc, statistic_times, pvalue_times



def main():
    ### Get data
    quant_filename = '../data/user_study_user_data/quantitative_raw_results.csv'
    qual_filename = '../data/user_study_user_data/qualitative_raw_results.csv'

    quant_data = quant.extract_quant_data_from_csv(quant_filename)
    qual_data = qual.extract_qual_data_from_csv(qual_filename)


    ### Qual Analysis
    trust_nums = [[],[],[]]
    for i in range(len(qual_data)):
        trust = qual_data[i].post_questionnaire.trust_of_feedback.num
        
        if not trust % 1 and int(qual_data[i].user_number) < 15:
            trust_nums[int(trust-1)].append(int(qual_data[i].user_number))
        else:
            print(f"WARNING: Non-integer found for trust value for user {qual_data[i].user_number}. Trust was {trust}")


    # # Count occurrences of each number
    # counts = {}
    # for number in trust_nums:
    #     counts[number] = counts.get(number, 0) + 1

    # # Create the bar graph
    # plt.bar(counts.keys(), counts.values())
    # plt.xlabel("Number")
    # plt.ylabel("Frequency")
    # plt.title("Number Occurrence Bar Graph")
    # plt.show()


    ### Quant Analysis
    LEDS_ON_VIDEO_TYPES = (1, 2, 5, 6, 9, 10)
    LEDS_OFF_VIDEO_TYPES = (2, 3, 7, 8, 11, 12)
    ALL_VIDEO_TYPES = tuple(range(12))
    populated_data = populate_cm_for_each_experiment(quant_data)

    # ### BY_USER_THEN_VIDEO_TYPE: trust and leds on
    # type_lists = [LEDS_ON_VIDEO_TYPES, LEDS_OFF_VIDEO_TYPES]
    # groupings = ListsOfGroupings(type_lists=type_lists, user_lists=trust_nums)

    ### First Group vs Second Group
    guinea_pigs = range(1, 15)
    normal = range(15, 35)
    groupings_halves = ListsOfGroupings(user_lists=[guinea_pigs, normal])

    ### Individual Users
    all_users = [range(1,35)]
    all_users_individually = [[i] for i in range(1, 35)]
    guinea_pigs_individually = [[j] for j in range(1, 15)]
    normal_individually = [[k] for k in range(15, 35)]
    groupings = ListsOfGroupings(type_lists=[LEDS_ON_VIDEO_TYPES, LEDS_OFF_VIDEO_TYPES], user_lists=trust_nums)

    # gather_data_and_visualize_multiple_groups_of_data(populated_data, DataGroupingType.BY_USER, groupings_halves)


    groupings_leds_on = ListsOfGroupings(type_lists=[LEDS_ON_VIDEO_TYPES], user_lists=all_users_individually)
    groupings_leds_off = ListsOfGroupings(type_lists=[LEDS_OFF_VIDEO_TYPES], user_lists=all_users_individually)

    groupings_guinea_pigs = ListsOfGroupings(user_lists=guinea_pigs_individually)

    all_stats = analyze_individual_cms_from_two_groups(populated_data, DataGroupingType.BY_USER_THEN_VIDEO_TYPE, groupings_leds_on, groupings_leds_off)

    


    # print(populated_data)
    # leds_on_rt, leds_on_cm = get_grouped_data(populated_data, LEDS_ON_VIDEO_TYPES)
    # leds_off_rt, leds_off_cm = get_grouped_data(populated_data, LEDS_OFF_VIDEO_TYPES)
    # grouped_response_times = [leds_on_rt, leds_off_rt]

    # print(leds_on_cm)
    # print(leds_off_cm)

    # acc_leds_on, f1_leds_on, mcc_leds_on = get_cm_metrics(leds_on_cm)
    # acc_leds_off, f1_leds_off, mcc_leds_off = get_cm_metrics(leds_off_cm)

    # print(acc_leds_on, f1_leds_on, mcc_leds_on)
    # print(acc_leds_off, f1_leds_off, mcc_leds_off)


    # plt.boxplot(grouped_response_times)
    # plt.title("Response Times (Human)")
    # plt.xlabel("LED Status")
    # plt.ylabel("time (s)")
    # plt.xticks([1, 2], ["LEDs On", "LEDs Off"])
    # plt.show()

    # Calculate true positive rate:



if __name__ == "__main__":
    main()