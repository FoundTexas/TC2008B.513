from mesa import Agent, Model
#import random
import time
import socket

host, port = "192.168.0.12", 8080  # poner host y puerto
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host,port))

class Grafo():
  def __init__(self):
    self.Calles = []
    
  def SetCalles(self,c):
    self.Calles.append(c)

class Calle(Agent):
  def __init__(self, unique_id,Speed,Dir):
    #super().__init__(unique_id, model)
    self.Speed = Speed
    self.Dir = Dir
    self.Conexiones = []
    self.Dist = 30
    self.unique_id = unique_id
  
  def SetConexion(self,c):
    self.Conexiones = c
  
  def  __ne__(self,other):
    return self.unique_id != other.unique_id

class CarPython(Agent):
  def __init__(self, unique_id,CurDir,CurTarget,FinalTarget):
    #super().__init__(unique_id,model)
    self.MaxSpeed = 10
    self.CurSpeed = 0
    self.AcelDelt = 0.25
    self.DeacelDelt = -0.25
    self.CurDir = CurDir
    self.CurTarget = CurTarget
    self.FinalTarget = FinalTarget

  def SetDirCar(self,CurTarget):
    print("Calle:" + str(CurTarget.unique_id))
    self.CurDir = CurTarget.Dir
    self.DistanceToTarget = 30
    self.CurTarget = CurTarget
    self.CurSpeed = self.CurSpeed /2

  def MoveCar(self):
    print(self.DistanceToTarget)
    self.CurSpeed += self.AcelDelt
    if(self.CurSpeed > self.MaxSpeed):
      self.CurSpeed = self.MaxSpeed

    self.DistanceToTarget -= self.CurSpeed
    tmp = []
    tmp = self.CurDir
    tmp.append(self.CurSpeed)
    print(tmp)
    SpeedString = ','.join(map(str,tmp))
    tmp.pop()
    sock.sendall(SpeedString.encode("UTF-8"))

class CarModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):
        self.num_agents = N
        a = CarPython(N,self)
        # Create agents
        #for i in range(self.num_agents):
            #a = MoneyAgent(i, self)

class StopLight(Agent):
  def __init__(self,model,unique_id):
    super().__init__(unique_id)
    self.GL = False
    self.YL = True
    self.RL = False
    self.GLT = 3
    self.YLT = 1
    self.RLT = 4
    

def main():
  GPS = Grafo()
  #Semaforo1 = StopLight(1)
  calle1 = Calle(1,20,[0,0,1])
  GPS.SetCalles(calle1)
  
  #Semaforo2 = StopLight(2)
  calle2 = Calle(2,20,[1,0,0])
  GPS.SetCalles(calle2)
  
  #Semaforo3 = StopLight(3)
  calle3 = Calle(3,20,[0,0,-1])
  GPS.SetCalles(calle3)
  
  #Semaforo4 = StopLight(4)
  calle4 = Calle(4,20,[-1,0,0])
  GPS.SetCalles(calle4)
  
  #Semaforo5 = StopLight(5)
  calle5 = Calle(5, 20,[0,0,1])
  GPS.SetCalles(calle5)
  
  #Semaforo6 = StopLight(6)
  calle6 = Calle(6, 20,[1,0,0])
  GPS.SetCalles(calle6)

  #Semaforo7 = StopLight(7)
  calle7 = Calle(7, 20,[0,0,-1])
  GPS.SetCalles(calle7)

  #Semaforo8 = StopLight(8)
  calle8 = Calle(8, 20,[1,0,0])
  GPS.SetCalles(calle8)

  #Semaforo9 = StopLight(9)
  calle9 = Calle(9, 20,[0,0,1])
  GPS.SetCalles(calle9)

  #Semaforo10 = StopLight(10)
  calle10 = Calle(10, 20,[-1,0,0])
  GPS.SetCalles(calle10)
  
  tmp = [calle2,calle5]
  calle1.SetConexion(tmp)
  tmp = [calle8,calle3]
  calle2.SetConexion(tmp)
  tmp = [calle4]
  calle3.SetConexion(tmp)
  tmp = [calle1]
  calle4.SetConexion(tmp)
  tmp = [calle6]
  calle5.SetConexion(tmp)
  tmp = [calle7]
  calle6.SetConexion(tmp)
  tmp = [calle3,calle8]
  calle7.SetConexion(tmp)
  tmp = [calle9]
  calle8.SetConexion(tmp)
  tmp = [calle10]
  calle9.SetConexion(tmp)
  tmp = [calle7]
  calle10.SetConexion(tmp)

  timeout = time.time() + 60
  McQueen = CarPython(1,calle1.Dir,calle1, calle9)
  McQueen.SetDirCar(calle1)

  i = 0

  while (McQueen.CurTarget != McQueen.FinalTarget):
    if(i == 0):
      if(McQueen.DistanceToTarget < 0):
        i+= 1
        McQueen.SetDirCar(calle2)
      else:
        McQueen.MoveCar()
    elif(i == 1):
      if(McQueen.DistanceToTarget < 0):
        i+= 1
        McQueen.SetDirCar(calle8)
      else:
        McQueen.MoveCar()
    elif(i == 2):
      if(McQueen.DistanceToTarget < 0):
        i+= 1
        McQueen.SetDirCar(calle9)
      else:
        McQueen.MoveCar()

    time.sleep(1)


main()
