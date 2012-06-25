
class SeqUtils(object):
    @classmethod
    def expect_single(cls, seq):
        assert len(seq) == 1
        return seq[0]
