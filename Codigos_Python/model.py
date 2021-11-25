from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import random
import time

host, port = "192.168.0.12", 8080  # Poner host y puerto
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))


class Semaforo(Agent):
    def __init__(self, unique_id, model,s):
      super().__init__(unique_id, model)
      self.type = "SEMAFORO"
      self.state = s
      self.Yellow = True
      self.Green = False
      self.Red = False
      self.Started = False
    
    def SetPair(self,Ne,No):
      self.Spar = Ne
      self.Sop = No
    
    def CheckCoche(self):
        cellCont = self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]))
        d = [0,0]
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "CALLE":
                    d = cellCont[index].Dir
        else:
            return False

        cellCont = self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0]-d[0], self.pos[1]-d[1])))
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "COCHE":
                    self.Sop.Go(8)
                    self.Sop.Spar.Go(0)
                    self.Spar.Go(0)
                    
                    self.Go(8)
                    return True
        else:
            return False

        return False

    
    def Go(self, t):
        if self.Started == False:
            self.Started = True
            self.state = t

    def Lights(self):
        if self.Started == True:
            if self.state > 0:
                if self.state < 4:
                    self.Red = False
                    self.Green = False
                    self.Yellow = True
                else:
                    self.Yellow = False
                    self.Green = True
                    self.Red = False
            elif self.state == 0:
                self.Yellow = False
                self.Green = False
                self.Red = True
            self.state -= 1
            if self.state <= -8:
                self.state = 8
        if self.Started == False:
            self.Started = self.CheckCoche()
    
    def step(self):
        self.Lights()

class Calle(Agent):
    def __init__(self, unique_id, model, dir):
      super().__init__(unique_id, model)
      self.type = "CALLE"
      self.Dir = [0,0]
      self.Dir[0] = dir[0]
      self.Dir[1] = dir[1]

class Cruce(Agent):
    def __init__(self, unique_id, model, dir,dir2):
      super().__init__(unique_id, model)
      self.type = "CRUCE"
      self.Dir = [0,0]
      self.Dir[0] = dir[0]
      self.Dir[1] = dir[1]
      self.Dir2 = [0,0]
      self.Dir2[0] = dir2[0]
      self.Dir2[1] = dir2[1]
      print(self.Dir,self.Dir2)

class Obstaculo(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "OBSTACULO"

class Coche(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "COCHE"
        self.isCollecting = True
        self.curpos = [4,4]
        self.target = [4,4]
        self.Dir = [0,0]
        self.cruzando = False

    def nextCellCont(self,X,Y):
        return self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0]+X, self.pos[1]+Y)))

    def GetDir(self):
        cellCont = self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]))

        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "CALLE":
                    self.cruzando = False
                    return cellCont[index].Dir
                elif cellCont[index].type == "CRUCE":
                    if self.cruzando == False:
                        self.cruzando = True
                        rng1 = random.randrange(0,2)
                        if rng1 == 0:
                            return cellCont[index].Dir
                        if rng1 == 1:
                            return cellCont[index].Dir2
        
        return self.Dir
    
    def Obstacle(self, cellCont):
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "COCHE":
                    return True
                elif cellCont[index].type == "OBSTACULO":
                    return True
                elif cellCont[index].type ==  "SEMAFORO":
                    if cellCont[index].Red == True:
                        return True
                   
        return False

    def move(self):

        self.curpos[0] = self.pos[0]
        self.curpos[1] = self.pos[1]

        self.Dir = self.GetDir()
        X = self.Dir[0]
        Y = self.Dir[1]

        nextCell = self.nextCellCont(X,Y)
        obstruct = self.Obstacle(nextCell)
        if (obstruct == False):
            self.model.grid.move_agent(self, (self.pos[0]+X, self.pos[1]+Y))

    def step(self):
        self.move()


class CruceModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.running = True
        self.grid = MultiGrid(width, height, True)
        self.schedule2 = RandomActivation(self)
        self.schedule = RandomActivation(self)

        dirx = 1
        diry = -1
        for g in range(round((width/2)-1),round((width/2)+1)):
            for p in range(round((width/2)-1),round((width/2)+1)):
                o = Cruce(g,self,[dirx,0],[0,diry])
                dirx *= -1
                self.grid.place_agent(o,(g,p))
            diry *= -1

        s1 = Semaforo(111,self,0)
        self.grid.place_agent(s1, (round((width/2)-1), round((height/2)+1)))
        s2 = Semaforo(112,self,0)
        self.grid.place_agent(s2, (round((width/2)), round((height/2)-2)))

        s3 = Semaforo(113,self,8)
        self.grid.place_agent(s3, (round((width/2)-2), round((height/2)-1)))

        s4 = Semaforo(114,self,8)
        self.grid.place_agent(s4, (round((width/2)+1), round((height/2))))
        s4.SetPair(s2,s3)
        s2.SetPair(s4,s1)
        s3.SetPair(s1,s4)
        s1.SetPair(s3,s2)

        self.schedule2.add(s1)
        self.schedule2.add(s2)
        self.schedule2.add(s3)
        self.schedule2.add(s4)

        for g in range(round((width-1)/2)):
            for p in range(round((width-1)/2)):
                o = Obstaculo(g,self)
                self.grid.place_agent(o,(g,p))

        for g in range(round((width-1)/2)):
            for p in range(round((width+2)/2),width):
                o = Obstaculo(g,self)
                self.grid.place_agent(o,(g,p))

        for g in range(round((width+2)/2),width):
            for p in range(round((width+2)/2),width):
                o = Obstaculo(g,self)
                self.grid.place_agent(o,(g,p))
        
        for g in range(round((width+2)/2),width):
            for p in range(round((width-1)/2)):
                o = Obstaculo(g,self)
                self.grid.place_agent(o,(g,p))

        for i in range(self.num_agents):
          a =  Coche(i, self)
          self.grid.place_agent(a, (4, 4))
          self.grid.move_to_empty(a)
            
          self.schedule.add(a)
        
        for x in range(round((width-1)/2)):
          obs1 = Calle(x,self,[1,0])
          self.grid.place_agent(obs1, (x, round((width-1)/2)))
          obs2 = Calle(x+10,self,[-1,0])
          self.grid.place_agent(obs2, (x, round(width/2)))
        
        for x in range(round((width+1)/2), width):
          obs1 = Calle(x,self,[1,0])
          self.grid.place_agent(obs1, (x, round((width-1)/2)))
          obs2 = Calle(x+10,self,[-1,0])
          self.grid.place_agent(obs2, (x, round(width/2)))

        for y in range(round((height-1)/2)):
          obs1 = Calle(y,self,[0,-1])
          self.grid.place_agent(obs1, (round((height-1)/2),y))
          obs2 = Calle(y+10,self,[0,1])
          self.grid.place_agent(obs2, (round(height/2),y))
        
        for y in range(round((height+1)/2), height):
          obs1 = Calle(y,self,[0,-1])
          self.grid.place_agent(obs1, (round((height-1)/2),y))
          obs2 = Calle(y+10,self,[0,1])
          self.grid.place_agent(obs2, (round(height/2),y))

    def step(self):
        self.schedule2.step()
        self.schedule.step()


def agent_portrayal(agent):
    portrayal = {"Shape": "rect", "Filled": "True", "w": 1, "h": 1}

    if agent.type == "COCHE":
        if agent.Dir == [1,0]:
            portrayal["h"] = 0.5
        elif agent.Dir == [-1,0]:
            portrayal["h"] = 0.5
        elif agent.Dir == [0,1]:
            portrayal["w"] = 0.5
        elif agent.Dir == [0,-1]:
            portrayal["w"] = 0.5

        portrayal["Color"] = "SlateBlue"
        portrayal["Layer"] = 2

    elif agent.type == "OBSTACULO":
        portrayal["Color"] = "YellowGreen"
        portrayal["Layer"] = 1
    
    elif agent.type == "CALLE":
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
    
    elif agent.type == "CRUCE":
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
    
    elif agent.type == "SEMAFORO":
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5
        if agent.Yellow == True:
            portrayal["Color"] = "yellow"
        elif agent.Green == True:
            portrayal["Color"] = "green"
        elif agent.Red == True:
            portrayal["Color"] = "red"
        portrayal["Layer"] = 4

    return portrayal


grid = CanvasGrid(agent_portrayal,10, 10, 600, 500)
num_agents_slider = UserSettableParameter('slider', "Number of agents", 1, 1, 10, 1)

server = ModularServer(CruceModel,
                       [grid],
                       "Simulación Cajas",
                       {"N": 3, "width": 10, "height": 10})

server.port = 8521
server.launch()