#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
#  My first attempt at GNU Follows:
#  Modified Version 20100901
#  Copyright (c) 2010 Craig Gooder
#
#  Highlander01HMI UC_V1k.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Highlander01HMI UC_V1k.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Highlander01HMI UC_V1k.py.  If not, see <http://www.gnu.org/licenses/>.

import serial

from Tkinter import *
from tkSimpleDialog import askstring
from tkFileDialog   import asksaveasfilename
from tkFileDialog   import askopenfilename

from tkMessageBox import askokcancel

import wx
import sys
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *

import threading
import time

import math

gcodethreadenable = False
gcodethreadmanual = False
gcodethreadrun = False
gcodethreadstep = False
gcodereset = False
gcodestring = '#'
introcube = True
redrawrun = False
redrawtext = ''
drawz = False
drawmouse = False
drawxrot = 0
drawyrot = 0
usbreadenable = False
doxrot = False
doyrot = False
dozrot = False
drawrotdegstr = '90.0'
drawrotdegno = 90
panleftenable = False
panrightenable = False
panupenable = False
pandownenable = False
panmm = 5
viewoxm = -40.0
viewoxp = 20.0
viewoym = -30.0
viewoyp = 30.0
viewozm = -40.0
viewozp = 40.0
zoominenable = False
zoomoutenable = False
zoompercent = 125.0

#Routine~~~~~~~~~~~~~~~~~~~~~~~~~~~ GCode Run Thread ~~~~~~~~~~~~~~~~~~~~~~~~~~~

