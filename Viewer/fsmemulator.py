#!/usr/bin/env python3
from simpleeval import simple_eval
import time

class DeviceReading:
	def __init__(self, data):
		self.data = data
		self.isStale = False

#INPUT = ( SOURCE, PARAMETERS )
#READING , (G:SCTIME)
#INTERNAL , (NAME)
#USER, (NAME)	
class FsmInput:
	def __init__(self, source, parameters):
		self.source = source
		self.parameters = parameters
		self.data = 0

	def load(self, data):
		self.data = data
		
	def execute(self):
		return self.data

class FsmExpression:
	def __init__(self,expressionString):
		self.expressionString = expressionString;
		self.inputs = []
		
	def addInput(self,input):
		self.inputs.append(input)		
		
	def execute(self):
		try:
			mapping = {}
			mapping['time'] = 1000*time.time()
			inp_index = 1
			for input in self.inputs:
				key = "x"+str(inp_index)
				inp_index = inp_index + 1
				mapping[key] = input.execute()
				
			expressions = []
			for expression in self.expressionString.split(";"):
				if len( expression.strip() ) > 0:
					expressions.append( expression.strip() )
			result = 0
			for expression in expressions:
				split = expression.split(":=")
				if len(split) == 1:
					result = simple_eval( split[0], names=mapping )
				elif len(split) == 2:
					result = simple_eval( split[1], names=mapping )
					mapping[split[0]] = result
			return result
		except Exception as e:
			print('Exception: ', self.expressionString, ' : ', str(e))
			return 0
				
class FsmCondition:
	def __init__(self,expressionString):
		self.expression = FsmExpression(expressionString)

	def addInput(self, input):
		self.expression.addInput(input)
		
	def execute(self):
		return self.expression.execute()
		

#OUTPUT = (DESTINATION, PARAMETERS)
#INTERNAL, (NAME)
#PRINTOUT,()
#DISPLAY, (NAME)
#SETTING, (Z:CACHE)		
class FsmOutput:
	def __init__(self, destination, parameters, expressionString):
		self.destination = destination
		self.parameters = parameters
		self.expression = FsmExpression(expressionString)
		self.internalMap = {}
		self.settingValuesList = []
		self.displayMap = {}
	
	def addInput(self, input):
		self.expression.addInput(input)
		
	def execute(self):
		result = self.expression.execute()
		if self.destination == 'PRINTOUT':
			print('Output = ', result )
		elif self.destination == 'INTERNAL':
			self.internalMap[self.parameters[0]] = result
		elif self.destination == 'DISPLAY':
			self.displayMap[self.parameters[0]] = result
		elif self.destination == 'SETTING':
			self.settingValuesList.append(parameters[1]+":"+result)

class FsmAction:
	def __init__(self, when, conditionString):
		self.when = when
		self.condition = FsmCondition(conditionString)
		self.outputs = []
		
	def addOutput(self, output):
		self.outputs.append(output)
		
	def execute(self, when):
		if when == self.when and self.condition.execute():
			for output in self.outputs:
				output.execute()
					
class FsmTransition:
	def __init__(self, conditionString, nextState):
		self.condition = FsmCondition(conditionString)
		self.nextState = nextState
		
	def execute(self):
		return self.condition.execute()
		
class FsmState:
	def __init__(self, name):
		self.name = name
		self.transitions = []
		self.actions = []
		self.displayMap = {}
		
	def addTransition(self, transition):
		self.transitions.append(transition)
		
	def addAction(self, action):
		self.actions.append(action)
		
	def execute(self, isNewState, currentState):
		if isNewState:
			for action in self.actions:
				action.execute('ON_ENTERING_STATE')
		
		for action in self.actions:
			action.execute('WITHIN_STATE')
			
		for transition in self.transitions:
			if transition.execute():
				for action in self.actions:
					action.execute('ON_EXITING_STATE')
				return transition.nextState
		
		return currentState

