#!/usr/bin/env python3

import logging
from fsmemulator import FsmEmulator

class FsmInputDisplay:
	def __init__(self, type, parameters):
		self.type = type
		self.parameters = parameters
		
class FsmOutputDisplay:
	def __init__(self, type, parameters):
		self.type = type
		self.parameters = parameters
		
class FsmTransitionDisplay:
	def __init__(self, from_index, to_index, parameters):
		self.from_index = from_index
		self.to_index = to_index
		self.parameters = parameters
		
class FsmStateDisplay:
	def __init__(self, name, bounds):
		self.name = name
		self.bounds = bounds
		self.stateTags = []
		self.outputTags = []
		self.transitions = []
		self.outputs = []
		
	def addTransition(self, transition):
		self.transitions.append(transition)
		
	def addOutput(self, output):
		self.outputs.append(output)

		
class FsmDisplay:
	
	def __init__(self, name, layout,  bounds):
		self.name = name
		self.layout = layout
		self.bounds = bounds
		self.startState = -1
		self.endState = -1
		self.states = []
		self.inputs = []
		
	def addState(self, state):
		self.states.append(state)
		
	def addInput(self, input):
		self.inputs.append(input)
		
	def setupPlacement(self):
		if self.layout == 'Rectangle':
			hgt = 50
			sepX = 20
			sepY = 50
			leftX = sepX
			rightX = self.bounds[0]-sepX-self.states[0].bounds[2]
			upY = sepY
			left = True
		
			for state in self.states:
				state.bounds[0] = leftX
				state.bounds[1] = upY
				if not left:
					state.bounds[0] = rightX
					upY = upY + sepY + hgt
				left = not left
			
	
	def setupInputs(self, fsm):
		inputList = fsm.getAllInputs('USER')
		found = []
		input_index = 0
		for input in inputList:
			if not ( input.parameters[0] in found  ):
				found.append( input.parameters[0] )
				input_index = input_index + 1
				inputDisplay = FsmInputDisplay('TEXT', [input.parameters[0], input.parameters[1]] )
				self.addInput(inputDisplay)
				
	
	def setup(self, fsm):
		wth = 100
		hgt = 50
		sepX = 20
		sepY = 50
		leftX = sepX
		rightX = self.bounds[0]-sepX-wth
		upY = sepY
		left = True
		
		self.startState = fsm.startState
		self.endState = fsm.endState
		
		state_index = 0
		for state in fsm.states:
			b1 = [leftX, upY, wth, hgt]
			if not left:
				b1[0] = rightX
				upY = upY + sepY + hgt
			stateDisplay = FsmStateDisplay(state.name, b1)
			outputDisplay = FsmOutputDisplay('TEXT', ['{:.3f}'])
			stateDisplay.addOutput(outputDisplay)
			for transition in state.transitions:
				transitionDisplay = FsmTransitionDisplay(state_index, transition.nextState, [])
				stateDisplay.addTransition(transitionDisplay)
				
			self.addState(stateDisplay)
			state_index = state_index + 1
			left = not left
			
		self.setupInputs(fsm)