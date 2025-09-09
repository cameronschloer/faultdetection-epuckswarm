import extract_data_quantitative_human_experiments as quant
import extract_data_qualitative_human_experiments as qual
import analysis_utils as au
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
from dataclasses import dataclass
import scipy.stats as stats
from copy import deepcopy
import statistics
import pandas as pd


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

def calculate_percentage_confusion_matrix_times(data):
    pass



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
        accuracy, f1_score, mcc, bal_acc = au.get_cm_metrics(grouped_cms[i])
        print(f"group {i}: ", accuracy, f1_score, mcc, bal_acc)

    group_num_list = range(1, len(grouped_resp_times_for_plotting)+1)
    plt.boxplot(grouped_resp_times_for_plotting, showmeans=True)
    plt.title("Response Times (Human)")
    plt.xlabel("Feedback")
    plt.ylabel("time (s)")
    plt.xticks(group_num_list, [f"Group {i}" for i in group_num_list])
    plt.show()


def remove_zeros(list_to_remove_from):
    list_with_no_zeros = [num for num in list_to_remove_from if num != 0]
    return list_with_no_zeros

def analyze_individual_cms_from_two_groups(data:quant.UserQuantData, data_grouping_type:DataGroupingType, group_one_head_list:ListsOfGroupings, group_two_head_list:ListsOfGroupings):
    
    grouped_resp_times1, grouped_cms1 = gather_response_times_and_summed_cms(data, data_grouping_type, group_one_head_list)
    grouped_resp_times2, grouped_cms2 = gather_response_times_and_summed_cms(data, data_grouping_type, group_two_head_list)

    print(grouped_cms1)
    print(grouped_cms2)

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
        metrics1 = au.get_cm_metrics(grouped_cms1[i])
        accs1.append(metrics1.balanced_accuracy)
        mccs1.append(metrics1.mcc)
        metrics2 = au.get_cm_metrics(grouped_cms2[i])
        accs2.append(metrics2.balanced_accuracy)
        mccs2.append(metrics2.mcc)
        difference_acc = metrics1.balanced_accuracy - metrics2.balanced_accuracy
        difference_mcc = metrics1.mcc - metrics2.mcc
        differences_between_accs.append(difference_acc)
        differences_between_mccs.append(difference_mcc)

    print(differences_between_accs)
    print(differences_between_mccs)
    # print(accs1)
    # print(accs2)
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
    if 0 in differences_between_mccs:
        print("Zero in mccs")
    if 0 in differences_between_accs:
        print("Zero in accs")
    differences_between_mccs_no_zeros = remove_zeros(differences_between_mccs)
    differences_between_accs_no_zeros = remove_zeros(differences_between_accs)
    print(differences_between_mccs_no_zeros, differences_between_accs_no_zeros)
    statistic_mcc, pvalue_mcc = stats.wilcoxon(differences_between_mccs_no_zeros)
    statistic_acc, pvalue_acc = stats.wilcoxon(differences_between_accs_no_zeros)
    statistic_times, pvalue_times = stats.wilcoxon(differences_times)


    print("Mcc Test statistic:", statistic_mcc, "P-value:", pvalue_mcc)
    print("Acc Test statistic:", statistic_acc, "P-value:", pvalue_acc)
    print("Times Test statistic:", statistic_times, "P-value:", pvalue_times)

    group_num_list = range(1, 3)
    plt.boxplot([accs1, accs2], showmeans=True)
    plt.title("Balanced Accuracy Values vs Feedback")
    plt.xlabel("Feedback")
    plt.ylabel("Balanced Accuracy")
    plt.xticks(group_num_list, ["Have Feedback", "No Feedback"])
    plt.show()

    plt.boxplot([mccs1, mccs2], showmeans=True)
    plt.title("MCC Values vs Feedback")
    plt.xlabel("Feedback")
    plt.ylabel("MCC")
    plt.xticks(group_num_list, ["Have Feedback", "No Feedback"])
    plt.show()

    plt.boxplot([differences_between_accs], showmeans=True)
    plt.title("Balanced Accuracy Differences by Feedback")
    plt.xlabel("Feedback")
    plt.ylabel("Balanced Accuracy")
    # plt.xticks(1, "Difference Between Paired Balanced Accuracies")
    plt.show()

    plt.boxplot([differences_between_mccs], showmeans=True)
    plt.title("MCC Differences by Feedback")
    plt.xlabel("Feedback")
    plt.ylabel("MCC")
    # plt.xticks(1, "Difference Between Paired Balanced Accuracies")
    plt.show()

    group_num_list = range(1, 3)
    plt.boxplot([times1, times2], showmeans=True)
    plt.title("Response Times vs Feedback")
    plt.xlabel("Feedback")
    plt.ylabel("time (s)")
    plt.xticks(group_num_list, ["Have Feedback", "No Feedback"])
    plt.show()

    return statistic_acc, pvalue_acc, statistic_times, pvalue_times

