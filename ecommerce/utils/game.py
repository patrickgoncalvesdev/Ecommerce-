import itertools


def get_permutations(guess, name: str):
    if name == "DEZENA":
        case = 2
    elif name == "CENTENA":
        case = 3
    else:
        case = 4
    return [''.join(p) for p in itertools.permutations(guess, case)]
