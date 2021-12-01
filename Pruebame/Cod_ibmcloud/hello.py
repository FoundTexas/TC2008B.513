from flask import Flask, render_template, request, jsonify
import json, logging, os, atexit

from model import CruceModel

app = Flask(__name__, static_url_path = '')

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

model = CruceModel(20,len(matrix[0]),len(matrix),matrix)

def positionsToJSON(ps,pb):
    posDICT = []
    for p in range(len(ps)):
        pos = {
            "x" : ps[p][0],
            "y" : ps[p][1],
            "z" : ps[p][2],
            "b": pb[p].Routeing
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


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


@app.route('/')

def root():
    return jsonify([{"message":"Hello"}])

@app.route('/calles', methods=['GET','POST'])

def calles():
    positions = model.Calles
    return CallesToJSON(positions)

@app.route('/muliagentes', methods=['GET','POST'])

def multiagentes():
    positions,bools = model.step()
    return positionsToJSON(positions,bools)

@app.route('/semaforos', methods=['GET','POST'])

def semaforos():
    lights = model.step2()
    return BoolsToJSON(lights)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port = port, debug = True)