def plot_each_metric(x_ticks_list, acc, bal_acc, f1, mcc):
    plt.boxplot(acc, showmeans=True)
    plt.title("Accuracy vs Video Type")
    plt.xlabel("Video Type")
    plt.ylabel("Accuracy")
    plt.xticks(x_ticks_list)
    plt.show()

    plt.boxplot(bal_acc, showmeans=True)
    plt.title("Balanced Accuracy vs Video Type")
    plt.xlabel("Video Type")
    plt.ylabel("Balanced Accuracy")
    plt.xticks(x_ticks_list)
    plt.show()

    plt.boxplot(f1, showmeans=True)
    plt.title("F1 Score vs Video Type")
    plt.xlabel("Video Type")
    plt.ylabel("F1 Score")
    plt.xticks(x_ticks_list)
    plt.show()

    plt.boxplot(mcc, showmeans=True)
    plt.title("MCC vs Video Type")
    plt.xlabel("Video Type")
    plt.ylabel("MCC")
    plt.xticks(x_ticks_list)
    plt.show()

def get_strs_from_faults_present(faults_present, num_faults):
    if faults_present == au.FaultType.NO_FAULTS_PRESENT:
        if num_faults != 0:
            raise ValueError("Should have no faults for no faults present!!!")
        return ("NONE", "NONE")
    elif faults_present == au.FaultType.PROX_FAULT:
        if num_faults == 1:
            return ("PROX", "NONE")
        elif num_faults == 2:
            return ("PROX", "PROX")
        else:
            raise ValueError("Only one or two faults should be present")
    elif faults_present == au.FaultType.WHEEL_FAULT:
        if num_faults == 1:
            return ("WHEEL", "NONE")
        elif num_faults == 2:
            return ("WHEEL", "WHEEL")
        else:
            raise ValueError("Only one or two faults should be present")
    elif faults_present == au.FaultType.WHEEL_AND_PROX_FAULT:
        if num_faults != 2:
            raise ValueError("Should have 2 faults present!!!")
        return ("WHEEL", "PROX")
    else:
        raise ValueError(f"Got bad faults present: {faults_present}")

def create_csv_with_responses_and_vars(data):
    # bal_acc = [[] for _ in range(au.NUM_VIDEOS)]
    # faults = deepcopy(bal_acc)
    # Create a sample DataFrame
    columns = ['user_num', 'fault_type1', 'fault_type2', 'bal_acc', 'vid_type']
    df = pd.DataFrame(columns=columns)
    k = 0
    for i in range(len(data)):
        for j in range(len(data[i].video_experiments)):
            bal_acc = data[i].video_experiments[j].performance_metrics.balanced_accuracy
            vid_type = data[i].video_experiments[j].metadata.video_type
            faults_present = data[i].video_experiments[j].faults_present
            num_faults = data[i].video_experiments[j].metadata.num_faults
            faults_strs = get_strs_from_faults_present(faults_present, num_faults)
            user_num = data[i].user_number
            # Add a new row as a dictionary
            new_row = {'user_num': user_num, 'fault_type1': faults_strs[0], 'fault_type2': faults_strs[1], 'bal_acc': bal_acc, 'vid_type': vid_type}
            df.loc[k] = new_row
            k += 1

    # Save the DataFrame to a CSV file
    df.to_csv('data.csv', index=False)


