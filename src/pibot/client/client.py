'''
Created on 26 Oct 2013

@author: andy
'''
from redis import Redis
from pibot.common.commands import Commands, COMMAND_QUEUE_NAME

class Client(object):

    def __init__(self, host='brickpi', port=6379, messageLife=60):
        self.redis = Redis(host,port)
        self.messageLife = messageLife
        if not self.redis.ping():
            raise Exception('Unable to connect to Redis Server %1:%2'.format(host,port))

    def turnLeft(self):
        params = {}
        self._sendCommand(Commands.LEFT, params)
    
    def turnRight(self):
        params = {}
        self._sendCommand(Commands.RIGHT, params)
    
    def goForward(self):
        params = {}
        self._sendCommand(Commands.FORWARD, params)
    
    def goBack(self):
        params = {}
        self._sendCommand(Commands.REVERSE, params)
    
    def doSpin(self):
        params = {}
        self._sendCommand(Commands.SPIN, params)

    def _sendCommand(self, command, params=None):
        """
        Put a command on the Redis Queue
        """
        commandLine = command + '::' + ','.join([str(k)+'='+str(v) for k,v in params.iteritems()])
        self.redis.rpush(COMMAND_QUEUE_NAME, commandLine)
        self.redis.expire(COMMAND_QUEUE_NAME, self.messageLife)

if __name__ == '__main__':
    client = Client()
    client.goForward()
    client.turnLeft()
    client.turnRight()
    client.goBack()
    client.doSpin()



