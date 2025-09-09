from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

NUM_VIDEOS = 12
NUM_USERS = 44
UNKNOWN_STR = "unknown"
NA_STR = "nada"
NONE_STR = "NONE"
MAX_NUM_ERRORS = 2


class FaultType(Enum):
	WHEEL_FAULT = 0
	PROX_FAULT = 1
	OTHER_FAULT = 2
	NOT_A_FAULT = 3
	WHEEL_AND_PROX_FAULT = 4
	TYPE_NOT_GIVEN = 5
	NO_FAULTS_PRESENT = 6

@dataclass
class ConfusionMatrix:
	true_positives: int = 0
	true_negatives: int = 0
	false_positives: int = 0
	false_negatives: int = 0
	revoked_false_positives: int = 0
	revoked_true_positives: int = 0
	total_robots: int = 0

@dataclass
class PerformanceMetrics:
	accuracy: float = None
	balanced_accuracy: float = None
	mcc: float = None
	f1_score: float = None

@dataclass
class ClassificationsOfCMs:
	leds_on: ConfusionMatrix
	leds_off: ConfusionMatrix
	large_num_robots: ConfusionMatrix
	small_num_robots: ConfusionMatrix
	wheel_fault: ConfusionMatrix
	prox_fault: ConfusionMatrix
	no_fault: ConfusionMatrix
	one_fault: ConfusionMatrix
	two_faults: ConfusionMatrix
	two_faults_wheel_and_prox: ConfusionMatrix
	two_faults_just_wheels: ConfusionMatrix
	two_faults_just_prox: ConfusionMatrix
	#Finish deciding hypotheses before actually analyzing
	# Those who trust the feedback a little, but not a lot, will benefit the most (2). Those who don't trust at all or a lot will not do as well.
	lowest_trust: ConfusionMatrix
	mid_trust: ConfusionMatrix
	high_trust: ConfusionMatrix
	# Robot experience on a trend line. I expect performance and years of experience to be correlated
	robot_experience_3_or_greater: ConfusionMatrix
	less_robot_experience: ConfusionMatrix

	# I expect years of experience of video games to correlate with performance

	# I expect STEM education to correlate with performance (but everyone had lots, so probably won't be easy to tell)

	# Those with extra beneficial experience to do better
	
	# I expect mental demand to be less with swarm feedback, but trust may affect it.

	# Physical to be the same
	# temporal to be the same
	# Rated performance to be slightly better or the same
	# Effort less with feedback
	# Frustration about the same
	# usefulness to be low
	# ease of understanding high
	# Trust to be overall low due to training
	# difficulty to be high
	# free responses can be summarized for my own benefit more than anything else. I may plug into gemini for summary and most unique points

	# Speed to be improved with feedback, about the same accuracy, maybe slightly better?
	# swarm performance in all these should be tested too
	# Percentage time in false positive will be slightly less with feedback.
	# Percentage time in false negative will be slightly less with feedback. Human will be less than swarm in both.
	# First videos will be worse than middles because of the learninging curve, but end will also be worse than middel because of burnout.
	# Swarm helping will most likely depend on if it actually guessed the right robot.
	# Time between true positive swarm and true positive human will likely be small if seen and trusted.
	# Most videos will have the swarm correctly identify the robots.
	# The swarm will have less false negatives than the humans

Dataline = namedtuple("Dataline", "time robot tolerators attackers")

def calculate_balanced_accuracy(tp, tn, fp, fn):
	"""Calculates balanced accuracy.

	Args:
		tp: True positives.
		tn: True negatives.
		fp: False positives.
		fn: False negatives.

	Returns:
		Balanced accuracy when at least one tp or fn value exists and at least one tn or fp value exists.

		Ignores inconsequential part. 
		Sensitivity is meaningless when there are no possible true positives, only true negative values (non-faulty robots) in the experiment since there are no tp or fn regardless of what the classifier does. 
		Speicificity is meaningless when there are no possible true negatives, only true positive values (faulty robots) in the experiment since there are no tn or fp regardless of what the classifier does.
	"""

	use_sensitivity = True
	if tp == 0 and fn == 0:
		use_sensitivity = False
	else:
		sensitivity = tp / (tp + fn)
	
	if tn == 0 and fp == 0:
		if use_sensitivity:
			return sensitivity
		else:
			raise ValueError("ERROR: \"calculate_balanced_accuracy\" received zero values for all values. Nothing to calculate.")
	else:
		specificity = tn / (tn + fp)
		if not use_sensitivity:
			return specificity

	balanced_accuracy = (sensitivity + specificity) / 2
	return balanced_accuracy

def calc_accuracy(tp, tn, total):
	try:
		accuracy = (tp+tn)/total
		return accuracy
	except ZeroDivisionError:
		print("WARNING: No accuracy could be found, division by Zero")
		print(f"tp: {tp}, tn: {tn}")
		raise ValueError("Total should not be zero ever")

