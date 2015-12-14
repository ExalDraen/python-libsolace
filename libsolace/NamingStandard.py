
def name(name, environment):
    try:
        return name % environment
    except TypeError, e:
        return name
