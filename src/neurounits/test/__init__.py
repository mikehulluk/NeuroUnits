



class TestingPluginBase():
    pass



def do_test(args):
    from straight.plugin import load
    plugins = load('neurounits.test_plugins', subclasses=TestingPluginBase)
    print plugins


    #handlers = plugins.produce()
    
