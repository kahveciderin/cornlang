# Cornlang (codenamed "Metal") parser, tokenizer and lexer.

fcon = -1
with open('language_test.ppl', 'r') as lang:
    fcon = lang.readlines()

def check_id_constraints(var, c):
    retval = c.isalpha() or c == '_'
    if var != "":
        retval |= c.isnumeric()
    return retval

tokens = []

for line in fcon:
    line = line.strip()

    # identifier
    fullid = ""

    # number
    fullnum = 0
    number_base = -1 # not used
    number_char = -1 # not used

    # string
    in_string = False
    fullstr = ""
    is_escaping = False

    # symbol
    fullsym = ""

    # comment
    is_comment = False

    for c in line + ' ': # make the loop go one more time after line ends
        if is_comment:
            break
        oldfullsym = fullsym
        if in_string:
            if c == '"' and not is_escaping:
                in_string = False
                tokens.append({'token': fullstr, 'type': 'str'})
            elif c == '\\' and not is_escaping:
                is_escaping = True
            else:
                fullstr += c
                is_escaping = False
        else:
            if check_id_constraints(fullid, c):
                fullid += c
            else:
                if fullid != "":
                    tokens.append({'token': fullid, 'type': 'identifier'})
                fullid = ""

                if c.isnumeric():
                    fullnum = fullnum * 10 + int(c)
                    number_char += 1
                    if number_char == 0:
                        number_base = 10
                else:
                    if number_char > -1:
                        tokens.append({'token': fullnum, 'type': 'number'})
                    number_char = -1
                    fullnum = 0

                    if c == '"':
                        in_string = True
                        fullstr = ""
                    elif c in ['(', ')', '[', ']', '{', '}']:
                        tokens.append({'token': c, 'type': 'bracket'})
                    elif c == ';':
                        tokens.append({'token': c, 'type': 'semi'})
                    elif c == '#':
                        is_comment = True
                    else:
                        if not c.isspace():
                            # is symbol
                            fullsym += c
        if oldfullsym == fullsym: # we haven't added a token somewhere
            if not fullsym.isspace() and fullsym != '':
                tokens.append({'token': fullsym, 'type': 'sym'})
                fullsym = ""

print("\n".join(["Token: {}\t\t\tType: {}".format(x["token"], x["type"]) for x in tokens]))

# tokenization done, time for lexing!