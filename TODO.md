[ ] CSVProcessor.process_file() account for different styles when rewriting files. check quotes + separators while parsing each file originally, and set write style accordingly? 

[ ] Revisit the approach for handling buggy headers

[ ] Check for file issues when processing arguments, maybe again right before using

[ ] Add proper README

[ ] --dryrun option? not critical since we're renaming new files anyway

[ ] Consider exempting titles and connecting words when tokenizing names.

[X] implement autocolumns feature from og version?

[X] case sensitivity for column names?

[ ] i'll want a better program name than main.py once this is an independent tool

[ ] are docstrings crucial if my comments already do that? linter seems to think so

[ ] replace handler methods with lambda statements when possible, a majority are one line now anyway