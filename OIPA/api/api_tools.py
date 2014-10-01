__author__ = 'robin'

def comma_separated_parameter_to_list(csp):
    '''returns the csp as a list with all leading and trailing whitespace removed'''
    if csp is None:
        return None
    return [x.strip() for x in csp.split(',')]