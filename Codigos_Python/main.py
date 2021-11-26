# Versión prueba del reto!!!!!!!!!!
#
#
#
#
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import time
import socket

#host, port = "192.168.0.12", 8080  # Poner host y puerto
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((host, port))


class Grafo():
    def __init__(self):
        self.gps = []

    def setGPS(self, calle):
        self.gps.append(calle)


class Calle(Agent):
    def __init__(self, unique_id, model, dir, largo, inicio):
        super().__init__(unique_id, model)
        self.type = "CALLE"
        self.inicio = inicio
        self.dir = dir
        self.conexiones = []
        self.largo = largo
        self.numCarros = 0

    def setConexion(self, c):
        self.conexiones = c

    def contarAutos(self):
        temp = 0
        if self.dir == "E":
            for i in range(self.largo):
                if len(self.model.grid.get_cell_list_contents([self.inicio[0] + i, self.inicio[1]])) < 2:
                    temp += 1
            self.numCarros = temp
        elif self.dir == "N":
            for i in range(self.largo):
                if len(self.model.grid.get_cell_list_contents([self.inicio[0], self.inicio[1] + i])) < 2:
                    temp += 1
        elif self.dir == "S":
            for i in range(self.largo):
                if len(self.model.grid.get_cell_list_contents([self.inicio[0], self.inicio[1] - i])) < 2:
                    temp += 1
        elif self.dir == "O":
            for i in range(self.largo):
                if len(self.model.grid.get_cell_list_contents([self.inicio[0] - i, self.inicio[1]])) < 2:
                    temp += 1

        self.numCarros = temp

    def step(self):
        self.contarAutos()


class CarPython(Agent):
    def __init__(self, unique_id, model, calle, target):
        super().__init__(unique_id, model)
        self.type = "CAR"
        self.calle = calle
        self.dir = self.calle.dir
        self.target = target
        self.speed = 20
        self.acDelta = 1

    def cambiarCalle(self):
        if self.pos == tuple(self.target.inicio):
            self.calle = self.target
            self.target = random.choice(self.target.conexiones)
            self.moverCarro()
        else:
            self.moverCarro()

    def isOtherCar(self, cellCont):
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "CAR":
                    return True
        return False

    def isGreenLight(self, cellCont):
        if len(cellCont) > 0:
            for index in range(len(cellCont)):
                if cellCont[index].type == "SPLT":
                    if cellCont[index].state == 2 and cellCont[index].viewDir == self.dir:
                        return False
        return True

    def nextCellCont(self):
        if self.dir == "N":
            return self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0], self.pos[1] + 1)))
        elif self.dir == "S":
            return self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0], self.pos[1] - 1)))
        elif self.dir == "E":
            return self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0] + 1, self.pos[1])))
        elif self.dir == "O":
            return self.model.grid.get_cell_list_contents(self.model.grid.torus_adj((self.pos[0] - 1, self.pos[1])))

    def moverCarro(self):
        nextCell = self.nextCellCont()
        carNFront = self.isOtherCar(nextCell)
        greenL = self.isGreenLight(nextCell)

        if carNFront == False and greenL == True:
            if self.dir == "N":
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + 1))
            elif self.dir == "S":
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - 1))
            elif self.dir == "E":
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1]))
            elif self.dir == "O":
                self.model.grid.move_agent(self, (self.pos[0] - 1, self.pos[1]))

    def step(self):
        self.cambiarCalle()
        #temp = [self.pos[0], 0, self.pos[1]]
        #posString = ','.join(map(str, temp))
        #sock.sendall(posString.encode("UTF-8"))

        print("Calle: ", self.calle.unique_id)
        print("Pos: ", self.pos)

class StopLight(Agent):
    def __init__(self, unique_id, model, viewDir):
        super().__init__(unique_id, model)
        self.viewDir = viewDir
        self.state = 1  # 0=verde 1=amarillo 2=rojo
        self.type = "SPLT"
        self.others = []
        self.holdOn = 0

    def otherSPLTS(self, others):
        self.others = others

    def step(self):
        if self.state == 2 and self.holdOn > 0:
            self.holdOn -= 1
        elif self.holdOn == 0:
            self.state = 0
            for i in range(len(self.others)):
                self.others[i].state = 2
                self.others[i].holdOn = 3