class FsmEmulator:


	def __init__(self, name, startState, endState, parameters):
		self.name = name
		self.startState = startState
		self.endState = endState
		self.parameters = parameters
		self.previousState = -1
		self.currentState = startState
		self.isNewState = True
		self.isRunning = True
		self.states = []
		self.readingList = []
		self.settingList = []
		self.settingValuesList = []
		self.deviceMap = {}
		self.internalMap = {}
		self.inputMap = {}
		
	def getAllInputs(self, type):
		inputList = []
		for state in self.states:
			for transition in state.transitions:
				for input in transition.condition.expression.inputs:
					if type == input.source:
						inputList.append(input)
			for action in state.actions:
				for input in action.condition.expression.inputs:
					if type == input.source:
						inputList.append(input)
				for output in action.outputs:
					for input in output.expression.inputs:
						if type == input.source:
							inputList.append(input)
							
		return inputList

	def getStateInputs(self, state_index, type):
		inputList = []
		state = self.states[state_index]
		for transition in state.transitions:
			for input in transition.condition.expression.inputs:
				if type == input.source:
					inputList.append(input)
		for action in state.actions:
			for input in action.condition.expression.inputs:
				if type == input.source:
					inputList.append(input)
			for output in action.outputs:
				for input in output.expression.inputs:
					if type == input.source:
						inputList.append(input)
							
		return inputList	
		
	def getAllOutputs(self, type):
		outputList = []
		for state in self.states:
			for action in state.actions:
				for output in action.outputs:
					if type == output.destination:
						outputList.append(output)
											
		return outputList

	def getStateOutputs(self, currentState, type):
		outputList = []
		state = self.states[currentState]
		for action in state.actions:
			for output in action.outputs:
				if type == output.destination:
					outputList.append(output)
					
		return outputList
				
	def addState(self, state):
		self.states.append(state)
		
	def loadInputs(self, currentState):
		self.loadInternalInputs(currentState)
		self.loadUserInputs(currentState)
		if self.loadDeviceInputs(currentState) == False:
			return False
		return True
		
	def loadInternalInputs(self, currentState):
		inputList = self.getStateInputs(currentState, 'INTERNAL')
		for input in inputList:
			if input.parameters[0] in self.internalMap:
				datum = self.internalMap[input.parameters[0]]
				input.load(datum)
			else:
				datum = 0
				input.load(datum)
		return True
		
	def loadUserInputs(self, currentState):
		inputList = self.getStateInputs(currentState, 'USER')
		for input in inputList:
			if input.parameters[0] in self.inputMap:
				datum = self.inputMap[input.parameters[0]]
				input.load(datum)
			else:
				datum = 0
				input.load(datum)

	def loadDeviceInputs(self, currentState):
		inputList = self.getStateInputs(currentState, 'READING')
		for input in inputList:
			if not ( input.parameters[1] in self.deviceMap ):
				return False
			else:
				deviceReading = self.deviceMap[input.parameters[1]]
				if deviceReading.isStale:
					return False
				
		for input in inputList:
			deviceReading = self.deviceMap[input.parameters[1]]
			input.load(deviceReading.data)
			deviceReading.isStale = True
			self.deviceMap[input.parameters[1]] = deviceReading
			
		return True
		
	def setup(self):
		list = []
		ftd = 1000
		if len(self.parameters) > 0:
			ftd = self.parameters[0]
		inputList = self.getAllInputs('READING')
		tag = 0
		for input in inputList:
			device = input.parameters[0]+'@P,'+str(ftd)
			if not ( device in list ):
				input.parameters[1] = tag
				tag = tag + 1
				list.append( device )
			else:
				input.parameters[1] = list.index( device )
				
		if len(list) == 0:
			list.append('M:OUTTMP'+'@P,'+str(ftd))
					
		outputList = self.getAllOutputs('INTERNAL')
		for output in outputList:
			output.internalMap = self.internalMap
	
		tag = 0
		outputList = self.getAllOutputs('SETTING')
		for output in outputList:
			device = output.parameters[0]
			if device in self.settingList:
				output.parameters[1] = self.settingList.index(device)
			else:
				output.parameters[1] = tag
				tag = tag + 1
				self.settingList.append(device)
			output.settingValuesList = self.settingValuesList
	
		for state_index in range( len(self.states) ):
			outputList = self.getStateOutputs(state_index, 'DISPLAY')
			for output in outputList:
				output.displayMap = self.states[state_index].displayMap

		self.readingList = list
		
	def setUserInput(self, key, value):
		self.inputMap[key] = float(value)
	
	def setDevice(self, tag, reading):
		if tag in self.deviceMap:
			deviceReading = self.deviceMap[tag]
			deviceReading.data = reading
			deviceReading.isStale = False
			self.deviceMap[tag] = deviceReading
		else:
			deviceReading = DeviceReading(reading)
			self.deviceMap[tag] = deviceReading

		
	def execute(self):
		if self.isRunning and self.loadInputs(self.currentState):
			self.isRunning = self.currentState != self.endState
			state = self.states[self.currentState]
			nextState = state.execute(self.isNewState, self.currentState)
			self.isNewState = self.currentState != nextState
			self.previousState = self.currentState
			self.currentState = nextState
			
