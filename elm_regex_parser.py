#!/usr/bin/python

import argparse
from Bio import SeqUtils
from collections import OrderedDict

def get_args(argv=None):
    parser = argparse.ArgumentParser(description='Mark each position in an ELM Regular Expression as fixed, variable or wildcard.')
    parser.add_argument('regex')
    return parser.parse_args()

def unnested_parentheses(regex):
    '''Expressions in parentheses.'''
    parentheses = []
    start = []
    parentheses = []
    parentheses_alt = []
    alt = []
    for index,character in enumerate(regex):
        if character == '(':  # start of group or position of interest
            start.append(index)
        elif character == ')':  # end of group or position of interest
            parentheses.append([start.pop(),index])
        elif character == '|':  # marker of alternative groups
            alt.append(index)
    for index in alt:  # alternative groups
        index_before = index - 1
        index_after = index + 1
        parentheses_tmp = parentheses[:]
        for sublist in parentheses_tmp:
            if sublist[1] == index_before or sublist[0] == index_after:  # if close parenthesis is followed by '|' or if open parenthesis follows '|'
                parentheses_alt.append(sublist)
                parentheses.remove(sublist)
#            if sublist[0] == index_after:
#                parentheses_alt.append(sublist)
#                parentheses.remove(sublist)
    parentheses_alt.append(alt)
    return parentheses, parentheses_alt

def unnested_brackets(regex):
    '''Expressions in brackets.'''
    brackets = []
    start = None
    end = None
    has_parentheses = True
    start_parentheses = None
    end_brackets = False
    has_braces = False
    for index,character in enumerate(regex):
        if character == '[':
            if end_brackets:
                brackets.append([start,end])
#                end_brackets = False
            start = index
            if regex[index - 1] == '(':  # mark start of parentheses surrounding brackets
                has_parentheses = True
                start_parentheses = index - 1
            else:
                start = index
        elif character == ']':
            end = index
            end_brackets = True
            if index == len(regex) - 2 and regex[index + 1] == '$':
                end = index + 1
                brackets.append([start,end])
                end_brackets = False
            if index == len(regex) - 1:  # last position of the regex
                brackets.append([start,end])
                end_brackets = False
        else:
            if end_brackets:
                if character == '{':
                    has_braces = True
                else:
                    if has_braces:
                        if character == '}':
#                            end = index
                            if index < len(regex) - 1 and regex[index + 1] == '$':
                                end = index + 1
                            else:
                                end = index
                            brackets.append([start,end])
                            has_braces = False
                            end_brackets = False
                    else:
                        if character == ')' and has_parentheses:
                            if ( index == len(regex) - 1 or ( index < len(regex) - 1 and regex[index + 1] == '$' )) and ( index < len(regex) - 1 and regex[index + 1] != '|' ):  # last position or last before C-term mark, and not before '|'
                                start = start_parentheses
                                end = index
                                has_parentheses = False
                                start_parentheses = None
                        brackets.append([start,end])
                        has_braces = False
                        end_brackets = False
    return brackets

def unnested_characters(regex):
    '''Isolated letters or dots.'''
    characters = []
    start = None
    end = None
    has_parentheses = False
    has_braces = False
    has_brackets = False
    for index,character in enumerate(regex):
        if character == '^' and not has_brackets:  # N-term
            start = index
        elif ( character.isalpha() or character == '.' ) and ( not has_brackets ):  # AA or dots
            if regex[index - 1] != '^':  # not first character after '^'
                start = index
            elif regex[index - 1] == '(':  # first character in group or position of interest
                start = index - 1
                has_parentheses = True
                continue
            if index < len(regex) - 1:  # not last position in regex
                if regex[index+1] == '$':
                    start = None
                    end = None
                    continue
                if regex[index+1] != '{': #and regex[index+1] != '$':  # check if not followed by braces or by C-term mark
                    end = index
#                    if regex[index+1] == '$':
#                        end = None
#                        continue
#                        end = index + 1
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
        elif character == '(':  # start of group or position of interest, marking end of region
            if start != None:
                end = index - 1
                characters.append([start,end])
                start = None
                end = None
        elif character == ')':  # end of group or position of interest
            if has_parentheses:  # if reading inside group or position of interest
                end = index
                characters.append([start,end])
                has_parentheses = False
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
#                        end = index
                        if index < len(regex) - 1 and regex[index + 1] == '$':
                            end = index + 1
                        else:
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

def accepted_aa(aa_options):
    '''Return string of accepted amino acids.'''
    aa_list = SeqUtils.IUPACData.protein_letters
    if '^' in aa_options:
        accepted_aa_str = ''.join([ aa for aa in aa_list if aa not in aa_options ])
    else:
        accepted_aa_str = ''.join([ aa for aa in aa_list if aa in aa_options ])
    return accepted_aa_str

def wildcard_aa():
    '''Return string of all amino acids.'''
    aa_list = SeqUtils.IUPACData.protein_letters
    return ''.join([ aa for aa in aa_list ])

def expand_wildcard(regex):
    '''Replace wildcard in regex by [all-aa]'''
    new_regex = []
    for char in regex:
        if char == '.':
            new_regex.append(wildcard_aa())
        else:
            new_regex.append(char)
    return new_regex

def expand_brackets(regex,marks):
    '''Make dict with all possible combinations of regex by expanding brackets.'''
    pos_elements = OrderedDict()
    aa_options = []
    start = False
    for index,character in enumerate(marks):
        if character == '!':
            start = not(start)
            if not start:
                pos_elements[index] = accepted_aa(aa_options)
                aa_options = []
        else:
            if start:
                aa_options.append(regex[index])
            else:
                pos_elements[index] = regex[index]
    return pos_elements

