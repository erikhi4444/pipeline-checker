import os
import re

log_directory = 'c:\\logs\\'
error_patterns = [
    #re.compile(r'\berror\b', re.IGNORECASE),
    #re.compile(r'fatal', re.IGNORECASE),
    #re.compile(r'cannot', re.IGNORECASE),
    #re.compile(r'undefined', re.IGNORECASE),
    #re.compile(r'fail', re.IGNORECASE),
    #re.compile(r'missing', re.IGNORECASE),
    #re.compile(r'conflict', re.IGNORECASE),
    re.compile(r'Exception\b', re.IGNORECASE),
    #re.compile(r'warning', re.IGNORECASE),
]

ignore_patterns = [
    re.compile(r'End of inner exception', re.IGNORECASE),
    re.compile(r'To see full exception', re.IGNORECASE),
    re.compile(r'_.Exception', re.IGNORECASE),
]

maxMatches = 50
searchFirstNChars = 70
outputStrLen = 90
printNextLines = 3

def summarize_logs(directory):
    summary = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8', errors='ignore') as file:
                
                matches = 0
                lineNum = 0
                printMoreLinesCounter = 0
                # Gap between writes
                summary.append("-------------------------------");
                summary.append(f'--->>> {filename}:')
                prevLine = ">"
                
                for line in file:
                    hasMatch = False
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
                                    if printMoreLinesCounter == 0:
                                        summary.append(f'   [{lineNum-1}]  >>  {prevLine[:outputStrLen].strip()}')
                                    printMoreLinesCounter = printNextLines
                                    summary.append(f'   [{lineNum}]   {line[:outputStrLen].strip()}')
                                    matches += 1
                                    hasMatch = True
                                # Always break loop on pattern finding
                                # Either it was already added to the summary,
                                # or it was ignored
                                break
                    if not hasMatch:            
                        if printMoreLinesCounter > 0:
                            printMoreLinesCounter -= 1
                            
                            if len(line) < outputStrLen :
                                summary.append(f'   [{lineNum}]  >  {line.strip()}')
                            else:
                                summary.append(f'   [{lineNum}]  >  {line[:outputStrLen].strip()} [...](len:{len(line)})')
                            if printMoreLinesCounter == 0:
                                # Gap between writes
                                summary.append("");
                        
                    if printMoreLinesCounter == 0 and matches >= maxMatches:
                        break
                    
                    lineNum += 1
                    prevLine = line
    return summary
    
    
summary = summarize_logs(log_directory)
for line in summary:
    print(line)
