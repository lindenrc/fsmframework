#!/usr/bin/env python3

import logging
import acsys.dpm
from fsmemulator import getSupercycleDemo
from fsmemulator import FsmEmulator

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('acsys')
log.setLevel(logging.INFO)
fsm = getSupercycleDemo()

async def my_app(con):

	deviceList = fsm.setup()
	
    # Setup context

	async with acsys.dpm.DPMContext(con) as dpm:

        # Add acquisition requests

		count = 0
		for device in deviceList:
			await dpm.add_entry(count, device)
			count = count + 1
			
        # await dpm.add_entry(0, 'M:OUTTMP@p,1000')
        # await dpm.add_entry(1, 'X:SCTIME@p,1000')

        # Start acquisition

		await dpm.start()

        # Process incoming data

		async for ii in dpm:
			fsm.setDevice( ii.meta['name'], ii.data )
			fsm.execute()
			

acsys.run_client(my_app)