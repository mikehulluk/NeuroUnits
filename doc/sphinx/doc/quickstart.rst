

Quickstart
~~~~~~~~~~~

A neurounits component can be loaded from a string using:

.. code-block:: python 

    src_text = """define_component simple_exp {  

    <=> INPUT t:(ms)  
    a = [0] if [t<100ms] else [1.5]
    A' = (a-A)/{20ms}

        initial {
            A = 0.0
        }
    }
    """

    component = NeuroUnitParser.Parse9MLFile( src_text )




Plotting:
~~~~~~~~~

A graph of the AST can be plotted using:

.. code-block:: python 

    ActionerPlotNetworkX(component)
