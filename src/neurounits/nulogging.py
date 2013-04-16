




#import logbook
#log_neurounits = logbook.Logger('neurounits')
import logging
print logging
log_neurounits = logging.getLogger('neurounits')



def MLine(s):
    if '\n' in s:
        return '\n%s' % s
    else:
        return s

