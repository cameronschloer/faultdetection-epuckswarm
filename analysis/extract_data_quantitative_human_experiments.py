import pandas as pd
import analysis_utils as au
from dataclasses import dataclass, field
NUM_DUPLICATE_VIDEOS = 2
NUM_EXPERIMENT_COLUMNS = 3
REVOKE_STR = "-Revoke"
BEACON_STR = "(beacon) "
# TODO(Cameron): Check that "NONE" actually didn't get replaced by unknown...
TRUE_VALUES_STR = "True Values"
TIMESTAMP_COLUMN = 1
REASON_COLUMN = 2
MAX_NUM_ERRORS = 2
ROW_VALUE_COLUMN = 0
PROX_STR = "Prox Sensor Random"
WHEEL_STR = "Wheel Fault"

@dataclass
class FaultyRobotGuess:
	is_revoke: bool = False
	robot_id: int = -1
	timestamp: float = -0.1
	reason: str = ""
	fault_type: au.FaultType = None
	is_false_positive: bool = None
	correctly_identified: bool = None

@dataclass
class VideoMetadata:
	video_type: int = -1
	seed: int = -1
	user_watch_order: int = -1
	num_faults: int = -1
	num_robots: int = -1
	are_leds_on: bool = None
	  
@dataclass   
class VideoExperiment:
	guesses: list[FaultyRobotGuess]
	true_values: list[FaultyRobotGuess]
	faults_present: au.FaultType = None
	response_times: list[float] = None
	metadata: VideoMetadata = field(default_factory=lambda: VideoMetadata())
	confusion_matrix: au.ConfusionMatrix = field(default_factory=lambda: au.ConfusionMatrix())
	performance_metrics: au.PerformanceMetrics = field(default_factory=lambda: au.PerformanceMetrics())

@dataclass   
class UserQuantData:
	video_experiments: list[VideoExperiment]
	user_number: int = -1
	
def populate_metadata(video_type, seed, user_watch_order):
	metadata = VideoMetadata(video_type=video_type, seed=seed, user_watch_order=user_watch_order)
	metadata.num_robots = au.find_swarm_size_by_video_type(video_type)
	metadata.are_leds_on = au.find_leds_on_by_video_type(video_type)
	metadata.num_faults = au.find_num_faults_by_video_type(video_type)
	return metadata


def set_fault_type_by_reason(reason):
	if reason == PROX_STR:
		return au.FaultType.PROX_FAULT
	elif reason == WHEEL_STR:
		return au.FaultType.WHEEL_FAULT
	elif reason != au.NA_STR and reason != "":
		return au.FaultType.OTHER_FAULT
	else:
		return au.FaultType.TYPE_NOT_GIVEN


def construct_faulty_robot_guess(df, rows, starting_row_index, column_index, user_num, video_type, remove_beacon_guesses):
	list_of_guesses = []
	for i in rows:
		robot_id = df.iloc[starting_row_index+i, column_index]
		if au.UNKNOWN_STR == robot_id or au.NONE_STR == robot_id:
			break
		else:
			is_revoke = False
			if robot_id.endswith(REVOKE_STR):
				robot_id = robot_id.replace(REVOKE_STR, "")
				is_revoke = True
			elif robot_id.startswith(BEACON_STR):
				print("Beacon guess found")
				if remove_beacon_guesses:
					continue
				else:
					robot_id = robot_id.replace(BEACON_STR, "")

			timestamp = df.iloc[starting_row_index+i, column_index+TIMESTAMP_COLUMN]
			try:
				bad_robot_id = True
				if au.NA_STR != robot_id:
					robot_id = int(robot_id)
				bad_robot_id = False
				if au.NA_STR != timestamp:
					timestamp = float(timestamp)
			except ValueError:
				blame_str = "robot_id" if bad_robot_id else "timestamp"
				blame_value = robot_id if bad_robot_id else timestamp
				print(f"Bad {blame_str} got through: {blame_value}")
				print("starting_row_index", starting_row_index)
				print("i", i)
				print("column_index", column_index)
				# print(df.iloc[starting_row_index+i,:])
				print("user_num", user_num)
				print("video_type", video_type)
			reason = df.iloc[starting_row_index+i, column_index+REASON_COLUMN]
			fault_type = set_fault_type_by_reason(reason)
			faulty_robot_guess = FaultyRobotGuess(is_revoke, robot_id, timestamp, reason, fault_type)
			list_of_guesses.append(faulty_robot_guess)

	return list_of_guesses

def construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, column_index, user_num, video_type, remove_beacon_guesses):
	guess_rows = range(1, last_guess_row_index - guess_row_index)
	faulty_robot_guesses = construct_faulty_robot_guess(df, guess_rows, guess_row_index, column_index, user_num, video_type, remove_beacon_guesses)
	video_experiment.guesses = faulty_robot_guesses

	true_value_rows = range(MAX_NUM_ERRORS)
	true_faulty_robots = construct_faulty_robot_guess(df, true_value_rows, true_values_row_index, column_index, user_num, video_type, remove_beacon_guesses)
	video_experiment.true_values = true_faulty_robots

	wheel, prox = False, False
	if len(true_faulty_robots) == 0:
		video_experiment.faults_present = au.FaultType.NO_FAULTS_PRESENT
	else:
		for i in range(len(true_faulty_robots)):
			if true_faulty_robots[i].fault_type == au.FaultType.PROX_FAULT:
				prox = True
			elif true_faulty_robots[i].fault_type == au.FaultType.WHEEL_FAULT:
				wheel = True
		if prox and not wheel:
			video_experiment.faults_present = au.FaultType.PROX_FAULT
		elif wheel and not prox:
			video_experiment.faults_present = au.FaultType.WHEEL_FAULT
		elif wheel and prox:
			video_experiment.faults_present = au.FaultType.WHEEL_AND_PROX_FAULT
		else:
			raise ValueError("ERROR in construct_video_experiment: True faults present but not for a valid reason")
	
	return video_experiment


def extract_quant_data_from_csv(filename, remove_beacon_guesses):
	df = pd.read_csv(filename)
	# print(df.info())

	df.fillna('unknown', inplace=True)

	all_user_data = []

	for i in range(1,au.NUM_USERS+1):
		# MISSING_USER = 43
		# if i == MISSING_USER:
		# 	continue
		user_data = UserQuantData([], i)
		user_str = "User " + str(i)
		guess_row = df[df.iloc[:, ROW_VALUE_COLUMN].str.endswith(user_str)]

		if guess_row.empty:
			print(f"No user found for user string: {user_str}")
			continue

		guess_row_index = guess_row.index[ROW_VALUE_COLUMN]
		true_values_row_index = au.find_row_index(df, TRUE_VALUES_STR, ROW_VALUE_COLUMN, guess_row_index)
		last_guess_row_index = true_values_row_index - 1
		num_expected_duplicates = 0
		for j in range(1,au.NUM_VIDEOS+1):
			column = "Video Type " + str(j)
			column_index = df.columns.get_loc(column)
			if au.UNKNOWN_STR == df.iloc[guess_row_index, column_index]:
				print(f"WARNING: No experiment data found for video type {j} for user {i}")
				num_expected_duplicates += 1
				continue

			video_experiment = VideoExperiment([],[],[])
			seed = df.iloc[guess_row_index, column_index]

			user_watch_str = df.iloc[guess_row_index, column_index+1]
			user_watch_order = int(user_watch_str.replace("Exp ", ""))

			video_experiment.metadata = populate_metadata(j, seed, user_watch_order)

			video_experiment = construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, column_index, i, j, remove_beacon_guesses)

			user_data.video_experiments.append(video_experiment)
			

		num_duplicates = 0
		for j in range(1,NUM_DUPLICATE_VIDEOS+1):
			duplicate_column = "Video Type Duplicate " + str(j)
			duplicate_column_index = df.columns.get_loc(duplicate_column)
			if au.UNKNOWN_STR == df.iloc[guess_row_index, duplicate_column_index]:
				continue
			else:
				num_duplicates += 1
			
			video_experiment = VideoExperiment([],[],[])
			
			seed = df.iloc[guess_row_index, duplicate_column_index]

			user_watch_str = df.iloc[guess_row_index, duplicate_column_index+1]
			user_watch_order = int(user_watch_str.replace("Exp ", ""))

			video_type_str = df.iloc[guess_row_index, duplicate_column_index+2]
			video_type_num = int(video_type_str.replace("Type ", ""))
			
			video_experiment.metadata = populate_metadata(video_type_num, seed, user_watch_order)

			video_experiment = construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, duplicate_column_index, i, video_type_num, remove_beacon_guesses)


			user_data.video_experiments.append(video_experiment)

		if len(user_data.video_experiments) != au.NUM_VIDEOS:
			print(f"WARNING: Expected user {user_data.user_number} to have {au.NUM_VIDEOS} videos, but they had {len(user_data.video_experiments)} videos")

		if num_duplicates != num_expected_duplicates:
			print(f"WARNING: Different expected number of duplicates and number of actual duplicates for user {user_data.user_number}, expected: {num_expected_duplicates}, actual: {num_duplicates}. This is most likely because the number of videos the user watched was not the expected value.")

		all_user_data.append(user_data)
		print(f"Finished adding data for user {user_data.user_number}")
	
	return all_user_data

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
				print(f"WARNING: Match found in guesses, but the timestamp was not valid: {experiment.guesses[i].timestamp} [of type {type(experiment.guesses[i].timestamp)}], will keep searching to see if another value matches and has a valid timestamp.")
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
		print(f"WARNING: No match found in calculate_response_times. This means a response time could not be calculated for this value.")
		return None
					
	if true_value_found:
		response_time = guess_time - fault_injection_time
		return response_time
	else:
		raise ValueError(f"No true value found in calculate_response_times.")


