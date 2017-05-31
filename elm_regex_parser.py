#!/usr/bin/python

import argparse

def get_args(argv=None):
    parser = argparse.ArgumentParser(description='Mark each position in an ELM Regular Expression as fixed, variable or wildcard.')
    parser.add_argument('regex')
    return parser.parse_args()

def unnested_parentheses():
    '''Expressions in parentheses.'''
    pass

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
            continue
    return brackets

if __name__ == "__main__":
    args = get_args()
    brackets = unnested_brackets(args.regex)
    print args.regex
    marks = ''
    flatten_brackets = [ item for sublist in brackets for item in sublist ]
    for index,character in enumerate(args.regex):
        if index in flatten_brackets:
            marks += '|'
        else:
            marks += ' '
    print marks
#brackets,braces,parentheses
