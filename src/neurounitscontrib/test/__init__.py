



class TestingPluginBase(object):
    def get_name(self, ):
        raise NotImplementedError()

    def run(self, args):
        raise NotImplementedError()




def do_test(args):
    from straight.plugin import load
    from straight.plugin.loaders import ClassLoader
    plugin_classes = load('neurounitscontrib.test.plugins', subclasses=TestingPluginBase)
    plugins = plugin_classes.produce()


    print 'Testing Plugins:'
    for plugin in plugins:
        print ' * Plugin:', plugin.get_name()

    # Run all:
    print 'Running:'
    for plugin in plugins:
        print ' * Plugin:', plugin.get_name()
        plugin.run(args)



    #handlers = plugins.produce()

