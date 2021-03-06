import time
from telnetlib import Telnet
from string import split
from socket import error
from subprocess import call

# class Color for use in class Light (each light has it's own color)
class Color:
    _red    = float(0)
    _green  = float(0)
    _blue   = float(0)
    
    def __init__(self, red=0, green=0, blue=0):
        self.setColor(red, green, blue)
        
    def setColor(self, red=0, green=0, blue=0):
        self._red = red
        self._green = green
        self._blue = blue
        
    def getRed(self):
        return self._red
    
    def getGreen(self):
        return self._green
    
    def getBlue(self):
        return self._blue


# class Light for use in class Boblight
class Light(object):
    _name           = None
    _vScanFrom      = float(0)
    _vScanTo        = float(0)
    _hScanFrom      = float(0)
    _hScanTo        = float(0)
    _speed          = int(0)
    _interpolation  = bool(False)
    _color          = Color(1, 1, 1)
    _setManually    = bool(False)

    
    def __init__(self, name, vSanFrom=0, vScanTo=0, hScanFrom=0, hScanTo=0, setManually=False, color=Color(), speed=0, interpolation=False):
        self._name = str(name)
        self._vScanFrom = float(vSanFrom)
        self._vScanTo = float(vSanFrom)
        self._hScanFrom = float(hScanFrom)
        self._hScanTo = float(hScanTo)
        self._setManually = bool(setManually)
        self._color = Color(color)
        self._speed = int(speed)
        self._interpolation = bool(interpolation)
    
    def setInterpolation(self, interpolation):
        self._interpolation = interpolation
            
    def setSetManually(self, setManually):
        self._setManually = setManually
        
    def setSpeed(self, speed):
        self._speed = speed
        
    def getName(self):
        return self._name
    
    def getSpeed(self):
        return self._speed
    
    def getColor(self):
        return self._color
    
    def getHScanFrom(self):
        return self._hScanFrom
    
    def getHScanTo(self):
        return self._hScanTo
    
    def getVScanFrom(self):
        return self._vScanFrom
    
    def getVScanTo(self):
        return self._vScanTo
    
    def getInterpolation(self):
        return self._interpolation


