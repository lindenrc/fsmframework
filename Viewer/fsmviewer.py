# Run tkinter code in another thread

import tkinter as tk
import threading
import logging
import acsys.dpm
import time
from fsmemulator import getSupercycleDemo
from fsmemulator import getCountdownDemo
from fsmemulator import FsmEmulator
from fsmdisplay import FsmDisplay

class FsmFrame(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.fsm = 0
		self.dsp = 0
		self.deviceList = []
		self.canvas = 0
		self.isLoaded = False
		self.isStarted = False
		self.start()

	def callback(self):
		self.root.quit()

	def loadFsm(self):
		self.isLoaded = True
		self.fsm = getCountdownDemo()
		self.deviceList = self.fsm.setup()
		self.dsp = FsmDisplay(self.fsm.name, [1000, 600])
		self.dsp.setup(self.fsm)

		self.root.title(self.dsp.name)
		self.canvas = tk.Canvas(self.root, width=self.dsp.bounds[0], height=self.dsp.bounds[1])
		self.canvas.pack(side=tk.LEFT)

		self.drawTransitions()
		self.drawStates()
		self.drawInputs()
	
	def startFsm(self):
		if self.isLoaded:
			self.isStarted = True
		else:
			print('No Displays Loaded')
		
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
		sepX = 50
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

	def drawTransition(self, from_index, to_index):
		fromState = self.dsp.states[from_index]
		toState = self.dsp.states[to_index]
		x1 = fromState.bounds[0] + fromState.bounds[2]/2
		y1 = fromState.bounds[1] + fromState.bounds[3]/2
		x2 = toState.bounds[0] + toState.bounds[2]/2
		y2 = toState.bounds[1] + toState.bounds[3]/2
		self.canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
		
	def drawOutput(self, state_index, output_index, value):
		state = self.dsp.states[state_index]
		output = state.outputs[output_index]
		sepX = 50
		sepY = 10
		textH = 10
		xText = state.bounds[0] + sepX
		yText = state.bounds[1] + state.bounds[3] + sepY + output_index*textH
		
		if len(state.outputTags) > output_index:
			self.canvas.delete(state.outputTags[output_index])
			
		state.outputTags = [0, 0, 0, 0]
		state.outputTags[output_index] = self.canvas.create_text(xText, yText, text=output.parameters[0].format( value ) )		
		
	def drawStates(self):
		for state_index in range( len( self.dsp.states ) ):
			self.drawState( state_index, state_index == self.dsp.startState )
	
	def drawTransitions(self):
		for state in self.dsp.states:
			for transition in state.transitions:
				self.drawTransition(transition.from_index, transition.to_index)
	
	def drawInputs(self):
		frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
		frame.pack(fill = tk.Y, side=tk.RIGHT, expand=True)
		label = tk.Label(frame, text="Fsm Inputs")
		label.pack()
		for input in self.dsp.inputs:
			row = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
			row.pack()
			button = tk.Button(row, text="Send", command = lambda: self.send( input.parameters[0], text.get()))
			button.pack(side=tk.RIGHT)
			text = tk.Entry(row, width=10)
			text.pack(side=tk.RIGHT)
			label = tk.Label(row, text=input.parameters[1])
			label.pack(side=tk.RIGHT)
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
		
		#self.canvas = tk.Canvas(self.root, width=self.dsp.bounds[0], height=self.dsp.bounds[1])
		#self.canvas.pack(side=tk.LEFT)

		#self.drawTransitions()
		#self.drawStates()
		#self.drawInputs()
		
		self.root.mainloop()


async def my_app(con):

	
    # Setup context

	async with acsys.dpm.DPMContext(con) as dpm:

        # Add acquisition requests
		fsm = fsmFrame.fsm
		deviceList = fsmFrame.deviceList
		
		count = 0
		for device in deviceList:
			await dpm.add_entry(count, device)
			count = count + 1
			
        # Start acquisition

		await dpm.start()

        # Process incoming data

		fsmFrame.showTransition(fsm.previousState, fsm.currentState)
		
		async for ii in dpm:
			fsm.setDevice( ii.meta['name'], ii.data )
			fsm.execute()
			fsmFrame.fsmFrame.showTransition(fsm.previousState, fsm.currentState)
			if fsm.previousState != fsm.currentState:
				fsmFrame.showOutput(fsm.previousState, fsm.states[fsm.previousState].displayMap)			
			fsmFrame.showOutput(fsm.currentState, fsm.states[fsm.currentState].displayMap)


#Launch FsmViewer

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('acsys')
log.setLevel(logging.INFO)


fsmFrame = FsmFrame()

while not fsmFrame.isStarted:
	time.sleep(1)
	
acsys.run_client(my_app)