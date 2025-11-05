import hashlib
import random
from typing import Dict, Set
import csv
import sys
from faker import Faker
import time

TOKENIZE_NAME_PARTS = True
WARN_MISSING_FLAGS = False
WARN_MAX_ATTEMPTS = True

USE_DEFAULT_COLUMNS_AS_FALLBACK = True
USE_AUTO_COLUMNS_AS_FALLBACK = False

DEFAULT_NAME_COLUMNS = ["First Name","Last Name","Preferred Name","Camper"]

GENERATION_ATTEMPT_LIMIT = 20
INDENT_LEVEL = 2


def printi(output):
    print((" " * INDENT_LEVEL)+output)

# TODO Future
#
# clean up starting methods, 'universal_start' etc
#
# find best home for non-class methods
#
# improve documentation for methods and classes


class Renamer:
    """_summary_ Renamer class for generating and storing safe names. 
                 Each Renamer instance maintains a mapping of original names to safe names, 
                 ensuring that renamings are consistent throughout and between files
    Returns:
        _type_: _description_
    """

    # Initializes the Renamer with a seed for deterministic name generation.
    def __init__(self, seed: str = "safenames"):
        """_summary_ Initializes the Renamer with a seed for deterministic name generation.

        Args:
            seed (str, optional): _description_. Seed for consistent generation. Defaults to "safenames". 
        """
        self.mappings: Dict[str, str] = {}
        self.used_names: Set[str] = set()
        self.seed = seed    

        # Use Faker to generate names
        self.fake = Faker()
        # Faker.seed(hash(seed) % (2**32))  # Deterministic seed from string
        Faker.seed(seed)
        
    # Generates or retrieves a safe name for the given original name.
    def get_safe_name(self, original: str) -> str:
        """_summary_ Generates or retrieves a safe name for the given original name.

        Args:
            original (str): _description_ original name to be replaced.

        Returns:
            str: _description_ safe name corresponding to the original name.
        """

        # Return empty or whitespace-only names
        if not original or not original.strip():
            return original
            
        # Strip whitespace for consistent mapping, return existing mapping if present
        original = original.strip()
        if original in self.mappings:
            return self.mappings[original]
        
        # Try to generate a unique name. While building, capping attempts at 1020 meant no collisions
        max_attempts = GENERATION_ATTEMPT_LIMIT

        for attempt in range(max_attempts):
            candidate = self.fake.first_name()
            if candidate not in self.used_names:
                self.mappings[original] = candidate
                self.used_names.add(candidate)
                return candidate

        # If attempts fail, add number suffix to ensure uniqueness
        base_name = self.fake.first_name()
        counter = len(self.used_names)
        candidate = f"{base_name}{counter}"
        
        self.mappings[original] = candidate
        self.used_names.add(candidate)
        if WARN_MAX_ATTEMPTS:
            printi(f"Max attempts reached ({attempt}). Assigned unique name '{candidate}' for original name '{original}'.")

        return candidate

class CSVIterator:
    """_summary_ CSVIterator class for processing CSV files and replacing names in specified columns.
    """

    def __init__(self, name_columns: list[str]):
        self.name_columns = name_columns
    
    #iterate through input file, replacing names in target columns and writing to output file
    def process_file(self, input_path: str, output_path: str, renamer: Renamer):
        with open(input_path, 'r', newline='', encoding='utf-8-sig') as infile:
                    
            #before setting up reader, read and store header (fixes DictWriter bug where irregular header lines would be recreated unfaithfully, rather than leaving headers untouched)
            # header_line = infile.readline() # Add this line to store the header before printing verbatim as output header
            reader = csv.DictReader(infile)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                # outfile.write(header_line)
                if reader.fieldnames:

                    writer = csv.DictWriter(
                        outfile, 
                        fieldnames=reader.fieldnames,
                        quoting=csv.QUOTE_ALL, # Ensures all fields are quoted, convention for CM files
                        # extrasaction='ignore'  # Add this to handle extra columns
                    )
                    writer.writeheader() #comment out if using the header_line bug fix
                    
                    #iterate through rows, 
                    for row in reader:
                        #replacing names when relevant
                        for col in self.name_columns:
                            if col in row and row[col]:
                                row[col] = renamingFunction(renamer,row[col])

                        # Write row with replaced names
                        writer.writerow(row)

