

Overview
---------

NeuroUnits is a library for parsing units for modelling in neuroscience.
NeuroUnits specifies a grammar, allowing you to write quantities and
expressions involving units in a human readable fashion.

Stand-alone.

One of the major use-cases of the library is the simplify the specification of
voltage-gated membrane mechanisms and synapse for multicompartmental model
neuron specificaiton

.. code-block:: python

    Simple Examples...

Features Include:
  * Output to LaTeX
  * Solving of Eqnets using scipy.integrate
  * Import from NeuroML (InDev)
  * Creation of NMODL files

NeuroUnits can be standalone, although it is intended to be used within other software packages.

NeuroUnits Structure
---------------------

Different uses in modelling with require different levels of complexity in
handling of the units. For example, we might want to annotate a .csv file to
say that the first column is measured in mV and the second in 'mA/cm'. In a
more complex case, we might want to define the dynamics of a voltage-dependant
calcium calcium channel. Obviously simple grpahing library plotting the csv
file does not reuqire the same level of complexity as one to read the channel
definition.  NeuroUnits has 3 levels complexity:

    * *Level 1* **Simple Quantities and Units** 
    * *Level 2* **Expressions involving Quantities**
    * *Level 3* **Complex Equation Set and Library Defintions**

The Python library implements all these levels and acts as a reference. BNF
definition of the grammar is also given.


Parsing is done through the python class NeuroUnitParser:

.. code-block:: python

    from neurounits import NeuroUnitParser 

    # Level 1:
    NeuroUnitParser.Unit("mA/cm2")
    NeuroUnitParser.QuantitySimple("2 mS/cm2")

    # Level 2:
    NeuroUnitParser.QuantityExpression("2 mS/cm2")
    NeuroUnitParser.QuantityExpression("( {2 mS/cm2} * {5 mV} ) ")
    NeuroUnitParser.QuantityExpression("( {2 mS/cm2} * {5 mV} ) * std.geom.area_of_spehere(r=5um)")

    # Level 3:
    NeuroUnitParser.Library("2 mS/cm2")




Level 1: Simple Units and Quantities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
('mV','10pA/cm2', '0.1e-2mm')

Level 2: Expressions involving Quantities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Level 3: EquationSets and Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





More
-----


Installation
~~~~~~~~~~~~~

Grammer
~~~~~~~~

Standard Libraries
~~~~~~~~~~~~~~~~~~


Testing
~~~~~~~


Developer Notes:
-------------------
Units strings can be tricky to interpret; especially in Levels 2 & 3. In
defining NeuroUnits, I have tried to  describes a grammar that is unambigous,
is easy-to-read, allows for common use-cases and is as straight forward to
parse as possible.  Some compromise had to be made with the third; the parsing
algorithm is not as elegant as possible, but uses some simple preprocessing and
then 2 parsers which are defined as BNF grammars. (since 'regex' libraries and
'LR' parsers are available for most more languages, this shouldn't be an
issue).


..
    #V
    #Contents:
    #----------
    #
    #.. toctree::
    #   :maxdepth: 2
    #


..
    #Indices and tables
    #==================
    #
    #* :ref:`genindex`
    #* :ref:`modindex`
    #* :ref:`search`

