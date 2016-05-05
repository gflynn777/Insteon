import pickle, serial

class Util:
    
    @staticmethod
    def save_obj(obj, filename):
        if len(obj) == 0:
            print("ERROR! Not saving empty object!")
            return
        print("Writing to file.........")
        with open(filename, 'wb') as output:
            pickle.dump(obj, output, -1)
    
    @staticmethod
    def load_obj(filename):
        return pickle.load(open(filename, 'rb'))
    
    @staticmethod
    def most_common(lst):
        return max(set(lst), key=lst.count)
    
    @staticmethod
    def getChecksum(address):
        total = 0x00
        for i in range(6, len(address)):
            total += address[i]
        
        total = (total ^ 0xFF) + 1
        total = total & 0xFF
        return total

#Not Used
class Singleton():
    _instance = None
    def __new__(self): #init and new are called every time
        if not self._instance:
            self._instance = super(Singleton, self).__new__(self)
            self.ser = serial.Serial(
                    port='COM4',
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=0.04
                    )
        return self._instance
 
 
    
#Defines a singleton decorator
def singleton(myClass):
    instances = {}
    def getInstance(*args, **kwargs):
        if myClass not in instances:
            instances[myClass] = myClass(*args, **kwargs)
        return instances[myClass]
    return getInstance

@singleton
class SerialInstance(object):
    ser = serial.Serial(
                    port='COM4',
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=0.04
                    )
    def close(self):
        self.ser.close()
        
    
        