def plot_each_video_type(data):
    acc = [[] for _ in range(au.NUM_VIDEOS)]
    bal_acc, f1, mcc = deepcopy(acc), deepcopy(acc), deepcopy(acc)
    for i in range(len(data)):
        for j in range(len(data[i].video_experiments)):
            metrics = data[i].video_experiments[j].performance_metrics
            vid_type = data[i].video_experiments[j].metadata.video_type
            acc[vid_type-1].append(metrics.accuracy)
            bal_acc[vid_type-1].append(metrics.balanced_accuracy)
            f1[vid_type-1].append(metrics.f1_score)
            mcc[vid_type-1].append(metrics.mcc)
    
    group_num_list = range(1, au.NUM_VIDEOS+1)
    plot_each_metric(group_num_list, acc, bal_acc, f1, mcc)


def generate_wilcoxon_results_from_lists(lists):
    stats_bundle = [[] for _ in range(len(lists))]
    for i in range(len(lists)):
        stat, pval = stats.wilcoxon(remove_zeros(lists[i]))
        stats_bundle[i].append((stat, pval))
    return stats_bundle

def get_averages_from_group(metrics_list, small_idxs, large_idxs):
    small_diffs = [(metrics_list[index]-metrics_list[index+2]) for index in small_idxs]
    large_diffs = [(metrics_list[index]-metrics_list[index+2]) for index in large_idxs]
    small_avg, large_avg = statistics.mean(small_diffs), statistics.mean(large_diffs)
    return small_avg, large_avg


def plot_each_difference(data, average_it):
    average_acc_diff = [[], []]
    average_bal_acc_diff, average_f1_diff, average_mcc_diff = deepcopy(average_acc_diff), deepcopy(average_acc_diff), deepcopy(average_acc_diff)
    acc_diff = [[] for _ in range(int(au.NUM_VIDEOS/2))]
    bal_acc_diff, f1_diff, mcc_diff = deepcopy(acc_diff), deepcopy(acc_diff), deepcopy(acc_diff)
    accepted_list_users = list(range(14, 44))
    accepted_list_users.append(3)
    accepted_list_users.append(10)
    print(accepted_list_users)
    for i in range(len(data)):  # range(len(data))
        if i not in accepted_list_users:
            continue
        acc = [None for _ in range(au.NUM_VIDEOS)]
        bal_acc, f1, mcc = deepcopy(acc), deepcopy(acc), deepcopy(acc)
        for j in range(len(data[i].video_experiments)):
            metrics = data[i].video_experiments[j].performance_metrics
            vid_type = data[i].video_experiments[j].metadata.video_type
            if acc[vid_type-1] is None:
                acc[vid_type-1] = metrics.accuracy
                bal_acc[vid_type-1] = metrics.balanced_accuracy
                f1[vid_type-1] = metrics.f1_score
                mcc[vid_type-1] = metrics.mcc
            else:
                acc[vid_type-1] = (acc[vid_type-1] + metrics.accuracy) / 2
                bal_acc[vid_type-1] = (bal_acc[vid_type-1] + metrics.balanced_accuracy) / 2
                f1[vid_type-1] = (f1[vid_type-1] + metrics.f1_score) / 2
                mcc[vid_type-1] = (mcc[vid_type-1] + metrics.mcc) / 2
        small_idxs, large_idxs = [], []
        for j in range(int(au.NUM_VIDEOS/4)):
            index = j*4
            NUM_SIZES = 2
            for k in range(NUM_SIZES):
                if acc[index+k] is not None and acc[index+2+k] is not None:
                    if average_it:
                        if k == 0:
                            small_idxs.append(index+k)
                        else:
                            large_idxs.append(index+k)
                    acc_diff[j*2+k].append(acc[index+k]-acc[index+2+k])
                    bal_acc_diff[j*2+k].append(bal_acc[index+k]-bal_acc[index+2+k])
                    f1_diff[j*2+k].append(f1[index+k]-f1[index+2+k])
                    mcc_diff[j*2+k].append(mcc[index+k]-mcc[index+2+k])
        
        if average_it:
            acc_avg_sm, acc_avg_lg = get_averages_from_group(acc, small_idxs, large_idxs)
            bal_acc_avg_sm, bal_acc_avg_lg = get_averages_from_group(bal_acc, small_idxs, large_idxs)
            f1_avg_sm, f1_avg_lg = get_averages_from_group(f1, small_idxs, large_idxs)
            mcc_avg_sm, mcc_avg_lg = get_averages_from_group(mcc, small_idxs, large_idxs)
            average_acc_diff[0].append(acc_avg_sm)
            average_acc_diff[1].append(acc_avg_lg)
            average_bal_acc_diff[0].append(bal_acc_avg_sm)
            average_bal_acc_diff[1].append(bal_acc_avg_lg)
            average_f1_diff[0].append(f1_avg_sm)
            average_f1_diff[1].append(f1_avg_lg)
            average_mcc_diff[0].append(mcc_avg_sm)
            average_mcc_diff[1].append(mcc_avg_lg)

    if average_it:
        group_num_list = range(1, int((au.NUM_VIDEOS/6))+1)
        acc_stats = generate_wilcoxon_results_from_lists(average_acc_diff)
        bal_acc_stats = generate_wilcoxon_results_from_lists(average_bal_acc_diff)
        f1_stats = generate_wilcoxon_results_from_lists(average_f1_diff)
        mcc_stats = generate_wilcoxon_results_from_lists(average_mcc_diff) 
    else:                     
        group_num_list = range(1, int((au.NUM_VIDEOS/2))+1)
        acc_stats = generate_wilcoxon_results_from_lists(acc_diff)
        bal_acc_stats = generate_wilcoxon_results_from_lists(bal_acc_diff)
        f1_stats = generate_wilcoxon_results_from_lists(f1_diff)
        mcc_stats = generate_wilcoxon_results_from_lists(mcc_diff)


    print("Acc stats:", acc_stats)
    print("Bal Acc stats:", bal_acc_stats)
    print("F1 stats:", f1_stats)
    print("Mcc stats:", mcc_stats)

    if average_it:
        plot_each_metric(group_num_list, average_acc_diff, average_bal_acc_diff, average_f1_diff, average_mcc_diff)
    else:
        plot_each_metric(group_num_list, acc_diff, bal_acc_diff, f1_diff, mcc_diff)

