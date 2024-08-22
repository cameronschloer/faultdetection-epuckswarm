import analysis_utils as au
from collections import namedtuple
import sys
import numpy as np
# import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import pandas as pd
from dataclasses import dataclass

ColorChange = namedtuple("ColorChange", "color time")
@dataclass
class AnalyzedFeedback:
	time_ranges_black: list[int]
	time_ranges_red: list[int]
	time_ranges_green: list[int]
	num_times_black: int = 0
	num_times_red: int = 0
	num_times_green: int = 0
	num_times_changed: int = 0
	percent_time_black: float = 0.0
	percent_time_red: float = 0.0
	percent_time_green: float = 0.0


def convert_time_steps_to_video_time(time_steps):
	steps_removed_from_beginning = 450
	steps_per_second = 10
	video_time = float(time_steps - steps_removed_from_beginning) / float(steps_per_second)
	return video_time

def experiment_details(file):
	"""
	Returns the number of robots and faulty robot information from the XML file
	"""
	
	root = ET.parse(file)
	run = root.find('.//experiment_run')
	fault_behavior = run.get('fault_behavior')
	id_faulty = run.get('id_faulty_robot')
	faulty_ids = id_faulty.split(' ')
	injection_step = run.get('injection_step')

	num_led_bins = root.find('.//foraging').get('led_bins')

	num_robots = root.find('arena').find('distribute').find('entity').get('quantity')

	seed = root.find('.//experiment').get('random_seed')

	return fault_behavior, faulty_ids, injection_step.split(' '), num_led_bins, int(num_robots), seed



def find_feedback_changes(data: list[au.Dataline], num_robots):
	"""
	(FIXME) Returns the proportion of time the robot is considered faultly for each robot

	Robot is considered faulty if a majority of other robots considers it faulty, and back to normal when no one thinks so
	"""

	color_changes = [[ColorChange("Black", 0)] for _ in range(num_robots)]

	max_time = data[-1].time
	min_time = data[0].time

	for line in data:
		is_comm_timestep = int(str(line.time)[-2:]) >= 90

		if not is_comm_timestep:
			print("I SKIPPED SOMETHING!!!!")
			continue

		robot_idx = line.robot

		current_time = convert_time_steps_to_video_time(line.time)
		if len(line.attackers) == len(line.tolerators) and len(line.tolerators) == 0:
			current_color = ColorChange("Black", current_time)
		elif len(line.attackers) > len(line.tolerators):
			current_color = ColorChange("Red", current_time)
		else:
			current_color = ColorChange("Green", current_time)

		if current_color.color != color_changes[robot_idx][-1].color:
			color_changes[robot_idx].append(current_color)
			print(f"Robot {robot_idx} changed color to {current_color.color} at {current_color.time} seconds")

	return color_changes

def get_time_color_ends(color_change_list, current_idx, video_end_time):
	if current_idx + 1 < len(color_change_list):
		time_color_ends = color_change_list[current_idx+1].time
	else:
		time_color_ends = video_end_time
	
	return time_color_ends

def get_times(color_change_list, current_idx):
	VIDEO_END_TIME = 200
	start_time = color_change_list[current_idx].time
	end_time = get_time_color_ends(color_change_list, current_idx, VIDEO_END_TIME)
	percentage_time = (end_time - start_time) / VIDEO_END_TIME

	return start_time, end_time, percentage_time


def analyze_feedback_changes(color_changes):
	analyzed_feedback = [AnalyzedFeedback([], [], []) for _ in range(len(color_changes))]
	for i in range(len(color_changes)):
		analyzed_feedback[i].num_times_changed = len(color_changes[i]) - 1
		for j in range(len(color_changes[i])):
			if j != 0:
				if color_changes[i][j].color == color_changes[i][j-1].color:
					raise Exception("Color changes passed in has repeated \"changes\" of the same color. Check your data.")
				
			start_time, end_time, percentage_time = get_times(color_changes[i], j)
			if color_changes[i][j].color == "Black":
				analyzed_feedback[i].num_times_black += 1
				analyzed_feedback[i].time_ranges_black.append((start_time, end_time))
				analyzed_feedback[i].percent_time_black += percentage_time
			elif color_changes[i][j].color == "Red":
				analyzed_feedback[i].num_times_red += 1
				analyzed_feedback[i].time_ranges_red.append((start_time, end_time))
				analyzed_feedback[i].percent_time_red += percentage_time
			elif color_changes[i][j].color == "Green":
				analyzed_feedback[i].num_times_green += 1
				analyzed_feedback[i].time_ranges_green.append((start_time, end_time))
				analyzed_feedback[i].percent_time_green += percentage_time

	return analyzed_feedback
				





# def detailed_analysis_file(exp_file, nohup_file, dest=''):
# 	fault_behavior, id_faulty, injection_step, num_led_bins, num_robots, seed = experiment_details(exp_file)
# 	# time_data, first_times = time_sus(au.process_file(nohup_file), num_robots)

# 	injection_steps = np.zeros(num_robots)
# 	injection_steps[np.array(id_faulty, dtype=int)] = np.array(injection_step)
# 	data = {
# 		'is_faulty': [str(robot) in id_faulty for robot in range(num_robots)],
# 		'injection_step' : injection_steps,
# 		'time_found' : first_times,
# 		'percent_time_found' : time_data
# 	}
# 	df = pd.DataFrame.from_dict(data, 'index')
# 	df.to_json(dest+f'processed_data_{seed}.json')




if __name__ == "__main__":
	if len(sys.argv) < 3:
		raise Exception("usage python3 analyze_output.py <path_to_experiment_file> <path_to_data_file>")
	
	
	data = au.process_file(sys.argv[2])
	
	fault_behavior, faulty_ids, injection_steps, num_led_bins, num_robots, seed = experiment_details(sys.argv[1])
	
	color_changes = find_feedback_changes(data, num_robots)
	analyzed_feedback = analyze_feedback_changes(color_changes)
	print(analyzed_feedback)