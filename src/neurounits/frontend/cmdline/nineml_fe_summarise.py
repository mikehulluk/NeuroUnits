

import os





def cmdline_summarise(args):
    import mredoc
    print 'Summarise'

    
    from neurounits import NeuroUnitParser, MQ1
    from neurounits.nineml_fe.nineml_fe_utils import get_src_9ml_files
    
    src_files = get_src_9ml_files(args)

    # Read all the input files:
    library_manager = NeuroUnitParser.Parse9MLFiles(filenames=src_files)


    print args.what
    if not args.what:
        objs = list(library_manager.objects)
    else:
        objs = [ library_manager.get(name) for name in args.what ]

    summaries = []
    for o in objs:
        print 'Summarising:', repr(o)
        summaries.append( o.to_redoc() )


    summary_obj = mredoc.Section(
            'Summary output',
            *summaries

            )

    fname = os.path.expanduser( '~/Desktop/testout1.pdf')
    summary_obj.to_pdf(fname)
    os.system('xdg-open %s' % fname)


