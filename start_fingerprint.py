import hashlib
import time
from nomes import *
from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver
import RPi.GPIO as GPIO
import os
from datetime import datetime

BOTAO_PIN = 18
PORTA_ABERTA = 24
PORTA_FECHADA = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BOTAO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PORTA_ABERTA, GPIO.OUT)
GPIO.setup(PORTA_FECHADA, GPIO.OUT)

## tenta inicializar sensor de digitais
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
except Exception as e:
    print('O leitor de digitais nao pode ser inicializado!')
    visor.lcd_clear()
    visor.lcd_display_string('  Impossivel  ', 1)
    visor.lcd_display_string(' inizalizar! ',2)
    print('Mensagem exceção: ' + str(e))
    exit(1)
    
def updateEstadoPorta(estado):
    file = open("/home/pi/Desktop/porta/estado_porta.txt", 'w+')
    file.write(str(estado))
    file.flush()
    file.close()
    return
    
def nomeArquivo(nome):
    file = open("/home/pi/Desktop/porta/nome.txt", 'w+' )
    file.write(str(nome))
    file.flush()
    file.close()
    return

def dataArquivo(data):
    file = open("/home/pi/Desktop/porta/data.txt", 'w+')
    file.write(str(data))
    file.flush()
    file.close
    return
    
def abrir_Porta():
    controle_porta(0)
    estado = "Aberta"
    updateEstadoPorta(estado)
    return
    
def fechar_Porta():
    controle_porta(1)
    estado = "Fechada"
    updateEstadoPorta(estado)
    return
    
def controle_porta(estado):
    if estado == 0:
        estado = "Aberta"
        updateEstadoPorta(estado)
        GPIO.output(PORTA_FECHADA, GPIO.LOW)
        GPIO.output(PORTA_ABERTA, GPIO.HIGH)
    elif estado == 1:
        estado = "Fechada"
        updateEstadoPorta(estado)
        GPIO.output(PORTA_FECHADA, GPIO.HIGH)
        GPIO.output(PORTA_ABERTA, GPIO.LOW)
    #GPIO.cleanup()
    return
    
def cadastrar_dedo():
    print("Botão pressionado!")
    print("Iniciando cadastro...!")
    visor.lcd_clear()
    visor.lcd_display_string("Iniciando ", 1)
    visor.lcd_display_string("cadastro...", 2)
    time.sleep(2)
    visor.lcd_clear()
    modelo_contagem = f.getTemplateCount()
    capacidade_armazenamento = f.getStorageCapacity()
    print('Modelos Atualmente usados :' + str(modelo_contagem) + '/' + str (capacidade_armazenamento))
    visor.lcd_clear()
    visor.lcd_display_string('Usando :' + str(modelo_contagem) + '/' + str (capacidade_armazenamento))
    time.sleep(2)
    
    ##tenta cadastrar novo dedo
    tentativa = 0
    assinatura = []
    posicao = []
    
    while tentativa < 3 and len(assinatura) < 2:
        try:
            print('Esperando por dedo...')
            visor.lcd_clear()
            visor.lcd_display_string('   Esperando    ', 1)
            visor.lcd_display_string('      dedo......', 2)
            
            ###aguarda enquanto dedo é lido
            while ( f.readImage() == False ):
                pass
            
            ##converte imagem lida e armazena no buffer 1
            f.convertImage(0x01)
            
            ##checa se dedojá existe
            resultado = f.searchTemplate()
            posicaoNumero = resultado[0]
            
            if( posicaoNumero >= 0 ):
                print('Digital já existe na posição #' + str(posicaoNumero))
                visor.lcd_clear()
                visor.lcd_display_string('   Já Existe ', 1)
                visor.lcd_display_string('      em #' + str(posicaoNumero))
                time.sleep(2)
                visor.lcd_clear()
                break
            
            print('Remova dedo...')
            visor.lcd_clear()
            visor.lcd_display_string('Remova dedo...')
            time.sleep(2)
            
            print('Esperando pelo mesmo dedo novamente...')
            visor.lcd_clear()
            visor.lcd_display_string('Esperando mesmo ')
            visor.lcd_display_string('dedo novamente..')
            time.sleep(2)
            
            while ( f.readImage() == False ):
                pass
                
            ##converte imagem lida e armazena no buffer 2
            f.convertImage(0x02)
            
            if ( f.compareCharacteristics() == 0):
                raise Exception('Dedos não combinam!')
            
            ##cria um modelo
            f.createTemplate()
            
            #salva template em uma nova posicao
            test_confirm = 1
            posicao.append(f.storeTemplate())
            assinatura.append(hashlib.sha256(str(f.downloadCharacteristics(0x01)).encode('utf-8')).hexdigest())
            
            if(test_confirm == 1):
                print('Dedo salvo com sucesso!')
                visor.lcd_clear()
                visor.lcd_display_string('Salvo em #' + str(posicao), 1)
                time.sleep(2)
                print('Aguardando digital...')
                visor.lcd_clear()
                visor.lcd_display_string(' Aguardando ',1)
                visor.lcd_display_string(' digital...', 2)
                return 0
            else:
                print('Operação falhou!')
                visor.lcd_clear()
                visor.lcd_display_string('   ERRO!   ', 1)
                time.sleep(2)
                print('Tentativas expiradas')
                visor.lcd_clear()
                visor.lcd_display_string('   Tentativas   ', 1)
                visor.lcd_display_string('   expiradas   ', 2)
    
            time.sleep(2)
            visor.lcd_clear()
            
        except Exception as e:
            tentativa += 1
            visor.lcd_clear()
            visor.lcd_display_string('   ERRO!   ', 1)
            time.sleep(2)
            print('Mensagem exception: ' + str(e))
            visor.lcd_clear()
            visor.lcd_display_string(str(e)[:16], 1)
            visor.lcd_display_string(str(e)[16:], 2)
            print('Tente Novamente..')
            
