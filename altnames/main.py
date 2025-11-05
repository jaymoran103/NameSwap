import sys
from faker import Faker
#from typing import Dict,Set



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
    def get_safe_name(self, original: str) -> str:

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
        print("usage: main.py [-f <file>] [-c <column>] [--help]")

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


if __name__ == "__main__":
    # arg_queue = sys.argv[1:]
    config = Configuration()
    config.processArgs(sys.argv[1:])

    if config.validateConfig():
        config.reportReady()
    
    if config.userConfirm():
        files = config.files
        columns = config.columns
        renamer = Renamer()
        #fileiterator = CSVIterator(renamer,config) #TODO Implement

