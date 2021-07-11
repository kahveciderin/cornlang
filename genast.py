# Cornlang (codenamed "Metal") parser, tokenizer and lexer.

import copy

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
    number_base = -1  # not used
    number_char = -1  # not used

    # string
    in_string = False
    fullstr = ""
    is_escaping = False

    # symbol
    fullsym = ""

    # comment
    is_comment = False

    for c in line + ' ':  # make the loop go one more time after line ends
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
                    elif c == '$':
                        tokens.append({'token': c, 'type': 'formatter'})
                    # elif c in ['+', '-', '*', '/', '^', '~', '%', '!']:
                    #     tokens.append({'token': c, 'type': 'math'})
                    elif c == ';':
                        tokens.append({'token': c, 'type': 'semi'})
                    elif c == '#':
                        is_comment = True
                    else:
                        if not c.isspace():
                            # is symbol
                            fullsym += c
        if oldfullsym == fullsym:  # we haven't added a token somewhere
            if not fullsym.isspace() and fullsym != '':
                tokens.append({'token': fullsym, 'type': 'sym'})
                fullsym = ""


# tokenization done, time for lexing!

errors = []

def error_out():
    if(len(errors) > 0):
        print("\n".join(errors))
        exit(-1)
ast = {
    'globals': {},
    'body': []
}

def set_ast_scope(scope, val):
    nscope = copy.copy(scope)
    cur_d = ast
    for v in scope[:-1]:
        cur_d.setdefault(v, {})
        cur_d = cur_d[v]
    cur_d[scope[-1]] = val

def append_ast_scope(scope, val):
    nscope = [] # ['funcs'] + copy.copy(scope)
    for a in scope:
        nscope += ['body', a]
    nscope += ['body']
    cur_d = ast
    for v in nscope[:-1]:
        cur_d.setdefault(v, {})
        cur_d = cur_d[v]
    cur_d[nscope[-1]].append(val)

def get_ast_scope(scope):
    accumulator = copy.copy(ast)
    for elem in scope:
        accumulator = accumulator[elem]
    return accumulator

# returns itt after incrementing - itt should point to the first opening curly bracket
def lex_scope(scope, itt, entr='{}'):

    def incr_itt(cnt = 1):
        nonlocal itt
        itt += cnt
        if itt >= len(tokens):
            errors.append("Premature end-of-file detected, terminating...")
            error_out()

    scope_checker = 0

    print("CHECK SCOPE =>", scope, "itt", itt, "symbol", tokens[itt]["token"])

    self_function = False

    while True:
        incr_itt()  # get next token

        old_sf = self_function

        print("scope", scope, "itt", itt)
        token = tokens[itt]
        if token["type"] == 'identifier':
            if token["token"] == "fun":  # function definition
                incr_itt()
                function_name = tokens[itt]["token"]
                if tokens[itt]["type"] != "identifier":
                    errors.append("Expected identifier as function name, got {}".format(
                        tokens[itt]["type"]))
                incr_itt()
                function_arguments = []
                function_return = ""
                while tokens[itt]["token"] != '=>':  # TODO: check for EOF
                    arg_name = tokens[itt]["token"]
                    incr_itt()
                    if tokens[itt]["token"] != ':':
                        errors.append("Expected seperator in function argument '{}': did you mean to call {}?".format(
                            arg_name, function_name))
                    incr_itt()
                    arg_type = tokens[itt]["token"]
                    incr_itt()
                    function_arguments.append({'name': arg_name, 'type': arg_type})
                incr_itt()
                function_return = tokens[itt]["token"]

                append_ast_scope(scope, {
                    'name': function_name,
                    'args': function_arguments,
                    'return': function_return,
                    'body': [] 
                })

                new_scope = scope + [function_name]
                itt = lex_scope(copy.copy(new_scope), itt)

                print("FUNCTION => ", function_name,
                    function_arguments, function_return, "itt:", itt)

            elif tokens[itt + 1]["token"] == "(":

                append_ast_scope(scope, {
                    'name': token["token"],
                    'args': [{} if self_function else {'type': 'none', 'val': ''}] + [] # TODO: Add recursive arguments parsing
                })                
                print("{}FUNCTION CALL".format("SELF " if self_function else ""), token["token"])
        elif token["type"] == 'bracket':
            # print("scope", scope, "bracket", token["token"], "sc", scope_checker)
            if token["token"] == entr[1]:
                scope_checker -= 1
                if scope_checker == 0:
                    break  # break out of the loop, scope end reached
            elif token["token"] == entr[0]:
                scope_checker += 1
            # print("newsc", scope_checker)
        elif token["type"] == 'sym':
            if token["token"] == '.':
                self_function = True
        if old_sf == self_function:
            self_function = False
    return itt


ti = -1


tokens = [{'token': '{', 'type': 'bracket'}] + tokens
tokens.append({'token': '}', 'type': 'bracket'})

print("\n".join(["Token: {}\t\t\tType: {}".format(
    x["token"], x["type"]) for x in tokens]))

lex_scope([], ti)
error_out()

print(ast)