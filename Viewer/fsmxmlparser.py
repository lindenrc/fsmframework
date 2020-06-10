#!/usr/bin/env python3

from fsmemulator import *
from fsmdisplay import *
import xml.etree.ElementTree as et

def parse(filename):
	fsm = FsmEmulator("",0,-1)
	dsp = FsmDisplay("",'Rectangle', [])
	try:
		tree = et.parse(filename)
		root = tree.getroot()
		fsm = FsmEmulator( root.attrib['name'], int(root.attrib['startState']), int(root.attrib['endState']) )
		bounds = []
		for item in root.attrib['bounds'].split(","):
			bounds.append( float(item) )
		dsp = FsmDisplay( root.attrib['name'], root.attrib['layout'], bounds )
		sta_index = 0
		for state in root:
			bounds = []
			for item in state.get('bounds').split(","):
				bounds.append( float(item) )
			fsm.addState( FsmState(state.attrib['name']) )
			dsp.addState( FsmStateDisplay(state.attrib['name'], bounds) )
			dsp.states[sta_index].addOutput( FsmOutputDisplay("TEXT", state.get('parameters').split(",") ) )
			tra_index = 0
			for transition in state.findall('transition'):
				fsm.states[sta_index].addTransition( FsmTransition(transition.get('expression'), int(transition.get('nextState'))) )
				dsp.states[sta_index].addTransition( FsmTransitionDisplay( sta_index, int(transition.get('nextState')), [] ) )
				for input in transition.findall('input'):
					parameters = input.get('parameters').split(",")
					fsm.states[sta_index].transitions[tra_index].condition.addInput( FsmInput( input.get('source'), parameters) )
				tra_index = tra_index + 1
			act_index = 0;
			for action in state.findall('action'):
				fsm.states[sta_index].addAction( FsmAction(action.get('when'), action.get('expression')) )
				for input in action.findall('input'):
					parameters = input.get('parameters').split(",")
					fsm.states[sta_index].actions[tra_index].condition.addInput( FsmInput( input.get('source'), parameters) )
				out_index = 0
				for output in action.findall('output'):
					parameters = output.get('parameters').split(",")
					fsm.states[sta_index].actions[act_index].addOutput( FsmOutput( output.get('destination'), parameters, output.get('expression') ) )
					for input in output.findall('input'):
						parameters = input.get('parameters').split(",")
						fsm.states[sta_index].actions[act_index].outputs[out_index].addInput( FsmInput( input.get('source'), parameters) )
					out_index = out_index + 1
				act_index = act_index + 1
			sta_index = sta_index + 1
				
				
			
	except Exception as e:
		print("exception: ", str(e))
	
	fsm.setup()
	dsp.setupInputs(fsm)
	dsp.setupPlacement()
	
	return [fsm, dsp]
	
	
