#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

import neurounits
import datetime


class MyFrame(wx.Frame):

    def EvtSrcText(self, *args, **kwargs):
        print 'Change to src text'
        pass

    def default_text(self):
        self.src_text.WriteText('''
        EQNSET eqn1{
            a = 4
            b = 6
            g(x) = x+2
            f(y) = g(y) /3
        }
        EQNSET eqn2{
            a = 4
            b = 6
        }
        EQNSET eqn3{
            a = 4
            b = 6
        }
        ''')

    def update_from_src(self, *args, **kwargs):
        src_text = self.src_text.GetValue()
        print 'Updateing', src_text

        library_manager = neurounits.NeuroUnitParser.File(src_text)
        #print ast

        from neurounits.writers import StringWriterVisitor
        strs = [StringWriterVisitor().visit(eqn) for eqn in library_manager.eqnsets ]

        ast_output = '' + str(datetime.datetime.now()) + '\n'
        #ast_output += 'Name:' + ast.name if ast.name else '<None>' + '\n'

        #ast_output += 'EqnSets + \n'
        ast_output += '\n\n'.join(  strs ) #[ '* ' + eqn.name for eqn in ast.eqnsets] )
        
        self.details_box.Clear()
        self.details_box.WriteText(ast_output) #(panel1, size=(20,20), style=wx.TE_MULTILINE)
        



    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(650, 600))

        splitter = wx.SplitterWindow(self, -1)


        # Setup Panel 1:
        panel1 = wx.Panel(splitter, -1)
        panel1.SetBackgroundColour(wx.LIGHT_GREY)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # The src_text box:
        self.src_text = wx.TextCtrl(panel1, size=(20,20), style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.EvtSrcText, self.src_text)
        vbox.Add(self.src_text, 1, wx.EXPAND | wx.ALL, 5)

        self.update_button =wx.Button(panel1, size=(-1,20), label="Update")
        self.Bind(wx.EVT_BUTTON, self.update_from_src, self.update_button)
        vbox.Add(self.update_button, 0,  wx.EXPAND | wx.ALL, 5)

        # The output details box:
        self.details_box = wx.TextCtrl(panel1, size=(20,20), style=wx.TE_MULTILINE)
        self.details_box.SetBackgroundColour(wx.GREEN)
        vbox.Add(self.details_box, 1, wx.EXPAND | wx.ALL, 5)




        panel1.SetSizer(vbox)



        # Setup Panel 2:
        panel2 = wx.Panel(splitter, -1)
        wx.StaticText(panel2, -1, "Whether you think that you can, or that you can't, you are usually right." "\n\n Henry Ford", (100,100), style=wx.ALIGN_CENTRE)
        panel2.SetBackgroundColour(wx.WHITE)



        splitter.SplitVertically(panel1, panel2)
        self.Centre()



        self.default_text()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'splitterwindow.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()


import sys
sys.exit(0)





class ExamplePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)


        #panel = wx.Panel(self)
        self.SetBackgroundColour('#4f5049')
        vbox = wx.BoxSizer(wx.HORIZONTAL)

        splitter = wx.SplitterWindow(self, -1)

        # Create the left panel:
        leftPan = wx.Panel(self)
        leftPan.SetBackgroundColour('#ededed')
        vbox.Add(leftPan, 1, wx.EXPAND | wx.ALL, 5)


        # Create the middle panel:
        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#00eded')
        vbox.Add(midPan, 1, wx.EXPAND | wx.ALL, 20)



        self.SetSizer(vbox)

        return

        # create some sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.quote = wx.StaticText(self, label="Your quote: ")
        grid.Add(self.quote, pos=(0,0))

        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        #self.logger = wx.TextCtrl(self, size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logger = wx.TextCtrl(self, size=(200,300), style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.EvtBigText, self.logger)

        # A button
        self.button =wx.Button(self, label="Save")
        self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

        # the edit control - one line version.
        self.lblname = wx.StaticText(self, label="Your name :")
        grid.Add(self.lblname, pos=(1,0))
        self.editname = wx.TextCtrl(self, value="Enter here your name", size=(140,-1))
        grid.Add(self.editname, pos=(1,1))
        self.Bind(wx.EVT_TEXT, self.EvtText, self.editname)
        self.Bind(wx.EVT_CHAR, self.EvtChar, self.editname)

        # the combobox Control
        self.sampleList = ['friends', 'advertising', 'web search', 'Yellow Pages']
        self.lblhear = wx.StaticText(self, label="How did you hear from us ?")
        grid.Add(self.lblhear, pos=(3,0))
        self.edithear = wx.ComboBox(self, size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        grid.Add(self.edithear, pos=(3,1))
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.edithear)
        self.Bind(wx.EVT_TEXT, self.EvtText,self.edithear)

        # add a spacer to the sizer
        grid.Add((10, 40), pos=(2,0))

        # Checkbox
        self.insure = wx.CheckBox(self, label="Do you want Insured Shipment ?")
        grid.Add(self.insure, pos=(4,0), span=(1,2), flag=wx.BOTTOM, border=5)
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.insure)

        # Radio Boxes
        radioList = ['blue', 'red', 'yellow', 'orange', 'green', 'purple', 'navy blue', 'black', 'gray']
        rb = wx.RadioBox(self, label="What color would you like ?", pos=(20, 210), choices=radioList,  majorDimension=3,
                         style=wx.RA_SPECIFY_COLS)
        grid.Add(rb, pos=(5,0), span=(1,2))
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)

        hSizer.Add(grid, 0, wx.ALL, 5)
        hSizer.Add(self.logger)
        mainSizer.Add(hSizer, 0, wx.ALL, 5)
        mainSizer.Add(self.button, 0, wx.CENTER)
        self.SetSizerAndFit(mainSizer)

    def OnClick(self,*args,**kwargs):
        pass
    def EvtText(self,*args, **kwargs):
        pass
    def EvtChar(self,*args, **kwargs):
        pass
    def EvtComboBox(self,*args, **kwargs):
        pass
    def EvtCheckBox(self,*args, **kwargs):
        pass
    def EvtRadioBox(self,*args, **kwargs):
        pass
    def EvtBigText(self,*args, **kwargs):
        pass


app = wx.App(False)
frame = wx.Frame(None)
panel = ExamplePanel(frame)
frame.Show()
app.MainLoop()
