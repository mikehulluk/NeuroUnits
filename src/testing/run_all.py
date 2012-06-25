

from test_base import ReportGenerator

# Need to be imported, so they hook into the documentataion system:
import test_quantityexprs
import test_eqnsets

try:
    import test_neuroml_import
except ImportError:
    print "Can't test test_neuroml_import; files not installed"


ReportGenerator.report_all()

