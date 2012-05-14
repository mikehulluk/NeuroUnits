

Overview
---------

NeuroUnits is a library for parsing units for modelling in neuroscience.
NeuroUnits specifies a grammar, allowing you to write quantities and
expressions involving units in a human readable fashion.  One of the major
use-cases of the library is the simplify the specification of
voltage-gated membrane mechanisms and synapse for multicompartmental model
neuron specification


Features Include:
  * Parsing of units and expressions
  * Use python-quanities (piquant to come...)
  * Output to LaTeX
  * Solving of ode's using scipy.integrate
  * Import from ChannelML (InDev)
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


The neurounits package performs all parsing through classmethods of 'NeuroUnitParser'.
For example, we can write code like this:


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
    NeuroUnitParser.EqnSet("""
       EQNSET syn_simple {
            g' = - g/g_tau
            i = gmax * (v-erev) * g
            
            gmax = 300pS
            erev = 0mV
            
            g_tau = 20ms
            <=> INPUT     v: mV       METADATA {"mf":{"role":"MEMBRANEVOLTAGE"} }
            <=> OUTPUT    i:(mA)      METADATA {"mf":{"role":"TRANSMEMBRANECURRENT"} }
            
            ==>> on_event() {
                g = g + 1.0 
                }
        } """)




Level 1: Simple Units and Quantities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Level 1 involves specification of units and quantities. It does not allow for 
expressions involving units, nor constants. For example:
  * ``mV`` 
  * ``10pA/cm2``
  * ``0.1e-2mm``
  * ``14 centimeter second``

are valid Level1 strings. 





Level 2: Expressions involving Quantities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In expressions involving quantities, all numerical constants in the expression
must appear within curly braces ``{...}`` . The reason is to prevent ambiguous
statements such as ``1 pA / F`` which could refer to either the *one
pico-amps-per-farad*, or *one pico-amp divided by Faraday's constant*. This
would instead by written as ``{1 pA/F}`` or ``{1pA}/F``


NeuroUnits supports function calls and constants as other programming
languages. One difference is keyword-arguments; function-calls must use
python-style keyword arguments, for example, ``myfunc(arg1=7, arg2=12)`` , except in the
case of single argument functions, in which case they are optional. Functions
can both take arguments and return values with dimensions.  NeuroUnits provides
a standard library defining some commonly used constants and functions.
(NeuroUnits handles namespaces similarly to python) 

The following are all examples of Level2 expressions. 


 * ``math.std.sinh( {1um}/{5um} )``
 * ``math.geom.area_of_sphere( r={1um}/{5um} ) * {5pS/cm2} * {50mV}``

.. todo::
    Better example using electronic distances.



Function calls OK
Can also reference functions and constants from the standard library, provided they are fully addressed.



Level 3: Equation-Sets and Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Level3 allows more complex of libraries and sets of ODE's. It is designed for
specifying channels and synapses for Neuroscience simualtions.  It draws on
concepts from existing neuroscience tools and libraries such as NineML() and
NEURON.

Libraries
^^^^^^^^^^

Function defs
Constants.

EqnSets
^^^^^^^^^^



Standard Libaray
~~~~~~~~~~~~~~~~


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

