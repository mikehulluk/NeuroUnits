#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------

from neurounits.units_misc import Chainmap
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from .base import ASTObject
from neurounits.ast.astobjects import Parameter, SuppliedValue, AssignedVariable
from neurounits.ast.astobjects_nineml import AnalogReducePort
from neurounits.ast.astobjects_nineml import Regime
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
from neurounits.io_types import IOType
from neurounits.units_misc import LookUpDict


import itertools


class Block(ASTObject):

    def __init__(self, name, library_manager, builder):
        super(Block, self).__init__()
        self.name = name
        self.library_manager = library_manager
        self._builder = builder

    @property
    def terminal_symbols(self):
        raise NotImplementedError()

    def get_terminal_obj(self, symbol):
        raise NotImplementedError()

    def has_terminal_obj(self, symbol):
        raise NotImplementedError()

    def to_redoc(self):
        from neurounits.writers import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)

    @property
    def short_name(self):
        return self.name.split('.')[-1]




class Library(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitLibrary(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata,name):
        super(Library,self).__init__(library_manager=library_manager, builder=builder, name=name)
        import neurounits.ast as ast


        # Top-level objects:
        self._function_defs = LookUpDict( builddata.funcdefs, accepted_obj_types=(ast.FunctionDef, ast.BuiltInFunction) )
        self._symbolicconstants = LookUpDict( builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant, ) )
        self._eqn_assignment = LookUpDict( builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,) )

    def get_terminal_obj(self, symbol):
        ##print self.functiondefs
        possible_objs = LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.functiondefs).get_objs_by(funcname=symbol)

        #print'Looking for:'
        #print self.functiondefs.get_objects_attibutes(attr='funcname')
        #print 'Symbol:', '"%s"' % symbol
        ###print 'Looking for:', symbol
        ###print possible_objs
        if not len(possible_objs) == 1:
            raise KeyError("Can't find terminal: %s" % symbol)

        return possible_objs[0]


    @property
    def functiondefs(self):
        return self._function_defs

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants, key=lambda a: a.symbol)

    @property
    def assignments(self):
        return list( iter(self._eqn_assignment) )

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)




