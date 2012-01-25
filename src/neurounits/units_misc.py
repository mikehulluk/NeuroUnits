def safe_dict_merge(*args):
    out_dct = {}
    for dct in args:
        for k,v in dct.iteritems():
            assert not k in out_dct
            out_dct[k] = v
    return out_dct
