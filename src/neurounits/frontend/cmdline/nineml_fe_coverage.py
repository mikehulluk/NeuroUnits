

import coverage
import os
import shutil

def do_coverage(args):
    from neurounitscontrib.test import do_test
    from neurounitscontrib.demo import do_demo
    print 'Doing Coverage'

    cov = coverage.coverage( include='*neurounits*')
    cov.start()


    do_test(None)
    do_demo(None)


    cov.stop()
    cov.save()
    cov_dir = os.path.expanduser('~/.neurounits/.coverage/')

    if os.path.exists(cov_dir):
        shutil.rmtree(cov_dir)

    if not os.path.exists(cov_dir):
        os.makedirs(cov_dir)
    cov.html_report(directory=cov_dir)

    print 'Coverage run finished, output in: ', cov_dir
