import os
import re

# This script was designed for checking ADO build logs, but can be repurposed for other log folders.
# It does the following:
#     -Searches for terms
#     -Has the option to exclude specified secondary matches from the results
#     -Includes neighboring lines for context
#     -Several string formatting features such as max length of the string to print,
#      and how many following lines to print for context.
#
# There are no command line args. All vars are set within the file.

# Directory with the downloaded logs
logDirectory = 'c:\\logs\\'

# Patterns you want to search the data for
# Use \b to indicatea word boundary
error_patterns = [
    #re.compile(r'\berror\b', re.IGNORECASE),
    #re.compile(r'undefined', re.IGNORECASE),
    #re.compile(r'fail', re.IGNORECASE),
    #re.compile(r'missing', re.IGNORECASE),
    #re.compile(r'conflict', re.IGNORECASE),
    re.compile(r'Exception\b', re.IGNORECASE),
    #re.compile(r'warning', re.IGNORECASE),
]

# Patterns that will invalidate a match.
# When working on a new data set, start with this empty, and
# add to it to simplify the returned data
ignore_patterns = [
    re.compile(r'End of inner exception', re.IGNORECASE),
    re.compile(r'To see full exception', re.IGNORECASE),
    re.compile(r'Standard Error from Local Service', re.IGNORECASE),
]

# Max number or matches you return per file.
# Some files may have hundreds of matches, so you may want to use a lower number for exploration
maxMatches = 10

# Only look at the first n chars for a match
# If you search the whole string, you main get non-relevent matches (toward the end of the string)
# especially when searching for tags
searchFirstNChars = 70

# How many chars of each line to output. Set to a large number to print out the whole line.
outputStrLen = 90

# After a match, n lines are printed out for context. This value is how many context lines are printed
printNextLines = 3

# Function to format the data lines
def formatDataLine(lineNum, header, data):
    # Use line like normal if it fits within the defined length.
    # If not, truncate it, and say how long the line was
    if len(data) < outputStrLen :
       return f'  [{lineNum}] {header} {data.strip()}'
    else:
       return f'  [{lineNum}] {header} {data[:outputStrLen].strip()} [...](len:{len(data)})'

def summarizeLogs(directory):
    summary = []
    
    for filename in os.listdir(directory):
        # Look in text files, but skip initializeLog.txt since that is code used by the pipeline,
        # and not an error log.
        if filename.endswith('.txt') and filename != "initializeLog.txt":
            with open(os.path.join(directory, filename), 'r', encoding='utf-8', errors='ignore') as file:
                
                matches = 0
                lineNum = 0
                printMoreLinesCounter = 0
                prevLine = ">"
                
                # Gap between data from each file
                summary.append("-------------------------------");
                summary.append(f'--->>> {filename}:')
                
                for line in file:
                    matchWasPrinted = False
                    if matches < maxMatches:
                        for pattern in error_patterns:
                            if pattern.search(line[:searchFirstNChars]):
                                ignore = False
                                # If ignore pattern found, don't count this as a match
                                for pattern in ignore_patterns:
                                    # search entire printed string space, plus a few more chars
                                    if pattern.search(line[:outputStrLen + 10]):
                                        ignore = True
                                        break
                                
                                if not ignore:
                                    # If this is the first match (in a possible cluster of matches),
                                    # add the previous line for context
                                    if printMoreLinesCounter == 0:
                                        summary.append( formatDataLine(lineNum - 1, " -- ", prevLine))
                                    
                                    # Print the line matching the query
                                    summary.append( formatDataLine(lineNum, ">", line))
                                    matchWasPrinted = True
                                    
                                    # Refresh number of context lines that need to be printed after this
                                    printMoreLinesCounter = printNextLines
                                    
                                    # increase the number of matches found this file
                                    matches += 1
                                    
                                # Always break loop on pattern finding
                                # Either it was already added to the summary,
                                # or it was ignored
                                break
                                
                    # If no match was printed, then see if we need to print lines after a match (for context)
                    if not matchWasPrinted:            
                        if printMoreLinesCounter > 0:
                            printMoreLinesCounter -= 1
                            summary.append( formatDataLine(lineNum, "  - ", line))
                            if printMoreLinesCounter == 0:
                                # Gap between writes
                                summary.append("");
                    
                    # If there are no more non-matching context lines to print, and
                    # the max number of matches for a file is hit, stop searching the file early
                    if printMoreLinesCounter == 0 and matches >= maxMatches:
                        break
                    
                    lineNum += 1
                    prevLine = line
    return summary
    
    
summary = summarizeLogs(logDirectory)
for line in summary:
    print(line)
