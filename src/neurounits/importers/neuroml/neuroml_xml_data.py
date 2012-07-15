#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
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
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#-------------------------------------------------------------------------------

import re
import xml.etree.cElementTree as etree

from .errors import NeuroUnitsImportNeuroMLNotImplementedException


def ignore(*args,**kwargs):
    pass
def not_supported(*args,**kwargs):
    raise NeuroUnitsImportNeuroMLNotImplementedException()


ns_regex = re.compile(r'{(?P<NS>.*)}(?P<TAG>.*)')
def strip_namespace(tag):
    m = ns_regex.match(tag)
    return m.groupdict()['TAG']

def recursive_strip_namespaces(xmlNode):
    xmlNode.tag = strip_namespace(xmlNode.tag)
    for child in xmlNode.getchildren():
        recursive_strip_namespaces(child)


def dispatch_subnodes( node, dispatch_map):

    for n in node.getchildren():
        if n.tag in dispatch_map:
            dispatch_map[n.tag](n)
        else:
            print ' -- ', n
            assert False















class ChannelML_Q10Setting(object):
    def __init__(self, gate, q10factor, experimental_temp, mode):
        self.gate = gate
        self.q10factor = q10factor
        self.experimental_temp = experimental_temp
        self.mode = mode




class ChannelML_GateEqn(object):
    def __init__(self, sn):
        self.name = sn.attrib['name']
        self.frm = sn.attrib['from']
        self.to = sn.attrib['to']

        self.expr_form  = sn.attrib['expr_form']
        self.rate = sn.attrib.get('rate',None)
        self.scale = sn.attrib.get('scale',None)
        self.midpoint = sn.attrib.get('midpoint',None)
        self.expr  = sn.attrib.get('expr',None)



    def getSubString(self, what):
        #LUT = {
        #       'rate':    lambda : "{%f mV-1}" % float( self.rate) ,
        #       'scale':   lambda : "{%f s-1}" % float( self.scale),
        #       'midpoint':lambda : "{%f mV}" % float( self.midpoint),
        #       }

        LUT = {
               'rate':    lambda : "{%f}" % float( self.rate) ,
               'scale':   lambda : "{%f}" % float( self.scale),
               'midpoint':lambda : "{%f}" % float( self.midpoint),
               }

        return LUT[what]()

    def getEqn(self):


        if self.expr_form == 'generic':


            # A hack, so we don't need to deal with the tertiary operator:
            if "?" in self.expr:
                assert self.expr.count("?") == 1

                A,BC = self.expr.split("?")
                B,C = BC.split(":")

                self.expr = "[%s]if[%s]else[%s]"%(B.strip(),A.strip().replace(" ",""),C.strip())

            return self.expr


        scale = "{%f}"% float( self.scale ) #self.getSubString('scale')
        rate = self.getSubString('rate')
        midpoint = self.getSubString('midpoint')

        if self.expr_form == 'sigmoid':
            return ' (1 * %s) / ( 1.0 + exp ( (V - %s)/%s  ) ) '%( rate,midpoint, scale )

        elif self.expr_form == 'exponential':
            return ' %s * exp ( 1.0 * (V- %s)/%s ) '%( rate, midpoint,scale)

        elif self.expr_form == 'exp_linear':
            return '%s * ( (V - %s) / %s) / (1 - exp( -1.0 * ((V - %s)/%s) )) ' % (rate, midpoint, scale, midpoint, scale,)

        else:
            assert False

class ChannelML_Transition(ChannelML_GateEqn):
    pass
class ChannelML_TimeCourse(ChannelML_GateEqn):
    pass
class ChannelML_SteadyState(ChannelML_GateEqn):
    pass



class ChannelML_Gate(object):

    def load_closed_state(self, sn):
        self.closedstates.append(sn.attrib['id'] )
    def load_open_state(self, sn):
        self.openstates.append(sn.attrib['id'] )
    def load_time_course(self, sn):
        self.time_courses.append( ChannelML_TimeCourse(sn) )
    def load_steady_state(self, sn):
        self.steady_states.append( ChannelML_SteadyState(sn) )
    def load_transition(self, sn):
        self.transitions.append( ChannelML_Transition(sn) )

    def load_initialisation(self, sn):
        assert not self.initialisation
        self.initialisation = sn.attrib['value']






    def __init__(self, node):

        self.openstates = []
        self.closedstates = []
        self.time_courses = []
        self.steady_states = []
        self.transitions = []

        self.initialisation = None

        self.name = node.attrib['name']
        self.instances = int( node.attrib['instances'] )

        tag_handlers = {
                        'closed_state': self.load_closed_state,
                        'open_state':   self.load_open_state,
                        'time_course':  self.load_time_course,
                        'steady_state': self.load_steady_state,

                        'transition' :  self.load_transition,
                        'initialisation': self.load_initialisation,
                      }

        # Load the Subnodes:
        dispatch_subnodes(node, tag_handlers)



        assert self.openstates
        assert self.closedstates

        #print len(self.openstates)
        #print len(self.closedstates)



