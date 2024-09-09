import pandas as pd
import analysis_utils as au
from dataclasses import dataclass

NUM_DUPLICATE_VIDEOS = 2
NUM_EXPERIMENT_COLUMNS = 3
REVOKE_STR = "-Revoke"
BEACON_STR = "(beacon) "
# TODO(Cameron): Check that "NONE" actually didn't get replaced by unknown...
NONE_STR = "NONE"
TRUE_VALUES_STR = "True Values"
TIMESTAMP_COLUMN = 1
REASON_COLUMN = 2
MAX_NUM_ERRORS = 2
ROW_VALUE_COLUMN = 0


@dataclass
class FaultyRobotGuess:
	is_revoke: bool = False
	robot_id: int = -1
	timestamp: float = -0.1
	reason: str = ""
	reason_enum: au.FaultType = None
	is_false_positive: bool = None

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
	response_times: list[float]
	metadata: VideoMetadata = VideoMetadata()
	confusion_matrix: au.ConfusionMatrix = au.ConfusionMatrix()

@dataclass   
class UserQuantData:
	video_experiments: list[VideoExperiment]
	user_number: int = -1
	
def populate_metadata(video_type, seed, user_watch_order):
	metadata = VideoMetadata(video_type=video_type, seed=seed, user_watch_order=user_watch_order)

	LARGE_NUM_ROBOTS = 64
	SMALL_NUM_ROBOTS = 16
	SIZE_MODULO_NUM = 2
	metadata.num_robots = SMALL_NUM_ROBOTS if video_type % SIZE_MODULO_NUM else LARGE_NUM_ROBOTS
	
	LEDS_MODULO_NUM = 4
	LEDS_OFF_THRESHOLD = 2
	metadata.are_leds_on = (video_type-1) % LEDS_MODULO_NUM < LEDS_OFF_THRESHOLD

	FAULT_GROUPING_NUM = 4
	metadata.num_faults = int((video_type-1)/FAULT_GROUPING_NUM)

	return metadata


def construct_faulty_robot_guess(df, rows, starting_row_index, column_index, user_num, video_type):
	list_of_guesses = []
	for i in rows:
		robot_id = df.iloc[starting_row_index+i, column_index]
		if au.UNKNOWN_STR == robot_id or NONE_STR == robot_id:
			break
		else:
			is_revoke = False
			if robot_id.endswith(REVOKE_STR):
				robot_id = robot_id.replace(REVOKE_STR, "")
				is_revoke = True
			elif robot_id.startswith(BEACON_STR):
				print("Beacon guess found")
				continue
				#robot_id = robot_id.replace(BEACON_STR, "")

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
				print(f"Bad {blame_str} got through: {timestamp}")
				print(starting_row_index)
				print(i)
				print(column_index)
				# print(df.iloc[starting_row_index+i,:])
				print(user_num)
				print(video_type)
			reason = df.iloc[starting_row_index+i, column_index+REASON_COLUMN]
			faulty_robot_guess = FaultyRobotGuess(is_revoke, robot_id, timestamp, reason)
			list_of_guesses.append(faulty_robot_guess)

	return list_of_guesses

def construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, column_index, user_num, video_type):
	guess_rows = range(1, last_guess_row_index - guess_row_index)
	faulty_robot_guesses = construct_faulty_robot_guess(df, guess_rows, guess_row_index, column_index, user_num, video_type)
	video_experiment.guesses = faulty_robot_guesses

	true_value_rows = range(MAX_NUM_ERRORS)
	true_faulty_robots = construct_faulty_robot_guess(df, true_value_rows, true_values_row_index, column_index, user_num, video_type)
	video_experiment.true_values = true_faulty_robots


	return video_experiment



def extract_quant_data_from_csv(filename):
	df = pd.read_csv(filename)
	# print(df.info())

	df.fillna('unknown', inplace=True)

	all_user_data = []

	for i in range(1,au.NUM_USERS+1):
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

			video_experiment = construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, column_index, i, j)

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

			video_experiment = construct_video_experiment(df, video_experiment, guess_row_index, last_guess_row_index, true_values_row_index, duplicate_column_index, i, video_type_num)


			user_data.video_experiments.append(video_experiment)

		if len(user_data.video_experiments) != au.NUM_VIDEOS:
			print(f"WARNING: Expected user {user_data.user_number} to have {au.NUM_VIDEOS} videos, but they had {len(user_data.video_experiments)} videos")

		if num_duplicates != num_expected_duplicates:
			print(f"WARNING: Different expected number of duplicates and number of actual duplicates for user {user_data.user_number}, expected: {num_expected_duplicates}, actual: {num_duplicates}. This is most likely because the number of videos the user watched was not the expected value.")

		all_user_data.append(user_data)
		print(f"Finished adding data for user {user_data.user_number}")
	
	return all_user_data


def main():
	filename = '../data/user_study_user_data/quantitative_raw_results.csv'
	data = extract_quant_data_from_csv(filename)
	print(data)

if __name__ == "__main__":
    main()