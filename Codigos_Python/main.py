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

host, port = "192.168.0.12", 8080  # Poner host y puerto
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))


class Grafo():
    def __init__(self):
        self.gps = []

    def setGPS(self, calle):
        self.gps.append(calle)


class Calle(Agent):
    def __init__(self, unique_id, model, dir, largo, inicio, fin):
        super().__init__(unique_id, model)
        self.inicio = inicio
        self.fin = fin
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
        self.calle = calle
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

    def moverCarro(self):
        if self.calle.dir == "E":
            if len(self.model.grid.get_cell_list_contents((self.pos[0]+1, self.pos[1]))) < 3:
                self.model.grid.move_agent(self, (self.pos[0]+1, self.pos[1]))
        elif self.calle.dir == "O":
            if len(self.model.grid.get_cell_list_contents((self.pos[0]-1, self.pos[1]))) < 3:
                self.model.grid.move_agent(self, (self.pos[0]-1, self.pos[1]))
        elif self.calle.dir == "N":
            if 1>0:
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1]+1))
        elif self.calle.dir == "S":
            if len(self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]-1))) < 3:
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1]-1))

    def step(self):
        self.cambiarCalle()
        temp = [self.pos[0], 0, self.pos[1]]
        posString = ','.join(map(str, temp))
        sock.sendall(posString.encode("UTF-8"))

        print("Calle: ", self.calle.unique_id)
        print("Pos: ", self.pos)


class GPS(Model):
    def __init__(self, width, height, numCarros):
        self.numAgents = numCarros
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.gps = []

        c1 = Calle(1, self, "N", 1, [3, 0], [3, 1])
        self.grid.place_agent(c1, tuple(c1.inicio))
        self.gps.append(c1)
        c2 = Calle(2, self, "N", 1, [3, 1], [3, 2])
        self.grid.place_agent(c2, tuple(c2.inicio))
        self.gps.append(c2)
        c2_2 = Calle(22, self, "E", 1, [3, 1], [5, 1])
        self.grid.place_agent(c2_2, tuple(c2_2.inicio))
        self.gps.append(c2_2)
        c3 = Calle(3, self, "N", 2, [3, 2], [3, 4])
        self.grid.place_agent(c3, tuple(c3.inicio))
        self.gps.append(c3)
        c5 = Calle(5, self, "O", 1, [3, 4], [2, 4])
        self.grid.place_agent(c5, tuple(c5.inicio))
        self.gps.append(c5)
        c6 = Calle(6, self, "S", 1, [2, 4], [2, 3])
        self.grid.place_agent(c6, tuple(c6.inicio))
        self.gps.append(c6)
        c7 = Calle(7, self, "S", 1, [2, 3], [2, 2])
        self.grid.place_agent(c7, tuple(c7.inicio))
        self.gps.append(c7)
        c8 = Calle(8, self, "S", 2, [2, 2], [2, 0])
        self.grid.place_agent(c8, tuple(c8.inicio))
        self.gps.append(c8)
        c8_2 = Calle(82, self, "O", 2, [2, 2], [0, 2])
        self.grid.place_agent(c8_2, tuple(c8_2.inicio))
        self.gps.append(c8_2)
        c10 = Calle(10, self, "E", 1, [2, 0], [3, 0])
        self.grid.place_agent(c10, tuple(c10.inicio))
        self.gps.append(c10)
        c12 = Calle(12, self, "N", 1, [5, 1], [5, 2])
        self.grid.place_agent(c12, tuple(c12.inicio))
        self.gps.append(c12)
        c13 = Calle(13, self, "O", 2, [5, 2], [3, 2])
        self.grid.place_agent(c13, tuple(c13.inicio))
        self.gps.append(c13)
        c17 = Calle(17, self, "E", 2, [0, 3], [2, 3])
        self.grid.place_agent(c17, tuple(c17.inicio))
        self.gps.append(c17)
        c18 = Calle(18, self, "S", 2, [0, 2], [0, 0])
        self.grid.place_agent(c18, tuple(c18.inicio))
        self.gps.append(c18)
        c18_2 = Calle(182, self, "N", 1, [0, 2], [0, 3])
        self.grid.place_agent(c18_2, tuple(c18_2.inicio))
        self.gps.append(c18_2)
        c21 = Calle(21, self, "E", 1, [0, 0], [2, 0])
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

        #for i in range(self.numAgents):


class Main:

    model = GPS(10, 10, 1)

    count = 0

    while count < 30:
        model.step()
        count += 1
        time.sleep(0.7)


Main()
