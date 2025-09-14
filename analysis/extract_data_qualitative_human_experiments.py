import pandas as pd
import analysis_utils as au
from dataclasses import dataclass, field



PREQUESTIONNAIRE_STR = "Pre-Questionnaire"
POSTQUESTIONNAIRE_STR = "Post-Questionnaire"
ROBOTICS_YEARS_STR = "Years w/ Robots in Simulation"
VIDEO_GAMES_YEARS_STR = "Years Playing Video Games"
STEM_YEARS_STR = "Years of STEM Education/Learning"
HELPFUL_EXPERIENCE_STR = "Have Helpful Experience?"
HARMFUL_EXPERIENCE_STR = "Have Harmful Experience?"
MENTAL_DEMAND_STR = "Mental Demand w/ swarm feedback"
PHYSICAL_DEMAND_STR = "Physical Demand w/ swarm feedback"
TEMPORAL_DEMAND_STR = "Temporal Demand w/ swarm feedback"
PERFORMANCE_STR = "Performance w/ swarm feedback"
EFFORT_STR = "Effort w/ swarm feedback"
FRUSTRATION_STR = "Frustration w/ swarm feedback"
USEFULNESS_STR = "Usefulness of Swarm Feedback"
EASE_STR = "Ease to understand Swarm Feedback"
TRUST_STR = "Trust of Swarm Feedback"
DIFFICULTY_STR = "Difficulty finding faulty robots"
IMPROVE_INTERFACE_STR = "Anything to improve user interface?"
QUESTIONS_OR_COMMENTS_STR = "Any other questions or comments?"
FIRST_ROW = 0
QUESTION_COLUMN = 1
NULL_INT = -1
NULL_FLOAT = -0.1
NULL_STR = ""


@dataclass
class NumAndComment:
	num: float = None
	comment: str = None


@dataclass
class BoolAndComment:
	boolean: bool = None
	comment: str = None


@dataclass
class PreQuestionnaire:
	robotics_years: NumAndComment = field(default_factory=lambda: NumAndComment())
	video_games_years: NumAndComment = field(default_factory=lambda: NumAndComment())
	stem_years: NumAndComment = field(default_factory=lambda: NumAndComment())
	help: BoolAndComment = field(default_factory=lambda: BoolAndComment())
	harm: BoolAndComment = field(default_factory=lambda: BoolAndComment())


@dataclass
class NasaTlxScale:
	with_swarm_feedback: float = None
	without_swarm_feedback: float = None
	comment: str = None


@dataclass   
class PostQuestionnaire:
	mental_demand: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	physical_demand: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	temporal_demand: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	performance: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	effort: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	frustration: NasaTlxScale = field(default_factory=lambda: NasaTlxScale())
	feedback_usefulness: NumAndComment = field(default_factory=lambda: NumAndComment())
	feedback_ease_of_understanding: NumAndComment = field(default_factory=lambda: NumAndComment())
	trust_of_feedback: NumAndComment = field(default_factory=lambda: NumAndComment())
	finding_faulty_difficulty: NumAndComment = field(default_factory=lambda: NumAndComment())
	improve_interface: str = None
	other_comments_or_questions: str = None


@dataclass   
class UserQualData:
	pre_questionnaire: PreQuestionnaire = field(default_factory=lambda: PreQuestionnaire())
	post_questionnaire: PostQuestionnaire = field(default_factory=lambda: PostQuestionnaire())
	user_number: int = None


@dataclass   
class QuestionRows:
	robotics_years_row: int = None
	video_games_years_row: int = None
	stem_years_row: int = None
	help_row: int = None
	harm_row: int = None
	mental_demand_row: int = None
	physical_demand_row: int = None
	temporal_demand_row: int = None
	performance_row: int = None
	effort_row: int = None
	frustration_row: int = None
	feedback_usefulness_row: int = None
	feedback_ease_row: int = None
	trust_of_feedback_row: int = None
	difficulty_row: int = None
	improve_interface_row: int = None
	comments_or_questions_row: int = None


