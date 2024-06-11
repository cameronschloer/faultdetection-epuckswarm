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
    
    # Iterate through each line
    for line in lines:
        # Split the line by spaces
        parts = line.replace("\t", " ").replace("\n", " ").split(" ")
        parts 
        print(parts)

        # # Check for Clock line
        # current_clock = int(parts[1])
        # modified_lines.append(line)
        # # Check if any value except "-1" is present
        # if any(val != "-1" for val in parts[3:]):
        #     # If yes, keep the line and the current clock
        #     modified_lines.append(line)
        # elif current_clock is not None:
        #     # If no, check if a clock was previously found
        #     # If a clock was found, keep all lines with that clock and reset
        #     modified_lines.extend([line for line in lines if line.startswith(f"Clock: {current_clock}")])
        #     current_clock = None
    
    # Clear the file content and write modified lines
    # file.seek(0)
    # file.truncate()
    # file.writelines(modified_lines)

# Get the filename from command line arguments (assuming first argument after script name)
if len(sys.argv) > 1:
  filename = sys.argv[1]
else:
  print("Error: Please provide a filename as an argument.")
  sys.exit(1)

# Call the function with the filename and print completion message
analyze_and_modify_file(filename)

print("File analysis and modification complete!")