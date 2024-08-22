from collections import namedtuple

Dataline = namedtuple("Dataline", "time robot tolerators attackers")

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