def populate_confusion_matrix(experiment, remove_revoked):
	# Focus on the hypothesis first, then try to explain those results, not just going looking for some new interesting find.
	confusion_matrix = au.ConfusionMatrix()

	confusion_matrix.total_robots = experiment.metadata.num_robots

	actual_faulty_ids = []
	for faulty_robot in experiment.true_values:
		actual_faulty_ids.append(faulty_robot.robot_id)

	guess_faulty_ids = set()
	revoked_guesses = []
	for guess_robot in experiment.guesses:
		if guess_robot.is_revoke:
			if guess_robot.robot_id in guess_faulty_ids:
				if remove_revoked:
					guess_faulty_ids.remove(guess_robot.robot_id)
			else:
				print("WARNING: Revoked id found but no guess was made for it before...")
			continue
		
		guess_faulty_ids.add(guess_robot.robot_id)

	response_times = []
	for guess_id in guess_faulty_ids:
		if au.NA_STR == guess_id or au.NONE_STR == guess_id:
			continue
		elif guess_id in actual_faulty_ids:					
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

	LARGE_SWARM_SIZE = 64
	SMALL_SWARM_SIZE = 16
	num_total_robots = LARGE_SWARM_SIZE if experiment.metadata.video_type % 2 == 0 else SMALL_SWARM_SIZE  # Large for even, Small for odd
	num_faulty_robots = len(experiment.true_values)
	confusion_matrix.true_negatives = (num_total_robots - num_faulty_robots) - confusion_matrix.false_positives

	if num_faulty_robots != (confusion_matrix.true_positives + confusion_matrix.false_negatives):
		raise ValueError("Cannot have a different number of faulty robots than the sum of true positives and false negatives")
	
	return confusion_matrix, response_times

def populate_cm_for_each_experiment(data, remove_revoked):
	for i in range(len(data)):
		print(f"Populating user {data[i].user_number}")
		# Go through each video
		for j in range(len(data[i].video_experiments)):
			experiment = data[i].video_experiments[j]
			data[i].video_experiments[j].confusion_matrix, data[i].video_experiments[j].response_times  = populate_confusion_matrix(experiment, remove_revoked)
			data[i].video_experiments[j].performance_metrics = au.get_cm_metrics(data[i].video_experiments[j].confusion_matrix)
	return data

def get_quant_data_from_csv(filename, remove_beacon_guesses, removed_revoked):
	extracted_data = extract_quant_data_from_csv(filename, remove_beacon_guesses)
	cm_populated_data = populate_cm_for_each_experiment(extracted_data, removed_revoked)
	return cm_populated_data

def main():
	filename = '../data/user_study_user_data/quantitative_raw_results.csv'
	data = get_quant_data_from_csv(filename)
	print(data)

if __name__ == "__main__":
	main()