def get_datum_from_df_cell(df, row_index, column_index, user_num, return_type):
	datum = df.iloc[row_index, column_index]
	if au.UNKNOWN_STR == datum:
		print(f"WARNING: In get_datum_from_df_cell for user {user_num} on [{row_index}, {column_index}], got unknown string.")
		return None

	is_nada = False
	if au.NA_STR == datum:
		is_nada = True

	if return_type is int:
		datum = NULL_INT if is_nada else int(datum)
	elif return_type is str:
		datum = NULL_STR if is_nada else str(datum)
	elif return_type is float:
		datum = NULL_FLOAT if is_nada else float(datum)
	elif return_type is bool:
		datum = None if is_nada else bool(datum)
	else:
		raise TypeError(f"ERROR: In get_datum_from_df_cell for user {user_num} on [{row_index}, {column_index}], got invalid datatype {return_type}.")
		
	return datum


def retrieve_num_and_comment_data(df, question_row, column_index, user_num):
	COMMENT_ROW_INCREMENT = 1
	num_and_comment = NumAndComment()

	num_and_comment.num = get_datum_from_df_cell(df, question_row, column_index, user_num, float)
	num_and_comment.comment = get_datum_from_df_cell(df, question_row+COMMENT_ROW_INCREMENT, column_index, user_num, str)
	return num_and_comment


def retrieve_bool_and_comment_data(df, question_row, column_index, user_num):
	COMMENT_ROW_INCREMENT = 1
	bool_and_comment = BoolAndComment()

	bool_and_comment.boolean = get_datum_from_df_cell(df, question_row, column_index, user_num, bool)
	bool_and_comment.comment = get_datum_from_df_cell(df, question_row+COMMENT_ROW_INCREMENT, column_index, user_num, str)
	return bool_and_comment


def construct_pre_questionnaire(df, question_rows, column_index, user_num):
	pre_questionnaire = PreQuestionnaire()

	# First test question
	pre_questionnaire.robotics_years = retrieve_num_and_comment_data(df, question_rows.robotics_years_row, column_index, user_num)
	if None == pre_questionnaire.robotics_years.num:
		print(f"WARNING: In construct_pre_questionnaire, received unknown string at the beginning of parsing data for user {user_num}. Leaving all data for user blank.")
		return None
	
	# Fill out the rest of the questions
	pre_questionnaire.video_games_years = retrieve_num_and_comment_data(df, question_rows.video_games_years_row, column_index, user_num)
	pre_questionnaire.stem_years = retrieve_num_and_comment_data(df, question_rows.stem_years_row, column_index, user_num)
	pre_questionnaire.help = retrieve_bool_and_comment_data(df, question_rows.help_row, column_index, user_num)
	pre_questionnaire.harm = retrieve_bool_and_comment_data(df, question_rows.harm_row, column_index, user_num)

	return pre_questionnaire


def retrieve_nasa_tlx_data(df, question_row, column_index, user_num):
	WITHOUT_FEEDBACK_INCREMENT = 1
	COMMENT_ROW_INCREMENT = 2
	nasa_tlx = NasaTlxScale()

	nasa_tlx.with_swarm_feedback = get_datum_from_df_cell(df, question_row, column_index, user_num, float)
	nasa_tlx.without_swarm_feedback = get_datum_from_df_cell(df, question_row+WITHOUT_FEEDBACK_INCREMENT, column_index, user_num, float)
	nasa_tlx.comment = get_datum_from_df_cell(df, question_row+COMMENT_ROW_INCREMENT, column_index, user_num, str)
	return nasa_tlx


