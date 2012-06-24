

import os
import glob

from os.path import join as Join


def EnsureDir(l):
    d = os.path.dirname(l)
    if not os.path.exists(d):
        os.makedirs(d)
    return d

class TestLocations(object):

    @classmethod
    def getPackageRoot(cls):
        return "/home/michael/hw_to_come//libs/NeuroUnits"


    @classmethod
    def getEqnSetFiles(cls):
        loc = Join(cls.getPackageRoot(), "src/test_data/eqnsets/" )
        print loc
        files = glob.glob( loc+"/*.eqn" )
        return files


    @classmethod
    def getTestOutputDir(cls,):

        return EnsureDir("/tmp/neurounits_test/")
