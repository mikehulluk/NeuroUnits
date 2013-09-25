

import logging
#print logging
log_neurounits = logging.getLogger('neurounits')

h = logging.StreamHandler()
log_neurounits.addHandler(h)



def MLine(s):
    if '\n' in s:
        return '\n%s' % s
    else:
        return s

