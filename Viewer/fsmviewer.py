# Run tkinter code in another thread

import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading
import logging
import acsys.dpm
import time
from fsmemulator import getSupercycleDemo
from fsmemulator import getCountdownDemo
from fsmemulator import FsmEmulator
from fsmdisplay import FsmDisplay
from fsmxmlparser import parse

class FsmFrame(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.fsm = 0
		self.dsp = 0
		self.canvas = 0
		self.widgets = []
		self.state = 'INIT_FSM'
		self.isRunning = True
		self.isStopped = False
		self.areSettingsEnabled = False
		self.start()

	def callback(self):
		self.root.quit()

	def loadDemo(self):
	
		self.fsm = getSupercycleDemo()
		self.fsm.setup()
		self.dsp = FsmDisplay(self.fsm.name, 'Rectangle', [400, 400])
		self.dsp.setup(self.fsm)
		
		self.root.title(self.dsp.name)
		self.canvas = tk.Canvas(self.root, width=self.dsp.bounds[0], height=self.dsp.bounds[1])
		self.canvas.pack(side=tk.LEFT)

		self.drawTransitions()
		self.drawStates()
		self.drawInputs()
		
		self.state = 'LOAD_FSM'
		
	def loadFsm(self):
		
		self.deleteWidgets()
		filename = askopenfilename()
		result = parse(filename)
		
		self.fsm = result[0]
		self.dsp = result[1]

		self.root.title(self.dsp.name)
		self.canvas = tk.Canvas(self.root, width=self.dsp.bounds[0], height=self.dsp.bounds[1])
		self.canvas.pack(side=tk.LEFT)

		self.drawTransitions()
		self.drawStates()
		self.drawInputs()
		
		self.state = 'LOAD_FSM'
	
	def deleteWidgets(self):
		for widget in self.widgets:
			widget.destroy()
		self.widgets = []
		self.canvas.delete('all')
		self.canvas.destroy()
			
	def startFsm(self):
		if self.state == 'LOAD_FSM':
			self.state = 'RUN_FSM'
		else:
			print('No Displays Loaded')
		
	def stopFsm(self):
		self.isStopped = True
		
	def toggleSettings(self):
		self.areSettingsEnabled = not self.areSettingsEnabled
		utext = 'Settings Disabled'
		if self.areSettingsEnabled:
			utext = 'Settings Enabled'
		self.toggle.config(text=utext)
		
	def showTransition(self, from_index, to_index):
		if from_index != to_index and from_index >= 0:
			self.drawState( from_index, False)
			
		if from_index != to_index and to_index >= 0:
			self.drawState( to_index, True)
			
	def showOutput(self, state_index, displayMap):
		output_index = 0
		for value in displayMap.values():
			self.drawOutput( state_index, output_index, value)
			output_index = output_index + 1
			
	def drawState(self, state_index, isCurrent):
		state = self.dsp.states[state_index]
		color = "black"
		border = 3
		sepX = state.bounds[2]/2
		sepY = -4
		xText = state.bounds[0] + sepX
		yText = state.bounds[1] + state.bounds[3]/2 + sepY
		
		if isCurrent:
			color = "green"
			
		if len(state.stateTags) > 0:
			self.canvas.delete(state.stateTags[0])
			self.canvas.delete(state.stateTags[1])
			self.canvas.delete(state.stateTags[2])
		
		state.stateTags = [0,0,0]
		state.stateTags[0] = self.canvas.create_rectangle(state.bounds[0], state.bounds[1], state.bounds[0]+state.bounds[2], state.bounds[1]+state.bounds[3], fill=color)
		state.stateTags[1] = self.canvas.create_rectangle(state.bounds[0] + border + 1, state.bounds[1] + border + 1, state.bounds[0]+state.bounds[2]-2*border, state.bounds[1]+state.bounds[3]-2*border, fill="white")
		state.stateTags[2] = self.canvas.create_text(xText, yText, text=state.name )
		
	def drawTransition(self, from_index, to_index, connections):
		fromState = self.dsp.states[from_index]		
		toState = self.dsp.states[to_index]
		bounds1 = fromState.bounds
		bounds2 = []
		for connection in connections:
			bounds2 = connection.bounds
			self.drawTransitionBetween(bounds1, bounds2)
			bounds1 = bounds2
		bounds2 = toState.bounds
		self.drawTransitionBetween(bounds1, bounds2)

	def drawTransitionBetween(self, bounds1, bounds2):
		x1 = bounds1[0] + bounds1[2]/2
		y1 = bounds1[1] + bounds1[3]/2
		x2 = bounds2[0] + bounds2[2]/2
		y2 = bounds2[1] + bounds2[3]/2
		self.canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
		
	def drawOutput(self, state_index, output_index, value):
	
		if isinstance(value, list):
			value = value[0]
			
		state = self.dsp.states[state_index]
		output = state.outputs[output_index]
		sepX = state.bounds[2]/2
		sepY = 15
		textH = 10
		border = 1
		xText = state.bounds[0] + sepX
		yText = state.bounds[1] + state.bounds[3] + sepY + output_index*textH
		
		if len(state.outputTags) == 0:
			state.outputTags = [0, 0, 0, 0]
			state.outputTags[0] = self.canvas.create_rectangle(state.bounds[0], state.bounds[1]+state.bounds[3], state.bounds[0]+state.bounds[2], state.bounds[1]+state.bounds[3]+sepY+2*textH, fill='white')
			state.outputTags[1] = self.canvas.create_rectangle(state.bounds[0] + border + 1, state.bounds[1]+state.bounds[3] + border + 1, state.bounds[0]+state.bounds[2]-2*border, state.bounds[1]+state.bounds[3]+sepY+2*textH-2*border, fill="cyan")
		
		if  not (state.outputTags[output_index+2] == 0 ):
			self.canvas.delete(state.outputTags[output_index+2])
			
		state.outputTags[output_index+2] = self.canvas.create_text(xText, yText, text=output.parameters[0].format( value ) )		

	def drawStates(self):
		for state_index in range( len( self.dsp.states ) ):
			self.drawState( state_index, state_index == self.dsp.startState )
	
	def drawTransitions(self):
		for state in self.dsp.states:
			for transition in state.transitions:
				self.drawTransition(transition.from_index, transition.to_index, transition.connections)
	
	def drawInputs(self):
		if len(self.dsp.inputs) == 0:
			return
		frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
		frame.pack(fill = tk.Y, side=tk.RIGHT, expand=True)
		label = tk.Label(frame, text="Fsm Inputs")
		label.pack()
		
		self.widgets.append(frame)
		self.widgets.append(label)
		for input in self.dsp.inputs:
			row = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
			row.pack()
			button = tk.Button(row, text="Send", command = lambda: self.send( input.parameters[0], text.get()))
			button.pack(side=tk.RIGHT)
			text = tk.Entry(row, width=10)
			text.pack(side=tk.RIGHT)
			label = tk.Label(row, text=input.parameters[1])
			label.pack(side=tk.RIGHT)
			self.widgets.append(row)
			
	def send(self, key, value):
		try:
			self.fsm.setUserInput(key, float(value))
		except:
			print('Invalid input')
		
			
	def run(self):
		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)
		top = tk.Frame(self.root, width = 800, height = 200, relief=tk.RAISED, borderwidth=1)
		top.pack(fill=tk.BOTH, expand=True)

		load = tk.Button(top, text="Load Fsm", command = self.loadFsm)
		load.pack(side=tk.LEFT)
		start = tk.Button(top, text="Start Fsm", command = self.startFsm)
		start.pack(side=tk.LEFT)
		stop = tk.Button(top, text="Stop Fsm", command = self.stopFsm)
		stop.pack(side=tk.LEFT)
		self.toggle = tk.Button(top, text="Settings Disabled", command = self.toggleSettings)
		self.toggle.pack(side=tk.LEFT)
		
		self.loadDemo()
		
		self.root.mainloop()