def plot_each_fault_type(data):
    acc_diff = [[] for _ in range(int(au.NUM_VIDEOS/2))]
    bal_acc_diff, f1_diff, mcc_diff = deepcopy(acc_diff), deepcopy(acc_diff), deepcopy(acc_diff)
    accepted_list_users = list(range(14, 44))
    accepted_list_users.append(3)
    accepted_list_users.append(10)
    print(accepted_list_users)
    for i in range(len(data)):
        if i not in accepted_list_users:
            continue
        acc = [None for _ in range(au.NUM_VIDEOS)]
        bal_acc, f1, mcc = deepcopy(acc), deepcopy(acc), deepcopy(acc)
        for j in range(len(data[i].video_experiments)):
            metrics = data[i].video_experiments[j].performance_metrics
            print(metrics)
            vid_type = data[i].video_experiments[j].metadata.video_type
            if acc[vid_type-1] is None:
                acc[vid_type-1] = metrics.accuracy
                bal_acc[vid_type-1] = metrics.balanced_accuracy
                f1[vid_type-1] = metrics.f1_score
                mcc[vid_type-1] = metrics.mcc
            else:
                acc[vid_type-1] = (acc[vid_type-1] + metrics.accuracy) / 2
                bal_acc[vid_type-1] = (bal_acc[vid_type-1] + metrics.balanced_accuracy) / 2
                f1[vid_type-1] = (f1[vid_type-1] + metrics.f1_score) / 2
                mcc[vid_type-1] = (mcc[vid_type-1] + metrics.mcc) / 2
        for j in range(int(au.NUM_VIDEOS/4)):
            index = j*4
            NUM_SIZES = 2
            for k in range(NUM_SIZES):
                if acc[index+k] is not None and acc[index+2+k] is not None:
                    acc_diff[j*2+k].append(acc[index+k]-acc[index+2+k])
                    bal_acc_diff[j*2+k].append(bal_acc[index+k]-bal_acc[index+2+k])
                    f1_diff[j*2+k].append(f1[index+k]-f1[index+2+k])
                    mcc_diff[j*2+k].append(mcc[index+k]-mcc[index+2+k])
                    
    
    group_num_list = range(1, int((au.NUM_VIDEOS/2))+1)
    plot_each_metric(group_num_list, acc_diff, bal_acc_diff, f1_diff, mcc_diff)


