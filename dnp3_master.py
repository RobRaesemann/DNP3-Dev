import asyncio
from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
import time

# The sequence of events handler - this receives measurment
# data from the master and prints it to the console. We need
# a custom implementation because the default printing one is
# not so useful
class SOEHandler(opendnp3.ISOEHandler):
    
    def _setValues(self, values):
        self._values = values

    def _getValues(self):
        return self._values

    values = property(_getValues, _setValues)

    def __init__(self):
        super(SOEHandler, self).__init__()

    def Process(self, info, values):
        # print("SOE processing")
        # print(f'values {values.Count()}\ttype: {type(values)}')

        a_vals = []
        b_vals = []
               
        if (type(values) == opendnp3.ICollectionIndexedAnalog):
            class BOSVisitor(opendnp3.IVisitorIndexedAnalog):
                def __init__(self):
                    super(BOSVisitor, self).__init__()
                def OnValue(self, indexed_instance):
                    #print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    a_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitor())
            self.values['analog'] = a_vals.copy()

        if (type(values) == opendnp3.ICollectionIndexedBinary):
            class BOSVisitorBin(opendnp3.IVisitorIndexedBinary):
                def __init__(self):
                    super(BOSVisitorBin, self).__init__()
                def OnValue(self, indexed_instance):
                    #print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    b_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitorBin())
            self.values['binary'] = b_vals.copy()

        # print(f'a_vals: {len(a_vals)} b_vals: {len(b_vals)}')
        # print(f'a: {len(self.values["analog"])} b: {len(self.values["binary"])}')
    

    def Start(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass

    def End(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass



class Dnp3_Master:
    _values ={'analog': [],'binary': []}

    def _setValues(self, values):
        self._values = values

    def _getValues(self):
        return self._values

    values = property(_getValues, _setValues)

    def __init__(self,outstation_ip, outstation_id):

        self._soe_handler = SOEHandler()
        self._soe_handler.values = self.values

        log_handler = asiodnp3.ConsoleLogger().Create()

        self._manager = asiodnp3.DNP3Manager(1, log_handler)
        retry = asiopal.ChannelRetry().Default()
        listener = asiodnp3.PrintingChannelListener().Create()
        channel = self._manager.AddTCPClient('client', opendnp3.levels.NOTHING, retry, outstation_ip, '0.0.0.0', 20000, listener)
        master_application = asiodnp3.DefaultMasterApplication().Create()
        stack_config = asiodnp3.MasterStackConfig()
        stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
        stack_config.link.RemoteAddr = outstation_id

        self._master = channel.AddMaster('master', self._soe_handler, master_application, stack_config)

    def open(self):
        
        self._master.Enable()
        self._master.AddClassScan(opendnp3.ClassField().AllClasses(),
                                                          openpal.TimeDuration().Minutes(30),
                                                          opendnp3.TaskConfig().Default())

    def __del__(self):
        channel.Shutdown()
        channel = None
        manager.Shutdown()
        manager = None



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