class usbgcodethread ( threading.Thread ):

	def __init__(self, lineno, text ):
		threading.Thread.__init__(self)
		print 'usbgcodethread init'
		self.lineno = lineno
		self.text = text

	def run (self):
		usbport = '/dev/ttyUSB0'
		MyUSB = serial.Serial(usbport, 115200, timeout=0.005)
		global gcodereset
		global gcodethreadenable
		global gcodethreadmanual
		global gcodethreadrun
		global gcodethreadstep
		global gcodestring
		global usbreadenable
		step = 1
		steptwocount = 0
		stepfourcount = 0
		stepm = 1
		stepmpass = 1
		stepmtwocount = 0
		stepmthreecount = 0
		stepmfourcount = 0
		stepmelevencount = 0
		stepr = 1
		steprtwocount = 0
		steprfourcount = 0
		while usbreadenable:
			data = MyUSB.readline()
			nextline = False
			if len(data)>0:
				print data
				#Bandaid, not always getting clean ok back, so just going with letter o for now
				#if data == 'ok\r\n':
				#	print 'Python read ok'
				#	nextline = True
				if data[0] == 'o':
					print 'Python read o'
					nextline = True
				if data == 'B59\r\n':
					print 'Buffer Full'

			if gcodereset == True:
				self.lineno = 0
				gcodereset = False

			if gcodethreadenable == False:
				stepr = 1
				steprtwocount = 0
				steprfourcount = 0

			if gcodethreadenable:
				if gcodethreadrun:
						stringa = self.text.GetLineText(self.lineno)
						stringb = ''
						stringalen = len(stringa)
						if stepr == 1:
							print '------------'
							stringa = self.text.GetLineText(self.lineno)
							stringb = ''
							stringalen = len(stringa)
							if stringalen > 2:
								index = 0
								while index < stringalen:
									if stringa[index] != ' ':
										stringb = stringb + stringa[index]
									index = index +1
							stringr = '?' + str(len(stringb)) + '\r\n'
							print 'Python sent:' + stringr
							stringb = stringb + '?'
							print stringb
							MyUSB.write(stringb)
							stepr = 2
						if stepr == 2:
							steprtwocount = steprtwocount + 1
							if len(data)>0:
								print data
								if data == stringr:
									print 'good! sent length = return'
									stringb = '*'
									MyUSB.write(stringb)
									print stringb
									self.lineno = self.lineno + 1
									stepr = 3
								if data != stringr:
									print 'bad! data'
									stringb = '#'
									MyUSB.write(stringb)
									stepr = 4

							if steprtwocount > 25:
								print 'No Arduino Response 25, Python Send Cancel #'
								stringb = '#'
								MyUSB.write(stringb)
								stepr = 4
								steprtwocount = 0
						if stepr == 3:
							if nextline == True:
								stepr = 1

						if stepr == 4:
							steprfourcount = steprfourcount + 1
							if steprfourcount == 1:
								print 'Wait until Arduino sends #0'
							if data == '#0':
								print 'no r n'
								stepr = 1
								steprfourcount = 0
							if data == '#0\r\n':
								print 'yes r n'
								stepr = 1
								steprfourcount = 0
							if steprfourcount > 10:
								print 'retry python send usb clear = #'
								stringb = '#'
								MyUSB.write(stringb)
								steprfourcount = 0
						
						if len(stringa)<1:
							gcodethreadrun=False
							gcodethreadenable=False
							self.lineno = 0

				if gcodethreadstep == False:
					step = 1
					steptwocount = 0
					stepfourcount = 0

				if gcodethreadstep:
					if step == 1:
						print '------------'
						stringa = self.text.GetLineText(self.lineno)
						stringb = ''
						stringalen = len(stringa)
						if stringalen > 2:
							index = 0
							while index < stringalen:
								if stringa[index] != ' ':
									stringb = stringb + stringa[index]
								index = index +1
						stringr = '?' + str(len(stringb)) + '\r\n'
						print 'Python sent:' + stringr
						stringb = stringb + '?'
						print stringb
						MyUSB.write(stringb)
						step = 2
					if step == 2:
						steptwocount = steptwocount + 1
						if len(data)>0:
							if data == stringr:
								print 'good! sent length = return'
								stringb = '*'
								MyUSB.write(stringb)
								print stringb
								self.lineno = self.lineno + 1
			      	        			gcodethreadstep = False
							if data != stringr:
								print 'bad! data not= stringr'
								stringb = '#'
								MyUSB.write(stringb)
								step = 4
								print 'step 4'

						if steptwocount > 25:
							print 'No Arduino Response 25, Python Send Cancel #'
							stringb = '#'
							MyUSB.write(stringb)
							step = 4
							steptwocount = 0
					if step == 3:

	      	        			gcodethreadstep = False

					if step == 4:
						if steprfourcount == 1:
							print 'Wait until Arduino sends #0'
						stepfourcount = stepfourcount + 1
						if data == '#0':
							print 'no r n'
		      	        			gcodethreadstep = False
						if data == '#0\r\n':
							print 'yes r n'
		      	        			gcodethreadstep = False
						if stepfourcount > 10:
							print 'retry python send usb clear = #'
							stringb = '#'
							MyUSB.write(stringb)
							if stepfourcount > 25:
			      	        			gcodethreadstep = False
								print 'step 4 clear failed'
							


					#time.sleep(0.1)
                			if len(stringa)<2:
                				gcodethreadrun=False
                				gcodethreadenable=False
                				self.lineno = 0

				if gcodethreadmanual == False:
					stepm = 1
					stepmpass = 1
					stepmtwocount = 0
					stepmthreecount = 0 
					stepmfourcount = 0

				if gcodethreadmanual:
					#send data ex G91 X01 F100?
					#? asks arduino t send back a char count
					if stepm == 1:
						print '------------'
						stringa = gcodestring
						stringb = ''
						stringalen = len(stringa)
						if stringalen > 2:
							index = 0
							while index < stringalen:
								if stringa[index] != ' ':
									stringb = stringb + stringa[index]
								index = index +1
						stringr = '?' + str(len(stringb)) + '\r\n'
						print 'Python characters sent:' + stringr
						stringb = stringb + '?'
						print stringb
						MyUSB.write(stringb)
						stepm = 2
					#Evaluate Arduino char count response sent back
					#If Char count sent back matches count sent then send execute char *
					#If Char counts are not = send buffer clear char #
					#If there is no response send buffer clear char #
					if stepm == 2:
						stepmtwocount = stepmtwocount + 1
						if len(data)>0:
							if stepmtwocount < 25:
								if data == stringr:
									print 'good! data = stringr'
									stringb = '*'
									MyUSB.write(stringb)
									print 'Python sent execute char:' + stringb
									stepm = 3
									nextline = False
							if data != stringr:
								print 'bad! data not= stringr'
								stringb = '#'
								MyUSB.write(stringb)
								print 'Python sent buffer clear: ' + stringb 
								stepm = 11

						if stepmtwocount > 25:
							print 'No Arduino Response 25, Python Send Cancel #'
							stringb = '#'
							MyUSB.write(stringb)
							print 'Python sent buffer clear: ' + stringb 
							stepm = 11
							stepmtwocount = 0
					#Get Execute response back from Arduino
					if stepm == 3:
						stepmthreecount = stepmthreecount + 1
	      	        			if nextline == True:
							stepm = 4
							nextline = False
						if stepmthreecount > 25:
							stringb = '*'
							MyUSB.write(stringb)
							print 'Python sent execute char:' + stringb
							stepmthreecount = 0
							
					if stepm == 4:
						if stepmpass == 2:
							gcodethreadmanual = False
							nextline = False
						if stepmpass == 1:
		      	        			gcodestring = 'G90'
							stepm = 1
							stepmpass = 2

					#Wait for buffer cleared response #0 from Arduino
					if stepm == 11:
						stepmelevencount = stepmelevencount + 1
						if data == '#0':
							#Note this data comes with no /r/n
							stepm = 1
						if data == '#0\r\n':
							stepm = 1
						if stepmelevencount > 1000:
							print '11retry python send usb clear = #'
							stringb = '#'
							MyUSB.write(stringb)
							stepfourcount = 0

					#time.sleep(0.1)
                			if len(stringa)<2:
                				gcodethreadrun=False
                				gcodethreadenable=False
                				self.lineno = 0

		print 'usbgcodethread has ended'

#Routine~~~~~~~~~~~~~~~~~~~~~~~~~~~ Canvas Base ~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MyCanvasBase(glcanvas.GLCanvas):
  def __init__(self, parent):
    glcanvas.GLCanvas.__init__(self, parent, -1)
    self.init = False
    # initial mouse position
    self.lastx = self.x = 0
    self.lasty = self.y = 0
    self.size = None
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
    self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

  def OnEraseBackground(self, event):
    pass # Do nothing, to avoid flashing on MSW

  def OnSize(self, event):
    size = self.size = self.GetClientSize()
    if self.GetContext():
      self.SetCurrent()
      glViewport(0, 0, size.width, size.height)
    event.Skip()

  def OnPaint(self, event):
	dc = wx.PaintDC(self)
	self.SetCurrent()
	if not self.init:
	    self.InitGL()
	    self.init = True
	self.OnDraw()

  def OnMouseDown(self, evt):
    global drawmouse
    if drawmouse:
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

  def OnMouseUp(self, evt):
    self.ReleaseMouse()

  def OnMouseMotion(self, evt):
    if evt.Dragging() and evt.LeftIsDown():
      self.lastx, self.lasty = self.x, self.y
      self.x, self.y = evt.GetPosition()
      self.Refresh(False)

#---------------------Draws GCode File  ------------------