def main():
    ### Get data
    QUANT_FILENAME = '../data/user_study_user_data/quantitative_raw_results.csv'
    QUAL_FILENAME = '../data/user_study_user_data/qualitative_raw_results.csv'
    REMOVE_BEACON_GUESSES = True
    REMOVE_REVOKED = True

    quant_data = quant.get_quant_data_from_csv(QUANT_FILENAME, REMOVE_BEACON_GUESSES, REMOVE_REVOKED)
    qual_data = qual.extract_qual_data_from_csv(QUAL_FILENAME)

    AVERAGE_IT = True
    create_csv_with_responses_and_vars(quant_data)
    # plot_each_video_type(quant_data)


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
    LEDS_OFF_VIDEO_TYPES = (3, 4, 7, 8, 11, 12)
    LEDS_ON_AND_SMALL_TYPES = (1, 5, 9)
    LEDS_ON_AND_LARGE_TYPES = (2, 6, 10)
    LEDS_OFF_AND_SMALL_TYPES = (3, 7, 11)
    LEDS_OFF_AND_LARGE_TYPES = (4, 8, 12)
    ALL_VIDEO_TYPES = tuple(range(12))

    # ### BY_USER_THEN_VIDEO_TYPE: trust and leds on
    # type_lists = [LEDS_ON_VIDEO_TYPES, LEDS_OFF_VIDEO_TYPES]
    # groupings = ListsOfGroupings(type_lists=type_lists, user_lists=trust_nums)

    ### First Group vs Second Group
    guinea_pigs = range(1, 15)
    normal = range(15, au.NUM_USERS)
    groupings_halves = ListsOfGroupings(user_lists=[guinea_pigs, normal])

    ### Individual Users
    all_users = [range(1,au.NUM_USERS)]
    all_users_individually = [[i] for i in range(1, au.NUM_USERS)]  # list(range(1, 5)) + list(range(6,au.NUM_USERS))
    guinea_pigs_individually = [[j] for j in range(1, 15)]
    normal_individually = [[k] for k in range(15, au.NUM_USERS)]
    leds_types_list = [LEDS_ON_VIDEO_TYPES, LEDS_OFF_VIDEO_TYPES]
    leds_and_sizes_type_lists = [LEDS_ON_AND_SMALL_TYPES, LEDS_ON_AND_LARGE_TYPES, LEDS_OFF_AND_SMALL_TYPES, LEDS_OFF_AND_LARGE_TYPES]
    groupings = ListsOfGroupings(type_lists=leds_and_sizes_type_lists, user_lists=trust_nums)

    # gather_data_and_visualize_multiple_groups_of_data(populated_data, DataGroupingType.BY_USER, groupings_halves)

    trouble_makers = [[12], [15]]

    groupings_leds_on = ListsOfGroupings(type_lists=[LEDS_ON_VIDEO_TYPES], user_lists=all_users_individually)
    groupings_leds_off = ListsOfGroupings(type_lists=[LEDS_OFF_VIDEO_TYPES], user_lists=all_users_individually)

    groupings_guinea_pigs = ListsOfGroupings(user_lists=guinea_pigs_individually)

    # all_stats = analyze_individual_cms_from_two_groups(quant_data, DataGroupingType.BY_USER_THEN_VIDEO_TYPE, groupings_leds_on, groupings_leds_off)

    # print(quant_data[2].user_number)
    # print(quant_data[2].video_experiments[9].metadata.user_watch_order)
    # print(quant_data[2].video_experiments[9].metadata.video_type)
    # cm, rts = populate_confusion_matrix(quant_data[2].video_experiments[9])
    # print(cm)

    


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


    # plt.boxplot(grouped_response_times, showmeans=True)
    # plt.title("Response Times (Human)")
    # plt.xlabel("Feedback")
    # plt.ylabel("time (s)")
    # plt.xticks([1, 2], ["Have Feedback", "No Feedback"])
    # plt.show()

    # Calculate true positive rate:



if __name__ == "__main__":
    main()