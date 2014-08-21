
assert False

import os
import glob


def get_src_9ml_files(args):

    assert False, 'If not includes, then lets look up in the Location class!'

    # Load from all the include directories, but only add files once 
    # to prevent duplicate entries in the library_manager
    src_files = []
    for incl_path in args.include:
        assert os.path.exists(incl_path)
        # Add all the files in a directory:
        if os.path.isdir(incl_path):
            new_files = sorted([ os.path.abspath(fname)  for fname in glob.glob(incl_path+'/*.9ml') ] )
            for fname in new_files:
                if not fname in src_files:
                    src_files.append(fname)
        # Add an individual file:
        elif os.path.isfile(incl_path):
            if not incl_path in src_files:
                src_files.append(incl_path)

    return src_files
