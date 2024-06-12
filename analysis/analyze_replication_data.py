import sys

def analyze_and_modify_file(filename):
  """
  This function analyzes a text file and modifies it based on specific criteria.

  Args:
    filename: The path to the text file.
  """
  # Open the file for reading and writing
  with open(filename, "r+") as file:
    lines = file.readlines()
    modified_lines = []
    current_clock = None
    
    cache = []
    did_vote = False
    
    # Iterate through each line
    for line in lines:
        # Split the line by spaces
        parts = line.replace("\t", " ").replace("\n", " ").split(" ")
        parts = [i for i in parts if i != ""]

        if len(parts) > 0 and parts[0] == "Clock:":
          if current_clock != int(parts[1]):
              current_clock = int(parts[1])
              if did_vote:
                  modified_lines = modified_lines + cache
              cache = []
              cache.append(line)
              did_vote = False
          else:
              cache.append(line)
              tol_list = [vote for vote in parts[7:27] if vote != '-1']
              attack_list = [vote for vote in parts[28:48] if vote != '-1']
              did_vote = len(tol_list) != 0 or len(attack_list) != 0
    
    # Clear the file content and write modified lines
    file.seek(0)
    file.truncate()
    file.writelines(modified_lines)

# Get the filename from command line arguments (assuming first argument after script name)
if len(sys.argv) > 1:
  filename = sys.argv[1]
else:
  print("Error: Please provide a filename as an argument.")
  sys.exit(1)

# Call the function with the filename and print completion message
analyze_and_modify_file(filename)