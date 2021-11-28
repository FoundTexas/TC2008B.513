from asyncio.windows_events import NULL
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import random

def f2m(s):
  file1 = open(s, 'r')
  Lines = file1.readlines()
  file1.close()
  matrix = []

  for i in range (len(Lines)):
    matrix.append(s2v(Lines[i]))

  return matrix

def s2v(s):
  vector = []
  for i in s:
    if i != ' ' and i != '\n':
      #b = int(i)
      vector.append(i)
  return vector

class Semaforo(Agent):
    def __init__(self, unique_id, model):
      super().__init__(unique_id, model)
      self.type = "SEMAFORO"
      self.state = 0
      self.Yellow = True
      self.Green = False
      self.Red = False
      self.Started = False
    
    def SetPair(self,Npar,No):
      self.Spar = Npar
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
    def __init__(self, unique_id, model):
      super().__init__(unique_id, model)
      self.type = "CRUCE"
      self.Dir = [0,0]
      self.Dir2 = [0,0]
    
    def SetConexiones(self, dir):
      self.Dir[0] = dir[0]
      self.Dir[1] = dir[1]
      print(self.unique_id,"Dir",self.Dir)
    def SetConexiones2(self, dir2):
      self.Dir2[0] = dir2[0]
      self.Dir2[1] = dir2[1]
      print(self.unique_id,"Dir2",self.Dir2)

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
    def __init__(self, N, width, height, matrix):
        self.num_agents = N
        self.running = True
        self.grid = MultiGrid(width, height, True)
        self.schedule2 = RandomActivation(self)
        self.schedule = RandomActivation(self)
        self.cruces = []
        self.semaforos = []
        
        for X in range(width):
          for Y in range(height):
            if matrix[Y][X] == ".":
              o = Obstaculo(Y+X*10,self)
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "X":
              o = Cruce(Y+X*10,self)
              self.grid.place_agent(o,(X,(height-1)-Y))
              self.cruces.append(o)

        for i in range(self.num_agents):
          a =  Coche(i, self)
          self.grid.place_agent(a, (0, 0))
          self.grid.move_to_empty(a)
          self.schedule.add(a)

        for X in range(width):
          for Y in range(height):
            if matrix[Y][X] == "1":
              o = Calle(Y+X*10,self,[1,0])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "2":
              o = Calle(Y+X*10,self,[-1,0])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "3":
              o = Calle(Y+X*10,self,[0,1])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "4":
              o = Calle(Y+X*10,self,[0,-1])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "a":
              s = Semaforo(Y+X*10,self)
              self.grid.place_agent(s,(X,(height-1)-Y))
              self.semaforos.append(s)
              self.schedule.add(s)
              o = Calle(Y+X*10,self,[1,0])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "d":
              s = Semaforo(Y+X*10,self)
              self.grid.place_agent(s,(X,(height-1)-Y))
              self.semaforos.append(s)
              self.schedule.add(s)
              o = Calle(Y+X*10,self,[-1,0])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "w":
              s = Semaforo(Y+X*10,self)
              self.grid.place_agent(s,(X,(height-1)-Y))
              self.semaforos.append(s)
              self.schedule.add(s)
              o = Calle(Y+X*10,self,[0,1])
              self.grid.place_agent(o,(X,(height-1)-Y))
            elif matrix[Y][X] == "s":
              s = Semaforo(Y+X*10,self)
              self.grid.place_agent(s,(X,(height-1)-Y))
              self.semaforos.append(s)
              self.schedule.add(s)
              o = Calle(Y+X*10,self,[0,-1])
              self.grid.place_agent(o,(X,(height-1)-Y))

        for c in range(len(self.cruces)):
          g = self.nextCellCont(self.cruces[c],1,0)
          g = self.nextCellCont(self.cruces[c],0,1)

        for s in range(len(self.semaforos)):
          self.CheckSemaforo(self.semaforos[s])
    
    def AssignSemaforos(self,a,X,Y):
      tmp = a
      tmp2 = a
      if X != 0:
        if X > 0:
          x = X + 3
          y = Y + 1
        elif X < 0:
          x = X - 3
          y = Y - 1
        cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+Y)))
        if len(cellCont) > 0:
          for index in range(len(cellCont)):
            if cellCont[index].type == "SEMAFORO":
              tmp2 = cellCont[index]
      if Y != 0:
        if Y > 0:
          x = X - 1
          y = Y + 3
        elif Y < 0:
          x = X + 1
          y = Y - 3
        cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+X, a.pos[1]+y)))
        if len(cellCont) > 0:
          for index in range(len(cellCont)):
            if cellCont[index].type == "SEMAFORO":
              tmp2 = cellCont[index]

      cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+y)))
      if len(cellCont) > 0:
        for index in range(len(cellCont)):
          if cellCont[index].type == "SEMAFORO":
            tmp = cellCont[index]
      
      a.SetPair(tmp2,tmp)

    def CheckSemaforo(self,a):
      cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0], a.pos[1])))
      if len(cellCont) > 0:
        for index in range(len(cellCont)):
          if cellCont[index].type == "CALLE":
            dir = cellCont[index].Dir
            self.AssignSemaforos(a,dir[0],dir[1])

    def nextCellCont(self,a,X,Y):
      cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+X, a.pos[1]+Y)))
      x = X
      if x != 0:
        abs(x)/x
      y = Y
      if y != 0:
        abs(y)/y

      if len(cellCont) > 0:
        for index in range(len(cellCont)):

          if cellCont[index].type == "CALLE":
            if cellCont[index].Dir == [x,y]:
              if a.Dir[0] == 0 and a.Dir[1] == 0:
                a.SetConexiones([x,y])
              elif a.Dir2[0] == 0 and a.Dir2[1] == 0:
                a.SetConexiones2([x,y])
              return False
            else:
              x *= -1
              y *= -1
              if a.Dir[0] == 0 and a.Dir[1] == 0:
                a.SetConexiones([x,y])
              elif a.Dir2[0] == 0 and a.Dir2[1] == 0:
                a.SetConexiones2([x,y])
              return True

          elif cellCont[index].type == "CRUCE":
            if Y == 0:
              self.nextCellCont(a,X+X,Y)
            elif X == 0:
              self.nextCellCont(a,X,Y+Y)

          elif cellCont[index].type == "OBSTACULO":
            x *= -1
            y *= -1
            if a.Dir[0] == 0 and a.Dir[1] == 0:
              a.SetConexiones([x,y])
            elif a.Dir2[0] == 0 and a.Dir2[1] == 0:
              a.SetConexiones2([x,y])
            return True

      return True

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

matrix = f2m('input.txt')
print("Start")
print(len(matrix), len(matrix[0]))
print(matrix[0][0])

grid = CanvasGrid(agent_portrayal,len(matrix[0]), len(matrix), 500, 500)
num_agents_slider = UserSettableParameter('slider', "Number of agents", 1, 1, 10, 1)

server = ModularServer(CruceModel,
                       [grid],
                       "Simulación Cajas",
                       {"N": num_agents_slider, "width": len(matrix[0]), "height": len(matrix), "matrix": matrix})

server.port = 8521
server.launch()