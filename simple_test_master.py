from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
import time

SLEEP_SECONDS = 5

# The sequence of events handler - this receives measurment
# data from the master and prints it to the console. We need
# a custom implementation because the default printing one is
# not so useful
class SOEHandler(opendnp3.ISOEHandler):

    # Attributes
    def _setValues(self, values):
        self._values = values

    def _getValues(self):
        return self._values

    values = property(_getValues, _setValues)

    def __init__(self):
        super(SOEHandler, self).__init__()

    # Methods
    def Process(self, info, values):
        print(f'values {values.Count()}\ttype: {type(values)}')

        # Temporary vars to hold analog and binary values
        a_vals = []
        b_vals = []
               
        # Handle the analog values       
        if (type(values) == opendnp3.ICollectionIndexedAnalog):
            class BOSVisitor(opendnp3.IVisitorIndexedAnalog):
                def __init__(self):
                    super(BOSVisitor, self).__init__()
                def OnValue(self, indexed_instance):
                    print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    a_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitor())
            # Copy analog values to attribute
            self.values['analog'] = a_vals.copy()

        if (type(values) == opendnp3.ICollectionIndexedBinary):
            class BOSVisitorBin(opendnp3.IVisitorIndexedBinary):
                def __init__(self):
                    super(BOSVisitorBin, self).__init__()
                def OnValue(self, indexed_instance):
                    print(f'({indexed_instance.index}, {indexed_instance.value.value})')
                    b_vals.append(indexed_instance.value.value)
            values.Foreach(BOSVisitorBin())
            # Copy binary values to attribute
            self.values['binary'] = b_vals.copy()

        print(f'a_vals: {len(a_vals)} b_vals: {len(b_vals)}')
        print(f'a: {len(self.values["analog"])} b: {len(self.values["binary"])}')
    

    def Start(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass

    def End(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass



values = {
    'analog': [],
    'binary': []
}


print("Starting")


# Create the manager for DNP3. This is always the first thing you
# need to do for OpenDNP3.
log_handler = asiodnp3.ConsoleLogger().Create()
manager = asiodnp3.DNP3Manager(1, log_handler)
retry = asiopal.ChannelRetry().Default()
listener = asiodnp3.PrintingChannelListener().Create()
channel = manager.AddTCPClient('client', opendnp3.levels.NOTHING, retry, "127.0.0.1", '0.0.0.0', 20000, listener)

soe_handler = SOEHandler()
soe_handler.values = values

master_application = asiodnp3.DefaultMasterApplication().Create()
stack_config = asiodnp3.MasterStackConfig()
stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
stack_config.link.RemoteAddr = 10
master = channel.AddMaster('master', soe_handler, master_application, stack_config)
master.Enable()


time.sleep(SLEEP_SECONDS)

while(1):
    time.sleep(10)
    master.AddClassScan(opendnp3.ClassField().AllClasses(),
                                                openpal.TimeDuration().Minutes(30),
                                                opendnp3.TaskConfig().Default())
    values = soe_handler.values
    print(f"Analog Value Count: {len(values['analog'])}  Binary: {len(values['binary'])}")