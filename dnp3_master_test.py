

from dnp3_master import Dnp3_Master



async def create_Dnp3_Master():
    print("Creating test master")
    newmaster = Dnp3_Master('192.168.69.166',10)
    newmaster.open()

    while(1):
        time.sleep(5)
        values = newmaster.values
        print('==========================================')
        print(values)


loop = asyncio.get_event_loop()
asyncio.ensure_future(create_Dnp3_Master())
loop.run_forever()
loop.close()