class GPS(Model):
    def __init__(self, width, height, numCarros):
        self.numAgents = numCarros
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.gps = []

        c1 = Calle(1, self, "N", 1, [3, 0])
        self.grid.place_agent(c1, tuple(c1.inicio))
        self.gps.append(c1)
        c2 = Calle(2, self, "N", 1, [3, 1])
        self.grid.place_agent(c2, tuple(c2.inicio))
        self.gps.append(c2)
        c2_2 = Calle(22, self, "E", 1, [3, 1])
        self.grid.place_agent(c2_2, tuple(c2_2.inicio))
        self.gps.append(c2_2)
        c3 = Calle(3, self, "N", 2, [3, 2])
        self.grid.place_agent(c3, tuple(c3.inicio))
        self.gps.append(c3)
        c5 = Calle(5, self, "O", 1, [3, 4])
        self.grid.place_agent(c5, tuple(c5.inicio))
        self.gps.append(c5)
        c6 = Calle(6, self, "S", 1, [2, 4])
        self.grid.place_agent(c6, tuple(c6.inicio))
        self.gps.append(c6)
        c7 = Calle(7, self, "S", 1, [2, 3])
        self.grid.place_agent(c7, tuple(c7.inicio))
        self.gps.append(c7)
        c8 = Calle(8, self, "S", 2, [2, 2])
        self.grid.place_agent(c8, tuple(c8.inicio))
        self.gps.append(c8)
        c8_2 = Calle(82, self, "O", 2, [2, 2])
        self.grid.place_agent(c8_2, tuple(c8_2.inicio))
        self.gps.append(c8_2)
        c10 = Calle(10, self, "E", 1, [2, 0])
        self.grid.place_agent(c10, tuple(c10.inicio))
        self.gps.append(c10)
        c12 = Calle(12, self, "N", 1, [5, 1])
        self.grid.place_agent(c12, tuple(c12.inicio))
        self.gps.append(c12)
        c13 = Calle(13, self, "O", 2, [5, 2])
        self.grid.place_agent(c13, tuple(c13.inicio))
        self.gps.append(c13)
        c17 = Calle(17, self, "E", 2, [0, 3])
        self.grid.place_agent(c17, tuple(c17.inicio))
        self.gps.append(c17)
        c18 = Calle(18, self, "S", 2, [0, 2])
        self.grid.place_agent(c18, tuple(c18.inicio))
        self.gps.append(c18)
        c18_2 = Calle(182, self, "N", 1, [0, 2])
        self.grid.place_agent(c18_2, tuple(c18_2.inicio))
        self.gps.append(c18_2)
        c21 = Calle(21, self, "E", 1, [0, 0])
        self.grid.place_agent(c21, tuple(c21.inicio))
        self.gps.append(c21)

        c1.setConexion([c2, c2_2])
        c2.setConexion([c3])
        c2_2.setConexion([c12])
        c12.setConexion([c13])
        c13.setConexion([c3])
        c3.setConexion([c5])
        c5.setConexion([c6])
        c6.setConexion([c7])
        c7.setConexion([c8, c8_2])
        c8.setConexion([c10])
        c8_2.setConexion([c18, c18_2])
        c18_2.setConexion([c17])
        c17.setConexion([c7])
        c18.setConexion([c21])
        c21.setConexion([c10])
        c10.setConexion([c1])

        a = CarPython(1, self, c1, c2)
        self.schedule.add(a)

        self.grid.place_agent(a, tuple(c1.inicio))

    def step(self):
        self.schedule.step()


class Main:

    model = GPS(10, 10, 1)

    count = 0

    while count < 30:
        model.step()
        count += 1
        time.sleep(0.7)


Main()
