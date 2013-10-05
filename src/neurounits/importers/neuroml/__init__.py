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

from neurounits.importers.neuroml.neuroml_xml_data import _parse_channelml_file
from neurounits.importers.neuroml.neuroml_xml_to_eqnset import build_eqnset

from .errors import NeuroMLFileContainsNoChannels
from .errors import NeuroMLFileContainsMultipleChannels


class ChannelMLReader:

    @classmethod
    def LoadChlsRaw(self, filename):
        return _parse_channelml_file(filename)

    @classmethod
    def LoadChlRaw(self, filename):
        chl_infos = ChannelMLReader.LoadChlsRaw(filename).values()
        if len(chl_infos) == 0:
            raise NeuroMLFileContainsNoChannels()
        if len(chl_infos) > 1:
            raise NeuroMLFileContainsMultipleChannels()
        return chl_infos[0]

    @classmethod
    def BuildEqnset(cls, filename):
        chl_info = cls.LoadChlRaw(filename)
        (component, default_params) = build_eqnset(chl_info)
        return (component, chl_info, default_params)


