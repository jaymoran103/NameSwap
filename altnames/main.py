import sys
import time
import csv
from faker import Faker
from typing import Dict,Set



# Renamer class for generating and storing safe names
class Renamer:

    # Initializes the Renamer with a seed for deterministic name generation.
    def __init__(self, seed: str = "safenames"):
        self.mappings: Dict[str, str] = {}
        self.used_names: Set[str] = set()

        # Use Faker to generate names
        self.fake = Faker()
        Faker.seed(seed)
        # Faker.seed(hash(seed) % (2**32))  # Future - add option to make names random or deterministic

    # Generates or retrieves a safe name for the given original name.
    # def get_safe_name(self, original: str) -> str: TODO enforce type?
    def get_safe_name(self, original):

        # Return empty or whitespace-only names. Future - handle pre-validation in separate method?
        if not original or not original.strip() or original is None:
            return original
            
        # Strip whitespace for consistent mapping, return existing mapping if present
        original = original.strip()
        if original in self.mappings:
            return self.mappings[original]
        
        # Try to generate a unique name. While building, capping attempts at 10/20 meant no collisions
        #max_attempts = GENERATION_ATTEMPT_LIMIT #Future - reimplement
        max_attempts = 20 #magic number - log curve flattens out around 15 attempts

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

        WARN_MAX_ATTEMPTS = True #Future - reimplement as config field
        if WARN_MAX_ATTEMPTS:
            print(f"Max attempts reached ({attempt}). Assigned unique name '{candidate}' for original name '{original}'.")

        return candidate





# Configuration class to handle command-line arguments for inputs and options
class Configuration:

    def __init__(self):
        self.files = []
        self.columns = []

        self.flag_mappings = {
            "-f" : self.addFile,
            "-c" : self.addColumn
        } 
        #Future - features for later
        #optionMappings = {
        #   "--help","--menu" : printMenu(),
        #   "--autocolumns" : autoDetectColumns()
        #}
    

    def addFile(self,path:str):
        if path not in self.files:
            self.files.append(path)
    
    def addColumn(self,path:str):
        if path not in self.columns:
            self.columns.append(path) 

    def print_menu(self):
        print("usage: main.py [-f <file>] [-c <column>]")

    def processArgs(self,arg_queue:list):

        #Future - iterate over args rather than consuming a queue? since this isnt the original copy and is simple, im not concerned
        while len(arg_queue) > 0:
            current_arg = arg_queue.pop(0)

            #Catch input flags, using the following argument as their input
            if current_arg in self.flag_mappings:
                #If no argument follows the flag, reject
                if len(arg_queue) == 0:
                    print("caught input flag without an argument following. Exiting for safety")
                    exit(1)

                #If present, pop the next argumnent, using it as input for the flag function
                next_arg = arg_queue.pop(0)
                function = self.flag_mappings[current_arg]
                function(next_arg)

            #Future - apply options indicated by --option style flags (no following arguments)
            # elif current_arg in option_mappings:
            #     function = self.option_mappings[current_arg]
            #     function()

            else:
                #what if an argument isn't a flag? use as file later?
                #self.flag_mappings["-f"](current_arg)

                print(f"currently no support for argument: '{current_arg}' without a preceding flag. Exiting for safety")
                print()
                self.print_menu()
                exit(1)

    def validateConfig(self):
        if self.files == []:
            print("No files specified. Use -f <file> to add files.")
            return False
        if self.columns == []:
            print("No columns specified. Use -c <column> to add columns.")
            return False
        return True
        #Future - check validity of input files, maybe offer fallbacks for columns?

    def reportReady(self):
        print("Ready to start with the following configuration:")
        print(f"Files: {self.files}")
        print(f"Columns: {self.columns}")
        print()

    def userConfirm(self):
        response = input("Continue?? (y/n): ")
        if response.lower() in ['y', 'yes']:
            return True
        else:
            print("Operation cancelled by user.")
            return False




# CSVProcessor class for processing CSV files and replacing names in specified columns.
# Future - add graceful handling somewhere for file issues
class CSVProcessor:

    def __init__(self, config: Configuration, renamer: Renamer):
        self.config = config
        self.renamer = renamer

        self.name_columns = config.columns
        self.target_files = config.files

        self.output_prefix = "renamed"

    def start(self):
        print(f"Starting processing of files: {self.target_files}")
        for input_file in self.target_files:
            output_file = f"{self.output_prefix}-{input_file}"
            print(f"Processing {input_file} -> {output_file}",end="\n")
            self.process_file(input_file, output_file)
            print(f" ^ success")
    
    #iterate through input file, replacing names in target columns and writing to output file
    def process_file(self, input_path: str, output_path: str):

        with open(input_path, 'r', newline='', encoding='utf-8-sig') as infile:
                    
            #TODO - settle on final approach for handling cm file bugs in header row
            #before setting up reader, read and store header (fixes DictWriter bug where irregular header lines would be recreated unfaithfully, rather than leaving headers untouched)
            #header_line = infile.readline() # Add this line to store the header before printing verbatim as output header
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
                    
                    #iterate through rows, replacing names when relevant
                    for row in reader:
                        print(f"+{row}")
                        for col in self.name_columns:
                            if col in row and row[col]:
                                
                                row[col] = self.renamingFunction(self.renamer,row[col])

                        # Write row with replaced names
                        writer.writerow(row)
 
    #Given a name string, returns a renamed, ready to use version 
    #Based on TOKENIZE_NAME_PARTS status, will apply renamer to the whole string, or in chunks split by designated characters
    def renamingFunction(self,renamer_instance: Renamer,nameString: str):

        TOKENIZE_NAME_PARTS = True #TODO - reimplement as configurable option
        #Future - handle with first class function somewhere calling this function or get_safe_name directly?
        #Rename and return whole string if not tokenizing
        if not TOKENIZE_NAME_PARTS: 
            return renamer_instance.get_safe_name(nameString)

        else:
            #splittingStrings = ["del","jr","sr"] #Future - also exempt strings like titles and connecting words?
            splittingCharacters = [' ','-','–','—',',']

            built_string = ""
            pending_chars = ""

            #Iterate through characters in string, pausing to rename and append recent characters whenever a splitting character is reached.
            for c in nameString:
                # if splittingCharacters.contains(c):
                if c in splittingCharacters:
                    
                    renamed_string = renamer_instance.get_safe_name(pending_chars)
                    print(f"{pending_chars} -> {renamed_string}")
                    #append renamed string and splitting token, then clear pendingChars
                    built_string += renamed_string
                    built_string += c
                    pending_chars = ""
                else:
                    pending_chars+=c
                    

            #if a remainder exists, rename and append
            if pending_chars != "":                
                # built_string += renamer_instance.get_safe_name(pending_chars)
                # built_string += renamer_instance.get_safe_name(pending_chars)
                built_string += renamer_instance.get_safe_name(pending_chars)

            return built_string

if __name__ == "__main__":
    config = Configuration()
    config.processArgs(sys.argv[1:])

    if config.validateConfig():
        config.reportReady()
    else:
        print("Validation failed. Exiting")
        exit(0)
    
    if config.userConfirm():
        renamer = Renamer()
        file_processor = CSVProcessor(config,renamer)

        #Start process, timing for user feedback
        start_time = time.perf_counter()
        file_processor.start()
        end_time = time.perf_counter()

        #Determine elapsed time and print exit message
        elapsed_time = end_time - start_time
        print(f"Process finished in {elapsed_time:0.3f}s\n")


    else:
        exit(1)

