from PyQt5.QtCore import QState, pyqtSignal, QTimer
from paho.mqtt import publish
from datetime import datetime
from threading import Timer
from os.path import exists, join
from time import strftime
from pickle import load
from copy import copy
from os import system
import requests
import pprint
import json
from time import sleep              # Para usar la función sleep(segundos)
from toolkit.admin import Admin

class Startup(QState):
    ok  = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        Timer(0.05, self.model.log, args = ("STARTUP",)).start() 
        if exists("data\config"):
            with open("data\config", "rb") as f:
                data = load(f)
                if "encoder_feedback" in data:
                    for i in data["encoder_feedback"]:
                        if type(data["encoder_feedback"][i]) == bool:
                            self.model.config_data["encoder_feedback"][i] = data["encoder_feedback"][i]
                if "retry_btn_mode" in data:
                    for i in data["retry_btn_mode"]:
                        if type(data["retry_btn_mode"][i]) == bool:
                            self.model.config_data[ "retry_btn_mode"][i] = data[ "retry_btn_mode"][i]
        self.model.config_data["untwist"] = False
        self.model.config_data["flexible_mode"] = False

        if self.model.local_data["user"]["type"] != "":
            Timer(0.05, self.logout, args = (copy(self.model.local_data["user"]),)).start()

        self.model.local_data["user"]["type"] = ""
        self.model.local_data["user"]["name"] = ""
        self.model.local_data["user"]["pass"] = ""
        command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
            "lbl_info3" : {"text": "", "color": "black"},
            "lbl_boxTITLE" : {"text": "", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            "lbl_result" : {"text": "Se requiere un login para continuar", "color": "green"},
            "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"},
            "img_user" : "blanco.jpg",
            "lbl_user" : {"type":"", "user": "", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lcdNumber": {"value": "0", "visible": False},
            "lbl_nuts"  : {"text": "", "color": "black"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "position" : {"text": "POSICIÓN 1", "color": "black"},
            "img_center" : "logo.jpg"
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command["position"]["text"] = "POSICIÓN 2"
        command["lcdNumber"]["value"] = "0"
        command["lcdNumber"]["visible"] = True
        #command = {"position":{"text": "POSICIÓN 2"}, "lcdNumber": {"value": "0", "visible": True},#}
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        try:
            turnos = {
            "1":["07-00","18-59"],
            "2":["19-00","06-59"],
            }

            endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
            response = requests.get(endpoint, data=json.dumps(turnos))
            response = response.json()
            print("response: ",response)
            print("He aqui el elefante de la habitacion")

            command = {
                    "lcdNumber" : {"value": response["conteo"]}
                    }

            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        except Exception as ex:
            print("Error en el conteo ", ex)

        QTimer.singleShot(10, self.stopTorque)
        QTimer.singleShot(15, self.kioskMode)
        self.ok.emit()

    def stopTorque (self):
        publish.single(self.model.pub_topics["torque"]["tool1"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["torque"]["tool2"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["torque"]["tool3"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)

    def kioskMode(self):
        system("taskkill /f /im explorer.exe")
        publish.single("modules/set",json.dumps({"window" : False}),hostname='127.0.0.1', qos = 2)
        publish.single("visycam/set",json.dumps({"window" : False}),hostname='127.0.0.1', qos = 2)

    def logout(self, user):
        try:
            Timer(0.05, self.model.log, args = ("LOGOUT",)).start() 
            data = {
                "NAME": user["name"],
                "GAFET": user["pass"],
                "TYPE": user["type"],
                "LOG": "LOGOUT",
                "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                }
            endpoint = "http://{}/api/post/login".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        except Exception as ex:
            print("Logout Exception: ", ex)


class Login (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
    def onEntry(self, event):
        command = {
            "show":{"login": True},
            "allow_close": True
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)


class CheckLogin (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "lbl_result" : {"text": "ID recibido", "color": "green"},
            "lbl_steps" : {"text": "Validando usuario...", "color": "black"},
            "show":{"login": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(0.05,self.API_requests).start()

    def API_requests (self):
        try:
            endpoint = ("http://{}/api/get/usuarios/GAFET/=/{}/ACTIVE/=/1".format(self.model.server, self.model.input_data["gui"]["ID"]))
            response = requests.get(endpoint).json()

            if "TYPE" in response:
                self.model.local_data["user"]["type"] = response["TYPE"]
                self.model.local_data["user"]["name"] = response["NAME"]
                self.model.local_data["user"]["pass"] = copy(self.model.input_data["gui"]["ID"])
                data = {
                    "NAME": self.model.local_data["user"]["name"],
                    "GAFET":  self.model.local_data["user"]["pass"],
                    "TYPE": self.model.local_data["user"]["type"],
                    "LOG": "LOGIN",
                    "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                    }
                endpoint = "http://{}/api/post/login".format(self.model.server)
                resp = requests.post(endpoint, data=json.dumps(data))

                command = {
                    "lbl_user" : {"type":self.model.local_data["user"]["type"],
                                  "user": self.model.local_data["user"]["name"], 
                                  "color": "black"
                                  },
                    "img_user" : self.model.local_data["user"]["name"] + ".jpg"
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.model.log, args = ("LOGIN",)).start() 
                self.ok.emit()
            else:
                 command = {
                    "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                    "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                    }
                 publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                 publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                 self.nok.emit()
        except Exception as ex:
            print("Login request exception: ", ex)
            command = {
                "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()


class StartCycle (QState):
    ok = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.clamps = True

    def onEntry(self, event):
        minutos=0
        segundos=0
        color="black"
        try:
            query="SELECT INICIO, FIN FROM et_mbi_2.historial WHERE RESULTADO = 1 order by ID desc LIMIT 1;"
            endpoint = "http://{}/query/get/{}".format(self.model.server, query)
            print("Endpoint: ",endpoint)
        
            resp_ultimo_arnés = requests.get(endpoint).json()
            
            in_formato_ciclo=datetime.strptime(resp_ultimo_arnés["INICIO"][0], '%a, %d %b %Y %H:%M:%S GMT')
            out_formato_ciclo=datetime.strptime(resp_ultimo_arnés["FIN"][0], '%a, %d %b %Y %H:%M:%S GMT')

            # Calcula la diferencia entre la fecha de fin y la fecha de inicio
            diferencia = out_formato_ciclo - in_formato_ciclo
            
            # Extrae los minutos y segundos de la diferencia
            minutos, segundos = divmod(diferencia.total_seconds(), 60)

            if minutos >10 :
                color="red"
            else:
                color="green"
            # Imprime el resultado
            print(f"ciclo: {int(minutos)} min {int(segundos)} segundos")
            print(in_formato_ciclo)

        except Exception as ex:
            print("Excepción al momento de extraer el ultimo arnes", ex)
        
        command = {
                "lineEdit" : False,
                "lineEditKey": True,
                }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        print("lineEdit desactivado")
        self.model.pdcr_iniciada=False
        self.model.qr_box_actual=""
        self.model.caja_repetida_hm_asociado=""
        self.model.qr_validado=[]
        self.model.key_calidad_caja_repetida=False
        self.model.caja_por_validar=""
        #reiniciar variable para dar delay entre cada pin
        self.model.nuevo_pin = False
        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False
        #regresa variable que permite escanear otra caja
        self.model.pdcr_iniciada=False
        #para funcionamiento normal de llave
        self.model.reintento_torque = False
        command = {
            "DISABLE_PDC-R":False,
            "DISABLE_PDC-RMID":False,
            "DISABLE_MFB-S":False,
            "DISABLE_MFB-P1":False,
            "DISABLE_MFB-P2":False,
            "DISABLE_PDC-P":False,
            "DISABLE_PDC-D":False,
            "DISABLE_MFB-E":False,
            "DISABLE_BATTERY":False,
            "DISABLE_BATTERY-2":False
            }
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""
        self.model.herramienta_activa = "0"     # Se resetea la herramienta activa en cada inicio de ciclo... para que el sistema pueda activar la herramienta requerida y no interfiera con las demás.

        self.model.reset()
        Timer(0.05, self.model.log, args = ("IDLE",)).start() 




        command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
            "lbl_info3" : {"text": "", "color": "black"},
            "lbl_boxTITLE" : {"text": f"último ciclo: \n{int(minutos)} min {int(segundos)} segundos", "color": color},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            "lbl_result" : {"text": "Esperando nuevo ciclo", "color": "green"},
            "lbl_steps" : {"text": "Escanea la etiqueta FET", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts" : {"text": "", "color": "orange"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent" : {"text": "", "color": "orange"},
            "position" : {"text": "POSICIÓN 1", "color": "black"},
            "img_center" : "logo.jpg",
            "allow_close": False,
            "cycle_started": False,
            "statusBar": "clear"
            }
        if self.model.shutdown == True:
            Timer(0.05, self.logout, args = (copy(self.model.local_data["user"]),)).start()
            command["lbl_result"] = {"text": "Apagando equipo...", "color": "green"}
            command["lbl_steps"] = {"text": ""}
            command["shutdown"] = True
            self.clamps = False
            QTimer.singleShot(3000, self.torqueClamp)
        if self.model.config_data["trazabilidad"]:
            command["lbl_info3"] = {"text": "Trazabilidad\n\nActivada", "color": "green"}
        else:
            command["lbl_info3"] = {"text": "Trazabilidad\nDesactivada", "color": "red"}
        if self.model.config_data["untwist"]:
            command["lbl_info3"] = {"text": "MODO:\n\nREVERSA", "color": "red"}
        if self.model.config_data["flexible_mode"]:
            if self.model.config_data["untwist"]:
                command["lbl_info3"]["text"] += "\nPUNTUAL"
                command["lbl_info3"]["color"] = "red"
            else:
                command["lbl_info3"] = {"text": "MODO:\n\nAPRIETE\nPUNTUAL", "color": "red"}
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("shutdown", None)
        command.pop("show", None)

        command["position"]["text"] = "POSICIÓN 2"
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        try:
            turnos = {
            "1":["07-00","18-59"],
            "2":["19-00","06-59"],
            }

            endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
            response = requests.get(endpoint, data=json.dumps(turnos))
            response = response.json()
            print("response: ",response)

            command = {
                    "lcdNumber" : {"value": response["conteo"]}
                    }

            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        except Exception as ex:
            print("Error en el conteo ", ex)
                
        QTimer.singleShot(100, self.stopTorque)

        if not(self.model.shutdown):
            self.ok.emit()


    def torqueClamp (self):
        command = {}
        for i in self.model.torque_cycles:
             command[i] = self.clamps
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def stopTorque (self):
        for i in self.model.pub_topics["torque"]:
            profile = self.model.torque_data[i]["stop_profile"]
            publish.single(self.model.pub_topics["torque"][i],json.dumps({"profile" : profile}),hostname='127.0.0.1', qos = 2)

    def logout(self, user):
        try:
            Timer(0.05, self.model.log, args = ("LOGOUT",)).start() 
            data = {
                "NAME": user["name"],
                "GAFET": user["pass"],
                "TYPE": user["type"],
                "LOG": "LOGOUT",
                "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                }
            endpoint = "http://{}/api/post/login".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        except Exception as ex:
            print("Logout Exception: ", ex)


class Config (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.admin = None

    def onEntry(self, event):
        Timer(0.05, self.model.log, args = ("CONFIG",)).start() 
        admin = Admin(data = self.model)

        command = {
            "lbl_result" : {"text": "Sistema en configuración", "color": "green"},
            "lbl_steps" : {"text": "Ciclo de operación deshabilitado", "color": "black"}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def onExit (self, event):
        if exists("data\config"):
            with open("data\config", "rb") as f:
                data = load(f)
                if "encoder_feedback" in data:
                    for i in data["encoder_feedback"]:
                        if type(data["encoder_feedback"][i]) == bool:
                            self.model.config_data["encoder_feedback"][i] = data["encoder_feedback"][i]
                if "retry_btn_mode" in data:
                    for i in data["retry_btn_mode"]:
                        if type(data["retry_btn_mode"][i]) == bool:
                            self.model.config_data[ "retry_btn_mode"][i] = data[ "retry_btn_mode"][i]
                if "untwist" in data:
                    if type(data["untwist"]) == bool:
                        self.model.config_data["untwist"] = data["untwist"]


class ScanQr (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "show":{"scanner": True}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("show")
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = True
        print("model qr_keyboard = True")

    def onExit(self, QEvent):
        command = {
            "show":{"scanner": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = False
        print("model qr_keyboard = False")


class CheckQr (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()
    rework  = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "lbl_result" : {"text": "Datamatrix escaneado", "color": "green"},
            "lbl_steps" : {"text": "Validando", "color": "black"}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)


        Timer(0.05, self.API_requests).start()

    def API_requests (self):
        try:
            print("Estado de Sistema de Trazabilidad: ",self.model.config_data["trazabilidad"])
            pedido = None
            dbEvent = None
            coincidencias = 0
            self.model.qr_codes["FET"] = self.model.input_data["gui"]["code"]
            temp = self.model.input_data["gui"]["code"].split (" ")
            self.model.qr_codes["HM"] = "--"
            self.model.qr_codes["REF"] = "--"
            correct_lbl = False
            
            for i in temp:
                if "HM" in i:
                    self.model.qr_codes["HM"] = i

                    if "HM000000011936" in i:
                        self.model.config_data["trazabilidad"] = False
                        
                    if "HM000000011925" in i:
                        self.model.config_data["trazabilidad"] = False

                    if "HM000000011920" in i:
                        self.model.config_data["trazabilidad"] = False


                    if self.model.config_data["trazabilidad"] == False:
                        command = {
                            "lbl_info3" : {"text": "Trazabilidad\nDesactivada", "color": "red"}
                        }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                ############# MODIFICACIÓN #############
                if "IL" in i or "IR" in i: #Se agregó la opción de escanear etiquetas con prefijo "IR"
                ############# MODIFICACIÓN #############
                    self.model.qr_codes["REF"] = i
                if "EL." in i:
                    correct_lbl = True

            if not(correct_lbl):
                command = {
                        "lbl_result" : {"text": "Datamatrix incorrecto", "color": "red"},
                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.nok.emit()
                return

            #### Trazabilidad FAMX2
            if self.model.config_data["trazabilidad"] and self.model.config_data["untwist"]==False and self.model.config_data["flexible_mode"]==False:
                try:
                    print("||||||||||||Consulta de HM a FAMX2...")
                    endpoint = "http://{}/seghm/get/seghm/NAMEPREENSAMBLE/=/INTERIOR/HM/=/{}".format(self.model.server,self.model.qr_codes["HM"])
                    famx2response = requests.get(endpoint).json()
                    print("Respuesta de FAMX2: \n",famx2response)
                    #No existen coincidencias del HM en FAMX2
                    if "items" in famx2response:
                        print("ITEMS por que no se encontraron coincidencias en FAMX2")
                        command = {
                            "lbl_result" : {"text": "HM no registrado en Sistema de Trazabilidad", "color": "red"},
                            "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                            }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return
                    #Si existe el HM en FAMX2
                    else:
                        print("FAMX2 Salida de FET: \n",famx2response["SALFET"])
                        print("FAMX2 Ubicación: \n",famx2response["UBICACION"])

                        respuesta_Fet=self.caja_FET_consulta(self.model.qr_codes["HM"])
                        #Si la columna que indica la hora de salida de FET, es diferente a None, significa que completó esa estación y SI puede entrar a Torque.
                        if famx2response["SALFET"] != None: #AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
                            print("El arnés ya salió de FET")
                            print("famx2response[UBICACION]",famx2response["UBICACION"])
                            self.model.name_FET=str(famx2response["NAMEFET"])
                            ubic_sinspace = famx2response["UBICACION"]
                            ubic_sinspace = ubic_sinspace.replace(" ","")
                            #Si la ubicación del HM del Arnés se encuentra entrando en reparación, NO podrá entrar a Torque
                            if ubic_sinspace != "SALIDA_DE_FET" and ubic_sinspace != "ENTRADA_A_TORQUE":

                                command = {
                                "lbl_result" : {"text": "Ubicación Incorrecta de HM:" + ubic_sinspace, "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                self.nok.emit()
                                return
                            if self.model.config_data["comparacion_cajasDP"]:
                                if respuesta_Fet == None:
                                    print("No se encontró registro en FET")
                                    FET_arnes_station = str(famx2response["NAMEFET"])
                                    FET_arnes_station = FET_arnes_station.replace(" ","")
                            
                                    command = {
                                    "lbl_result" : {"text": "No se encontró registros de cajas en FET " + FET_arnes_station, "color": "red"},
                                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                    }
                                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                    self.nok.emit()
                                    return

                            if famx2response["REFERENCIA"] !=self.model.qr_codes["REF"]:
                                print("La REFERENCIA no coincide con Trazabilidad, NO puede entrar a Torque")
                                command = {
                                "lbl_result" : {"text": "REFERENCIA de etiqueta no coincide con trazabilidad", "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                self.nok.emit()
                                return
                            
                            else:
                                #Se guarda el id del arnés de FAMX2 en el modelo para realizar updates en el servidor de FAMX2.
                                self.model.id_HM = famx2response["id"]
                                self.model.datetime = datetime.now()
                                #### Trazabilidad FAMX2 Update de Información
                                print("||Realizando el Update de ENTRADA a Trazabilidad en FAMX2")
                                print("ID a la que se realizará el Update para Trazabilidad",self.model.id_HM)
                                entTrazabilidad = {
                                    "ENTTORQUE": self.model.datetime.strftime("%Y/%m/%d %H:%M:%S"),
                                    "UBICACION": "ENTRADA_A_TORQUE",
                                    "NAMETORQUE": self.model.serial
                                    }
                                endpointUpdate = "http://{}/seghm/update/seghm/{}".format(self.model.server,self.model.id_HM)

                                respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                respTrazabilidad = respTrazabilidad.json()
                                print("respTrazabilidad del update: ",respTrazabilidad)

                                sleep(0.1)
                                respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                respTrazabilidad = respTrazabilidad.json()
                                print("respTrazabilidad del update: ",respTrazabilidad)

                                sleep(0.1)
                                respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                respTrazabilidad = respTrazabilidad.json()
                                print("respTrazabilidad del update: ",respTrazabilidad)

                                #### Trazabilidad FAMX2 Update de Información
                        #Si la columna que indica la hora de salida de FET es None, significa que no ha completado esa estación y NO puede entrar aún a Torque.
                        else:
                            print("El Arnés no ha pasado por la estación anterior (FET) por lo que no puede entrar a Torque")
                            command = {
                            "lbl_result" : {"text": "Arnés sin Historial de FET", "color": "red"},
                            "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                            }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                except Exception as ex:
                    print("Conexión con FAMX2 exception: ", ex)
                    command = {
                            "lbl_result" : {"text": "Error de Conexión con Sistema de Trazabilidad", "color": "red", "font": "40pt"},
                            "lbl_steps" : {"text": "Verifique su conexión o deshabilite el Sistema de Trazabilidad con supervisión \nde personal de calidad", "color": "black", "font": "22pt"}
                            }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.nok.emit()
                    return
            ####

            ####### Original
            endpoint = "http://{}/api/get/eventos".format(self.model.server)
            eventos = requests.get(endpoint).json()
            #print("Lista eventos:\n",eventos)
            for key in eventos["eventos"].keys():
                print("++++++++++++++Evento Actual++++++++++++++++:\n ",key)
                print("Valor Activo del Evento actual: ",eventos["eventos"][key][1])
                if eventos["eventos"][key][1] == 1:
                    endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server, key, self.model.qr_codes["REF"])
                    response = requests.get(endpoint).json()
                    #print("Response: ",response)
                    if "PEDIDO" in response:
                        dbEvent = key
                        coincidencias += 1
                        print("En este Evento se encuentra la modularidad \n")
                        pedido = response
            print("Coincidencias = ",coincidencias)
            if dbEvent != None:
                print("La Modularidad pertenece al Evento: ",dbEvent)
                if coincidencias != 1:
                    print("Datamatrix Redundante")
                    command = {
                        "lbl_result" : {"text": "Datamatrix redundante", "color": "red"},
                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                        }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.nok.emit()
                    return
                else:
                    print("Datamatrix Correcto")
            else:
                print("La Modularidad NO pertenece a ningún evento")
                command = {
                    "lbl_result" : {"text": "Datamatrix no registrado", "color": "red"},
                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.nok.emit()
                return

            endpoint = "http://{}/api/get/{}/pdcr/variantes".format(self.model.server, dbEvent)
            pdcrVariantes = requests.get(endpoint).json()
            print("Lista Final de Variantes PDC-R:\n",pdcrVariantes)

            endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server, self.model.qr_codes["HM"])
            response = requests.get(endpoint).json()

            if ("items" in response and not(response["items"])) or self.model.local_data["qr_rework"] or self.model.config_data["untwist"] or self.model.config_data["flexible_mode"]:
                #Si el modo de operación de la máquina es Flexible, Reversa, o Reversa Flexible
                if self.model.config_data["flexible_mode"] or self.model.config_data["untwist"]:
                    #Si el arnés ya ha pasado por la máquina anteriormente, y se va a retrabajar (debe tener SERIALES en response), hará lo siguiente:
                    if "SERIALES" in response:
                        print("Response*******: ",response["SERIALES"])
                        if type(response["SERIALES"]) != list:
                            print("ES UN SOLO REGISTRO!")
                            qr_retrabajo = json.loads(response["SERIALES"])
                            [qr_retrabajo.pop(key, None) for key in ['FET','HM','REF']]
                            self.model.input_data["database"]["qr_retrabajo"] = qr_retrabajo
                            if "PDC-P" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["PDC-P"] = "009"
                            if "MFB-E" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["MFB-E"] = "004"
                            print("Qr_retrabajo modelo: ",self.model.input_data["database"]["qr_retrabajo"])
                        else:
                            print("ES UNA LISTA DE REGISTROS!")
                            qr_retrabajo = json.loads(response["SERIALES"][-1])
                            [qr_retrabajo.pop(key, None) for key in ['FET','HM','REF']]
                            self.model.input_data["database"]["qr_retrabajo"] = qr_retrabajo
                            if "PDC-P" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["PDC-P"] = "009"
                            if "MFB-E" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["MFB-E"] = "004"
                            print("Qr_retrabajo modelo: ",self.model.input_data["database"]["qr_retrabajo"])
                    # Si el arnés que intentan retrabajar es la primera vez que entra a la máquina indicará un error al usuario
                    else:
                        command = {
                            "lbl_result" : {"text": "ERROR DE RETRABAJO", "color": "red"},
                            "lbl_steps" : {"text": "No se encontraron registros de este arnés", "color": "black"}
                            }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return
                modules = json.loads(pedido["MODULOS_TORQUE"])
                modules = modules[list(modules)[0]]
                modules_v = json.loads(pedido["MODULOS_VISION"])
                modules_v = modules_v[list(modules_v)[0]]

                print(f"\n\t\tMODULOS_VISION:\n{modules_v}")
                print("\n\t+++++++++++MODULARIDAD REFERENCIA+++++++++++\n",self.model.qr_codes["REF"])
                print(f"\n\t\tMODULOS_TORQUE:\n{modules}")
                #### MODIFICACIÓN PDCR ####
                flag_s = False
                flag_m = False
                flag_l = False
                flag_variantes = True
                flag_mfbp2_der = False
                flag_mfbp2_izq = False
                mfbp2_serie = ""
                mfbeBox = ""
                battery2Box = ""
                flag_294 = False
                flag_296 = False
                if "294" in self.model.qr_codes["REF"]:
                    print("Evento 294")
                    flag_294 = True
                if "296" in self.model.qr_codes["REF"]:
                    print("Evento 296")
                    flag_296 = True
                    #print("Aqui",pdcrVariantes)
                for s in pdcrVariantes["small"]:
                    if s in modules:
                        #print("Tiene un modulo de caja SMALL")
                        flag_s = True
                for m in pdcrVariantes["medium"]:
                    if m in modules:
                        #print("Tiene un modulo de caja Medium")
                        flag_m = True
                for l in pdcrVariantes["large"]:
                    if l in modules:
                        #print("Tiene un modulo de caja LARGE")
                        flag_l = True
                if "IL" in self.model.qr_codes["REF"]:
                    print("Modularidad de MFB-P2 Izquierda")
                    flag_mfbp2_izq = True
                if "IR" in self.model.qr_codes["REF"]:
                    print("Modularidad de MFB-P2 Derecha")
                    flag_mfbp2_der = True

                print("\t\tFLAGS:\n Flag S - ",flag_s," Flag M - ",flag_m," Flag L - ",flag_l,"\n Flag MFB-P2 DER - ",flag_mfbp2_der," Flag MFB-P2 IZQ - ",flag_mfbp2_izq)
                if flag_s == False and flag_m == False and flag_l == False:
                    flag_variantes = False

                #para mensajes que se publican
                if flag_l == True:
                    varianteDominante = "PDC-R"
                    self.model.largeflag = True
                    self.model.pdcr_serie = "12239061602"
                if flag_m == True and flag_l == False:
                    varianteDominante = "PDC-RMID"
                    self.model.mediumflag = True
                    self.model.pdcr_serie = "12239061502"
                if flag_s == True and flag_m == False and flag_l == False:
                    varianteDominante = "PDC-RS"
                    self.model.smallflag = True
                    self.model.pdcr_serie = "12239061402"

                ################# TORQUE #################
                for i in modules:
                    endpoint = "http://{}/api/get/{}/modulos_torques/MODULO/=/{}/_/=/_".format(self.model.server, dbEvent, i)
                    response = requests.get(endpoint).json()
                    if "MODULO" in response:
                        if type(response["MODULO"]) != list:
                            temp = {}
                            for i in response:
                                if "CAJA_" in i:
                                    temp.update(json.loads(response[i]))
                            for i in temp:
                                newBox = False
                                #print("Caja: ******: ",i)
                                if len(temp[i]) == 0:
                                    continue
                                if not(i in self.model.input_data["database"]["modularity"]):
                                    newBox = True
                                for j in temp[i]:
                                    if temp[i][j] == True:
                                        if newBox:
                                            if flag_296 == True or flag_294 == True:
                                                if flag_variantes == True:
                                                    #si hay una caja PDC-R se modifica por la variable PDC-R dominante
                                                    if i == "PDC-R" or i == "PDC-RMID" or i == "PDC-RS":
                                                        i = varianteDominante
                                                else:
                                                    #print("LA MODULARIDAD NO CONTIENE MÓDULOS QUE ESPECIFIQUEN SU VARIANTE EN LA PDC-R")
                                                    command = {
                                                        "lbl_result" : {"text": "La Modularidad no contiene módulos que especifiquen su variante en la PDC-R", "color": "red"},
                                                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                                        }
                                                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                                    self.model.input_data["database"]["modularity"].clear()
                                                    self.model.torque_data["tool1"]["queue"].clear()
                                                    self.model.torque_data["tool2"]["queue"].clear()
                                                    self.model.torque_data["tool3"]["queue"].clear()
                                                    self.nok.emit()
                                            self.model.input_data["database"]["modularity"][i] = []
                                            #print(" AQUI ESTÁ EL NUEVO I!!!!!!!!!: ",i)#### MODIFICACIÓN PDCR ####
                                            newBox = False
                                        if not(j in self.model.input_data["database"]["modularity"][i]):
                                            self.model.input_data["database"]["modularity"][i].append(j)
                                            #print(" AQUI ESTÁ EL J valor!!!!!!!!!: ",j)#### MODIFICACIÓN PDCR ####
                                if not(newBox):
                                    #Si la caja es MFB-P2, se acomodan sus torques de manera inversa (A29,A28...) a excepción de los torques para la Tool de 8mm (A20,A25 y A30)
                                    if i == "MFB-P2":
                                        self.model.input_data["database"]["modularity"][i].sort(reverse=True)
                                        if "A20" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A20"))
                                            self.model.input_data["database"]["modularity"][i].append("A20")
                                        if "A25" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A25"))
                                            self.model.input_data["database"]["modularity"][i].append("A25")
                                        if "A30" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A30"))
                                            self.model.input_data["database"]["modularity"][i].append("A30")
                                    #El resto de cajas ordenan sus torques de manera ascendente
                                    else:
                                        self.model.input_data["database"]["modularity"][i].sort()
                        else:
                            command = {
                                    "lbl_result" : {"text": "Módulos de torque redundantes", "color": "red"},
                                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                  }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                    else:
                        command = {
                                "lbl_result" : {"text": "Modulos de torque no encontrados", "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return

                ################# VISION #################
                for i in modules_v:
                    #petición a la base de datos local para ver que fusibles lleva cada modulo
                    endpoint = "http://{}/api/get/{}/modulos_fusibles/MODULO/=/{}/_/=/_".format(self.model.server, dbEvent, i)
                    response = requests.get(endpoint).json()
                    #si encuentra el módulo en la respuesta (que si existe en la base de datos local)...
                    if "MODULO" in response:
                        #si la respuesta para ese módulo no es de tipo lista ( esto quiere decir que no hay más de un módulo de este tipo)
                        if type(response["MODULO"]) != list:
                            current_module = {}
                            for i in response:
                                #si i tiene "CAJA_" y además no está vacío el objeto
                                if "CAJA_" in i and len(response[i]):
                                    if "PDC-R" in i:
                                        #si la caja determinante es PDC-R en los módulos pueden existir PDC-RS, PDC-RMID y PDC-R
                                        if varianteDominante == "PDC-R":
                                            if "PDC-RS" in i:
                                                i = i.replace("PDC-RS",varianteDominante)
                                            if "PDC-RMID" in i:
                                                i = i.replace("PDC-RMID",varianteDominante)
                                        #si la caja determinante es PDC-RMID en los módulos pueden existir PDC-RS y PDC-RMID
                                        if varianteDominante == "PDC-RMID":
                                            if "PDC-RS" in i:
                                                i = i.replace("PDC-RS",varianteDominante)
                                        #si la caja determinante es PDC-RS en los módulos solo pueden existir PDC-RS, entonces no se hace nada

                                    #a current_module le añades esa información
                                    current_module.update(json.loads(response[i]))

                            #recorremos las cajas en current_module
                            for box in current_module:
                                #Solamente se tomarán en cuenta los fusibles pertenecientes a la caja PDC-R para posteriormente en base a ellos determinar cuales CANDADOS revisará el PALPADOR
                                if "PDC-R" in box:                                 
                                    #recorremos las cavidades de los datos del modulo que tienen esa misma caja
                                    for cavity in current_module[box]:
                                        #nunca debería de llega una información de la base de datos de los modulos con un vacío, pero si llegara, no entrará al if
                                        if current_module[box][cavity] != "vacio":
                                            #si la cavidad no se encuentra en esa caja... y no es una cavidad vacía...
                                            if not(cavity in self.model.input_data["database"]["fuses"]):
                                                self.model.input_data["database"]["fuses"].append(cavity)
                        else:
                            command = {
                                    "lbl_result" : {"text": "Módulos de visión redundantes", "color": "red"},
                                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                    }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                    else:
                        command = {
                                "lbl_result" : {"text": "Modulos de visión no encontrados", "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return

                ###############################

                #esto debe ir antes de donde se actualiza self.model.mfbp2_serie
                #debe ir después de que ya existe modules
                #y además ir antes de donde se hace publish de las cajas en los label command = {f"lbl_box{current_boxx}" : {"text": f"{pub_i}", "color": "blue"}}

                print("Evento de este Arnés: ",dbEvent) #puede agregarse un if "aj23_2_pro3" in self.model.dbEvent para limitar a que solamente se cambie en un evento
                #se recorren todos los módulos del arnés para buscar el que determina la caja nueva
                
                self.leer_configuracion()
                if self.model.parametros["CAJA_VIEJA_SIEMPRE"]=="False":
                    for modulo in modules:
                        #para caja MFBP2 izquierda
                        if "A2975407930" in modulo:
                            print("contiene el modulo A2975407930")
                            #si se encuentra el módulo dentro del arnés, se cambia el QR de la caja del generado por la api: 12975407316 al 12975407930
                            pedido["QR_BOXES"] = pedido["QR_BOXES"].replace("12975407316","12975407930")
                        #para caja MFBP2 derechaA2975407830
                        if "A2975407830" in modulo:
                            print("contiene el modulo A2975407830")
                            #si se encuentra el módulo dentro del arnés, se cambia el QR de la caja del generado por la api: 12975407316 al 12975407930
                            pedido["QR_BOXES"] = pedido["QR_BOXES"].replace("12975407216","12975407830")
                            
                
                #self.leer_configuracion() #Función para leer archivo con configuración para caja correr con caja antigua
                #if self.model.parametros["caja_MFBP2_antigua"]=="True":
                #    if "aj2023_1_pro3" in dbEvent or "aj23_1_pro3" in dbEvent:                              #cuando se acaben las cajas de stock esto se quitará
                #        print("Es un caso especial de AJ23 1 PRO3 que debe llevar si o sí la caja vieja")   #cuando se acaben las cajas de stock esto se quitará
                #        pedido["QR_BOXES"] = pedido["QR_BOXES"].replace("12975407930","12975407316")
                        

                QR_CAJAS = json.loads(pedido["QR_BOXES"]) #se lee el string y se convierte a formato json, diccionario

                if flag_mfbp2_der == True and flag_mfbp2_izq == False:
                    self.model.mfbp2_serie = QR_CAJAS["MFB-P2"][0]
                if flag_mfbp2_der == False and flag_mfbp2_izq == True:
                    self.model.mfbp2_serie = QR_CAJAS["MFB-P2"][0]
                if flag_mfbp2_der == False and flag_mfbp2_izq == False:
                    self.model.mfbp2_serie = "Sin especificar"

                ###############################
                for i in self.model.input_data["database"]["modularity"]:
                    print("cajas dentro de modularity: ",i)
                    current_boxx = i
                    current_boxx = current_boxx.replace("-","")

                    if "PDC-R" in i:
                        if self.model.smallflag == True:    
                            self.model.cajas_habilitadas["PDC-RMID"] = 2
                        if self.model.mediumflag == True:
                            self.model.cajas_habilitadas["PDC-RMID"] = 2
                        if self.model.largeflag == True:
                            self.model.cajas_habilitadas["PDC-R"] = 2
                        current_boxx = "PDCR"
                    else:
                        self.model.cajas_habilitadas[i] = 2

                    serie = ""
                    if i == "MFB-P2":
                        serie = self.model.mfbp2_serie
                    if "PDC-R" in i:
                        serie = self.model.pdcr_serie

                    #copia de la caja actual, para utilizar en publish
                    pub_i = i

                    #cajas que no requieren escanearse (se inician en blue)
                    if i == "BATTERY" or i == "BATTERY-2":
                        command = {f"lbl_box{current_boxx}" : {"text": f"{pub_i}", "color": "blue"}}

                    #cajas que requieren escanearse (se inician en purple) #ESTO ES PARA SABER QUE LA LLEVA EL ARNÉS, PERO AÚN NO ESTÁN HABILITADAS POR EL PLC (por eso se requieren estos publish a los gui)
                    else:

                        #si no se activan estas banderas es porque es R LARGE
                        if "PDC-R" in i:
                            if self.model.smallflag == True:
                                pub_i = "PDC-RSMALL"
                            if self.model.mediumflag == True:
                                pub_i = "PDC-RMID"
                            if self.model.largeflag == True:
                                pub_i = "PDC-R"

                        command = {f"lbl_box{current_boxx}" : {"text": f"{pub_i}\n{serie}", "color": "purple"}}

                    #SE HACE EL PUBLISH PARA LA GUI CORRESPONDIENTE A ESA CAJA
                    if i in self.model.boxPos1:
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    if i in self.model.boxPos2:
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)


                #se reacomoda el orden de las tuercas de la caja MFB-P2
                if "MFB-P2" in self.model.input_data["database"]["modularity"]:
                    modularity = self.model.input_data["database"]["modularity"]["MFB-P2"]
                    orden_tuercas = {"A29": "A29", "A22": "A22", "A27": "A27", "A23": "A23", "A26": "A26", "A21": "A21", "A24": "A24", "A28": "A28"}

                    for tuerca in orden_tuercas:
                        if tuerca in modularity:
                            modularity.pop(modularity.index(tuerca))
                            modularity.append(orden_tuercas[tuerca])


                print("cajas habilitadas CICLO: ",self.model.cajas_habilitadas)

                ###############################
                print("*************************************COLECCIÓN TORQUE:*************************************")
                pprint.pprint(self.model.input_data["database"]["modularity"])
                print("*******************************************************************************************")

                #print("\t\tCOLECCIÓN FUSIBLES PDC-R:\n", self.model.input_data["database"]["fuses"]) #Descomentar para ver en consola las cavidades que llevan fusibles para la PDC-R
                #Se recorre la variable del modelo que indica qué cavidades pertenecen a c/candado; "s" = nombre del candado (Ejemplo: S1,S2...S10)
                for s in self.model.configCandados:
                    #Después se recorren las cavidades (cav) de cada candado del modelo (self.model.configCandados[s])
                    for cav in self.model.configCandados[s]:
                        #Si alguna cavidad se encuentra dentro de la colección de cavidades de la PDC-R que se está torqueando, se procede a agregar el candado correspondiente a la colección de candados...
                        if cav in self.model.input_data["database"]["fuses"]:
                            #Si el candado aún no existe en la colección de candados, se agrega (esta condición es para evitar que existan candados repetidos)
                            if not(s in self.model.input_data["database"]["candados"]):
                                self.model.input_data["database"]["candados"].append(s)
                print("\t\tCOLECCIÓN CANDADOS PDC-R:\n", self.model.input_data["database"]["candados"])
                self.model.input_data["database"]["pedido"] = pedido
                self.model.datetime = datetime.now()

                if self.model.local_data["qr_rework"]:
                    self.model.local_data["qr_rework"] = False

                if flag_296 == True or flag_294 == True:
                    print("dbEvent: ",dbEvent)
                    event = dbEvent.upper()
                    evento = event.replace('_',' ')
                    #Se agrega el nombre del evento a una variable en el modelo, el cual servirá para definir el oracle de las tuercas en caso de pertenecer a PRO1
                    self.model.evento = evento
                    command = {
                        "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                        "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                        "statusBar" : pedido["PEDIDO"] +" "+self.model.qr_codes["HM"]+" "+evento,
                        "cycle_started": True
                    }
                else:
                    command = {
                        "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                        "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                        "statusBar" : pedido["PEDIDO"],
                        "cycle_started": True
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                command = {
                    "position" : {"text": "POSICIÓN 1", "color": "black"},
                    "lbl_boxTITLE" : {"text": "||Cajas a utilizar||", "color": "black"},
                    "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                    "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                    "statusBar" : pedido["PEDIDO"] +" "+self.model.qr_codes["HM"]+" "+evento,
                    "cycle_started": True
                }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                command = {
                    "position" : {"text": "POSICIÓN 2", "color": "black"},
                    "lbl_boxTITLE" : {"text": "||Cajas a utilizar||", "color": "black"}
                }
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.1, self.torqueClamp).start()
                Timer(0.05, self.model.log, args = ("RUNNING",)).start() 
                self.ok.emit()
                
            else:
                self.model.retrabajo=True
                print("retrabajo true en checkqr")
                self.rework.emit()
                return
            ####### Original

        except Exception as ex:
            print("Datamatrix request exception: ", ex) 
            if flag_variantes == False:
                print("La Modularidad no contiene módulos que especifiquen su variante en la PDC-R")
                temp = "La Modularidad no contiene módulos que especifiquen su variante en la PDC-R"
            else:
                temp = f"Database Exception: {ex.args}"
            command = {
                "lbl_result" : {"text": temp, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.model.input_data["database"]["modularity"].clear()
            self.model.torque_data["tool1"]["queue"].clear()
            self.model.torque_data["tool2"]["queue"].clear()
            self.model.torque_data["tool3"]["queue"].clear()
            self.nok.emit()

    def leer_configuracion(self):
        """
        lee un txt en C:BIN/ llamado configuracion, cada renglon debe tener la forma: 
        condicion:True
        almacena todos los parametros en el diccionario parametros en el modelo

        """
        ruta_configuracion=join(self.model.ruta_principal, "configuracion.txt")
        if exists(ruta_configuracion):
            with open(ruta_configuracion) as configuracion:
                for linea in configuracion:
                    if not linea.startswith("#"):
                        linea.strip()
                        comando_configuracion=linea.split(":")
                        self.model.parametros[comando_configuracion[0]]=comando_configuracion[1]
        print("self.model.parametros",self.model.parametros)
                

    def torqueClamp (self):
        command = {}
        master_qr_boxes = json.loads(self.model.input_data["database"]["pedido"]["QR_BOXES"])
        print(f"\t\tQR_BOXES:\n{master_qr_boxes}\n")
        for i in self.model.torque_cycles:
            command[i] = False
            if i in self.model.input_data["database"]["modularity"]:
                if i in master_qr_boxes:
                    if not(master_qr_boxes[i][1]):
                        command[i] = True
                else:
                    command[i] = True
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def caja_FET_consulta(self,hm):
        famx2response=None
        try:
            print("||||||||||||Consulta de HM a FAMX2...")
            endpoint = "http://{}/seghm/get/SEGHM_BOX/HM/=/{}/_/_/_".format(self.model.server,hm)
            famx2response = requests.get(endpoint).json()
            #No existen coincidencias del HM en FAMX2
            if "items" in famx2response:
                print("ITEMS por que no se encontró HM en SEGHM_BOX, tabla de cajas registradas de FET")
                famx2response=None
                self.model.qr_error="Hm no encontrado"
                
            #Si existe el HM en FAMX2
            else:
                print("FAMX2 ",famx2response)
                return famx2response

                
        except Exception as ex:
            print ("caja_match_FET_consulta exception ", ex)
            famx2response=None
        return famx2response


class QrRework (QState):
    ok = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

        self.model.transitions.key.connect(self.rework)
        self.model.transitions.code.connect(self.noRework)

    def onEntry(self, QEvent):
        command = {
            "lbl_result" : {"text": "Datamatrix procesado anteriormente", "color": "red"},
            "lbl_steps" : {"text": "Escanea otro código o gira la llave para continuar", "color": "black"},
            "show":{"scanner": True}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("show")
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = True
        print("model qr_keyboard = True")
        
    def onExit(self, QEvent):
        self.model.en_ciclo=False
        command = {
            "show":{"scanner": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = False
        print("model qr_keyboard = False")

    def rework (self):
        self.model.retrabajo=True
        self.model.local_data["qr_rework"] = True
        Timer(0.05, self.ok.emit).start()

    def noRework(self):
        self.model.retrabajo=False
        Timer(0.05, self.ok.emit).start()


class Finish (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        minutos=0
        segundos=0
        color="black"
        try:
            query="SELECT INICIO, FIN FROM et_mbi_2.historial WHERE RESULTADO = 1 order by ID desc LIMIT 1;"
            endpoint = "http://{}/query/get/{}".format(self.model.server, query)
            print("Endpoint: ",endpoint)
        
            resp_ultimo_arnés = requests.get(endpoint).json()
            
            in_formato_ciclo=datetime.strptime(resp_ultimo_arnés["INICIO"][0], '%a, %d %b %Y %H:%M:%S GMT')
            out_formato_ciclo=datetime.strptime(resp_ultimo_arnés["FIN"][0], '%a, %d %b %Y %H:%M:%S GMT')

            # Calcula la diferencia entre la fecha de fin y la fecha de inicio
            diferencia = out_formato_ciclo - in_formato_ciclo
            
            # Extrae los minutos y segundos de la diferencia
            minutos, segundos = divmod(diferencia.total_seconds(), 60)
            if minutos >10 :
                color="red"
            else:
                color="green"
            # Imprime el resultado
            print(f"ciclo: {int(minutos)} min {int(segundos)} segundos")
            print(in_formato_ciclo)

        except Exception as ex:
            print("Excepción al momento de extraer el ultimo arnes", ex)
        self.model.en_ciclo=False
        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False
        #regresa variable que permite escanear otra caja
        self.model.pdcr_iniciada=False
        command = {
            "DISABLE_PDC-R":False,
            "DISABLE_PDC-RMID":False,
            "DISABLE_MFB-S":False,
            "DISABLE_MFB-P1":False,
            "DISABLE_MFB-P2":False,
            "DISABLE_PDC-P":False,
            "DISABLE_PDC-D":False,
            "DISABLE_MFB-E":False,
            "DISABLE_BATTERY":False,
            "DISABLE_BATTERY-2":False
            }
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        # Fragmento de código para guardar solamente los RE-intentos
        print("||||||| Intentos en Modelo: ",self.model.tries)
        for i in self.model.tries:
            for j in self.model.tries[i]:
                self.model.tries[i][j] -= 1
                if self.model.tries[i][j] <= 0:
                    self.model.tries[i][j] = 0
        print("||||||| RE-intentos en Modelo FINAL: ",self.model.tries)
        self.model.pdcr_iniciada=False
        self.model.qr_box_actual=""
        self.model.caja_repetida_hm_asociado=""
        self.model.qr_validado=[]
        self.model.key_calidad_caja_repetida=False
        self.model.caja_por_validar=""
        #para funcionamiento normal de llave
        self.model.reintento_torque = False

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""

        lblbox_clean = {
            "lbl_boxTITLE" : {"text": f"último ciclo: \n{int(minutos)} min {int(segundos)} segundos" , "color": color},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(lblbox_clean),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(lblbox_clean),hostname='127.0.0.1', qos = 2)

        flag_1 = False
        historial = {
            "HM": self.model.qr_codes["HM"],
            "RESULTADO": "1",
            "VISION": {},
            "ALTURA":{},
            "INTENTOS_VA": {},
            "TORQUE": self.model.result,
            "ANGULO": self.model.resultAngle,
            "INTENTOS_T": self.model.tries,
            "SERIALES": self.model.qr_codes,
            "INICIO": self.model.datetime.isoformat(),
            "FIN": strftime("%Y/%m/%d %H:%M:%S"),
            "USUARIO": self.model.local_data["user"]["type"] + ": " + self.model.local_data["user"]["name"],
            "NOTAS": {"TORQUE": ["OK"]},
            "SCRAP": self.model.local_data["nuts_scrap"]
            }
        print("|||||||||||| HISTORIAL INICIO: ",historial["INICIO"])
        print("|||||||||||| HISTORIAL FIN: ",historial["FIN"])

        if self.model.config_data["untwist"]:
            historial["RESULTADO"] = "0"
            historial["NOTAS"]["TORQUE"].insert(0,"DESAPRIETE")
            self.model.config_data["untwist"] = False
        else:
            historial["NOTAS"]["TORQUE"].insert(0,"APRIETE")
            flag_1 = True
        if self.model.config_data["flexible_mode"]:
            historial["NOTAS"]["TORQUE"].insert(-1, "FLEXIBLE")
            self.model.config_data["flexible_mode"] = False
            #flag_1 = False
        endpoint = "http://{}/api/post/historial".format(self.model.server)
        resp = requests.post(endpoint, data=json.dumps(historial))
        resp = resp.json()

        #### Trazabilidad FAMX2 Update de Información
        if self.model.config_data["trazabilidad"] and self.model.config_data["untwist"]==False and self.model.config_data["flexible_mode"]==False:
            if flag_1:
                try:
                    print("||Realizando el Update de SALIDA a Trazabilidad en FAMX2")
                    print("ID a la que se realizará el Update para Trazabilidad",self.model.id_HM)
                    salTrazabilidad = {
                        "SALTORQUE": historial["FIN"],
                        "UBICACION": "SALIDA_DE_TORQUE",
                        "NAMETORQUE": self.model.serial
                        }
                    endpointUpdate = "http://{}/seghm/update/seghm/{}".format(self.model.server,self.model.id_HM)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    print("respTrazabilidad del update: ",respTrazabilidad)
                    
                    sleep(0.1)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    print("respTrazabilidad del update: ",respTrazabilidad)

                    sleep(0.1)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    print("respTrazabilidad del update: ",respTrazabilidad)

                    sleep(0.1)
                    print("||Realizando el POST de valores en FAMX2")
                    historial["INICIO"] = self.model.datetime.strftime("%Y/%m/%d %H:%M:%S") #Se modifica el formato de la fecha de Inicio, para que coincida con el esperado por el servidor
                    endpointPost = "http://{}/seghm/post/seghm_valores".format(self.model.server)
                    
                    respPost = requests.post(endpointPost, data=json.dumps(historial))
                    respPost = respPost.json()
                    print("respuesta del POST a FAMX2 Valores: ",respPost)

                    sleep(0.1)
                    if "exception" in respPost:
                        respPost = requests.post(endpointPost, data=json.dumps(historial))
                        respPost = respPost.json()
                        print("respuesta del POST a FAMX2 Valores: ",respPost)

                        sleep(0.1)
                        if "exception" in respPost:
                            respPost = requests.post(endpointPost, data=json.dumps(historial))
                            respPost = respPost.json()
                            print("respuesta del POST a FAMX2 Valores: ",respPost)




                    #endpoint = "http://{}/seghm/get/seghm/NAMEPREENSAMBLE/=/INTERIOR/HM/=/{}".format(self.model.server,self.model.qr_codes["HM"])
                    #famx2response = requests.get(endpoint).json()
                    #print("Respuesta de FAMX2: \n",famx2response)



                except Exception as ex:
                    print("Excepción al momento de guardar datos en FAMX2", ex)
        #### Trazabilidad FAMX2 Update de Información

        if "items" in resp:
            if resp["items"] == 1:
                label = {
                    "DATE":  "FECHA"+ self.model.datetime.strftime("%Y/%m/%d %H:%M:%S"),
                    "REF":   "REF" + self.model.qr_codes["REF"],
                    "QR":    self.model.input_data["database"]["pedido"]["PEDIDO"],
                    "TITLE": "Estación de torques en arnes Interior" ,
                    "HM":    "HM" + self.model.qr_codes["HM"]
                }
                for i in self.model.result:
                    temp = []
                    for j in self.model.result[i]:
                        temp.append(str(self.model.result[i][j]))
                    label[i] = i + ": " + str(temp)

                #publish.single(self.model.pub_topics["printer"], json.dumps(label), hostname='127.0.0.1', qos = 2)

                if "HM000000011936" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True
                        
                if "HM000000011925" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True

                if "HM000000011920" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True


                if self.model.config_data["trazabilidad"] == True:
                    command = {
                        "lbl_info3" : {"text": "Trazabilidad\nActivada", "color": "green"}
                    }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                self.finalMessage()
                Timer(4, self.ok.emit).start()
                #QTimer.singleShot(50, self.finalMessage)
                #QTimer.singleShot(4050,self.ok.emit)
                
            else:
                command = {
                    "lbl_result" : {"text": "Error al guardar los datos", "color": "red"},
                    "lbl_steps" : {"text": "Gire la llave de reset", "color": "black"}
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        else:
            command = {
                "lbl_result" : {"text": "Error de conexión con la base de datos", "color": "red"},
                "lbl_steps" : {"text": "Gire la llave de reset", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def finalMessage(self):
        self.model.id_HM = None
        command = {
            "lbl_result" : {"text": "C I C L O\tT E R M I N A D O", "color": "green"},
            "lbl_steps" : {"text": "RETIRA LAS CAJAS", "color": "blue"},
            "img_center" : "AMTC.png"
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)




class Reset (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):

        self.model.en_ciclo=False
        self.model.retrabajo=False
        if "HM000000011936" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True
                        
        if "HM000000011925" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True

        if "HM000000011920" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True


        if self.model.config_data["trazabilidad"] == True:
            command = {
                "lbl_info3" : {"text": "Trazabilidad\nActivada", "color": "green"}
            }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False
        #regresa variable que permite escanear otra caja
        self.model.pdcr_iniciada=False
        self.model.qr_box_actual=""
        self.model.caja_repetida_hm_asociado=""
        self.model.qr_validado=[]
        self.model.key_calidad_caja_repetida=False
        self.model.caja_por_validar=""
        
        command = {
            "show":{"login": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        # Fragmento de código para guardar solamente los RE-intentos
        print("||||||| Intentos en Modelo: ",self.model.tries)
        for i in self.model.tries:
            for j in self.model.tries[i]:
                self.model.tries[i][j] -= 1
                if self.model.tries[i][j] <= 0:
                    self.model.tries[i][j] = 0
        print("||||||| RE-intentos en Modelo FINAL: ",self.model.tries)
        self.model.id_HM = None
        #para funcionamiento normal de llave
        self.model.reintento_torque = False

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False, f"DISABLE_{i}":False, i:False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""

        command = {
            "lbl_result" : {"text": "Se giró la llave de reset", "color": "green"},
            "lbl_steps" : {"text": "Reiniciando", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        command = {}
        for i in self.model.torque_cycles:
             command[i] = False
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        if self.model.datetime != None:
            historial = {
                "HM": self.model.qr_codes["HM"],
                "RESULTADO": "0",
                "VISION": {},
                "ALTURA":{},
                "INTENTOS_VA": {},
                "TORQUE": self.model.result,
                "ANGULO": self.model.resultAngle,
                "INTENTOS_T": self.model.tries,
                "SERIALES": self.model.qr_codes,
                "INICIO": self.model.datetime.isoformat(),
                "FIN": strftime("%Y/%m/%d %H:%M:%S"),
                "USUARIO": self.model.local_data["user"]["type"] + ": " + self.model.local_data["user"]["name"],
                "NOTAS": {"TORQUE": ["RESET"]},
                "SCRAP": self.model.local_data["nuts_scrap"]
                }
            if self.model.config_data["untwist"]:
                historial["NOTAS"]["TORQUE"].insert(0, "DESAPRIETE")
                self.model.config_data["untwist"] = False
            else:
                historial["NOTAS"]["TORQUE"].insert(0, "APRIETE")
            if self.model.config_data["flexible_mode"]:
                historial["NOTAS"]["TORQUE"].insert(-1, "FLEXIBLE")
                self.model.config_data["flexible_mode"] = False
            endpoint = "http://{}/api/post/historial".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(historial))
            resp = resp.json()
            
            if "items" in resp:
                if resp["items"] == 1:
                    pass
                else:
                    command = {
                        "lbl_result" : {"text": "Error de conexión", "color": "red"},
                        "lbl_steps" : {"text": "Datos no guardados", "color": "black"}
                        }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        QTimer.singleShot(500,self.ok.emit)