def getDemo():
	fsm = FsmEmulator('Demo', 0, 1, [])
	start_s = FsmState('Start')
	s_tra = FsmTransition('True', 1)
	s_act = FsmAction('WITHIN_STATE', 'True')
	s_out = FsmOutput('PRINTOUT', [], 'x1 + 6')
	s_in = FsmInput("CONSTANT", [])
	s_out.addInput(s_in)

	s_act.addOutput(s_out)
	start_s.addTransition(s_tra)
	start_s.addAction(s_act)

	end_s = FsmState('End')
	e_tra = FsmTransition('True', 0)
	e_act = FsmAction('WITHIN_STATE', 'True')
	e_out = FsmOutput('PRINTOUT', [], 'x1 + 10')
	e_in = FsmInput("CONSTANT", [])
	e_out.addInput(e_in)

	e_act.addOutput(e_out)
	end_s.addTransition(e_tra)
	end_s.addAction(e_act)

	fsm.addState(start_s)
	fsm.addState(end_s)
	return fsm

def getSupercycleDemo():
	fsm = FsmEmulator('Supercycle Demo', 0, -1, [])
	
	start_s = FsmState('Start')
	s_tra = FsmTransition('x1 > 30', 1)
	st_in = FsmInput("READING", ["G:SCTIME","0"])
	s_tra.condition.addInput(st_in)
	
	s_act = FsmAction('WITHIN_STATE', 'True')
	s_out = FsmOutput('DISPLAY', ["Output"], 'y := x1')
	s_in = FsmInput("READING", ["P:ISSTAT.STATUS.RAW","0"])
	s_out.addInput(s_in)

	s_act.addOutput(s_out)
	start_s.addTransition(s_tra)
	start_s.addAction(s_act)

	end_s = FsmState('End')
	e_tra = FsmTransition('x1 < 30', 0)
	et_in = FsmInput("READING", ["G:SCTIME","0"])
	e_tra.condition.addInput(et_in)
	
	e_act = FsmAction('WITH_STATE', 'True')
	e_out = FsmOutput('DISPLAY', ["Output"], 'y := x1')
	e_in = FsmInput("READING", ["G:SCTIME","0"])
	e_out.addInput(e_in)

	e_act.addOutput(e_out)
	end_s.addTransition(e_tra)
	end_s.addAction(e_act)

	fsm.addState(start_s)
	fsm.addState(end_s)
	return fsm
	
	
def getCountdownDemo():
	fsm = FsmEmulator('Countdown Demo', 0, -1, [])
	next = [1,3,0,5,2,7,4,9,6,8]
	dlys = [0, 5, 45, 10, 40, 15, 35, 20, 30, 25]
	for state_index in range(10):
		state = FsmState("State " + str(state_index + 1))
		
		transition = FsmTransition("x1 > " + str(dlys[state_index]), next[state_index] )
		t_input = FsmInput('READING',['G:SCTIME'])
		
		if state_index == 0:
			t_input = FsmInput('USER', ['input', 'Enter Value'])
			
		transition.condition.addInput(t_input)

		when = 'ON_ENTERING_STATE'
		when = 'WITHIN_STATE'
			
		action = FsmAction(when, 'True')
		output = FsmOutput('DISPLAY', ['Output'], 'x1')
		o_input = FsmInput('READING',['G:SCTIME'])	
		
		output.addInput(o_input)
		action.addOutput(output)
		
		state.addTransition(transition)
		state.addAction(action)
		
		fsm.addState(state)
		
	return fsm
		

		
#print('Demo Started')

#fsm = getDemo()
#fsm.execute()

#print('Demo Completed')