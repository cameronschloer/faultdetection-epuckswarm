from collections import namedtuple

# NUM_VIDEOS = 12
# NUM_DUPLICATE_VIDEOS = 2
# NUM_USERS = 34
# NUM_EXPERIMENT_COLUMNS = 3
# REVOKE_STR = "-Revoke"
# BEACON_STR = "(beacon) "
# UNKNOWN_STR = "unknown"
# NA_STR = "nada"
# NONE_STR = "NONE"
# TIMESTAMP_COLUMN = 1
# REASON_COLUMN = 2
# MAX_NUM_ERRORS = 2
# ROW_VALUE_COLUMN = 0

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