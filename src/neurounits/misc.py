
class SeqUtils(object):
    @classmethod
    def expect_single(cls, seq):
        assert len(seq) == 1
        return seq[0]

    @classmethod
    def filter_expect_single(cls, seq, filter_func):
        """ Filters a sequence according to the predicate filter_func, then 
        expects a single item to remain, which it returns.  If 0 or more than 
        1 objects are found, it raises an error.
        """
        filtered_seq = [s for s in seq if filter_func(s)]
        if len(filtered_seq) == 0:
            print seq
            raise ValueError('Unable to find any occurances')
        if len(filtered_seq) > 1:
            raise ValueError('Found too many occurances')
        return filtered_seq[0]