def construct_post_questionnaire(df, question_rows, column_index, user_num):
	post_questionnaire = PostQuestionnaire()

	# NASA TLX Questions
	post_questionnaire.mental_demand = retrieve_nasa_tlx_data(df, question_rows.mental_demand_row, column_index, user_num)
	post_questionnaire.physical_demand = retrieve_nasa_tlx_data(df, question_rows.physical_demand_row, column_index, user_num)
	post_questionnaire.temporal_demand = retrieve_nasa_tlx_data(df, question_rows.temporal_demand_row, column_index, user_num)
	post_questionnaire.performance = retrieve_nasa_tlx_data(df, question_rows.performance_row, column_index, user_num)
	post_questionnaire.effort = retrieve_nasa_tlx_data(df, question_rows.effort_row, column_index, user_num)
	post_questionnaire.frustration = retrieve_nasa_tlx_data(df, question_rows.frustration_row, column_index, user_num)

	# Custom Num and Comment Questions
	post_questionnaire.feedback_usefulness = retrieve_num_and_comment_data(df, question_rows.feedback_usefulness_row, column_index, user_num)
	post_questionnaire.feedback_ease_of_understanding = retrieve_num_and_comment_data(df, question_rows.feedback_ease_row, column_index, user_num)
	post_questionnaire.trust_of_feedback = retrieve_num_and_comment_data(df, question_rows.trust_of_feedback_row, column_index, user_num)
	post_questionnaire.finding_faulty_difficulty = retrieve_num_and_comment_data(df, question_rows.difficulty_row, column_index, user_num)

	# Free Response Questions
	post_questionnaire.improve_interface = get_datum_from_df_cell(df, question_rows.improve_interface_row, column_index, user_num, str)
	post_questionnaire.other_comments_or_questions = get_datum_from_df_cell(df, question_rows.comments_or_questions_row, column_index, user_num, str)

	return post_questionnaire


def populate_question_rows(df, max_rows):
	question_rows = QuestionRows()
	
	## Pre-questionnaire questions
	question_rows.robotics_years_row = au.find_row_index(df, ROBOTICS_YEARS_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.video_games_years_row = au.find_row_index(df, VIDEO_GAMES_YEARS_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.stem_years_row = au.find_row_index(df, STEM_YEARS_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.help_row = au.find_row_index(df, HELPFUL_EXPERIENCE_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.harm_row = au.find_row_index(df, HARMFUL_EXPERIENCE_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)


	## Post-questionnaire questions
	question_rows.mental_demand_row = au.find_row_index(df, MENTAL_DEMAND_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.physical_demand_row = au.find_row_index(df, PHYSICAL_DEMAND_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.temporal_demand_row = au.find_row_index(df, TEMPORAL_DEMAND_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.performance_row = au.find_row_index(df, PERFORMANCE_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.effort_row = au.find_row_index(df, EFFORT_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.frustration_row = au.find_row_index(df, FRUSTRATION_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.feedback_usefulness_row = au.find_row_index(df, USEFULNESS_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.feedback_ease_row = au.find_row_index(df, EASE_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.trust_of_feedback_row = au.find_row_index(df, TRUST_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.difficulty_row = au.find_row_index(df, DIFFICULTY_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.improve_interface_row = au.find_row_index(df, IMPROVE_INTERFACE_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)
	question_rows.comments_or_questions_row = au.find_row_index(df, QUESTIONS_OR_COMMENTS_STR, QUESTION_COLUMN, FIRST_ROW, max_rows)

	
	return question_rows


def return_valid_df_from_csv(filename):
	try:
		df = pd.read_csv(filename)
	except UnicodeDecodeError:
		# Try different encodings
		print("failed first pass")
		for encoding in ['utf-8', 'latin1', 'cp1252']:
			try:
				print(f"trying {encoding}")
				df = pd.read_csv(filename, encoding=encoding)
				break
			except UnicodeDecodeError:
				pass

		if df is None:
			print("all failed")
			# If all attempts fail, try ignoring errors
			df = pd.read_csv(filename, errors='ignore')

	df.fillna('unknown', inplace=True)
	return df


def extract_qual_data_from_csv(filename):
	df = return_valid_df_from_csv(filename)

	all_user_data = []

	max_rows = len(df)
	question_rows = populate_question_rows(df, max_rows)

	for i in range(1,au.NUM_USERS+1):
		user_data = UserQualData(user_number=i)
		user_str = "User " + str(i)
		user_column_index = df.columns.get_loc(user_str)

		user_data.pre_questionnaire = construct_pre_questionnaire(df, question_rows, user_column_index, i)
		if None == user_data.pre_questionnaire:
			print(f"WARNING: No data received for user {i}, skipping to next user")
			continue
		user_data.post_questionnaire = construct_post_questionnaire(df, question_rows, user_column_index, i)

		all_user_data.append(user_data)
		print(f"Finished adding data for user {user_data.user_number}")
	
	return all_user_data


def main():
	filename = '../data/user_study_user_data/qualitative_raw_results.csv'
	data = extract_qual_data_from_csv(filename)
	print(data)

if __name__ == "__main__":
    main()