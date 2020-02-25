from flask import *
import RPi.GPIO as GPIO
import time
import sys
from os import path, walk
import os
import psutil
from livereload import Server

BOTAO_PIN = 18
PORTA_ABERTA = 24
PORTA_FECHADA = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BOTAO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PORTA_ABERTA, GPIO.OUT)
GPIO.setup(PORTA_FECHADA, GPIO.OUT)

def nomeArquivo():
    file = open("/home/pi/Desktop/porta/nome.txt", 'r' )
    nome = file.read().strip()
    file.close()
    return nome

def dataArquivo():
    file = open("/home/pi/Desktop/porta/data.txt", 'r')
    data = file.read().strip()
    file.close
    return data

def updateEstadoPorta(estado):
    file = open("/home/pi/Desktop/porta/estado_porta.txt", 'w+')
    file.write(str(estado))
    file.flush()
    file.close()
    return
    
def getEstadoPorta():
    file = open("/home/pi/Desktop/porta/estado_porta.txt", 'r')
    state = file.read().strip()
    file.close()
    return state

def abrir_Porta():
    GPIO.output(PORTA_ABERTA, GPIO.HIGH)
    GPIO.output(PORTA_FECHADA, GPIO.LOW)
    estado = "Aberta"
    updateEstadoPorta(estado)
    return
    
def fechar_Porta():
    GPIO.output(PORTA_FECHADA, GPIO.HIGH)
    GPIO.output(PORTA_ABERTA, GPIO.LOW)
    estado = "Fechada"
    updateEstadoPorta(estado)
    return

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

@app.route("/", methods = ['GET'])
def index():
    #Le estado das GPIOS
    estadoPorta = getEstadoPorta()
    nome = nomeArquivo()
    data = dataArquivo()
    templateData = {
        'nome' : nome,
        'data' : data,
        'porta' : estadoPorta
        }
    return render_template('index.html', **templateData)

@app.route("/porta/<int:state>", methods=['POST'])
def led(state):
    if state == 1:
        abrir_Porta()
    elif state == 0:
        fechar_Porta()
    else:
        return ('Unknown LED state', 400)
    return ('', 204)
       
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    server = Server(app.wsgi_app)
    server.watch('/home/pi/Desktop/porta/estado_porta.txt', ignore = False)
    server.serve(port= 8080, host='192.168.0.16')
    