async def my_app(con):

	fsm = 0
	while fsmFrame.isRunning:
		
		if fsmFrame.state == 'INIT_FSM':
			time.sleep(1)
		elif fsmFrame.state == 'LOAD_FSM':
			fsm = fsmFrame.fsm
			time.sleep(1)
		elif fsmFrame.state == 'RUN_FSM':

			fsm = fsmFrame.fsm
			try:
			
				async with acsys.dpm.DPMContext(con) as dpm:

					while fsmFrame.isRunning:
		
						if fsmFrame.state == 'INIT_FSM':
							time.sleep(1)
						elif fsmFrame.state == 'LOAD_FSM':
							fsm = fsmFrame.fsm
							time.sleep(1)
						elif fsmFrame.state == 'RUN_FSM':
							try:
								count = 0
								for device in fsm.readingList:
									await dpm.add_entry(count, device)
									count = count + 1
			
								for device in fsm.settingList:
									await dpm.add_entry(count, device)
									count = count + 1
											
								await dpm.start()

								fsmFrame.showTransition(fsm.previousState, fsm.currentState)
				
								async for ii in dpm:
									if fsmFrame.isStopped:
										fsmFrame.isStopped = False
										fsmFrame.state = 'LOAD_FSM'
										await dpm.clear_list()
										await dpm.stop()
										break
									if isinstance(ii, acsys.dpm.ItemData):
										fsm.setDevice( ii.tag, ii.data )
									fsm.execute()
									
									if fsmFrame.areSettingsEnabled:
										for id,device in fsm.settingMap.items():
											split = device.split(',')
											tag = split[0]
											value = split[1]
											await dpm.apply_settings([(tag,value)])
									fsm.settingMap.clear()
			
									fsmFrame.showTransition(fsm.previousState, fsm.currentState)
									if fsm.previousState != fsm.currentState:
										fsmFrame.showOutput(fsm.previousState, fsm.states[fsm.previousState].displayMap)			
									fsmFrame.showOutput(fsm.currentState, fsm.states[fsm.currentState].displayMap)
						
							except Exception as e:
								print('Runtime Exception: ', str(e) )
								fsmFrame.state = 'LOAD_FSM'
								
			except Exception as e1:
						print('Startup Exception', str(e1) )
						fsmFrame.state = 'LOAD_FSM'

				
       

#Launch FsmViewer

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('acsys')
log.setLevel(logging.INFO)


fsmFrame = FsmFrame()
while fsmFrame.state != 'RUN_FSM':
	time.sleep(1)
acsys.run_client(my_app)