class drawgcode(MyCanvasBase):
  def InitGL(self):
    global viewoxm
    global viewoxp
    global viewoym
    global viewoyp
    global viewozm
    global viewozp

    # set viewing Projection
    glMatrixMode(GL_PROJECTION)
   
    #glOrtho(-2.0, 2.0, -2.0, 2.0, 0.5, 4.0)
    glOrtho(viewoxm, viewoxp, viewoym, viewoyp, viewozm, viewozp)
    # position viewer
    glTranslatef(-30.0, -20.0, 0.0)

    # position object
    global drawmouse
    if drawmouse:
        glRotatef(self.y, 0.0, 1.0, 0.0)
        glRotatef(self.x, 1.0, 0.0, 0.0)
    
    # ---------------Setting below are from my original cube program
 
    # Move Right And Into The Screen
    #glTranslatef(0.0, 0.0, -2.0)

    # This Will Clear The Background Color To Black
    glClearColor(0.0, 0.0, 0.0, 0.0)

    # Enables Clearing Of The Depth Buffer
    glClearDepth(1.0)

    # The Type Of Depth Test To Do
    glDepthFunc(GL_LESS)

    # Enables Depth Testing
    glEnable(GL_DEPTH_TEST)

    # Enables Smooth Color Shading
    glShadeModel(GL_SMOOTH)

    glMatrixMode(GL_MODELVIEW)

  def OnDraw(self):

	global panleftenable
	global panrightenable
	global panupenable
	global pandownenable
	global panmm
        global redrawrun
        global redrawtext
	global viewoxm
	global viewoxp
	global viewoym
	global viewoyp
	global viewozm
	global viewozp
	global zoominenable
	global zoomoutenable
	global zoompercent
	global introcube
	gcode = '00'
	tempjunk = 0.0
	icord = 0.0
	jcord = 0.0
	pxcord = 0.0
	xcord = 0.0
	circx = 0.0
	circxstep = 0.0
	circxstepcord = 0.0
	circxendcord = 0.0
	pycord = 0.0
	ycord = 0.0
	circy = 0.0
	circystep = 0.0
	circystepcord = 0.0
	circyendcord = 0.0
	pzcord = 0.0
	zcord = 0.0
	zcirc = 0.0
	circradius = 0.0
	circstep = 0.1
	circangle1 = 0.0
	circangle2 = 0.0
	circanglestep = 0.0
	circcircum = 0.0
	circdegdist = 0.0
	circdegstep = 0.0
	circdeltax = 0.0
	circdeltay = 0.0
	circquad = 0.0
	tempangle = 0.0
	processfileok = True


        #clear the screen and the depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if panleftenable == True:
            pan = panmm * -1
            glTranslatef(pan,0.0,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            panleftenable = False

        if panrightenable == True:
            glTranslatef(panmm,0.0,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            panrightenable = False

        if panupenable == True:
            glTranslatef(0.0,panmm,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            panupenable = False

        if pandownenable == True:
            pan = panmm * -1
            glTranslatef(0.0,pan,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            pandownenable = False

        if zoominenable == True:
            zoom = zoompercent/100.0
            glScalef(zoom,zoom,zoom)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            zoominenable = False

        if zoomoutenable == True:
            zoom = 100.0/zoompercent
            glScalef(zoom,zoom,zoom)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)
            zoomoutenable = False

        global drawrotdegno
        global doxrot        
        if doxrot:
            glRotatef(drawrotdegno, 1.0, 0.0, 0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)

        global doyrot        
        if doyrot:
            glRotatef(drawrotdegno, 0.0, 1.0, 0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)

        global dozrot        
        if dozrot:
            glRotatef(drawrotdegno, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glCallList(1)

    
        if redrawrun:
		#Use glNewList and glEndList calls to put drawing into a list
		#Benefit is that this time consuming gcode file processing is only done once
		#After this only very fast glClear and glCallList calls are required to do zooms, pans, & rotates
		glNewList(1, GL_COMPILE)
		
		#introduction code draws cube one time
		if introcube == True:
			# Start Drawing The Cube
			glBegin(GL_QUADS)
  
			# Set The Color To Blue
			glColor3f(0.0,10.0,0.0)
			# Top Right Of The Quad (Top)
			glVertex3f( 10.0, 5.0,-10.0)
			# Top Left Of The Quad (Top)
			glVertex3f(-10.0, 5.0,-10.0)
			# Bottom Left Of The Quad (Top)
			glVertex3f(-10.0, 5.0, 10.0)
			# Bottom Right Of The Quad (Top)
			glVertex3f( 10, 5.0, 10)
 
			# Set The Color To Orange
			glColor3f(10,5.0,0.0)
			# Top Right Of The Quad (Bottom)
			glVertex3f( 10,-5.0, 10)
			# Top Left Of The Quad (Bottom)
			glVertex3f(-10,-5.0, 10)
			# Bottom Left Of The Quad (Bottom)
			glVertex3f(-10,-5.0,-10)
			# Bottom Right Of The Quad (Bottom)
			glVertex3f( 10,-5.0,-10)
 
			# Set The Color To Red
			glColor3f(10,0.0,0.0)
			# Top Right Of The Quad (Front)
			glVertex3f( 10, 10, 5.0)
			# Top Left Of The Quad (Front)
			glVertex3f(-10, 10, 5.0)
			# Bottom Left Of The Quad (Front)
			glVertex3f(-10,-10, 5.0)
			# Bottom Right Of The Quad (Front)
			glVertex3f( 10,-10, 5.0)
 
			# Set The Color To Yellow
			glColor3f(10,10,0.0)
			# Bottom Left Of The Quad (Back)
			glVertex3f( 10,-10,-5.0)
			# Bottom Right Of The Quad (Back)
			glVertex3f(-10,-10,-5.0)
			# Top Right Of The Quad (Back)
			glVertex3f(-10, 10,-5.0)
			# Top Left Of The Quad (Back)
			glVertex3f( 10, 10,-5.0)
 
			# Set The Color To Blue
			glColor3f(0.0,0.0,10)
			# Top Right Of The Quad (Left)
			glVertex3f(-5.0, 10, 10)
			# Top Left Of The Quad (Left)
			glVertex3f(-5.0, 10,-10)
			# Bottom Left Of The Quad (Left)
			glVertex3f(-5.0,-10,-10)
			# Bottom Right Of The Quad (Left)
			glVertex3f(-5.0,-10, 10)
 
			# Set The Color To Violet
			glColor3f(10,0.0,10)
			# Top Right Of The Quad (Right)
			glVertex3f( 5.0, 10,-10)
			# Top Left Of The Quad (Right)
			glVertex3f( 5.0, 10, 10)
			# Bottom Left Of The Quad (Right)
			glVertex3f( 5.0,-10, 10)
			# Bottom Right Of The Quad (Right)
			glVertex3f( 5.0,-10,-10)
			# Done Drawing The Quad
 			glEnd()
			introcube = False

		# Draw x-axis line.
		glBegin( GL_LINES )
		glColor3f( 1, 0, 0 )	
		glVertex3f( 0, 0, 0 )
		glVertex3f( 50, 0, 0 )
		glEnd( )
		# Draw number 50 on x-axis line.
		glRasterPos2f(50,-5)
		glutInit()
		A = 53
		glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, A)
		glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, 48)
	
		# Draw y-axis line.
		glColor3f( 0, 1, 0 )
		glBegin( GL_LINES )
		glVertex3f( 0, 0, 0 )
		glVertex3f( 0, 50, 0 )
		glEnd( )
		glRasterPos2f(-5,50)
		glutInit()
		A = 53
		glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, A)
		glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, 48)

		# Draw z-axis line.
		glColor3f( 0, 0, 1 )
		glBegin( GL_LINES )
		glVertex3f( 0, 0, 0 )
		glVertex3f( 0, 0, 50 )
		glEnd( )
		lineno = 1
		index = 0
		strno = ''
		#for i in range (1,5):
		while processfileok == True:
			string = redrawtext.GetLineText(lineno)
			if len(string) < 2:
				processfileok = False
			while index < len(string):
				letter = string[index]
				#print letter
				if letter == 'N':
					#print 'line number: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False
					linenon = strno
					strno = ''
					#print linenon
				elif letter == 'G':
					#print 'motion code: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					gcode = strno
					strno = ''
					#print gcode
				elif letter == 'X':
					#print 'x cord.: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

						
					xcord = float(strno)
					strno = ''
					#print X cord
				elif letter == 'Y':
					#print 'Y cord.: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					ycord = float(strno)
					strno = ''
					#print ycord
				elif letter == 'Z':
					#print 'Z cord.: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False


					zcord = float(strno)
					strno = ''
					#print zcord
				elif letter == 'F':
					#print 'motion speed: '
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					fspeed = float(strno)
					strno = ''
					#print fspeed
				elif letter == 'I':
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					icord = float(strno)
					strno = ''
				elif letter == 'J':
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					jcord = float(strno)
					strno = ''
				elif letter == 'R':
					getno = True
					index = index + 1
					while getno == True:
						letter = string[index]
						if letter == ' ':
							if index < len(string):
								index = index + 1
						elif letter == '-' or letter == '.' or letter == '0' or letter == '1' or letter == '2' or letter == '3' or letter == '4' or letter == '5' or letter == '6' or letter == '7' or letter == '8' or letter == '9':
							strno = strno + letter
							if index < len(string):
								index = index + 1
						elif True:
							index = index - 1
							getno = False

						if index == len(string):
							getno = False

					circradius = float(strno)
					strno = ''

				elif letter == ' ':
					pass
				elif True:
                    			print letter
				index = index + 1

			lineno = lineno +1
			index = 0 

			if gcode == '00':
				glColor3f( 0.5, 1, 0.5 )
			elif gcode == '01' or gcode == '02' or gcode == '03':
				glColor3f( 1, 0.5, 0.5 )
			if gcode == '00' or gcode == '01':
				glBegin( GL_LINES )
				glVertex3f( pxcord, pycord, pzcord )
				glVertex3f( xcord, ycord, zcord )
				glEnd( )
			if gcode == '02':
				circxendcord = xcord
				circyendcord = ycord
				circx = pxcord + icord
				circy = pycord + jcord
				circdeltax = pxcord - circx
				circdeltay = jcord
				circradius = math.sqrt((circdeltax*circdeltax)+(circdeltay*circdeltay))
				circcircum = 2 * math.pi * circradius
				circdegdist = circcircum / 360.0
				circdegstep = circstep / circdegdist
				tempangle = math.acos(circdeltax/circradius)
				tempangle = math.degrees(tempangle)
				

				if circx > pxcord:
					if circy >= pycord:
						circquad = 180.0
						tempangle = tempangle - 90
						tempangle = 270 - tempangle
					if circy < pycord:
						circquad = 90
				if circx < pxcord:
					if circy > pycord:
						circquad = 270.0
						tempangle = 360 - tempangle
					if circy <= pycord:
						circquad = 0.0
				if circx == pxcord:
					if circy < pycord:
						circquad = 90.0
					if circy > pycord:
						circquad = 270.0
						tempangle = 270.0

				circangle1 = tempangle
				print circangle1

				circdeltax = xcord - circx
				tempangle = math.acos(circdeltax/circradius)
				tempangle = math.degrees(tempangle)

				if circx > xcord:
					if circy >= ycord:
						circquad = 180.0
						tempangle = tempangle - 90
						tempangle = 270 - tempangle
					if circy < ycord:
						circquad = 90
				if circx < xcord:
					if circy > ycord:
						circquad = 270.0
						tempangle = 360 - tempangle
					if circy <= ycord:
						circquad = 0.0
				if circx == xcord:
					if circy < ycord:
						circquad = 90.0
					if circy > ycord:
						circquad = 270.0
						tempangle = 270.0


				circangle2 = tempangle
				print circangle2
				circanglestep = circangle1
				
				while circanglestep < circangle2:
					circanglestep = circanglestep + circdegstep
					circxstep = circradius * math.cos(circanglestep * math.pi /180.0)
					circxstepcord = circx + circxstep
					circystep = circradius * math.sin(circanglestep * math.pi /180.0)
					circystepcord = circy + circystep
					xcord = circxstepcord
					ycord = circystepcord
					glBegin( GL_LINES )
					glVertex3f( pxcord, pycord, pzcord )
					glVertex3f( xcord, ycord, zcord )
					glEnd( )
					print circanglestep
					pxcord = xcord
					pycord = ycord
					pzcord = zcord

				xcord = circxendcord
				ycord = circyendcord

				glBegin( GL_LINES )
				glVertex3f( pxcord, pycord, pzcord )
				glVertex3f( xcord, ycord, zcord )
				glEnd( )

			if gcode == '03':
				circxendcord = xcord
				circyendcord = ycord
				circx = pxcord + icord
				circy = pycord + jcord
				circdeltax = pxcord - circx
				circdeltay = jcord
				circradius = math.sqrt((circdeltax*circdeltax)+(circdeltay*circdeltay))
				circcircum = 2 * math.pi * circradius
				circdegdist = circcircum / 360.0
				circdegstep = circstep / circdegdist
				tempangle = math.acos(circdeltax/circradius)
				tempangle = math.degrees(tempangle)
				

				if circx > pxcord:
					if circy >= pycord:
						circquad = 180.0
						tempangle = tempangle - 90
						tempangle = 270 - tempangle
					if circy < pycord:
						circquad = 90
				if circx < pxcord:
					if circy > pycord:
						circquad = 270.0
						tempangle = 360 - tempangle
					if circy <= pycord:
						circquad = 0.0
				if circx == pxcord:
					if circy < pycord:
						circquad = 90.0
					if circy > pycord:
						circquad = 270.0
						tempangle = 270.0

				circangle1 = tempangle
				print circangle1

				circdeltax = xcord - circx
				tempangle = math.acos(circdeltax/circradius)
				tempangle = math.degrees(tempangle)

				if circx > xcord:
					if circy >= ycord:
						circquad = 180.0
						tempangle = tempangle - 90
						tempangle = 270 - tempangle
					if circy < ycord:
						circquad = 90
				if circx < xcord:
					if circy > ycord:
						circquad = 270.0
						tempangle = 360 - tempangle
					if circy <= ycord:
						circquad = 0.0
				if circx == xcord:
					if circy < ycord:
						circquad = 90.0
					if circy > ycord:
						circquad = 270.0
						tempangle = 270.0


				circangle2 = tempangle
				print circangle2
				circanglestep = circangle1
				
				while circanglestep > circangle2:
					circanglestep = circanglestep - circdegstep
					circxstep = circradius * math.cos(circanglestep * math.pi /180.0)
					circxstepcord = circx + circxstep
					circystep = circradius * math.sin(circanglestep * math.pi /180.0)
					circystepcord = circy + circystep
					xcord = circxstepcord
					ycord = circystepcord
					glBegin( GL_LINES )					
					glVertex3f( pxcord, pycord, pzcord )
					glVertex3f( xcord, ycord, zcord )
					glEnd( )
					print circanglestep
					pxcord = xcord
					pycord = ycord
					pzcord = zcord

				xcord = circxendcord
				ycord = circyendcord

				glBegin( GL_LINES )					
				glVertex3f( pxcord, pycord, pzcord )
				glVertex3f( xcord, ycord, zcord )
				glEnd( )



					

			#print 'copy new coodinates to previous'
			pxcord = xcord
			pycord = ycord
			pzcord = zcord

			string = redrawtext.GetLineText(lineno)
			if len(string) < 2:
				processfileok = False
		glEndList()
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glCallList(1)

		#glColor3f( 0, 0, 1 )
		#glBegin( GL_LINES )
		#glVertex3f( 0, 0, 0 )
		#glVertex3f( 1, 1, 1 )
		#glEnd( )

        if self.size is None:
          self.size = self.GetCleintSize()
        w, h = self.size
        w = max(w, 50.0)
        h = max(h, 50.0)
        #Gooder01 increased x,yscale number to 500 to get rotate
        #working when window is expanded larger, was not working
        #when the window was small
        xScale = 500 / w
        yScale = 500 / h
        
        global drawmouse
        if drawmouse:
            glRotatef((self.y - self.lasty) * yScale, 1.0, 0.0, 0.0);
            glRotatef((self.x - self.lastx) * xScale, 0.0, 1.0, 0.0);

        self.SwapBuffers()



