




#import logbook
#log_neurounits = logbook.Logger('neurounits')

#print log_neurounits.__dict__

#assert False
import logging
print logging
log_neurounits = logging.getLogger('neurounits')

h = logging.StreamHandler()
log_neurounits.addHandler(h)

#print log_neurounits.__dict__
#assert False



def MLine(s):
    if '\n' in s:
        return '\n%s' % s
    else:
        return s

