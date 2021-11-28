# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python server to interact with Unity
# Sergio. Julio 2021

from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request, jsonify
import logging
import json, os, atexit

import numpy as np
from model import CruceModel

app = Flask(__name__, static_url_path = '')

model = CruceModel(4,10,10)

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