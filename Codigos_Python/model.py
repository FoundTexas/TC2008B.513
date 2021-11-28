from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import random

from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request, jsonify
import logging
import json, os, atexit

class Semaforo(Agent):
    def __init__(self, unique_id, model):
      super().__init__(unique_id, model)
      self.type = "SEMAFORO"
      self.state = 0
      self.Yellow = True
      self.Green = False
      self.Red = False
      self.Started = False
      self.rpos = [0.0,0.0]
      self.dir = 0
    
    def SetPair(self,Ne,No):
        self.Spar = Ne
        self.Sop = No

        print(self.unique_id,self.pos,self.Spar.unique_id,self.Spar.pos,self.Sop.unique_id,self.Sop.pos)
    
    def CheckCoche(self):
        cellCont = self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]))
        d = [0,0]
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "CALLE":
                    d = cellCont[index].Dir
                    if d[0] < 0:
                        self.rpos = [self.pos[0], self.pos[1]+0.5]
                        self.dir = 0
                    elif d[0] > 0:
                        self.rpos = [self.pos[0], self.pos[1]-0.5]
                        self.dir = 1
                    elif d[0] == 0:
                        if d[1] < 0:
                            self.rpos = [self.pos[0]-0.5, self.pos[1]]
                            self.dir = 2
                        elif d[1] > 0:
                            self.rpos = [self.pos[0]+0.5, self.pos[1]]
                            self.dir = 3
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
        d = dir
        if d[0] < -1:
            d[0] =-1
        elif d[0] > 1:
            d[0] = 1

        if d[1] < -1:
            d[1] =-1
        elif d[1] > 1:
            d[1] = 1

        self.Dir[0] = d[0]
        self.Dir[1] = d[1]
        print(self.unique_id,self.pos,"Dir",self.Dir)
    def SetConexiones2(self, dir2):

        d = dir2
        if d[0] < -1:
            d[0] =-1
        elif d[0] > 1:
            d[0] = 1

        if d[1] < -1:
            d[1] =-1
        elif d[1] > 1:
            d[1] = 1

        self.Dir2[0] = d[0]
        self.Dir2[1] = d[1]
        print(self.unique_id,self.pos,"Dir2",self.Dir2)

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
        self.Calles = []
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
                    self.Calles.append(o)

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
                    self.schedule2.add(s)
                    o = Calle(Y+X*100,self,[1,0])
                    self.grid.place_agent(o,(X,(height-1)-Y))
                elif matrix[Y][X] == "d":
                    s = Semaforo(Y+X*10,self)
                    self.grid.place_agent(s,(X,(height-1)-Y))
                    self.semaforos.append(s)
                    self.schedule2.add(s)
                    o = Calle(Y+X*100,self,[-1,0])
                    self.grid.place_agent(o,(X,(height-1)-Y))
                elif matrix[Y][X] == "w":
                    s = Semaforo(Y+X*10,self)
                    self.grid.place_agent(s,(X,(height-1)-Y))
                    self.semaforos.append(s)
                    self.schedule2.add(s)
                    o = Calle(Y+X*100,self,[0,1])
                    self.grid.place_agent(o,(X,(height-1)-Y))
                elif matrix[Y][X] == "s":
                    s = Semaforo(Y+X*10,self)
                    self.grid.place_agent(s,(X,(height-1)-Y))
                    self.semaforos.append(s)
                    self.schedule2.add(s)
                    o = Calle(Y+X*100,self,[0,-1])
                    self.grid.place_agent(o,(X,(height-1)-Y))
                self.Calles.append(o)

        print("Cruces")
        for c in range(len(self.cruces)):
            g = self.nextCellCont(self.cruces[c],1,0)
            g = self.nextCellCont(self.cruces[c],0,1)
        print("Semaforos")
        for s in range(len(self.semaforos)):
            self.CheckSemaforo(self.semaforos[s])
    
    def AssignSemaforos(self,a,X,Y):
        tmp = a
        tmp2 = a
        if X != 0:
            if X > 0:
                x = X + 2
                y = Y + 1
                print("X pos")
            elif X < 0:
                x = X - 2
                y = Y - 1
                print("X neg")
            cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+y)))
            if len(cellCont) > 0:
                for index in range(len(cellCont)):
                    if cellCont[index].type == "SEMAFORO":
                        tmp2 = cellCont[index]
            if X > 0:
                x = X + 1
                y = Y -1
                print("X pos")
            elif X < 0:
                x = X - 1
                y = Y + 1
                print("X neg")
            cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+y)))
            if len(cellCont) > 0:
                for index in range(len(cellCont)):
                    if cellCont[index].type == "SEMAFORO":
                        tmp = cellCont[index]
                        
        elif Y != 0:
            if Y > 0:
                x = X - 1
                y = Y + 2
                print("Y pos")
            elif Y < 0:
                x = X + 1
                y = Y - 2
                print("Y neg")
            cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+y)))
            if len(cellCont) > 0:
                for index in range(len(cellCont)):
                    if cellCont[index].type == "SEMAFORO":
                        tmp2 = cellCont[index]
            if Y > 0:
                x = X + 1
                y = Y + 1
                print("Y pos")
            elif Y < 0:
                x = X - 1
                y = Y - 1
                print("Y neg")
            cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+x, a.pos[1]+y)))
            if len(cellCont) > 0:
                for index in range(len(cellCont)):
                    if cellCont[index].type == "SEMAFORO":
                        tmp = cellCont[index]
      
        a.SetPair(tmp,tmp2)

    def CheckSemaforo(self,a):
      cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0], a.pos[1])))
      if len(cellCont) > 0:
        for index in range(len(cellCont)):
          if cellCont[index].type == "CALLE":
            dir = cellCont[index].Dir
            print(dir)
            self.AssignSemaforos(a,dir[0],dir[1])

    def nextCellCont(self,a,X,Y):
        cellCont = self.grid.get_cell_list_contents(a.model.grid.torus_adj((a.pos[0]+X, a.pos[1]+Y)))
        x = X
        y = Y

        if x < -1:
            x =-1
        elif x > 1:
            x = 1

        if y < -1:
            y =-1
        elif y > 1:
            y = 1
        
        print(a.pos, [x,y])
            
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "CALLE":
                    if cellCont[index].Dir[0] == x and cellCont[index].Dir[1] == y:
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
        self.schedule.step()

        ps = []
        for i in range(self.num_agents):
            xy = self.schedule.agents[i].pos
            p = [xy[0],0,xy[1]]
            ps.append(p)
        return ps

    def step2(self):
        self.schedule2.step()
        ps = []
        for i in range(len(self.schedule2.agents)):
            p = self.schedule2.agents[i]
            print(p)
            ps.append(p)
        return ps


