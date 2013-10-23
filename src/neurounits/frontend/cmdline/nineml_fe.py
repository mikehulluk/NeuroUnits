#! /usr/bin/python
# vim: set filetype=python :


import argparse





def handle_simulate(args):
    from neurounits.nineml_fe.nineml_fe_simulate import cmdline_simulate
    cmdline_simulate(args)

def handle_test(args):
    from neurounitscontrib.test import do_test
    do_test(args)

def handle_summarise(args):
    from neurounits.nineml_fe.nineml_fe_summarise import cmdline_summarise
    cmdline_summarise(args)



def handle_gui(args):
    from neurounits.gui.ninegui import run_gui
    run_gui()
def handle_demo(args):
    from neurounitscontrib.demo import do_demo
    do_demo(args)


def handle_coverage(args):
    from neurounits.frontend.cmdline.nineml_fe_coverage import do_coverage
    do_coverage(args)




# TODO:
def handle_visualise(args):
    print 'Visualising'
def handle_codegen(args):
    print 'Code-generating'
def handle_validating(args):
    print 'Code-validate'





def build_argparser():
    parser = argparse.ArgumentParser(description='Front-end to NineML.')

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-I','--include',type=str, action='append', help='Either a filename or a direcotry')
    parent_parser.add_argument('--safety-mode', action='store', choices=('cowboy','normal','safe'), default='normal')
    parent_parser.add_argument('--verbose', action='store_true', )

    subparsers = parser.add_subparsers()

    # Simulation: 
    # ===========
    simulate_subparser = subparsers.add_parser('simulate', parents=[parent_parser])
    simulate_subparser.set_defaults(func=handle_simulate)
    simulate_subparser.add_argument('component', type=str, )

   # Time steps:
    simulate_subparser.add_argument('--dt', type=str, required=True )
    simulate_subparser.add_argument('--endt', type=str, required=True )

    # Plotting Options:
    simulate_subparser.add_argument('--no-show-plot', action='store_false', default=True, dest='show_plot' )
    simulate_subparser.add_argument('--save_plot-file', action='append', type=str )
    simulate_subparser.add_argument('-p', '--plot-what', type=str, )
    simulate_subparser.add_argument('--phase-plot',  type=str, action='append' )

    
    # Save to CSV file:
    simulate_subparser.add_argument('--write-csv', type=str, dest='csv_filename', )
    simulate_subparser.add_argument('--csv-cols', type=str, dest='csv_columns', default='*')


    #

    # Visualise:
    # ==========
    visualise_subparser = subparsers.add_parser('visualise', parents=[parent_parser])
    visualise_subparser.set_defaults(func=handle_visualise)

    codegen_subparser = subparsers.add_parser('codegen', parents=[parent_parser])
    codegen_subparser.set_defaults(func=handle_codegen)

    validate_subparser = subparsers.add_parser('visualise', parents=[parent_parser])
    validate_subparser.set_defaults(func=handle_validating)


    # GUI interface:
    # ===============
    gui_subparser = subparsers.add_parser('gui', parents=[parent_parser])
    gui_subparser.set_defaults(func=handle_gui)


    # Demo interface
    demo_subparser = subparsers.add_parser('demo', parents=[parent_parser])
    demo_subparser.add_argument('what', nargs='*',  )
    demo_subparser.set_defaults(func=handle_demo)

    # test interface
    test_subparser = subparsers.add_parser('test', parents=[parent_parser])
    test_subparser.add_argument('what', nargs='*',  )
    test_subparser.set_defaults(func=handle_test)

    # Summarise
    summarise_subparser = subparsers.add_parser('summarise', parents=[parent_parser])
    summarise_subparser.add_argument('what', nargs='*',  )
    summarise_subparser.set_defaults(func=handle_summarise)

    coverage_subparser = subparsers.add_parser('coverage', parents=[parent_parser])
    coverage_subparser.set_defaults(func=handle_coverage)

    return parser


def main():
    parser = build_argparser()
    args = parser.parse_args()
    args.func(args)



if __name__ == '__main__':
    main()