#GPIO.add_event_detect(BOTAO_PIN, GPIO.FALLING, callback = cadastrar_dedo, bouncetime=300)
## Inicializa display LCD
try:
    visor = I2C_LCD_driver.lcd()
    visor.lcd_clear()
    visor.lcd_display_string('Initializing....', 1)

except Exception as e:
    print('The LCD could not be initialized')
    print('Exception message: ' +str(e))
    exit(1)

while True:
    modelo_contagem = f.getTemplateCount()
    capacidade_armazenamento = f.getStorageCapacity()
    print('Modelos Atualmente usados :' + str(modelo_contagem) + '/' + str (capacidade_armazenamento))
    visor.lcd_clear()
    visor.lcd_display_string('Usando :' + str(modelo_contagem) + '/' + str (capacidade_armazenamento))
    time.sleep(2)
    
    try:
        print('Aguardando dedo...')
        visor.lcd_clear()
        visor.lcd_display_string('   Aguardando   ', 1)
        visor.lcd_display_string('      dedo..... ', 2)
              
        while ( f.readImage() == False ):
            if GPIO.input(18) == GPIO.HIGH:
                cadastrar_dedo()
            pass
    
        f.convertImage(0x01)
    
        resultado = f.searchTemplate()
    
        posicaoNumero = resultado[0]
        precisao = resultado[1]
        valor_nome = str(posicaoNumero)
    
        if( posicaoNumero == -1 ):
            print('Nenhum encontrado!')
            visor.lcd_clear()
            visor.lcd_display_string('     Nenhum     ', 1)
            visor.lcd_display_string('   Encontrado   ', 2)
            time.sleep(2)
            visor.lcd_clear()
            continue
        
        print('Digital encontrada na posicao #' + str(posicaoNumero))
        print('A precisao é: ' + str(precisao))
    
        print("Olá, " + nome[valor_nome])
        print("Abrindo porta...")
        import os
        dataArquivo(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        nomeArquivo(nome[valor_nome])
        visor.lcd_clear()
        visor.lcd_display_string("Olá, " + nome[valor_nome], 1)
        visor.lcd_display_string("Abrindo porta...", 2)
        #adicionar trigger para fechamento de porta
        ##chave fim de curso, tempo etc...
        abrir_Porta()
        time.sleep(5)
        print("Fechando porta...")
        visor.lcd_clear()
        visor.lcd_display_string("Fechnado Porta...", 1)
        fechar_Porta()
        time.sleep(2)
        visor.lcd_clear()
    
    except Exception as e:
        print('Operação falhou!')
        print('Mensagem Exceção :' +str(e))