class ChannelMLInfo(object):


    def load_Q10Settings(self, node):
        if 'fixed_q10' in node.attrib:
            setting = ChannelML_Q10Setting( gate = node.get('gate',None),
                                            q10factor = node.attrib['fixed_q10'],
                                            experimental_temp = node.attrib['experimental_temp'],
                                            mode = 'fixed_q10' )
            self.q10settings.append(setting)
        else:
            assert 'q10_factor' in node.attrib
            setting = ChannelML_Q10Setting( gate = node.get('gate',None),
                                            q10factor = node.attrib['q10_factor'],
                                            experimental_temp = node.attrib['experimental_temp'],
                                            mode = 'q10_factor' )
            self.q10settings.append(setting)




    def load_parameters(self, node):
        for parameter in node.iter('parameter'):
            self.parameters[ parameter.get('name') ] = parameter.get('value')




    def load_conc_factor(self,node):
        self.unsupported_tags = "Unsupported NeuroML tag: 'conc_factor'"

    def load_conc_dependence(self,node):
        self.unsupported_tags = "Unsupported NeuroML tag: 'conc_dependence' "

        self.iv_conc_dep_name = node.attrib['name']
        self.iv_conc_dep_ion = node.attrib['ion']
        self.iv_conc_dep_charge = int( node.attrib['charge'] )
        self.iv_conc_dep_variable_name = node.attrib['variable_name']
        self.iv_conc_dep_min_conc = node.attrib['min_conc']
        self.iv_conc_dep_max_conc = node.attrib['max_conc']

    def load_gate(self, node):
        self.gates.append( ChannelML_Gate(node) )

    def load_offset(self, n):
        self.offset = float( n.attrib['value'] )



    def load_current_voltage_relation(self,node):
        self.iv_cond_law = node.attrib.get( 'cond_law', None)
        self.iv_ion = node.attrib.get( 'ion',None)
        self.iv_default_gmax = node.attrib.get( 'default_gmax', None )
        self.iv_default_erev = node.attrib.get( 'default_erev', None )
        self.iv_charge = node.attrib.get( 'charge', None )
        self.iv_fixed_erev = node.attrib.get( 'fixed_erev', None )



        tag_handlers = {
                           'q10_settings':self.load_Q10Settings,
                           'offset': self.load_offset,
                           'conc_dependence': self.load_conc_dependence,
                           'ohmic': ignore,
                           'conc_factor': self.load_conc_factor,
                           'gate': self.load_gate
                      }

        dispatch_subnodes(node, tag_handlers)



    def __init__(self, chl_type_node, units):
        print 'Loading Channel Type:', chl_type_node.get('name')

        self.name = chl_type_node.get('name')
        self.parameters = {}
        self.q10settings = []
        self.offset = 0.
        self.gates = []
        self.units = units

        #self.iv_conc_dep_name = None
        #self.iv_conc_dep_ion = None

        self.unsupported_tags = None

        #Sanity Checks:
        assert chl_type_node.get('density','yes') == 'yes'

        tag_handlers = {
                          'status': ignore,
                          'notes': ignore,
                          'authorList':ignore,
                          'publication':ignore,
                          'neuronDBref': ignore,
                          'modelDBref': ignore,
                          'impl_prefs': ignore,
                          'current_voltage_relation': self.load_current_voltage_relation,
                          'parameters': self.load_parameters
                      }

        dispatch_subnodes(chl_type_node, tag_handlers)












def _parse_channelml_file(xmlfile):


    tree = etree.parse(xmlfile)
    root = tree.getroot()
    recursive_strip_namespaces(root)

    if root.tag != 'channelml':
        return {}



    #print xmlfile
    chls = {}
    for ch in root.iter('channel_type'):
        chl = ChannelMLInfo(ch, units=root.attrib['units'])
        chls[ chl.name + ' (%s)'%xmlfile ] = chl

    return chls