#Given a name string, returns a renamed, ready to use version 
#Based on TOKENIZE_NAME_PARTS status, will apply renamer to the whole string, or in chunks split by designated characters
def renamingFunction(renamer: Renamer,nameString: str):

    #Rename and return whole string if not tokenizing
    if not TOKENIZE_NAME_PARTS:
        return renamer.get_safe_name(nameString)

    else:

        #splittingStrings = ["del","jr","sr"]
        splittingCharacters = [' ','-','–','—',',']
        

        builtString = ""
        pendingChars = ""

        #Iterate through characters in string, pausing to rename and append recent characters whenever a splitting character is reached.
        for c in nameString:
            # if splittingCharacters.contains(c):
            if c in splittingCharacters:

                renamedString = renamer.get_safe_name(pendingChars)
                
                #append renamed string and splitting token, then clear pendingChars
                builtString += renamedString
                builtString += c
                pendingChars = ""
            else:
                pendingChars+=c
                

        #if a remainder exists, rename and append
        if pendingChars != "":                
            builtString += renamer.get_safe_name(pendingChars)
            
        return builtString

#Prints given reason for cancelling, and exits program
def cancel_command(reason):
    printi("Cancelling Command: "+reason)
    exit(1)

#Given a set of input files, target columns, and an optional prefix, sets up renamer and iterator to process all files
def universal_start(files, columns, prefix):
    renamer = Renamer()
    iterator = CSVIterator(columns)
    if prefix is None:
        prefix = "renamed"

    for input_file in files:
        output_file = prefix+'-'+input_file
        iterator.process_file(input_file, output_file, renamer)
        printi(f"Processed {input_file} -> {output_file}")

#utility method to apply default name columns to a target set
def apply_default_columns(target_columns:set):
    for col in DEFAULT_NAME_COLUMNS:
        target_columns.add(col)

#utility method to apply auto-detected name columns from input files to a target set
def apply_auto_columns(target_columns:set, input_files:set):
    for file in input_files:
        auto_cols = smart_columns_file(file)
        for col in auto_cols:
            target_columns.add(col)

