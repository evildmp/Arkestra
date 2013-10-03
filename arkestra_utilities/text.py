# a collection of small text utilities


def concatenate(strings=[], with_string=""):
    return with_string.join(string for string in strings if string)
