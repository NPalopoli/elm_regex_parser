#!/usr/bin/python

import argparse

def get_args(argv=None):
    parser = argparse.ArgumentParser(description='Mark each position in an ELM Regular Expression as fixed, variable or wildcard.')
    parser.add_argument('regex')
    return parser.parse_args()

def unnested_parentheses(regex):
    '''Expressions in parentheses.'''
    parentheses = []
    start = []
    parentheses = []
    alt = []
    for index,character in enumerate(regex):
        if character == '(':  # start of group or position of interest
            start.append(index)
        elif character == ')':  # end of group or position of interest
            parentheses.append([start.pop(),index])
        elif character == '|':  # alternative groups
            alt.append(index)
    parentheses.append(alt)
    return parentheses
    
def unnested_brackets(regex):
    '''Expressions in brackets.'''
    brackets = []
    start = None
    end = None
    end_brackets = False
    has_braces = False
    for index,character in enumerate(regex):
        if character == '[':
            if end_brackets:
                brackets.append([start,end])
                end_brackets = False
            start = index
        elif character == ']':
            end = index
            end_brackets = True
            if index == len(regex) - 1:
                brackets.append([start,end])
                end_brackets = False
        else:
            if end_brackets:
                if character == '{':
                    has_braces = True
                else:
                    if has_braces:
                        if character == '}':
                            end = index
                            brackets.append([start,end])
                            has_braces = False
                            end_brackets = False
                    else:
                        brackets.append([start,end])
                        has_braces = False
                        end_brackets = False
    return brackets

def unnested_characters(regex):
    '''Isolated letters or dots.'''
    characters = []
    start = None
    end = None
    has_braces = False
    has_brackets = False
    for index,character in enumerate(regex):
        if character == '^' and not has_brackets:  # N-term
            start = index
        elif ( character.isalpha() or character == '.' ) and ( not has_brackets ):  # AA or dots
            start = index
            if index < len(regex) - 1:  # not last position in regex
                if regex[index+1] != '{':  # check if not followed by braces
                    end = index
                    characters.append([start,end])
                    start = None
                    end = None
            else:  # last position in regex
                end = index
                characters.append([start,end])
                start = None
                end = None
        elif character == '[':  # start of variable position
            has_brackets = True
            if start != None:
                end = index - 1
                characters.append([start,end])
                start = None
                end = None
        elif character == ']':  # end of variable position
            has_brackets = False
        elif character == '(':  # start of group or position of interest
            if start != None:
                end = index - 1
                characters.append([start,end])
                start = None
                end = None
        elif character == ')':  # end of group or position of interest
            start = None
            end = None
        elif character == '$' and not has_brackets:  # C-term
            end = index
            characters.append([start,end])
            start = None
            end = None
        else:  # variable number of positions
            if character == '{':
                has_braces = True
            else:
                if has_braces:
                    if character == '}':
                        end = index
                        characters.append([start,end])
                        has_braces = False
                        start = None
                        end = None
    return characters
            

def mark_positions(regex,positions,mark):
    '''Mark positions of regex with defined character.'''
    marks = ''
    flatten_positions = [ item for sublist in positions for item in sublist ]
    for index,character in enumerate(regex):
        if index in flatten_positions:
            marks += mark
        else:
            marks += ' '
    return marks

def merge_marks(marks1,marks2):
    '''Merge strings of position marks.'''
    merged_marks = list(marks1)
    for index,character in enumerate(marks2):
        if merged_marks[index] == ' ':
            merged_marks[index] = character
    return ''.join(merged_marks)

if __name__ == "__main__":
    args = get_args()
    print args.regex
    brackets = unnested_brackets(args.regex)
    brackets_marks = mark_positions(args.regex,brackets,'|')
    parentheses = unnested_parentheses(args.regex)
    parentheses_marks = mark_positions(args.regex,parentheses,':')
    all_marks = merge_marks(brackets_marks,parentheses_marks)
    characters = unnested_characters(args.regex)
    characters_marks = mark_positions(args.regex,characters,'*')
    all_marks = merge_marks(all_marks,characters_marks)
    print all_marks