# class Boblight for usage in your own code ;)
class Boblight:
    # strings for communication with boblightd
    _HELLO                  = "hello\n"
    _GETLIGHTS              = "get lights\n"
    _SETPRIORITY            = "set priority {0}\n"
    _SETLIGHTRGB            = "set light {0} rgb {1} {2} {3}\n"
    _SETLIGHTSPEED          = "set light {0} speed {1}\n"
    _SETLIGHTINTERPOLATION  = "set light {0} interpolation {1}\n"
    _SYNC                   = "sync\n"
    _PING                   = "ping\n"
    
    # helper strings
    _EOL        = "\n"
    _SPLITTER   = " "
    
    # attributes for server connection
    _host = None
    _port = None
    
    # attributes where our data is stored into
    _tn         = None
    _light      = []
    _priority   = int(254)
    _brightness = 1
    
    # helper attributes
    _timeout    = 1
    _reconnect  = False
    
    def __init__(self, host="", port=19333, priority=255, timeout=1):
        if host != "":
            self._timeout=timeout
            self.connect(host, port)
            self.setPriority(priority)
        else:
            raise Boblight.ConnectionError("At least <host> must be given!")
        
    def connect(self, host, port=19333):
        if self._tn:
            raise Boblight.ConnectionError("Already Connected!")
        else:
            self._host = host
            self._port = port
            try:
                hi = ""
                while hi == "":
                    print "Open connection"
                    self._tn = Telnet(host, port)
                    if self._tn:
                        print "Opened connection"
                    else:
                        print "Open connection failed"
                    
                    print "Say HELLO"
                    self._tn.write(self._HELLO)
                    hi = self._tn.read_until(self._EOL, self._timeout)
                    
                    if hi == "":
                        print "HELLO failed, restart daemon"
                        self._restartBoblightDaemon()
                    else:
                        print "Server said HELLO"
                    
                if not self._reconnect:
                    self._getLightsFromServer()
                
                self._reconnect = False
            except error, e:
                print e
    
    def _getLightsFromServer(self):
        print "Ask server for lights"
        self._tn.write(self._GETLIGHTS)
        lights = self._tn.read_until(self._EOL, self._timeout)

        size = int(lights.split(self._SPLITTER)[1])
        print "Server has "+str(size)+" lights"
        
        print "Get all the lights!"
        for i in range(0, size):
            light = self._tn.read_until(self._EOL, self._timeout)
            light_split = split(light, self._SPLITTER)

            self._light.append(Light(light_split[1], light_split[3], light_split[4], light_split[5], light_split[6]))

        print "Lights are in memory now"

    def _sendPriority(self):
        self.ping()
        print "Send priority"
        self._tn.write(self._SETPRIORITY.format(self._priority))
        print "Send priority END"
        
    def setPriority(self, priority):
        self._priority = self._checkPriority(priority)
        self._sendPriority()
        
    def _checkPriority(self, priority):
        if priority < 0:
            priority = 0
        if priority > 255:
            priority = 255
        return priority
    
    def sendColor(self, light):
        self.ping()
        print "Send color of light "+str(light)
        self._tn.write(self._SETLIGHTRGB.format(self._light[light].getName(),
                                                self._brightness * self._light[light].getColor().getRed(),
                                                self._brightness * self._light[light].getColor().getGreen(),
                                                self._brightness * self._light[light].getColor().getBlue()
                                                )
                       )
        print "Send color of light "+str(light)+" END"
        self.sync()
        
    def sendColorAll(self):
        self._sendColor()
    
    def _sendColor(self):
        self.ping()
        print "Send all lights color"
        for l in self._light:
            self._tn.write(self._SETLIGHTRGB.format(l.getName(),
                                                    self._brightness * l.getColor().getRed(),
                                                    self._brightness * l.getColor().getGreen(),
                                                    self._brightness * l.getColor().getBlue()
                                                    )
                           )
            
        print "Send all lights color END"
        self.sync()
    
    def setColor(self, red, green, blue):
        for l in self._light:
            l.getColor().setColor(red, green, blue)
            
        self._sendColor()
        
    def disconnect(self):
        self.ping()
        if self._tn:
            print "Disconnect from server"
            self._tn.close()
            self._tn = None
            print "Disconnected from server"
        else:
            raise Boblight.ConnectionError("There was no connection to disconnect from!")
        
    def sendSpeed(self, light):
        self.ping()
        print "Send speed of light "+str(light)
        self._tn.write(self._SETLIGHTSPEED.format(_light[light].getName(), _light[light].getSpeed()))

        print "Send speed of light "+str(light)+" END"
    
    def sendSpeedAll(self):
        self._sendSpeed()
    
    def _sendSpeed(self):
        self.ping()
        print "Send all lights speed"
        for l in self._light:
            self._tn.write(self._SETLIGHTSPEED.format(l.getName(), l.getSpeed()))

        print "Send all lights speed END"
        
    def setSpeed(self, speed):
        for l in self._light:
            l.setSpeed(speed)
        
        self._sendSpeed()
        
    def setInterpolation(self, interpolation):
        for l in self._light:
            l.setInterpolation(interpolation)
        
        self._sendInterpolation()
        
    def sendInterpolation(self, light):
        self.ping()
        print "Send interpolation of light "+str(light)
        self._tn.write(self._SETLIGHTINTERPOLATION.format(_light[light].getName(), _light[light].getInterpolation()))
            
        print "Send interpolation of light "+str(light)+" END"
        
    def sendInterpolationAll(self):
        self._sendInterpolation()
    
    def _sendInterpolation(self):
        self.ping()
        print "Send all lights interpolation"
        for l in self._light:
            self._tn.write(self._SETLIGHTINTERPOLATION.format(l.getName(), l.getInterpolation()))
            
        print "Send all lights interpolation END"
        
    def sync(self):
        print "Sync"
        self._tn.write(self._SYNC)
        print "Sync END"
        
    def getLightsCount(self):
        return self._light.__len__()
    
    def getLight(self):
        return self._light
    
    def ping(self):
        try:
            print "Ping the server"
            self._tn.write(self._PING)
            p = self._tn.read_until(self._EOL, self._timeout)
            print "Pong from server: "+p

            if p == "ping 1"+self._EOL:
                return True
            elif p == "ping 0"+self._EOL:
                return False
            else:
                self.reconnect()
        except EOFError:
            self.reconnect()
        except error, e:
            print e
            self.reconnect()

        return None

    def reconnect(self):
        self._reconnect = True
        while self._reconnect:
            try:
                self._tn = None
                print "Trying to reconnect to server"
                self.connect(self._host, self._port)
            except error, e:
                pass
        print "Reconnect OK"
        self._sendPriority()
        self._sendInterpolation()
        self._sendSpeed()
        self._sendColor()

    def getHost(self):
        return self._host
    
    def getPort(self):
        return self._port

    def getPriority(self):
        return self._priority

    def setBrightness(self, brightness):
        self._brightness = self._checkBrightness(brightness)
        self._sendColor();

    def _checkBrightness(self, brightness):
        if brightness < 0:
            brightness = 0
        if brightness > 1:
            brightness = 1
        return brightness

    def getBrightness(self):
        return self._brightness

    def _restartBoblightDaemon(self):
        print "Restart server"
        call("service boblightd restart", shell=True)
        print "Restart server END"
