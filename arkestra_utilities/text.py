# a collection of small text utilities

# usage: concatenate(strings=["one", "two", ""], with_string=", ")
# returns: "one, two"
def concatenate(strings=[], with_string=""):
    return with_string.join(string for string in strings if string)
