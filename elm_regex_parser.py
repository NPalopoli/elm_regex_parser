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
#    had_bracket = False
    for index,character in enumerate(regex):
        if character == '[':
#            if not had_bracket:
                start = index
#                had_bracket == True
#                continue
#            else:
#                brackets.append(unnested_brackets(regex[index:-2]))
        elif character == ']':
            end = index
            end_brackets = True
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
    print brackets

#brackets,braces,parentheses
