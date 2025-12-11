# LOGIC

[X] Revisit the approach for handling buggy (CM Generated) headers

[X] Check for file issues when processing arguments, maybe again right before using

[X] implement autocolumns feature from og version?

[X] case sensitivity for column names?

[X] CSVProcessor.process_file() account for different styles when rewriting files using csv.Sniffer

# DOCUMENTATION / REFACTORS

[X] i'll want a better program name than main.py once this is a standalone tool - NameSwap

[X] Add proper README

[X] added docstrings

[X] replace handler methods with lambda statements when possible, a majority are one line now anyway

# FUTURE FEATURES

[ ] Adapt name bank from poc demo for version without faker dependency.  

[X] Adapt mapping feature from poc demo
    [ ] Add mapping feature documentation to readme and --menu
    [ ] Revise config mapping implementation to defer to new command line arguments
    [ ] Consider saving column names as config info. Could go either way, complicates usage
    [ ] Consider enforcing mapping file format
    [ ] Review layout of print reports
[ ] Refactor finish_setup() to use helper methods.

[ ] Add direct renaming and a dryrun feature? Not needed for my use case.

[ ] Add option to tokenize over other common name components? Not needed for my use case.