class NineMLComponent(Block):






    # OK:
    @property
    def assignments(self):
        return list( iter(self._eqn_assignment) )

    @property
    def timederivatives(self):
        return list( iter(self._eqn_time_derivatives) )

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)

    @property
    def state_variables(self):
        return sorted(list(self._eqn_time_derivatives.get_objects_attibutes('lhs')), key=lambda a:a.symbol)

    @property
    def functiondefs(self):
        return iter(self._function_defs)

    @property
    def symbolicconstants(self):
        return sorted(list(self._symbolicconstants), key=lambda a:a.symbol)

    @property
    def parameters(self):
        return self._parameters

    @property
    def suppliedvalues(self):
        return self._supplied_values

    @property
    def analog_reduce_ports(self):
        return self._analog_reduce_ports_lut

    @property
    def terminal_symbols(self):
        possible_objs = itertools.chain(
                        self._parameters_lut,
                        self._supplied_lut,
                        self._analog_reduce_ports_lut,
                        self.assignedvalues,
                        self.state_variables,
                        self.symbolicconstants)

        possible_objs = list(possible_objs)
        for t in possible_objs:
            assert isinstance(t, ASTObject)
        return possible_objs




    def all_terminal_objs(self):
        possible_objs = self._parameters_lut.get_objs_by() + \
                        self._supplied_lut.get_objs_by() + \
                        self._analog_reduce_ports_lut.get_objs_by()+ \
                        LookUpDict(self.assignedvalues).get_objs_by()+ \
                        LookUpDict(self.state_variables).get_objs_by()+ \
                        LookUpDict(self.symbolicconstants).get_objs_by()

        return possible_objs



    def get_terminal_obj_or_port(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) + \
                        self._supplied_lut.get_objs_by(symbol=symbol) + \
                        self._analog_reduce_ports_lut.get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.state_variables).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol) + \
                        self.input_event_port_lut.get_objs_by(symbol=symbol) + \
                        self.output_event_port_lut.get_objs_by(symbol=symbol)



        if not len(possible_objs) == 1:
            all_syms = [ p.symbol for p in self.all_terminal_objs() ] + self.input_event_port_lut.get_objects_attibutes(attr='symbol')
            raise KeyError("Can't find terminal/EventPort: '%s' \n (Terminals/EntPorts found: %s)" % (symbol, ','.join(all_syms) ) )

        return possible_objs[0]



    def get_terminal_obj(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) + \
                        self._supplied_lut.get_objs_by(symbol=symbol) + \
                        self._analog_reduce_ports_lut.get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.state_variables).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)



        if not len(possible_objs) == 1:
            all_syms = [ p.symbol for p in self.all_terminal_objs()] 
            raise KeyError("Can't find terminal: '%s' \n (Terminals found: %s)" % (symbol, ','.join(sorted(all_syms)) ) )

        return possible_objs[0]


    # Recreate each time - this is not! efficient!!
    @property
    def _parameters_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[Parameter] )
    @property
    def _supplied_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[SuppliedValue] )
    @property
    def _analog_reduce_ports_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[AnalogReducePort] )
    @property
    def input_event_port_lut(self):
        import neurounits.ast as ast
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[ast.InEventPort] )
    @property
    def output_event_port_lut(self):
        import neurounits.ast as ast
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[ast.OutEventPort] )


    def has_terminal_obj(self, symbol):
        try:
            self.get_terminal_obj(symbol=symbol)
            return True
        except KeyError:
            return False
        except:
            raise



    # These should be tidied up:
    def getSymbolDependancicesDirect(self, sym, include_constants=False):

        assert sym in self.terminal_symbols

        if isinstance(sym, AssignedVariable):
            sym = self._eqn_assignment[sym]

        d = VisitorFindDirectSymbolDependance()

        return list(set(d.visit(sym)))

    def getSymbolDependancicesIndirect(self, sym,include_constants=False, include_ass_in_output=False):
        res_deps = []
        un_res_deps =  self.getSymbolDependancicesDirect(sym, include_constants=include_constants)

        while un_res_deps:
            p = un_res_deps.pop()

            if p is sym:
                continue
            if p in res_deps:
                continue

            p_deps = self.getSymbolDependancicesIndirect(p, include_constants=include_constants)
            un_res_deps.extend(p_deps)
            res_deps.append(p)

        if not include_ass_in_output:
            res_deps = [d for d in res_deps if not isinstance(d,AssignedVariable) ]
        return res_deps

    def getSymbolMetadata(self, sym):
        assert sym in self.terminal_symbols
        return self.get_terimal_symbol_obj(sym)._metadata._metadata


    def propagate_and_check_dimensions(self):
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self)


    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLComponent(self, **kwargs)


    def __init__(self,  library_manager, builder, builddata, name=None):
        super(NineMLComponent,self).__init__(library_manager=library_manager, builder=builder,  name=name)


        import neurounits.ast as ast

        # Top-level objects:
        self._function_defs = LookUpDict( builddata.funcdefs, accepted_obj_types=(ast.FunctionDef) )
        self._symbolicconstants = LookUpDict( builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant, ) )

        self._eqn_assignment = LookUpDict( builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,) )
        self._eqn_time_derivatives = LookUpDict( builddata.timederivatives, accepted_obj_types=(ast.EqnTimeDerivativeByRegime,) )


        self._transitions_triggers = LookUpDict( builddata.transitions_triggers )
        self._transitions_events = LookUpDict( builddata.transitions_events )
        self._rt_graphs = LookUpDict( builddata.rt_graphs)

        # This is a list of internal event port connections:
        self._event_port_connections = LookUpDict()

        from neurounits.ast import CompoundPortConnector
        # This is a list of the available connectors from this component
        self._compound_ports_connectors = LookUpDict( accepted_obj_types=(CompoundPortConnector,), unique_attrs=('symbol',))









    def add_compound_port(self, compoundportconnector ):
        self._compound_ports_connectors._add_item(compoundportconnector)



    def build_compound_port(self, local_name, porttype, direction, wire_mapping_txts):
        assert isinstance(local_name, basestring)
        assert isinstance(porttype, basestring)
        assert isinstance(direction, basestring)
        for src,dst in wire_mapping_txts:
            assert isinstance(src, basestring)
            assert isinstance(dst, basestring)


        import neurounits.ast as ast
        compound_port_def = self.library_manager.get(porttype)
        wire_mappings = []
        for wire_mapping_txt in wire_mapping_txts:
            wire_map = ast.CompoundPortConnectorWireMapping(
                            component_port = self.get_terminal_obj(wire_mapping_txt[0]),
                            compound_port = compound_port_def.get_wire(wire_mapping_txt[1]),
                            )
            wire_mappings.append(wire_map)

        conn = ast.CompoundPortConnector(symbol=local_name, compound_port_def = compound_port_def, wire_mappings=wire_mappings, direction=direction)
        self.add_compound_port(conn)






    def add_event_port_connection(self, conn):
        assert conn.dst_port in self.input_event_port_lut
        assert conn.src_port in self.output_event_port_lut
        self._event_port_connections._add_item(conn)


    def __repr__(self):
        return '<NineML Component: %s [Supports interfaces: %s ]>' % (self.name, ','.join([ "'%s'" % conn.compound_port_def.name for conn in  self._compound_ports_connectors]))

    @property
    def rt_graphs(self):
        return self._rt_graphs

    @property
    def transitions(self):
        return itertools.chain( self._transitions_triggers, self._transitions_events)

    def transitions_from_regime(self, regime):
        assert isinstance(regime,Regime)
        return [tr for tr in self.transitions if tr.src_regime == regime]

    def summarise(self):
        print
        print 'NineML Component: %s' % self.name
        print '  Paramters: [%s]' %', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self._parameters_lut)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.state_variables)

        print '  Inputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self._supplied_lut)

        print '  Outputs: [%s]'% ', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.assignedvalues)
        print '  ReducePorts: [%s] '% ', '.join("'%s (%s)'" % (p.symbol, p.get_dimension()) for p in self.analog_reduce_ports)

        print

        print

        print '  Time Derivatives:'

        for td in self.timederivatives:
            print '    %s -> ' % td.lhs.symbol
            for (regime, rhs) in td.rhs_map.rhs_map.items():
                print '      [%s] -> %s' % (regime.ns_string(), rhs)

        print '  Assignments:'
        for td in self.assignments:
            print '    %s -> ' % td.lhs.symbol
            for (regime, rhs) in td.rhs_map.rhs_map.items():
                print '      [In Regime:%s] -> %s' % (regime.ns_string(), rhs)

        print '  RT Graphs'
        for rt in self.rt_graphs:
            print '     Graph:', rt
            for regime in rt.regimes:
                print '       Regime:', regime

                for tr in self.transitions_from_regime(regime):
                    print '          Transition:', tr



    def all_ast_nodes(self):
        c = EqnsetVisitorNodeCollector()
        c.visit(self)
        return itertools.chain( *c.nodes.values() )

    def clone(self, ):


        #import gc
        #import collections
        #from neurounits.librarymanager import LibraryManager
        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        from neurounits.visitors.common.ast_node_connections import ASTAllConnections



        class ReplaceNodeHack(ReplaceNode):
            def replace_or_visit(self, o):
                if o == self.srcObj:
                    #print '    Replacing', self.srcObj, ' -> ', self.dstObj
                    return self.dstObj
                else:
                    return o

        #print 'Refs to library manager:'
        #lib_man_refs =  gc.get_referrers( self.library_manager)
        #for ref in lib_man_refs:
        #    print type(ref)
        #    print ref
        #print 'Len', len(lib_man_refs)

        #assert False
        #gc.collect()
        #prev_objs = list( gc.get_objects() )
        #type_count_before  = collections.Counter( [type(obj) for obj in prev_objs])

        #print type_count_before


        from neurounits.visitors.common.ast_cloning import ASTClone
        from collections import defaultdict

        import neurounits.ast as ast


        # CONCEPTUALLY THIS IS VERY SIMPLE< BUT THE CODE
        # IS A HORRIBLE HACK!

        no_remap = (ast.CompoundPortDef, ast.CompoundPortDefWireContinuous, ast.CompoundPortDefWireEvent, ast.BuiltInFunction, ast.FunctionDefParameter)
        # First, lets clone each and every node:
        #print
        #print 'Remapping nodes:'
        old_nodes = list(set(list( EqnsetVisitorNodeCollector(self).all() )))
        old_to_new_dict = {}
        for old_node in old_nodes:

            if not isinstance(old_node, no_remap):
                new_node = ASTClone().visit(old_node)
            else:
                new_node = old_node
            

            #print old_node, '-->', new_node
            assert type(old_node) == type(new_node)
            old_to_new_dict[old_node] = new_node

        # Clone self:
        old_to_new_dict[self] = ASTClone().visit(self)

        # Check that all the nodes hav been replaced:
        overlap = ( set(old_to_new_dict.keys()) & set(old_to_new_dict.values() )  )
        for o in overlap:
            assert isinstance(o, no_remap)

        # Now, lets visit each of the new nodes, and replace (old->new) on it:
        #print 
        #print 'Replacing Nodes:'
        for new_node in old_to_new_dict.values():
            #print 'Replacing nodes on:', new_node

            for old_repl, new_repl in old_to_new_dict.items():
                if new_repl == new_node:
                    continue
                #print ' -- Replacing:',old_repl, new_repl

                if isinstance( old_repl, no_remap):
                    continue

                replacer = ReplaceNodeHack(srcObj=old_repl, dstObj=new_repl)
                new_node.accept_visitor(replacer)


        # ok, so the clone should now be all clear:
        new_obj = old_to_new_dict[self]

        new_nodes = list( EqnsetVisitorNodeCollector(new_obj).all()  )


        # Who points to what!?
        connections_map_obj_to_conns = {}
        connections_map_conns_to_objs = defaultdict(list)
        for node in new_nodes:
            #print 'Node', node
            #print
            conns = list( node.accept_visitor( ASTAllConnections() ) )
            #print node, len(conns)
            connections_map_obj_to_conns[node] = conns

            for c in conns:
                connections_map_conns_to_objs[c].append(node)





        shared_nodes = set(new_nodes) & set(old_nodes)
        shared_nodes_invalid = [sn for sn in shared_nodes if not isinstance(sn, no_remap)]
        #print 
        if len(shared_nodes_invalid) != 0:
            print 'Shared Nodes:'
            print shared_nodes_invalid
            for s in shared_nodes_invalid:
                print  ' ', s, s in old_to_new_dict
                print  '  Referenced by:'
                for c in connections_map_conns_to_objs[s]:
                    print '    *', c 
                print
            assert len(shared_nodes_invalid) == 0
        #assert len(new_nodes) == len(old_nodes)

        return new_obj







        #assert False





        # Nasty Hack - serialise and unserialse to clone the object

        import pickle
        import cStringIO
        c = cStringIO.StringIO()


        old_lib_man = self.library_manager
        self.library_manager = None
        pickle.dump(self, c)
        new = pickle.load(cStringIO.StringIO(c.getvalue()))
        new.library_manager =  old_lib_man





        ## When we clone, however, we shouldn't also clone CompundPortDefintions amd sub components, since otherwise we
        ## can't maintain mapping between objects:
        #for compound_port_conn_orig in self._compound_ports_connectors:
        #    assert False

        #    # Change the wire mappings,
        #    # TODO!


        #    # Change the compund-port-definition:
        #    from neurounits.visitors.common.ast_replace_node import ReplaceNode
        #    compound_port_conn_cloned = new._compound_ports_connectors.get_single_obj_by(name=compound_port_conn_orig.name)
        #    comp_port_src = compound_port_conn_cloned.compound_port_def
        #    comp_port_dst = compound_port_conn_orig.compound_port_def
        #    ReplaceNode.replace_and_check(srcObj=comp_port_src, dstObj = comp_port_dst, root=self)
        #



        #gc.collect()
        #next_objs = list( gc.get_objects() )
        #type_count_after  = collections.Counter( [type(obj) for obj in next_objs])
        #count_change = type_count_after - type_count_before
        #print 'Changes:'
        ##print count_change
        #for obj, count in sorted(count_change.items(), key=lambda s:s[1]):
        #    print count, obj

        ##new_objs = [ o for o in next_objs if not o in prev_objs]

        #print 'Pointing at the new library manager:'
        #lib_mans = [o for o in next_objs if isinstance(o, (LibraryManager))]
        #print lib_mans


        #refs = gc.get_referrers(*lib_mans)
        #print refs

        #assert False




        return new






class NineMLModule(object):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLModule(self, **kwargs)

    def __init__(self, **kwargs):
        pass


