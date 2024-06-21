import matplotlib.pyplot as plt
import sys, os

def analyze_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

        total_times_voted = 0
        times_correct = 0
        
        for line in lines:
            parts = line.replace("\t", " ").replace("\n", " ").split(" ")
            parts = [i for i in parts if i != ""]

            if parts[3] == '15':
                tol_list = [vote for vote in parts[7:27] if vote != '-1']
                attack_list = [vote for vote in parts[28:48] if vote != '-1']

                if len(tol_list) != 0 or len(attack_list) != 0:
                    total_times_voted = total_times_voted + 1

                    if len(tol_list) < len(attack_list):
                        times_correct = times_correct + 1
                
                # Note: if the else statment is uncommented, we get closer data to what the paper got
                
                # else:
                #     total_times_voted = total_times_voted + 1
                #     times_correct = times_correct + 1

                #print(f"clock: {parts[1]}, tol: {len(tol_list)}, att: {len(attack_list)}, cnt: {times_correct}, total: {total_times_voted}")

    if total_times_voted != 0:
        return times_correct/total_times_voted
    else:
        return 0.0

def graph(data_path):
    for task in os.scandir(data_path):
        fault_data = [(fault.name, [analyze_file(file) for file in os.scandir(fault)]) 
                      for fault in os.scandir(task)]

        names, data = zip(*fault_data)

        plt.title(task.name)
        plt.boxplot(data)
        plt.xticks(range(1, len(names) + 1), names, rotation=15, fontsize=6)
        plt.show()

if __name__ == "__main__":
    graph(sys.argv[1])