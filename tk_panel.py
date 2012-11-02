#!/usr/bin/env python
version = '1.0'
# python joyface.py

from Tkinter import *
from tkFileDialog import *
from math import *
from SimpleDialog import *
from ConfigParser import *
from decimal import *
import tkMessageBox
from subprocess import Popen, PIPE, STDOUT
import os

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master, width=700, height=400, bd=1)
        self.grid()
        self.InputFile = 'joyface.ini'
        self.LoadIniData()
        self.createMenu()
        self.createWidgets()

    def createMenu(self):
        #Create the Menu base
        self.menu = Menu(self)
        #Add the Menu
        self.master.config(menu=self.menu)
        #Create our File menu
        self.FileMenu = Menu(self.menu)
        #Add our Menu to the Base Menu
        self.menu.add_cascade(label='File', menu=self.FileMenu)
        #Add items to the menu
        self.FileMenu.add_command(label='Quit', command=self.quit)
        
        self.EditMenu = Menu(self.menu)
        self.menu.add_cascade(label='Edit', menu=self.EditMenu)
        self.EditMenu.add_command(label='Copy', command=self.CopyClpBd)
        self.EditMenu.add_command(label='Select All', command=self.SelectAllText)
        self.EditMenu.add_command(label='Delete All', command=self.ClearTextBox)
        self.EditMenu.add_separator()
        self.EditMenu.add_command(label='NC Directory', command=self.NcFileDirectory)
        self.EditMenu.add_command(label='tmp Directory', command=self.TMPFileDirectory)
        
        self.HelpMenu = Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.HelpMenu)
        self.HelpMenu.add_command(label='Help Info', command=self.HelpInfo)
        self.HelpMenu.add_command(label='About', command=self.HelpAbout)

    def createWidgets(self):
        
        self.sp1 = Label(self)
        self.sp1.grid(row=0)
        
        self.st00 = Label(self, text='USB port:')
        self.st00.grid(row=0, column=0, sticky=E)
        self.portVar = StringVar()
        self.port = Entry(self, width=20, textvariable=self.portVar)
        self.port.grid(row=0, column=1, columnspan=4, sticky=W)
        self.port.focus_set()
        self.port.insert(0,self.cp.get('Variables','usbport'))

        self.st01 = Label(self, text='recording file')
        self.st01.grid(row=1, column=0, sticky=E)
        self.fileNameVar = StringVar()
        self.fileName = Entry(self, width=20, textvariable=self.fileNameVar)
        self.fileName.grid(row=1, column=1, columnspan=4, sticky=W)
        self.fileName.focus_set()
        self.fileName.insert(0,self.cp.get('Variables','recording_file'))

        self.st02 = Label(self, text='s1 xpos')
        self.st02.grid(row=2, column=0, sticky=E)
        self.servo1_xVar = StringVar()
        self.servo1_x = Entry(self, width=3, textvariable=self.servo1_xVar)
        self.servo1_x.grid(row=2, column=1, sticky=W)
        
        self.st03 = Label(self, text='s2 ypos')
        self.st03.grid(row=2, column=2, sticky=E)
        self.servo1_yVar = StringVar()
        self.servo1_y = Entry(self, width=3, textvariable=self.servo1_yVar)
        self.servo1_y.grid(row=2, column=3, sticky=W)
        
        self.st04 = Label(self, text='s3 xpos')
        self.st04.grid(row=2, column=4, sticky=E)
        self.servo2_xVar = StringVar()
        self.servo2_x = Entry(self, width=3, textvariable=self.servo2_xVar)
        self.servo2_x.grid(row=2, column=5, sticky=W)
        
        self.st05 = Label(self, text='s4 ypos')
        self.st05.grid(row=2, column=6, sticky=E)
        self.servo2_yVar = StringVar()
        self.servo2_y = Entry(self, width=3, textvariable=self.servo2_yVar)
        self.servo2_y.grid(row=2, column=7, sticky=W)
        
        self.st06 = Label(self, text='s1 min')
        self.st06.grid(row=3, column=0, sticky=E)
        self.s1_minVar = StringVar()
        self.s1_min = Entry(self, width=3, textvariable=self.s1_minVar)
        self.s1_min.grid(row=3, column=1, sticky=W)
        self.s1_min.insert(0,self.cp.get('Variables','s1_min'))
        
        self.st07 = Label(self, text='s1 max')
        self.st07.grid(row=3, column=2, sticky=E)
        self.s1_maxVar = StringVar()
        self.s1_max = Entry(self, width=3, textvariable=self.s1_maxVar)
        self.s1_max.grid(row=3, column=3, sticky=W)
        self.s1_max.insert(0,self.cp.get('Variables','s1_max'))
        
        self.st08 = Label(self, text='s2 min')
        self.st08.grid(row=3, column=4, sticky=E)
        self.s2_minVar = StringVar()
        self.s2_min = Entry(self, width=3, textvariable=self.s1_minVar)
        self.s2_min.grid(row=3, column=5, sticky=W)
        self.s2_min.insert(0,self.cp.get('Variables','s1_min'))
        
        self.st09 = Label(self, text='s2 max')
        self.st09.grid(row=3, column=6, sticky=E)
        self.s2_maxVar = StringVar()
        self.s2_max = Entry(self, width=3, textvariable=self.s2_maxVar)
        self.s2_max.grid(row=3, column=7, sticky=W)
        self.s2_max.insert(0,self.cp.get('Variables','s2_max'))
        
        self.st10 = Label(self, text='s3 min')
        self.st10.grid(row=4, column=0, sticky=E)
        self.s3_minVar = StringVar()
        self.s3_min = Entry(self, width=3, textvariable=self.s3_minVar)
        self.s3_min.grid(row=4, column=1, sticky=W)
        self.s3_min.insert(0,self.cp.get('Variables','s3_min'))
        
        self.st11 = Label(self, text='s3 max')
        self.st11.grid(row=4, column=2, sticky=E)
        self.s3_maxVar = StringVar()
        self.s3_max = Entry(self, width=3, textvariable=self.s3_maxVar)
        self.s3_max.grid(row=4, column=3, sticky=W)
        self.s3_max.insert(0,self.cp.get('Variables','s3_max'))
        
        self.st12 = Label(self, text='s4 min')
        self.st12.grid(row=4, column=4, sticky=E)
        self.s4_minVar = StringVar()
        self.s4_min = Entry(self, width=3, textvariable=self.s4_minVar)
        self.s4_min.grid(row=4, column=5, sticky=W)
        self.s4_min.insert(0,self.cp.get('Variables','s4_min'))
        
        self.st13 = Label(self, text='s4 min')
        self.st13.grid(row=4, column=6, sticky=E)
        self.s4_maxVar = StringVar()
        self.s4_max = Entry(self, width=3, textvariable=self.s4_maxVar)
        self.s4_max.grid(row=4, column=7, sticky=W)
        self.s4_max.insert(0,self.cp.get('Variables','s4_max'))

        self.sp4 = Label(self)
        self.sp4.grid(row=8)
        
        self.RecButton = Button(self, text='Rec',command=self.Record)
        self.RecButton.grid(row=9, column=0, columnspan = 2)
        
        self.SaveButton = Button(self, text='Save',command=self.SaveConfig)
        self.SaveButton.grid(row=9, column=2, columnspan = 2)

        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=9, column=4, sticky=E)    

        self.spacer3 = Label(self, text='')
        self.spacer3.grid(row=10, column=0, columnspan=6)
        self.text_box = Text(self,width=40,height=10,bd=3)
        self.text_box.grid(row=11, column=0, columnspan=8, sticky=E+W+N+S)
        self.tbscroll = Scrollbar(self,command = self.text_box.yview)
        self.tbscroll.grid(row=11, column=8, sticky=N+S+W)
        self.text_box.configure(yscrollcommand = self.tbscroll.set) 

    def QuitFromAxis(self):
        sys.stdout.write("M2 (Face.py Aborted)")
        self.quit()

    def WriteToAxis(self):
        sys.stdout.write(self.text_box.get(0.0, END))
        self.quit()

    def Record(self):
        sys.stdout.write("Cant record yet")
        self.quit()

    def LoadIniData(self):
        FileName = self.InputFile
        self.cp=ConfigParser()
        try:
            self.cp.readfp(open(FileName,'r'))
            # f.close()
        except IOError:
            raise Exception,'NoFileError'
        return
        
    def GetDirectory(self, name):
        if len(name) == 0:
            name = '.'
        DirName = askdirectory(initialdir=name,title='Please select a directory')
        if len(DirName) > 0:
            return DirName 
       
    def CopyClpBd(self):
        self.text_box.clipboard_clear()
        self.text_box.clipboard_append(self.text_box.get(0.0, END))

    def SaveConfig(self):
        try:
            FileName = self.InputFile
            # nc dir and tmp_dir
            NcDir = self.cp.get("Directories", "ncfiles")
            if len(NcDir) == 0:
                NcDir = self.GetDirectory()
            self.cp.set("Directories", "ncfiles", NcDir)

            TMPDir = self.cp.get("Directories", "tmp_dir")
            if len(TMPDir) == 0:
                TMPDir = self.GetDirectory()
            self.cp.set("Directories", "tmp_dir", TMPDir)

            self.cp.set("Directories", "tmp_dir", TMPDir)
            self.cp.set("Directories", "ncfiles", NcDir)
            self.cp.set("Directories", "target_dir", self.TargetDirVar.get())
            self.cp.set("Gcode", "feedrate", self.FeedrateVar.get())
            self.cp.set("Gcode", "power", self.LaserPowerVar.get())
            self.cp.set("Files", "target", self.TargetNameVar.get())
            self.cp.set("Executable", "toolpathcode", self.ExecuteVar.get())
            self.fn=open(FileName,'w')
            self.cp.write(self.fn)
            self.fn.close()
        except:
            tkMessageBox.showinfo('Error', 'broke in save config')            

    def WriteToFile(self):
        try:
            NcDir = self.cp.get("Directories", "ncfiles")
            if len(NcDir)>0:
                NcDir = self.GetDirectory()
            self.NewFileName = asksaveasfile(initialdir=self.NcDir,mode='w', \
                master=self.master,title='Create NC File',defaultextension='.ngc')
            self.NewFileName.write(self.text_box.get(0.0, END))
            self.NewFileName.close()
        except:
            tkMessageBox.showinfo('Error', 'broke in write to file')            

    def NcFileDirectory(self):
        DirName = self.GetDirectory(self.cp.get("Directories", "ncfiles"))
        if len(DirName)>0:
            self.cp.set("Directories", "ncfiles", DirName)

    def TMPFileDirectory(self):
        DirName = self.GetDirectory(self.cp.get("Directories", "tmp_dir"))
        if len(DirName)>0:
            self.cp.set("Directories", "tmp_dir", DirName)

    def Simple(self):
        tkMessageBox.showinfo('Feature', 'Sorry this Feature has\nnot been programmed yet.')

    def ClearTextBox(self):
        self.text_box.delete(1.0,END)

    def SelectAllText(self):
        self.text_box.tag_add(SEL, '1.0', END)

    def SelectCopy(self):
        self.SelectAllText()
        self.CopyClpBd()

    def HelpInfo(self):
        SimpleDialog(self,
            text='Required fields are:\n'
            'Part Width & Length,\n'
            'Amount to Remove,\n'
            'and Feedrate\n'
            'Fractions can be entered in most fields',
            buttons=['Ok'],
            default=0,
            title='User Info').go()
    def HelpAbout(self):
        tkMessageBox.showinfo('Help About', 'Programmed by\n'
            'Big John T (AKA John Thornton)\n'
            'Rick Calder\n'
            'Brad Hanken\n'
            'Version ' + version)

app = Application()
app.master.title('Eye movement recorder')
app.mainloop()