def expand_pipe_alt(regex,marks):
    '''Make copies of regex with alternatives from pipes.'''


def expand_parentheses_alt(regex,marks):
    '''Make copies of regex with alternatives from parentheses and pipes.'''
    pos_elements = OrderedDict()
    aa_options = []
    start = False
    for index,character in enumerate(marks):
        if character == ';':
            start = not(start)
            if not start:
               pass 

def old_expand_parentheses(regex,marks):
    '''Split regex on sections marked by parentheses without alternatives.'''
    regex_sections = []
    index_starts = []
    index_ends = []
    index_pairs = []
    for index,character in enumerate(marks):
        if character == ';':
            if regex[index] == '(':
                index_starts.append(index)
            elif regex[index] == ')':
                index_ends.append(index)
    index_pairs = zip(index_starts,index_ends)
    if index_pairs:
        for number,pair in enumerate(index_pairs):
            start = pair[0]
            end = pair[1]
            if not regex_sections and int(start) != 0:
                regex_sections.append(regex[0:start])
            regex_sections.append(regex[start+1:end])
            if len(index_pairs) > 1 and len(index_pairs) > end + 1:  # more than one pair and current pair does not end in last position
                regex_sections.append(regex[end+1:index_pairs[number+1][0]])
        end = int(index_pairs[-1][1])
        end_regex = len(marks)-1
        if end != end_regex:
#    if int(end) not (len(marks)-1):
            regex_sections.append(regex[end+1:len(marks)])
    return regex_sections

def expand_parentheses(regex,marks):
    '''Split regex on list of sections marked by parentheses without alternatives.'''
    regex_sections = []
    marks_sections = []
    index_starts = []
    index_ends = []
    index_pairs = []
    marks_characters = list(marks)
    if ';' not in marks_characters:
        regex_sections.append(regex)
        marks_sections.append(marks)
        return regex_sections,marks_sections  # return regex and marks as tuple of lists if no parentheses without alternatives to remove
    mark_positions = [index for index, item in enumerate(marks_characters) if ';' == item]
    if mark_positions:
        if int(0) not in mark_positions:  # start from beginning
            mark_positions.insert(0,int(0))
        end_regex = len(marks)-1  # finish at end
        if end_regex not in mark_positions:
            mark_positions.append(end_regex+1)
        for index,position in enumerate(mark_positions):  # extract sections separated by parentheses without alternatives
            if index == 0:
                prev_position = position-1
            else:
                if prev_position+1 != position:
                    regex_sections.append(regex[prev_position+1:position])
                    marks_sections.append(marks[prev_position+1:position])
                prev_position = position
    return regex_sections,marks_sections  # return tuple with lists of regex and marks sections separated by parentheses without alternatives

''' 
if __name__ == "__main__":
    args = get_args()
    print args.regex
    characters = unnested_characters(args.regex)
    characters_marks = mark_positions(args.regex,characters,'*')
    brackets = unnested_brackets(args.regex)
    brackets_marks = mark_positions(args.regex,brackets,'!')
    parentheses, parentheses_alt = unnested_parentheses(args.regex)
    parentheses_marks = mark_positions(args.regex,parentheses,';')
    parentheses_alt_marks = mark_positions(args.regex,parentheses_alt,':')
    all_marks = merge_marks(brackets_marks,characters_marks)
    all_marks = merge_marks(all_marks,parentheses_marks)
    all_marks = merge_marks(all_marks,parentheses_alt_marks)
    print all_marks
    regex_split = expand_parentheses(args.regex,all_marks)
    print regex_split
    regex_no_wildcard = expand_wildcard(args.regex)
    print regex_no_wildcard
    print '---------------------------------------------------------'
#    pos_elements = expand_brackets(args.regex,all_marks)
    pos_elements = expand_brackets(regex_no_wildcard,all_marks)
    for key,value in pos_elements.items():
        print(key,value)
'''

if __name__ == "__main__":
    args = get_args()
    print '---------------------------------------------------------'
    print args.regex
    characters = unnested_characters(args.regex)
    characters_marks = mark_positions(args.regex,characters,'*')
    brackets = unnested_brackets(args.regex)
    brackets_marks = mark_positions(args.regex,brackets,'!')
    parentheses, parentheses_alt = unnested_parentheses(args.regex)
    parentheses_marks = mark_positions(args.regex,parentheses,';')
    parentheses_alt_marks = mark_positions(args.regex,parentheses_alt,':')
    all_marks = merge_marks(brackets_marks,characters_marks)
    all_marks = merge_marks(all_marks,parentheses_marks)
    all_marks = merge_marks(all_marks,parentheses_alt_marks)
    print all_marks
    regex_split,marks_split = expand_parentheses(args.regex,all_marks)
    print regex_split
    regex_dict = OrderedDict()
    regex_index = 0
    for number,section in enumerate(regex_split):
        regex_no_wildcard = expand_wildcard(section)
        print regex_no_wildcard
#    pos_elements = expand_brackets(args.regex,all_marks)
#        pos_elements = expand_brackets(regex_no_wildcard,all_marks)
        pos_elements = expand_brackets(regex_no_wildcard,marks_split[number])
#        pos_elements = expand_brackets(section,marks_split[number])
        for key,value in pos_elements.items():
            print(key,value)
            regex_dict[regex_index] = value
            regex_index += 1
    print('================')
    for key,value in regex_dict.items():
        print(key,value) 
    print('================')
