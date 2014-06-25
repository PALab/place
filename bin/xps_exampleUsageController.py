'''
XPS example
NOTE: insert IP address for controller on line 16, and user name/password on line 21
@author: henrik
'''
def main():
    initializeStuff()
    doStuff()

def initializeStuff():
    from pypal.automate.xps_control.XPS_C8_drivers import XPS
    global xps
    xps = XPS()
    xps.GetLibraryVersion()
    global socketId
    socketId = xps.TCP_ConnectToServer("xxx.xxx.x.xxx",5001,3)

    print "connected to: ", socketId
    #print xps.CloseAllOtherSockets(socketId)
    xps.ControllerStatusGet(socketId)
    xps.Login(socketId, "username", "password")
    #print self.xps.GroupStatusListGet(self.socketId)
    print "Controller is initialized."

def doStuff():
    global xps
    print xps.GroupKill(socketId, "GROUP1")
    print xps.GroupInitialize(socketId, "GROUP3")
    #print self.xps.GroupStatusGet(socketId, "GROUP3")
    #print xps.GroupHomeSearch(socketId, "GROUP3")
    #print xps.GatheringConfigurationSet(socketId,["GROUP3.POSITIONER.CurrentPosition"])
    #print xps.GatheringRun(socketId, 1000, 100)
    #print xps.GroupHomeSearch(socketId, "GROUP3")
    xps.GroupJogParametersSet(socketId, "GROUP1", [10], [0.])
    print 'Jog Command sent'
    print xps.GroupMoveAbsolute(socketId, "GROUP1", [20.])
    #print xps.GatheringStopAndSave(socketId)
    #data= xps.GatheringDataGet(socketId, 1)
    #print xps.GatheringConfigurationGet(socketId)

    print xps.TCP_CloseSocket(socketId)
    print "connection to Controller finished."

if __name__ == '__main__':
    main()