#Routine~~~~~~~~~~~~~~~~ Main Window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MainWindow(wx.Frame):
    
    usboff = True
    
    def __init__(self, parent = None, id = -1, title = "wxPython - Gooder01 - UC_V1k.py - Arduino - USB - Simen Grbl - CNC"):
        # Init
        wx.Frame.__init__(
                self, parent, id, title, size = (700,700),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )

        # TextCtrl
        #self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)

        #3D Code
        #self.control = myGLCanvas(self)

        #--------------Panels for Frame Layout

        panel1 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
	#panel2 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
        panel3 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
        panel4 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

        panel1.SetBackgroundColour("GREY")
        #panel2.SetBackgroundColour("RED")
        panel3.SetBackgroundColour("RED")
        panel4.SetBackgroundColour("BROWN")

        #--------------panel 1 vbox1 - Upper Left Corner of Frame - Buttons etc.
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(panel1, 1, wx.EXPAND)
        
        usbst1 = wx.StaticText(panel1, -1, 'USB Write Entry', pos=(10,10))

        self.usbtc1 = wx.TextCtrl(panel1, -1, pos=(10,30), size=(265,20))

	usbbtnon = wx.Button(panel1, -1, 'USB On', pos=(10,50), size=(80,25))
        self.Bind(wx.EVT_BUTTON, self.USBOn, usbbtnon)
        usbbtnwrite = wx.Button(panel1, -1, 'USB Write', pos=(195,50), size=(80,25))
        self.Bind(wx.EVT_BUTTON, self.usbcncwrite, usbbtnwrite)

        #note wx.RB_Group is only on first radio button to declare beginning of group
        astaxis = wx.StaticText(panel1, -1, 'Axis', pos=(15,92))
        self.aradiox=wx.RadioButton(panel1,-1, "X", pos=(55,90), style= wx.RB_GROUP)
        self.aradioy=wx.RadioButton(panel1,-1, "Y", pos=(100,90))
        self.aradioz=wx.RadioButton(panel1,-1, "Z", pos=(140,90))
        for eachRadio in [self.aradiox, self.aradioy, self.aradioz]:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, eachRadio)
        abtnzero = wx.Button(panel1, -1, 'Zero', pos=(200,88), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.manualzero, abtnzero)

        abtnminus = wx.Button(panel1, -1, 'Move -', pos=(10,120), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.manualmoveminus, abtnminus)
        abtnplus = wx.Button(panel1, -1, 'Move +', pos=(90,120), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.manualmoveplus, abtnplus)
        self.manualmovedisttc = wx.TextCtrl(panel1, -1, "0", pos=(170,120), size=(40,25))
        astmoveunits = wx.StaticText(panel1, -1, 'Units mm', pos=(215,125))
        #alist = ['continuous', '5mm', '1mm', '.5mm', '.1mm', '.05mm', '.01mm']
        #self.alistbox = wx.ListBox(panel1, -1, (65,120), (120,25), alist, wx.LB_SINGLE)

        astjogspd = wx.StaticText(panel1, -1, 'Jog Speed (mm/min)', pos=(10,171))
        self.asliderjspd = wx.Slider(panel1, 100, 25, 1, 750, pos=(150,150), size=(125,-1), 
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.asliderjspd.SetTickFreq(20,1)

        gcodestgcode = wx.StaticText(panel1, -1, 'GCode', pos=(10,230))

	gcodebtnstep = wx.Button(panel1, -1, 'Step', pos=(10,260), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.gcodestepr, gcodebtnstep)
        gcodebtnrun = wx.Button(panel1, -1, 'Run', pos=(90,260), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.gcoderun, gcodebtnrun)
        gcodebtnpause = wx.Button(panel1, -1, 'Pause', pos=(170,260), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.gcodepause, gcodebtnpause)
        gcodebtnstop = wx.Button(panel1, -1, 'Stop', pos=(250,260), size=(75,25))
        self.Bind(wx.EVT_BUTTON, self.gcodestop, gcodebtnstop)


        #--------------hbox1
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(vbox1, 1, wx.EXPAND)
        #hbox1.Add(panel2, 1, wx.EXPAND)
        #hbox1.Add(myCube(self), 1, wx.EXPAND)
        self.mydrawgcode = drawgcode(self)
        hbox1.Add(self.mydrawgcode, 1, wx.EXPAND)

        #--------------hbox2
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        #hbox2.Add(panel3, 1, wx.EXPAND)
        self.gcodetc1 = wx.TextCtrl(panel3, -1, size=(350,350), style = wx.TE_MULTILINE)
        self.gcodelineno = 0
        self.gcodestr = "hello test"
        hbox2.Add(panel3, 1, wx.EXPAND)
        hbox2.Add(panel4, 1, wx.EXPAND)


        #--------------box
        #box = wx.BoxSizer(wx.HORIZONTAL)
        box = wx.BoxSizer(wx.VERTICAL)
        #box.Add(panel3, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        box.Add(hbox1, 1, wx.EXPAND)
        box.Add(hbox2, 1, wx.EXPAND)

        #--------------Panel 4

        drawbtn = wx.Button(panel4, -1, 'Refresh', pos=(10,10), size=(110,25))
        self.Bind(wx.EVT_BUTTON, self.drawtest, drawbtn)

        drawbtnxm = wx.Button(panel4, -1, 'X-', pos=(120,10), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawxrotmr, drawbtnxm) 

        drawbtnxp = wx.Button(panel4, -1, 'X+', pos=(175,10), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawxrotpr, drawbtnxp)

        drawbtnmouse = wx.Button(panel4, -1, 'Mouse', pos=(230,10), size=(110,25))
        self.Bind(wx.EVT_BUTTON, self.drawmouser, drawbtnmouse)

        self.drawtxtrotdeg = wx.TextCtrl(panel4, -1, "20", pos=(10,50), size=(40,25))

        usbst1 = wx.StaticText(panel4, -1, 'Degrees', pos=(55,55))

        drawbtnym = wx.Button(panel4, -1, 'Y-', pos=(120,40), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawyrotmr, drawbtnym)

        drawbtnyp = wx.Button(panel4, -1, 'Y+', pos=(175,40), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawyrotpr, drawbtnyp)

        drawbtnzm = wx.Button(panel4, -1, 'Z-', pos=(120,70), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawzrotmr, drawbtnzm)

        drawbtnzp = wx.Button(panel4, -1, 'Z+', pos=(175,70), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.drawzrotpr, drawbtnzp)

        self.tczoompercent = wx.TextCtrl(panel4, -1, "110", pos=(10,130), size=(40,25))

        stzoom = wx.StaticText(panel4, -1, '% Zoom', pos=(55,135))

        drawbtnzoomin = wx.Button(panel4, -1, 'In', pos=(120,130), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.zoominr, drawbtnzoomin)

        drawbtnzoomout = wx.Button(panel4, -1, 'Out', pos=(175,130), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.zoomoutr, drawbtnzoomout)

        self.tcpanmm = wx.TextCtrl(panel4, -1, "5", pos=(10,160), size=(40,25))

        stpan = wx.StaticText(panel4, -1, 'mm Pan', pos=(55,165))

        drawbtnpanleft = wx.Button(panel4, -1, 'Left', pos=(120,160), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.panleftr, drawbtnpanleft)

        drawbtnpanright = wx.Button(panel4, -1, 'Right', pos=(175,160), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.panrightr, drawbtnpanright)

        drawbtnpanup = wx.Button(panel4, -1, 'Up', pos=(230,160), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.panupr, drawbtnpanup)

        drawbtnpandown = wx.Button(panel4, -1, 'Down', pos=(285,160), size=(55,25))
        self.Bind(wx.EVT_BUTTON, self.pandownr, drawbtnpandown)

        #-------------- something with layout
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()


        # StatusBar
        self.CreateStatusBar()

        # Filemenu -----------------------
        filemenu = wx.Menu()

        # Open
        menuitem = filemenu.Append(-1, "&Open", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnOpen, menuitem) # here comes the event-handler
        # Save
        menuitem = filemenu.Append(-1, "&Save", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnSave, menuitem) # here comes the event-handler
        # About
        menuitem = filemenu.Append(-1, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem) # here comes the event-handler
        # Separator
        filemenu.AppendSeparator()
        # Exit
        menuitem = filemenu.Append(-1, "E&xit", "Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuitem) # here comes the event-handler

        # Editmenu -----------------------
        editmenu = wx.Menu()
        # Cut
        menuitem = editmenu.Append(-1, "Cu&t", "Information about this program")
        # Copy
        menuitem = editmenu.Append(-1, "&Copy", "Information about this program")
        # Paste
        menuitem = editmenu.Append(-1, "&Paste", "Information about this program")


        # Menubar
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        menubar.Append(editmenu,"&Edit")
        self.SetMenuBar(menubar)

        # Show
        self.Show(True)

    #--------------Open a File
    def OnOpen(self,event):
		global introcube
		introcube = False
		self.gcodetc1.Clear()
		filenameo = askopenfilename()
		print filenameo
		fin = open(filenameo, "r")
		string = fin.read()
		fin.close()
		self.gcodestr = string
		self.gcodetc1.WriteText(string)
		print string
		self.drawtest(self)

    def OnSave(self,event):
		filename = asksaveasfilename()
		if filename:
			alltext = self.gcodetc1.GetValue()
			open(filename, 'w').write(alltext)


    def OnAbout(self,event):
        message = "Highlander01HMI is a GNU free Python HMI/GUI for use with Simen GRBL CNC software http://github.com/Highlander01/Highlander01HMI"
        caption = "About Highlander01HMI"
        wx.MessageBox(message, caption, wx.OK)


    def OnExit(self,event):
        self.Close(True)  # Close the frame.

    #--------------Add USB control
    def USBOn(self,event):
        usbport = '/dev/ttyUSB0'
        self.MyUSB1 = serial.Serial(usbport, 115200, timeout=0.005)
        global usbreadenable
        if usbreadenable:
            usbreadenable = False
        elif True:
            usbreadenable = True
            usbgcodethread(self.gcodelineno,self.gcodetc1).start()
        

    def usbcncread(self,event):
      #for i in range (1,10):
          #ser.read() only reads one character from usb buffer at a time Gooder20100419
          #data = ser.read()
          #ser.readline() reads a full line from usb buffer which is much nicer, less work Gooder20100419
          data = self.ser.readline()
          print data
          #print i

    def usbcncwrite(self,event):
          string = self.usbtc1.GetValue()
          self.MyUSB1.write(string)


    ######-----------End of Add USB control


    def OnRadio(self, event):
        if self.aradiox.GetValue():
            print 'x pressed'
        if self.aradioy.GetValue():
            print 'y pressed'
        if self.aradioz.GetValue():
            print 'z pressed'

    #--------------code for Manual Zero button
    def manualzero(self,event):
	if self.aradiox.GetValue():
		string = 'G92 X0' + '*'
		print string
	if self.aradioy.GetValue():
		string = 'G92 Y0' + '*'
		print string
	if self.aradioz.GetValue():
		string = 'G92 Z0' + '*'
		print string
	self.MyUSB1.write(string)

    #--------------code for Manual Move plus button
    def manualmoveplus(self,event):
	global gcodethreadenable
	global gcodethreadmanual
	global gcodestring
	movedist = float(self.manualmovedisttc.GetValue())

	if movedist >= 0.0 and movedist <= 100.0:
		gcodethreadenable = True
		gcodethreadmanual = True
		print 'in range'
		if self.aradiox.GetValue():
			string = 'G91 X' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
		if self.aradioy.GetValue():
			string = 'G91 Y' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
		if self.aradioz.GetValue():
			string = 'G91 Z' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
		gcodestring = string
	if movedist < 0.0 or movedist > 100.0:
		print 'Move distance is out of range.'
		self.manualmovedisttc.SetValue("0")
		




    #--------------code for Manual Move minus button
    def manualmoveminus(self,event):
	global gcodethreadenable
	global gcodethreadmanual
	global gcodestring
	movedist = float(self.manualmovedisttc.GetValue())
	if self.aradiox.GetValue():
		string = 'G91 X-' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
	if self.aradioy.GetValue():
		string = 'G91 Y-' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
	if self.aradioz.GetValue():
		string = 'G91 Z-' + str(movedist) + ' F' + str(self.asliderjspd.GetValue())
	if movedist > 0.0 or movedist < 100.0:
		gcodethreadenable = True
		gcodethreadmanual = True
		gcodestring = string
		print 'in range'
	elif True:
		print 'Move distance is out of range.'


    #--------------code for gcodestep button
    def gcodestepr(self,event):
	global gcodethreadstep
	gcodethreadstep = True
	global gcodethreadenable	
	gcodethreadenable = True
	global gcodethreadrun
	gcodethreadrun = False

    #--------------code for gcoderun button
    def gcoderun(self,event):
        global gcodethreadenable
        global gcodethreadrun
        gcodethreadenable = True
        gcodethreadrun = True

    #--------------code for gcodepause button
    def gcodepause(self,event):
        global gcodethreadrun
        if gcodethreadrun == False:
            gcodethreadrun = True
        elif gcodethreadrun == True:
            gcodethreadrun = False
        print 'gcode pause ' + str (gcodethreadrun)


    #--------------code for gcodestop button
    def gcodestop(self,event):
        global gcodethreadenable
        global gcodethreadrun
	global gcodereset
        gcodethreadenable = False
        gcodethreadrun = False
	gcodereset = True
        print "gcode stopped"

    
    def drawtest(self,event):
        global redrawrun
        global redrawtext
        redrawtext = self.gcodetc1
        redrawrun = True
        lineno = 1
        text = self.gcodetc1
        index = 0
        strno = ''
	self.mydrawgcode.OnDraw()

    def drawxrotmr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        drawrotdegstr = '-' + drawrotdegstr
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)
        global doxrot
        doxrot = True
        global doyrot
        doyrot = False
        global dozrot
        dozrot = False
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def drawxrotpr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)
        global doxrot
        doxrot = True
        global doyrot
        doyrot = False
        global dozrot
        dozrot = False
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def drawyrotmr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        drawrotdegstr = '-' + drawrotdegstr
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)        
        global doxrot
        doxrot = False
        global doyrot
        doyrot = True
        global dozrot
        dozrot = False
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def drawyrotpr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)        
        global doxrot
        doxrot = False
        global doyrot
        doyrot = True
        global dozrot
        dozrot = False
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def drawzrotmr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        drawrotdegstr = '-' + drawrotdegstr
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)        
        global doxrot
        doxrot = False
        global doyrot
        doyrot = False
        global dozrot
        dozrot = True
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def drawzrotpr(self,event):
        global drawrotdegstr
        drawrotdegstr = self.drawtxtrotdeg.GetValue()
        if drawrotdegstr == '':
            drawrotdegstr = '10'
        global drawrotdegno
        drawrotdegno = float(drawrotdegstr)        
        global doxrot
        doxrot = False
        global doyrot
        doyrot = False
        global dozrot
        dozrot = True
        global drawmouse
        drawmouse = False
	global redrawrun
	redrawrun = False
        self.mydrawgcode.OnDraw()

    def panleftr(self,event):
	global panleftenable
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
        global panmm
        panmmstr = self.tcpanmm.GetValue()
        if panmmstr == '':
            panmmstr = '10'
        panmm = float(panmmstr)
	panleftenable = True
	self.mydrawgcode.OnDraw()

    def panrightr(self,event):
	global panrightenable
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
        global panmm
        panmmstr = self.tcpanmm.GetValue()
        if panmmstr == '':
            panmmstr = '10'
        panmm = float(panmmstr)
	panrightenable = True
	self.mydrawgcode.OnDraw()

    def panupr(self,event):
	global panupenable
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
        global panmm
        panmmstr = self.tcpanmm.GetValue()
        if panmmstr == '':
            panmmstr = '10'
        panmm = float(panmmstr)
	panupenable = True
	self.mydrawgcode.OnDraw()

    def pandownr(self,event):
	global pandownenable
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
        global panmm
        panmmstr = self.tcpanmm.GetValue()
        if panmmstr == '':
            panmmstr = '10'
        panmm = float(panmmstr)
	pandownenable = True
	self.mydrawgcode.OnDraw()

    def zoominr(self,event):
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
	global zoominenable
        global zoompercent
        zoompercentstr = self.tczoompercent.GetValue()
        if zoompercentstr == '':
            zoompercentstr = '125'
        zoompercent = float(zoompercentstr)
	zoominenable = True
	self.mydrawgcode.OnDraw()

    def zoomoutr(self,event):
	global drawrotdegno
	drawrotdegno = 0.0
	global redrawrun
	redrawrun = False
	global zoomoutenable
        global zoompercent
        zoompercentstr = self.tczoompercent.GetValue()
        if zoompercentstr == '':
            zoompercentstr = '125'
        zoompercent = float(zoompercentstr)
	zoomoutenable = True
	self.mydrawgcode.OnDraw()


    def drawmouser(self,event):
        global doxrot
        doxrot = False
        global doyrot
        doyrot = False
        global dozrot
        dozrot = False
        global drawmouse
        drawmouse = True

app = wx.PySimpleApp()
frame = MainWindow()
app.MainLoop()

# Delete objects, so that this script works more than once
del frame
del app