def calc_f1_score(tp, fp, fn, tn):
	try:
		f1_score = (2*tp) / (2*tp + fp + fn)
		return f1_score
	except ZeroDivisionError:
		if tn > 0:
			print("WARNING: No F-Score could be found, division by Zero, but true negatives were present, so accuracy of 1 was awarded since all robots were correctly categorized")
			return 1
		else:
			raise ValueError("ERROR: No values in confusion matrix, nothing to calculate")
	

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
		print("WARNING: MCC undefined: returning MCC adjusted balanced accuracy")
		return 2 * calculate_balanced_accuracy(tp, tn, fp, fn) - 1  # This projects the accuracy to the MCC's range of -1 to 1

	mcc = numerator / denominator

	if mcc == 0:
		print(f"Returned zero in mcc with these values: tp: {tp}, fp: {fp}, fn: {fn}, tn: {tn}")
	return mcc

def get_cm_metrics(cm):
	tp = cm.true_positives
	tn = cm.true_negatives
	fp = cm.false_positives
	fn = cm.false_negatives
	total = cm.total_robots

	accuracy = calc_accuracy(tp, tn, total)
	bal_acc = calculate_balanced_accuracy(tp, tn, fp, fn)
	f1_score = calc_f1_score(tp, fp, fn, tn)
	mcc = calc_matthews_coefficient(tp, fp, fn, tn)

	return PerformanceMetrics(accuracy=accuracy, balanced_accuracy=bal_acc, mcc=mcc, f1_score=f1_score)

def find_swarm_size_by_video_type(video_type):
	LARGE_NUM_ROBOTS = 64
	SMALL_NUM_ROBOTS = 16
	SIZE_MODULO_NUM = 2

	num_robots = SMALL_NUM_ROBOTS if video_type % SIZE_MODULO_NUM else LARGE_NUM_ROBOTS
	return num_robots

def find_leds_on_by_video_type(video_type):
	LEDS_MODULO_NUM = 4
	LEDS_OFF_THRESHOLD = 2
	are_leds_on = (video_type-1) % LEDS_MODULO_NUM < LEDS_OFF_THRESHOLD
	return are_leds_on

def find_num_faults_by_video_type(video_type):
	FAULT_GROUPING_NUM = 4
	num_faults = int((video_type-1)/FAULT_GROUPING_NUM)
	return num_faults

def find_row_index(df, match_string, column_index, starting_row_index, max_row_search=100):
	for i in range(max_row_search):
		if match_string == df.iloc[starting_row_index+i,column_index]:
			true_values_row_index = starting_row_index + i
			return true_values_row_index
	raise Exception(f"ERROR: In \"find_row_index\" the string: \"{match_string}\" was not found")

def parse_votes(token):
	voters = []
	for subtoken in token.split(' ')[1:]:
		if subtoken == '-1' or subtoken == '' or subtoken == "\n":
			break
		voters.append(int(subtoken))
	return voters

def process_dataline(line):
	"""
	Processes a raw dataline into a dict of useful information
	"""

	if len(line.split('\t')) != 5:
		return None # there is no data here 

	
	tokens = line.split('\t')
	time = int(tokens[0].split(' ')[1])
	robot = int(tokens[1].split(' ')[1])
	tolerators = parse_votes(tokens[3])
	attackers = parse_votes(tokens[4])

	data = Dataline(time, robot, tolerators, attackers)

	return data


def process_file(file):
	"""
	Returns a list of processed datalines for the given file
	"""

	# Read in the data from the nohup.txt file
	lines = []
	with open(file, 'r') as datafile:
		for line in datafile.readlines():
			processed = process_dataline(line)
			if processed is not None:
				lines.append(processed)
	return lines
	# free responses can be summarized for my own benefit more than anything else. I may plug into gemini for summary and most unique points








Dataline = namedtuple("Dataline", "time robot tolerators attackers")

def find_row_index(df, match_string, column_index, starting_row_index, max_row_search=100):
	for i in range(max_row_search):
		if match_string == df.iloc[starting_row_index+i,column_index]:
			true_values_row_index = starting_row_index + i
			return true_values_row_index
	raise Exception(f"ERROR: In \"find_row_index\" the string: \"{match_string}\" was not found")

def parse_votes(token):
	voters = []
	for subtoken in token.split(' ')[1:]:
		if subtoken == '-1' or subtoken == '' or subtoken == "\n":
			break
		voters.append(int(subtoken))
	return voters

def process_dataline(line):
	"""
	Processes a raw dataline into a dict of useful information
	"""

	if len(line.split('\t')) != 5:
		return None # there is no data here 

	
	tokens = line.split('\t')
	time = int(tokens[0].split(' ')[1])
	robot = int(tokens[1].split(' ')[1])
	tolerators = parse_votes(tokens[3])
	attackers = parse_votes(tokens[4])

	data = Dataline(time, robot, tolerators, attackers)

	return data


def process_file(file):
	"""
	Returns a list of processed datalines for the given file
	"""

	# Read in the data from the nohup.txt file
	lines = []
	with open(file, 'r') as datafile:
		for line in datafile.readlines():
			processed = process_dataline(line)
			if processed is not None:
				lines.append(processed)
	return lines