cwd = os.getcwd()
files = os.listdir(cwd) 
print(files)

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

matrix = f2m('inputs.txt')

app = Flask(__name__, static_url_path = '')

model = CruceModel(20,len(matrix[0]),len(matrix),matrix)

def positionsToJSON(ps):
    posDICT = []
    for p in ps:
        pos = {
            "x" : p[0],
            "y" : p[1],
            "z" : p[2]
        }
        posDICT.append(pos)
    return json.dumps(posDICT)

def BoolsToJSON(g):
    posDICT = []
    for p in g:
        pos = {
            "Green" : p.Green,
            "Yellow" : p.Yellow,
            "Red" : p.Red,
            "Posx" : p.rpos[0],
            "Posz" : p.rpos[1],
            "dir" : p.dir
        }
        posDICT.append(pos)
    return json.dumps(posDICT)

def CallesToJSON(g):
    posDICT = []
    for p in g:
        pos = {
            "x" : p.pos[0],
            "y" : -1,
            "z" : p.pos[1]
        }
        posDICT.append(pos)
    return json.dumps(posDICT)

port = int(os.getenv('PORT',8585))

@app.route('/')

def root():
    return jsonify([{"message":"Hello"}])

@app.route('/calles', methods=['GET','POST'])

def calles():
    positions = model.Calles
    return CallesToJSON(positions)

@app.route('/muliagentes', methods=['GET','POST'])

def multiagentes():
    positions = model.step()
    return positionsToJSON(positions)

@app.route('/semaforos', methods=['GET','POST'])

def semaforos():
    lights = model.step2()
    return BoolsToJSON(lights)
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port = port, debug = True)