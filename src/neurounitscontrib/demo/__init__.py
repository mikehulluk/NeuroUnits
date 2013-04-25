



class DemoPluginBase(object):
    def get_name(self, ):
        raise NotImplementedError()

    def run(self, args):
        raise NotImplementedError()




def do_demo(args):
    from straight.plugin import load
    plugin_classes = load('neurounitscontrib.demo.plugins', subclasses=DemoPluginBase)
    plugins = plugin_classes.produce()


    print 'Testing Plugins:'
    for plugin in plugins:
        print ' * Plugin:', plugin.get_name()

    # Run all:
    print 'Running:'
    for plugin in plugins:
        print ' * Plugin:', plugin.get_name()
        plugin.run(args)


    import pylab
    pylab.show()
    #handlers = plugins.produce()

