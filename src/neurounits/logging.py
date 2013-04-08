




import logbook


log_neurounits = logbook.Logger('neurounits')



def MLine(s):
    if '\n' in s:
        return '\n%s' % s
    else:
        return s

