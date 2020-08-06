from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
import time

SLEEP_SECONDS = 5

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
        print(f'values {values.Count()}\ttype: {type(values)}')

        global analog_values
        global binary_values

        a_vals = []
        b_vals = []
               
        if (type(values) == opendnp3.ICollectionIndexedAnalog):
            class BOSVisitor(opendnp3.IVisitorIndexedAnalog):
                def __init__(self):
                    super(BOSVisitor, self).__init__()
                def OnValue(self, indexed_instance):
                    print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    a_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitor())
            analog_values = a_vals.copy()
            self.values['analog'] = a_vals.copy()

        if (type(values) == opendnp3.ICollectionIndexedBinary):
            class BOSVisitorBin(opendnp3.IVisitorIndexedBinary):
                def __init__(self):
                    super(BOSVisitorBin, self).__init__()
                def OnValue(self, indexed_instance):
                    print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    b_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitorBin())
            binary_values = b_vals.copy()
            self.values['binary'] = b_vals.copy()

        print(f'a_vals: {len(a_vals)} b_vals: {len(b_vals)}')
        print(f'a: {len(analog_values)} b: {len(binary_values)}')
    

    def Start(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass

    def End(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass





class Testmaster:

    _values = {'analog': [],'binary': []}

    def _setValues(self, values):
        _values = values

    def _getValues(self):
        return _values

    _values = property(_getValues, _setValues)

    def __init__(self):
        soe_handler = SOEHandler()
        soe_handler.values = _values

        # Create the manager for DNP3. This is always the first thing you
        # need to do for OpenDNP3.
        log_handler = asiodnp3.ConsoleLogger().Create()
        manager = asiodnp3.DNP3Manager(1, log_handler)
        retry = asiopal.ChannelRetry().Default()
        listener = asiodnp3.PrintingChannelListener().Create()
        channel = manager.AddTCPClient('client', opendnp3.levels.NOTHING, retry, '10.119.228.83', '0.0.0.0', 20000, listener)



        time.sleep(SLEEP_SECONDS)
        # NUMBER_OF_OUTPUTS = 20
        # group_variation = opendnp3.GroupVariationID(30, 5)
        # master.ScanRange(group_variation, 0, NUMBER_OF_OUTPUTS)

        while(1):
            time.sleep(10)
            # master.AddClassScan(opendnp3.ClassField().AllClasses(),
            #                                               openpal.TimeDuration().Minutes(30),
            #                                               opendnp3.TaskConfig().Default())
            print(f"Analog Value Count: {len(values['analog'])}  Binary: {len(values['binary'])}")


    def __del__(self):
        channel.Shutdown()
        channel = None
        manager.Shutdown()
        manager = None