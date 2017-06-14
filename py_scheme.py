import readline
from collections import ChainMap
from functools import reduce
from operator import mul, add, sub, eq

class SchemeSyntaxError(Exception):
    pass


def parse(expr):
    expr = expr.replace('(', ' ( ')
    expr = expr.replace(')', ' ) ')
    tokens = (tok for tok in expr.split())
    tokens = expr.split()
    ast_list = []
    while tokens:
        ast_list.append(parse_list(tokens))
    if tokens:
        raise SchemeSyntaxError('Unparsed tokens: {0}'.format(tokens))
    return ast_list


def parse_list(tokens):
    tok = tokens.pop(0)
    if tok != '(':
        raise SchemeSyntaxError("Expected '('")
    curr_list = []
    while tokens:
        tok = tokens[0]
        if tok == ')':
            tokens.pop(0)
            return curr_list
        if tok == '(':
            sub_list = parse_list(tokens)
            curr_list.append(sub_list)
        else:
            tok = tokens.pop(0)
            curr_list.append(parse_token(tok))
    raise SchemeSyntaxError("Expected ')'")


def parse_token(token):
    if token.startswith('"'):
        if not token.endswith('"'):
            raise SchemeSyntaxError('Expected "')
        return SchemeString(token)
    elif is_float(token):
        return SchemeFloat(token)
    elif is_int(token):
        return SchemeInt(token)
    else:
        return SchemeSymbol(token)


def is_float(token):
    try:
        f = float(token)
    except ValueError:
        return False
    else:
        return not f.is_integer()


def is_int(token):
    try:
        int(token)
        return True
    except ValueError:
        return False

# Define datatypes here
SchemeInt = int
SchemeFloat = float
SchemeBool = bool

# separate classes for symbols and strings
class SchemeSymbol(str):
    pass

class SchemeString(str):
    pass


class SchemeFunction(object):
    def __init__(self, params, body, environment):
        self.params = params
        self.body = body
        self.environment = environment


def scheme_apply(function, args):
    param_vals = dict(zip(function.params, args))
    new_environment = function.environment.new_child(param_vals)
    return scheme_eval(function.body, new_environment)


def scheme_eval(expr, environment):
    if isinstance(expr, (SchemeString, SchemeInt, SchemeFloat)):
        return expr

    elif isinstance(expr, SchemeSymbol):
        return environment[expr]

    elif isinstance(expr, list) and expr[0] == 'if':
        # (if pred x y)
        _, pred, x, y = expr
        if scheme_eval(pred, environment):
            return scheme_eval(x, environment)
        else:
            return scheme_eval(y, environment)

    elif isinstance(expr, list) and expr[0] == 'lambda':
        # (lambda (a1 a2...) body)
        _, params, body = expr
        return SchemeFunction(params, body, environment)

    elif isinstance(expr, list) and expr[0] == 'let':
        # (let ((v1 e1) (v2 e2) ...) body)
        _, binding_list, body = expr
        binding_map = {name: scheme_eval(_expr, environment) for (name, _expr) in binding_list}
        new_env = environment.new_child(binding_map)
        return scheme_eval(body, new_env)

    elif isinstance(expr, list) and expr[0] == 'set!':
        # (set! var expr)
        _, symbol, val_expr = expr
        environment[symbol] = scheme_eval(val_expr, environment)

    elif isinstance(expr, list) and expr[0] == 'define':
        # (define (sq x) (* x x))
        _, (name, *params), body = expr
        fn = SchemeFunction(params, body, environment)
        environment[name] = SchemeFunction(params, body, environment)

    else:
        # apply function
        fn, *args = map(lambda x: scheme_eval(x, environment), expr)
        if isinstance(fn, SchemeFunction):
            # apply in the interpeter
            return scheme_apply(fn, args)
        else:
            # apply in python
            return fn(*args)


def load_builtins():
    builtins = {
            '+': lambda *args: reduce(add, args),
            '*': lambda *args: reduce(mul, args),
            '-': lambda *args: reduce(sub, args),
            '=': lambda *args: reduce(eq, args)
            }
    return builtins


def run_repl(global_env):
    # Main interpreter loop
    input_count = 0
    while True:
        try:
            input_expr = input('In  [{}]: '.format(input_count))
            for ast in parse(input_expr):
                output = scheme_eval(ast, global_env)
            print('Out [{0}]: {1}'.format(input_count, output))
            input_count += 1
        except EOFError:
            s = input('Exit interpreter? ([y]/n): ')
            if 'n' not in s.lower():
                return
            else:
                continue


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Scheme interpreter')
    parser.add_argument('file_name', type=str, nargs='?',
            help='file to interpret', default=None)
    args = parser.parse_args()
    global_env = ChainMap(load_builtins())
    if args.file_name is not None:
        with open(args.file_name) as f:
            scheme_input = f.read()
            for ast in parse(scheme_input):
                scheme_eval(ast, global_env)
    run_repl(global_env)