#Handles command line arguments and returns sets of input files, target columns, and optional renaming prefix
def handle_arguments():

    #Bounce user if no arguments are provided
    if len(sys.argv) == 1:
        cancel_command("Expected arguments. Use --help for usage information.")

    #Booleans to be enabled by flags
    SKIP_USER_CONFIRMATION = False
    USE_AUTO_COLUMNS = False
    USE_DEFAULT_COLUMNS = False

    #Eventual function outputs, determined by given arguments
    target_columns = set()
    input_files = set()
    renaming_prefix = None


    #Iterate through arguments, identifying flags and adding subsequent arguments accordingly
    flag = None
    for argument in sys.argv:
        if argument == sys.argv[0]:
            #skipping any mentions of self (and status as first argument)
            continue
        #If not preceded by a flag, attempt to identify one or raise an issue
        if flag == None:
            #found a flag indicator - 
            if argument[0]=="-":
                if argument[1]=="f":
                    flag = "-f"
                    continue
                elif argument[1]=="c":
                    flag = "-c"
                    continue
                elif argument[1]=="p":
                    flag = "-p"
                    continue
                elif argument[1:]=="-defaultcolumns": #Special flag - adds default name columns
                    flag = None
                    USE_DEFAULT_COLUMNS = True
                    continue
                elif argument[1:]=="-skip": #Special flag - skips user confirmation before starting
                    SKIP_USER_CONFIRMATION = True
                    flag = None
                    continue
                elif argument[1:]=="-autocolumns": #Special flag - uses auto column detection
                    flag = None
                    USE_AUTO_COLUMNS = True
                    continue
                elif argument[1:]=="-help": #Special flag - shows help message and exits
                    printi("Usage: anonymizenames.py [-f inputfile] [-c targetcolumn] [-p renamingprefix] [--extraflags]")
                    printi("  -f <inputfile>        Specify an input CSV file to process. Can be used multiple times for multiple files. Inputs not preceded by a flag default to -f")
                    printi("  -c <targetcolumn>     Specify a column name to rename within the CSV files. Can be used multiple times for multiple columns.")
                    printi("  -p <renamingprefix>   Specify a prefix for output files. Defaults to 'renamed'.")
                    printi("  --defaultcolumns      optional: Automatically include default name columns.")
                    printi("  --autocolumns         optional: Automatically detect and include columns likely containing names.")
                    printi("  --skip                optional: Skip user confirmation before processing.")
                    printi("  --help                Show this help message and exit.")
                    printi("")
                    printi("Program requires at least one input file to run. Required columns can be specified or auto-detected.")
                    exit(0)
                else:
                    printi(f"flag {argument} not recognized. Currently expects '-f' or '-c'")#TODO Update this
                    continue
            
            #no indicator found
            else:
                if WARN_MISSING_FLAGS:
                    printi(f"found argument '{argument}' without a preceding flag. treating as default '-f' (input file)")
                # input_files.add(argument)
                flag = "-f"

        #If preceded by a flag, add argument accordingly
        if flag == "-f":
            flag = None
            input_files.add(argument)
        elif flag == "-c":
            flag = None
            target_columns.add(argument)
        elif flag == "-p":
            flag = None
            if renaming_prefix is None:
                renaming_prefix = argument
            else:
                printi(f"Multiple seed arguments found: ({renaming_prefix},{argument}). Using first and ignoring others")

    #If iteration ends with a flag still noted, let the user know they mighta missed something
    if flag is not None:
        printi(f"Possible issue: input ended with flag '{flag}' which was probably a mistake. Skipping that input")


    #Apply column adding methods if indicated by flags
    if USE_AUTO_COLUMNS:
        apply_auto_columns(target_columns, input_files)
    if USE_DEFAULT_COLUMNS:
        apply_default_columns(target_columns)

    #If no target columns were specified, try fallback methods indicated by booleans
    if len(target_columns)==0:
        if USE_AUTO_COLUMNS_AS_FALLBACK==True:
            printi("No target columns specified - using auto column search")
            apply_auto_columns(target_columns, input_files)
        if USE_DEFAULT_COLUMNS_AS_FALLBACK==True:
            printi("No target columns specified - using default name columns as fallback")
            apply_default_columns(target_columns)
    
    #validate inputs TODO revise or move to util method
    valid = True
    if len(input_files)<=0: #Reject if no input files are specified or available
        valid = False
    if len(target_columns)<=0: #Reject if no target columns are specified or available
        valid = False
    
    if not valid:
        cancel_command("Invalid inputs")
    
    printi("")
    printi(f"Ready to use renamer for files: {', '.join(input_files)}")
    printi(f"For columns: {', '.join(target_columns)}")

    # user_choice = input((" " * INDENT_LEVEL)+"Press ENTER to continue, or any other key then ENTER to cancel: ")
    print()

    user_cancel = False
    if not SKIP_USER_CONFIRMATION:
        user_cancel = input("Press ENTER to continue, or any key then ENTER to skip: ") != ""
    
    if user_cancel:
        cancel_command("Manual")
    else:
        return(input_files,target_columns,renaming_prefix)

#Given a set of header names, returns a set of those names which likely indicate name columns
def smart_columns(header_set:set):
    output_set = set()
    for name in header_set:
        string_name = name.lower()
        if string_name.contains("name"):
            output_set.add(name)

#Given a filepath to a CSV, returns a set of header names which likely indicate name columns
def smart_columns_file(filepath:str):
    output_set = set()
    with open(filepath, 'r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames:
            for name in reader.fieldnames:
                string_name = name.lower()
                if "name" in string_name:
                    output_set.add(name)
    return output_set

#Main method - handles arguments and calls universal start method
if __name__ == "__main__":
    # Handle command line input, to be used as arguments for setup
    input_files,target_columns,renaming_prefix = handle_arguments()
    
    start_time = time.perf_counter()
    universal_start(input_files, list(target_columns), renaming_prefix)
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    printi(f"Process finished in {elapsed_time:0.3f}s\n")
