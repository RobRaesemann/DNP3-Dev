from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
import time

# Create the manager for DNP3. This is always the first thing you
# need to do for OpenDNP3.
log_handler = asiodnp3.ConsoleLogger().Create()
manager = asiodnp3.DNP3Manager(1, log_handler)
retry = asiopal.ChannelRetry().Default()
listener = asiodnp3.PrintingChannelListener().Create()
channel = manager.AddTCPClient('client', opendnp3.levels.NOTHING, retry, '192.168.69.151', '0.0.0.0', 20000, listener)

SLEEP_SECONDS = 5

# The sequence of events handler - this receives measurment
# data from the master and prints it to the console. We need
# a custom implementation because the default printing one is
# not so useful
class SOEHandler(opendnp3.ISOEHandler):
    def __init__(self):
        super(SOEHandler, self).__init__()

    def Process(self, info, values):
        print(f'values {values.Count()}\ttype: {type(values)}')
       
        if (type(values) == opendnp3.ICollectionIndexedAnalog):
            class BOSVisitor(opendnp3.IVisitorIndexedAnalog):
                def __init__(self):
                    super(BOSVisitor, self).__init__()
                def OnValue(self, indexed_instance):
                    print(indexed_instance.index, indexed_instance.value.value)
            values.Foreach(BOSVisitor())

    def Start(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass

    def End(self):
        # This is implementing an interface, so this function
        # must be declared.
        pass

soe_handler = SOEHandler()

master_application = asiodnp3.DefaultMasterApplication().Create()
stack_config = asiodnp3.MasterStackConfig()
stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
stack_config.link.RemoteAddr = 10
master = channel.AddMaster('master', soe_handler, master_application, stack_config)
master.Enable()

time.sleep(SLEEP_SECONDS)
# NUMBER_OF_OUTPUTS = 20
# group_variation = opendnp3.GroupVariationID(30, 5)
# master.ScanRange(group_variation, 0, NUMBER_OF_OUTPUTS)

while(1):
    time.sleep(120)



master.Disable()
master = None
channel.Shutdown()
channel = None
manager.Shutdown()