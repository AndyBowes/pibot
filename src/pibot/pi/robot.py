'''
Created on 26 Oct 2013

@author: andy
'''
from redis import Redis 
from BrickPi import *

COMMAND_QUEUE_NAME = 'commandQueue'

class AbstractRobot(object):
    """
    The Robot listens for messages on the Redis Queue and then delegates control to the appropriate handler
    """
    def __init__(self, host='localhost',port=6379):
        self.redis = Redis(host,port)
        if not self.redis.ping():
            raise Exception('Unable to connect to Redis Server %1:%2'.format(host,port))
        self.handlers=self.registerCommandHandlers()
    
    def registerCommandHandlers(self):
        pass
    
    def start(self):
        """
        Start listening for messages
        """
        self.waitForCommands()
       
    def waitForCommands(self):
        # Infinite Loop to wait on messages from the Queue
        while True:
            # Blocking Pop with zero timeout will wait indefinitely
            _, command = self.redis.blpop(COMMAND_QUEUE_NAME)
            self.processCommand(command.split('::'))
    
    def processCommand(self,params):
        commandName = params[0]
        handler = self.handlers.get(commandName, None)
        if handler != None:
            handler(params[1].split(','))
        else:
            print 'Unsupported command : %'.format(commandName)

class MockRobot(AbstractRobot):
    """
    Test implementation of the AbstractRobot which can be used to test the connection to redis
    """
    def __init__(self, host='localhost',port=6379):
        super(MockRobot, self).__init__(host, port)

    def registerCommandHandlers(self):
        handlers = {'left'  :self._left,
                    'right' :self._right,
                    'forward':self._forward,
                    'back'  :self._reverse,
                    'spin'  :self._spin
                    }
        return handlers;

    def start(self):
        self.initialiseMotors()
        super(MockRobot, self).start()
    
    def _left(self,d=100,v=100):
        print 'Left'
    
    def _right(self,d=100,v=100):
        print 'Left'
    
    def _forward(self,d=100,v=100):
        print 'Forward'
    
    def _reverse(self,d=100,v=100):
        print 'Reverse'
    
    def _spin(self,d=100,v=100):
        print 'spin'
        
class BasicRobot(AbstractRobot):
    """
    Implementation of the AbstractRobot which actually controls the motors
    """
    def __init__(self, host='localhost',port=6379):
        super(MockRobot, self).__init__(host, port)

    def registerCommandHandlers(self):
        handlers = {'left'  :self._left,
                    'right' :self._right,
                    'forward':self._forward,
                    'back'  :self._reverse,
                    'spin'  :self._spin
                    }
        return handlers;
    
    def start(self):
        BrickPiSetup() # setup the serial port for communication
        BrickPi.MotorEnable[PORT_A] = 1 #Enable the Motor A
        BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D
        BrickPiSetupSensors() #Send the properties of sensors to BrickPi
        super(BasicRobot, self).start()
    
    def _performAction(self):
        BrickPiUpdateValues() # Ask BrickPi to update values for sensors/motors
        time.sleep(1) 
        self._stop()

    def _left(self,d=100,v=100):
        BrickPi.MotorSpeed[PORT_A] = 0 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = -50 #Set the speed of MotorA (-255 to 255)
        self._performAction()
        
    def _right(self,d=100,v=100):
        BrickPi.MotorSpeed[PORT_A] = -50 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = 0 #Set the speed of MotorA (-255 to 255)
        self._performAction()
    
    def _forward(self,d=100,v=100):
        BrickPi.MotorSpeed[PORT_A] = -50 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = -50 #Set the speed of MotorA (-255 to 255)
        self._performAction()
          
    def _reverse(self,d=100,v=100):
        BrickPi.MotorSpeed[PORT_A] = 50 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = 50 #Set the speed of MotorA (-255 to 255)
        self._performAction()
    
    def _spin(self,d=100,v=100):
        BrickPi.MotorSpeed[PORT_A] = -50 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = 50 #Set the speed of MotorA (-255 to 255)
        self._performAction()
        
    def _stop(self):
        BrickPi.MotorSpeed[PORT_A] = 0 #Set the speed of MotorA (-255 to 255)
        BrickPi.MotorSpeed[PORT_D] = 0 #Set the speed of MotorA (-255 to 255)
        BrickPiUpdateValues() # Ask BrickPi to update values for sensors/motors

if __name__ == '__main__':
    robot = BasicRobot('brickpi')
    robot.start()
