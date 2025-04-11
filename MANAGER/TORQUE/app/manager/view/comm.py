
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from paho.mqtt.client import Client
from threading import Timer
from time import sleep              # Para usar la función sleep(segundos)
from copy import copy
import time
import json
from datetime import datetime
import requests

class MqttClient (QObject):
    
    conn_ok         =   pyqtSignal()
    conn_nok        =   pyqtSignal()
    clamp           =   pyqtSignal()
    emergency       =   pyqtSignal()
    key             =   pyqtSignal()
    #llave para el proceso, no para finalizar
    key_process     =   pyqtSignal()
    #señales para emitir que estás en la zona correcta determinada por cada herramienta
    zone_tool1      =   pyqtSignal()
    zone_tool2      =   pyqtSignal()
    zone_tool3      =   pyqtSignal()
    #Se emite esta señal correspondiente al encoder 4 (Altura para palpador)
    zone_tool4      =   pyqtSignal()
    retry_btn       =   pyqtSignal()
    #señales para emitir resultados de torque de cada herramienta
    torque1         =   pyqtSignal()
    torque2         =   pyqtSignal()
    torque3         =   pyqtSignal()

    torque1_reversa =   pyqtSignal()
    torque2_reversa =   pyqtSignal()
    torque3_reversa =   pyqtSignal()

    #señal para indicar que el palpador ha sido presionado por un candado gg
    pin             =   pyqtSignal()

    login           =   pyqtSignal()
    logout          =   pyqtSignal()
    config          =   pyqtSignal()
    config_ok       =   pyqtSignal()
    ID              =   pyqtSignal()
    code            =   pyqtSignal()
    nok_code        =   pyqtSignal()
    visible         =   pyqtSignal()
    #emitir una señal que contenga el qr (  self.qr_box.emit(payload["qr_box"])  )
    qr_box          =   pyqtSignal(str)
    raffi_enabled   =   pyqtSignal(str)
    raffi_disabled  =   pyqtSignal(str)

    raffi_on   =   pyqtSignal()
    raffi_off  =   pyqtSignal()

    keyboard_key = ""
    keyboard_value = False
    mostrar_gdi = True
    
    nido = ["PDC-P","PDC-D","MFB-P1","MFB-P2","PDC-R","PDC-RMID","BATTERY","BATTERY-2","BATTERY-3","MFB-S","MFB-E"]
    nido_pub = ""
    color_nido = "blue"


    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.client = Client()
        QTimer.singleShot(5000, self.setup)
        self.Battery3clamp = False #Variable para enviar True o False a BATT3 en la GDI con F12
        self.last_f12_time = 0  # Variable para registrar el último tiempo de presionado de F12

    def setup(self):
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(host = "127.0.0.1", port = 1883, keepalive = 60)
            self.client.loop_start()
        except Exception as ex:
            print("Manager MQTT client connection fail. Exception: ", ex)

    def stop (self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def reset (self):
        self.stop()
        self.setup()

    def raffi_check(self, current_box, expected_key):

        if self.keyboard_key == expected_key:

            print("raffi check: ",current_box)
            print("Bloqueo de Raffis Valor: ",self.model.active_lock[current_box])

            if self.model.active_lock[current_box] == False:

                #si las cajas están habilitadas por el ciclo:
                if self.model.cajas_habilitadas[current_box] == 1 or self.model.cajas_habilitadas[current_box] == 2:

                    if self.keyboard_value == self.model.bool_state:

                        # solo se puede modificar cuando  ya ha pasado un segundo despuès de desactivar el raffi
                        if self.model.timer_raffi == False:
                            self.model.raffi[current_box] = 1
                            print("Valores de los raffi desde raffi check",self.model.raffi)
                            print("self.model.raffi[",current_box,"]: ", self.model.raffi[current_box])

                            #guardar F correspondiente al raffi actual activado, por ejemplo para la caja MFB-P2, es "keyboard_F8", por lo tanto se guarda "F8"
                            self.model.keyboard_raffi_pressed = expected_key
                            self.model.keyboard_raffi_pressed =  self.model.keyboard_raffi_pressed.replace("keyboard_","")
                            #se guarda el valor de la caja actual correspondiente a ese raffi activado
                            self.model.current_raffi_key = current_box
                            #señal para emitir con string que contenga la caja actual correspondiente a ese raffi activado
                            self.raffi_enabled.emit(current_box)
                            #señal para indicar que se activó un raffi
                            self.raffi_on.emit()

                            self.model.timer_raffi = True
                            Timer(1.5, self.raffi_timer).start()
                        else:
                            print("espere un segundo para activar el raffi")
                            self.model.bool_state = not (self.model.bool_state)

                    else:

                        # solo se puede modificar cuando  ya ha pasado un segundo despuès de activar el raffi
                        if self.model.timer_raffi == False:

                            self.model.raffi[current_box] = 0
                            print("Valores de los raffi desde raffi check",self.model.raffi)
                            print("self.model.raffi[",current_box,"]: ", self.model.raffi[current_box])

                            self.model.keyboard_raffi_pressed = expected_key
                            self.model.keyboard_raffi_pressed =  self.model.keyboard_raffi_pressed.replace("keyboard_","")
                            self.model.current_raffi_key = current_box
                            self.raffi_disabled.emit(current_box)
                            self.raffi_off.emit()

                            self.model.timer_raffi = True
                            Timer(1.5, self.raffi_timer).start()
                        else:
                            print("espere un segundo para desactivar el raffi")
                            self.model.bool_state = not (self.model.bool_state)
        
    def raffi_timer(self):
        #para convertir variable a False después de que el tiempo haya terminado
        self.model.timer_raffi = False

    def mensajes_clamp (self, current_box, payload):

        #convertir diccionario payload a string y guardarlo
        payload_str = json.dumps(payload)       

        if not("DISABLE_" in payload_str):

            condicion0 = False
            condicion1 = False
            condicion2 = False
            condicion3 = False

            if not("PDC-R" in payload_str):
                condicion0 = True
            elif self.model.varianteDominante == "PDC-RMID" and "PDC-RMID" in payload_str:
                condicion1 = True
            elif self.model.varianteDominante == "PDC-RS" and "PDC-RMID" in payload_str:
                condicion2 = True
            elif self.model.varianteDominante == "PDC-R" and not("PDC-RMID" in payload_str):
                condicion3 = True

            if condicion0 or condicion1 or condicion2 or condicion3:

                #busca el nombre del nido en el string del payload
                if current_box in payload_str: 

                    #variable para poner la serie de la caja en las cajas que sea necesario
                    serie = ""

                    #se asignan serie a las cajas que lo contengan
                    if "MFB-P2" in current_box:
                        serie = self.model.mfbp2_serie
                    if "PDC-R" in current_box:
                        serie = self.model.pdcr_serie

                    #0, no se solicitan en ciclo
                    #1, ya se escaneó
                    #2, aún requiere escanearse
                    #3, cajas terminadas en el ciclo

                    #"lbl_boxTITLE" : {"text": "", "color": "black"},
                    #"lbl_boxPDCR" : {"text": "", "color": "black"},
                    #"lbl_boxPDCP" : {"text": "", "color": "black"},
                    #"lbl_boxPDCD" : {"text": "", "color": "black"},
                    #"lbl_boxMFBP1" : {"text": "", "color": "black"},
                    #"lbl_boxMFBP2" : {"text": "", "color": "black"},
                    #"lbl_boxMFBE" : {"text": "", "color": "black"},
                    #"lbl_boxMFBS" : {"text": "", "color": "black"},
                    #"lbl_boxBATTERY" : {"text": "", "color": "black"},
                    #"lbl_boxBATTERY2" : {"text": "", "color": "black"},

                    #se hace el replace para current_box_pub, pero current_box sigue valiendo lo mismo
                    current_box_pub = current_box.replace("-","")
                    if current_box == "PDC-RMID":
                        current_box_pub = "PDCR"

                    #cajas que no están en ciclo
                    if self.model.cajas_habilitadas[current_box] == 0 or self.model.cajas_habilitadas[current_box] == 3:

                        command = {f"lbl_box{current_box_pub}" : {"text": "", "color": "blue"}}

                        if current_box in self.model.boxPos1:
                            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        if current_box in self.model.boxPos2:
                            self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

                    #se busca que la caja esté habilitada por el ciclo
                    elif self.model.cajas_habilitadas[current_box] == 1 or self.model.cajas_habilitadas[current_box] == 2:

                        raffi_box = "raffi_" + current_box
                        clamp_box = "clamp_" + current_box


                        #RAFFI DESHABILITADO
                        #los raffi solo se pueden activar cuando la caja ya fue clampeada
                        if raffi_box in payload:

                            #entonces al detectar un raffi_"" en False, significa que se deshabilita el raffi y la caja vuelve a su estado de clampeada
                            if payload[raffi_box] == False:
                                self.nido_pub = f"{current_box}\n{serie}"
                                self.color_nido = "green"

                        #HABILITAR/DESHABILITAR CAJA
                        if current_box in payload:

                            print("self.model.cajas_habilitadas[current_box]: ", self.model.cajas_habilitadas[current_box])

                            #al habilitar una caja, se muestra el mensaje de la caja habilitada
                            if payload[current_box] == True:
                                self.nido_pub = f"{current_box}\n{serie}"
                                self.color_nido = "blue"

                            #al deshabilitar una caja, se borra el label
                            if payload[current_box] == False:
                                self.nido_pub = ""
                                self.color_nido = "blue"

                                #si la caja está deshabilitada pero aún no se ha clampeado (se requiere volver a escanear porque el tiempo para escanearla se terminó)
                                if self.model.cajas_habilitadas[current_box] == 2:
                                    self.nido_pub = f"{current_box}\n{serie}"
                                    self.color_nido = "blue"


                        # CAJA CLAMPEADA
                        if clamp_box in payload:
                            if payload[clamp_box] == True:
                                self.nido_pub = f"{current_box}\n{serie}"
                                self.color_nido = "green"

                            #al deshabilitar una caja, se borra el label
                            if payload[clamp_box] == False:
                                self.nido_pub = ""
                                self.color_nido = "blue"

                                #si la caja está deshabilitada pero aún no se ha clampeado (se requiere volver a escanear porque el tiempo para escanearla se terminó)
                                if self.model.cajas_habilitadas[current_box] == 2:
                                    self.nido_pub = f"{current_box}\n{serie}"
                                    self.color_nido = "blue"
                        
                        #RAFFI HABILITADO
                        if raffi_box in payload:
                            if payload[raffi_box] == True:
                                self.nido_pub = f"{current_box}\n{serie}"
                                self.color_nido = "orange"
            

                        #cuando es SMALL se habilita el nido en MID, entonces si la bandera es true, cambiar mensaje
                        if self.model.smallflag == True:
                            self.nido_pub = self.nido_pub.replace("PDC-RMID","PDC-RSMALL")



                        #como la función mensajes clamp se hace cada que llega un mensaje del PLC,
                        #si este mensaje contiene la palabra encoder (así como la current_box en su mensaje)
                        if "encoder" in payload_str:
                            pass
                        #de lo contrario es un mensaje de el funcionamiento de las cajas , y hace un publish en la correspondiente gui
                        else:
                            command = {f"lbl_box{current_box_pub}" : {"text": f"{self.nido_pub}", "color": f"{self.color_nido}"}}
                    
                            for i in self.model.boxPos1:
                                if current_box == i:
                                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                            for i in self.model.boxPos2:
                                if current_box == i:
                                    self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

    def on_connect(self, client, userdata, flags, rc):
        try:
            connections = {
               "correct": True,
               "fails": "" 
               }
            for topic in self.model.sub_topics:
                client.subscribe(self.model.sub_topics[topic])
                if rc == 0:
                    print(f"Manager MQTT client connected to {topic} with code [{rc}]")
                else:
                    connections["correct"] = False
                    connection["fails"] += topic + "\n"
                    print("Manager MQTT client connection to " + topic + " fail, code [{}]".format(rc))
            if connections["correct"] == True:
               self.conn_ok.emit()
            else:
                print("Manager MQTT client connections fail:\n" + connection["fails"])
                self.conn_nok.emit()
        except Exception as ex:
            print("Manager MQTT client connection fail. Exception: ", ex)
            self.conn_nok.emit()

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload)
            print("payload",payload)
            string_payload = str(payload)
            ignorar = False
            if "encoder" in string_payload:
                ignorar = True
            if "bin" in string_payload:
                ignorar = True
            if "output" in string_payload:
                ignorar = True
            if ignorar == False:
                print ("   " + message.topic + " ", payload) 

            if message.topic == self.model.sub_topics["plc"]:
                if "emergency" in payload:
                    self.model.input_data["plc"]["emergency"] = payload["emergency"]
                    Timer(0.05, self.model.log, args = ("STOP",)).start() 
                    if payload["emergency"] == False:
                        self.emergency.emit()
                        
                        command = {
                            "lbl_boxTITLE" : {"text": "Paro de Emergencia \n ACTIVADO", "color": "red"},
                            "popOut":"Paro de emergencia activado",
                            "Paro_Emergencia":True
                            }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                    else:
                        command = {
                            "lbl_boxTITLE" : {"text": "", "color": "red"},
                            "Paro_Emergencia":False
                            }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                        #QTimer.singleShot(1000, self.closePopout)
                        self.closePopout()

            if message.topic == self.model.sub_topics["gui"]:
                if "ID" in payload:
                    self.model.input_data["gui"]["ID"] = payload["ID"]
                    self.ID.emit()
                
            if self.model.input_data["plc"]["emergency"] == False or self.model.alarma_emergencia==True:
                return

            if message.topic == self.model.sub_topics["keyboard"]:
                #ejemplo de mensaje: { "keyboard_E" : true }
                payload_str = json.dumps(payload)       # convertir diccionario payload a string y guardarlo
                payload_str = payload_str.replace("{","")
                payload_str = payload_str.replace("}","")
                payload_str = payload_str.replace('"',"")
                payload_str = payload_str.replace("true","True")
                payload_str = payload_str.replace("false","False")
                payload_str = payload_str.replace(" ","")
                separate_msj = payload_str.rsplit(":")
                self.keyboard_key = separate_msj[0]
                #eval() evalua una cadena de caracteres y decide si es True o False si cumple con las entradas esperadas convirtiendolo a booleano
                self.keyboard_value = eval(separate_msj[1])

                #if self.model.qr_scan_cont == 0:
                #    if self.model.qr_keyboard:
                #        self.model.qr_scan_cont = 1
                #        print("cont = 1")

                #if self.model.qr_scan_cont >= 1:
                #    self.model.qr_scan_cont = self.model.qr_scan_cont + 1
                #    print("cont = ",self.model.qr_scan_cont)

                #if self.model.qr_scan_cont >= 6:
                #    self.model.qr_scan_cont = 0
                #    self.model.qr_keyboard = False
                #    print("nok code emit, cont = 0")
                #    self.nok_code.emit()

                #print("key: ",self.keyboard_key)
                #print("value: ",self.keyboard_value)

                # PARA HABILITAR EL PALPADOR CON LA TECLA ESPACIO
                #if self.keyboard_key == "keyboard_space":
                #    print("se presionó el palpador de teclado")
                #    self.model.pin_pressed = True
                #    self.pin.emit()

                if self.model.config_data["shift_ctrl_function"] == True:
                    if self.keyboard_key == "keyboard_ctrl" and self.model.en_ciclo==True:
                        command = {
                                "lineEdit" : True,
                                "lineEdit_focus" : True
                                }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    if self.keyboard_key == "keyboard_shift" and self.model.en_ciclo==True:

                        command = {
                               "lineEditKey" : True,
                               "lineEditKey_focus":True
                                }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                if self.keyboard_key == "keyboard_esc":
                    command = {"popOut":"close"}
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    print("key no emit")

                if self.keyboard_key == "keyboard_F12":
                    current_time = time.time()

                    # Si han pasado menos de 2 segundos desde la última vez que se presionó, se ignora
                    if current_time - self.last_f12_time < 2:
                        print("Esperando antes de volver a permitir F12...")
                    else:
                        self.last_f12_time = current_time  # Actualiza el tiempo de la última pulsación

                        if "BATTERY" in self.model.input_data["database"]["modularity"]:
                            print("BATTERY aún está en modularity, no se puede activar BATTERY-3")

                        else:
                            print("Tecla F12 presionada, enviando señal de clamp de BATTERY-3")
                            if "BATTERY-3" in self.model.input_data["database"]["modularity"]:
                                # Alternar el estado
                                self.Battery3clamp = not self.Battery3clamp

                                if self.Battery3clamp:
                                    print("enviando BATT3 = True a GDI, también se requiere BATTERY-3=True y BATTERY=False")
                                    self.client.publish(self.model.pub_topics["plc"], json.dumps({"BATT3": True}), qos=2)
                                    command = {
                                        "lbl_result" : {"text": "BATTERY3 Habilitada", "color": "green"},
                                        "lbl_steps" : {"text": "Mover Herramienta para Continuar", "color": "black"},
                                        }
                                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                else:
                                    print("enviando BATT3 = False a GDI")
                                    self.client.publish(self.model.pub_topics["plc"], json.dumps({"BATT3": False}), qos=2)
                                    command = {
                                        "lbl_result" : {"text": "BATTERY3 Deshabilitada", "color": "red"},
                                        "lbl_steps" : {"text": "Mover Herramienta para continuar", "color": "black"},
                                        }
                                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                            else:
                                print("BATTERY-3 no encontrada en modularity")

                if self.model.llave == True:

                    if self.keyboard_key == "keyboard_esc":
                        command = {"message_pop":{"Visible":False}}
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        print("key no emit")
                        self.model.llave = False
                    elif self.keyboard_key == "click_derecho":
                        command = {"message_pop":{"Visible":False}}
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        self.key.emit()
                        print("key emit")
                        self.model.llave = False
                    #else:
                    #    command = {"popOut":"Mensaje no recibido, gire la llave nuevamente"}
                    #    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    #    print("AQUI HAY REMOVER EL MENSAJE PARA EVITAR QUE ESTE TODO EL TIEMPO")
                        
                self.raffi_check("BATTERY-3", "keyboard_F10")
                self.raffi_check("PDC-R", "keyboard_F9")
                self.raffi_check("PDC-RMID", "keyboard_F9")
                self.raffi_check("MFB-P2", "keyboard_F8")
                self.raffi_check("MFB-S", "keyboard_F7")
                self.raffi_check("MFB-P1", "keyboard_F6")
                self.raffi_check("BATTERY", "keyboard_F5")
                self.raffi_check("BATTERY-2", "keyboard_F4")
                self.raffi_check("MFB-E", "keyboard_F3")
                self.raffi_check("PDC-D", "keyboard_F2")
                self.raffi_check("PDC-P", "keyboard_F1")


            if message.topic == self.model.sub_topics["plc"]:
                for i in list(payload):
                    if "clamp_" in i:
                        box = i[6:]
                        #si clamp_box = True...
                        if payload[i] == True:
                            if not(box in self.model.input_data["plc"]["clamps"]):
                                self.model.input_data["plc"]["clamps"].append(box)
                                self.clamp.emit() 
                        #si clamp_box = False...
                        else:
                            if box in self.model.input_data["plc"]["clamps"]:
                                self.model.input_data["plc"]["clamps"].pop(self.model.input_data["plc"]["clamps"].index(box))

                #if "key" in payload:
                #    if payload["key"] == True:
                #        # si la variable es True, quiere decir que hubo un mal torqueo y se requiere llave para habilitar la reversa
                #        if self.model.reintento_torque == True:
                #            #esta llave solo es para proceso
                #            print("key_process.emit()")
                #            self.key_process.emit()
                #        # si la variable es False, quiere decir que estás en otra parte del proceso y la llave reiniciará el ciclo
                #        elif self.model.reintento_torque == False:
                #            command = {"popOut":"¿Seguro que desea dar llave?\n Presione Esc. para salir, Espacio para continuar..."}
                #            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                #            self.model.llave = True
                if "MFBP2_candado_limit" in payload:
                    
                    command = {
                        "MFBP2_candado_limit" :payload["MFBP2_candado_limit"]
                        }
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    
                if "MFBP1_candado_limit" in payload:
                    
                    command = {
                        "MFBP1_candado_limit" :payload["MFBP1_candado_limit"]
                        }
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    
                if "MFBS_candado_limit" in payload:
                    
                    command = {
                        "MFBS_candado_limit" :payload["MFBS_candado_limit"]
                        }
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    
                if "MFBE_candado_limit" in payload:
                    
                    command = {
                        "MFBE_candado_limit" :payload["MFBE_candado_limit"]
                        }
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    
                if "button" in payload:
                    if payload["button"] == True:
                        print("Tapa cerrada para BATTERY-2... deshabilitando BATTERY-2")
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({"BATTERY-2_disable" : True}), qos = 2)

                if "PALPADOR" in payload:
                    if payload["PALPADOR"] == True:
                        print("se presionó el palpador")
                        self.model.pin_pressed = True
                        self.pin.emit()
                    else:
                        self.model.pin_pressed = False

                if "Confirmacion_bloqueoT1" in payload and self.model.herramienta_bloqueada["tool1"]==True:
                    if payload["Confirmacion_bloqueoT1"] == True:
                        self.model.herramienta_bloqueada["tool1"]=False
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}), qos = 2)

                if "Confirmacion_bloqueoT2" in payload and self.model.herramienta_bloqueada["tool2"]==True:
                    if payload["Confirmacion_bloqueoT2"] == True:
                        self.model.herramienta_bloqueada["tool2"]=False
                
                if "Confirmacion_bloqueoT3" in payload and self.model.herramienta_bloqueada["tool3"]==True:
                    if payload["Confirmacion_bloqueoT3"] == True:
                        self.model.herramienta_bloqueada["tool3"]=False

                if "Precencia_PDCP" in payload and self.model.validacion_conectores_pdcp==True:
                    if payload["Precencia_PDCP"] == True:
                        self.model.caja_puesta=True
                        command = {
                            "lbl_steps" : {"text": f"Caja PDC-P detectada ", "color": "green"},
                            "lbl_result" : {"text": "Coloque candados", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                    else:
                        self.model.caja_puesta=False
                        command = {
                            "lbl_steps" : {"text": f"Coloca la Caja PDCP para Validación", "color": "green"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                
                if "PDCP_Validacion" in payload and self.model.validacion_conectores_pdcp==True:
                    if payload["PDCP_Validacion"] == True:
                        self.model.validacion_conectores_pdcp=False
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-P": True}), qos = 2)
                        command = {
                            "lbl_steps" : {"text": f"Coloca la Caja PDC-P en su lugar", "color": "green"},
                            "img_center" : "logo.jpg",
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                        command = {
                            "lbl_steps" : {"text": f"", "color": "green"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        Timer(15, self.boxTimeout, args = (self.model.caja_por_validar, self.model.qr_box_actual)).start()
                
                if "Conector_S1" in payload and self.model.validacion_conectores_pdcp==True:
                    if payload["Conector_S1"] == True:
                        command = {
                            "lbl_steps" : {"text": f"Caja PDC-P detectada ", "color": "green"},
                            "lbl_result" : {"text": "Coloca el conector S1", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                    else:
                        self.model.conector_s1=False
                        command = {
                            "lbl_steps" : {"text": "", "color": "red"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                
                if "Conector_S2" in payload and self.model.validacion_conectores_pdcp==True and self.model.caja_puesta==True:
                    if payload["Conector_S2"] == True:
                        command = {
                            "lbl_steps" : {"text": f"Caja PDC-P detectada ", "color": "green"},
                            "lbl_result" : {"text": "Coloca el conector S2", "color": "red"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                    else:
                        self.model.conector_s2=False
                        command = {
                            "lbl_steps" : {"text": "", "color": "red"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

                if "candados_finish" in payload:
                    if payload["candados_finish"] == True:
                        self.model.estado_candados = False
                        #regresa variable que permite escanear otra caja
                        self.model.pdcr_iniciada=False
                    if payload["candados_finish"] == False:
                        self.model.estado_candados = True

                if "TOOL1_ALTURA" in payload:
                    #si no se encuentra activado el modo de revisión de candados (funcionamiento normal)
                    if self.model.estado_candados == False:

                        caja = self.model.torque_data["tool1"]["current_trq"][0]
                        tuerca = self.model.torque_data["tool1"]["current_trq"][1]
                            
                        print("caja: ",caja)
                        print("tuerca: ",tuerca)

                        if caja == "PDC-P" or caja == "PDC-D":
                            pass
                        else:
                            if payload["TOOL1_ALTURA"] == True:
                                self.model.altura_zone["tool1"] = True
                            else:
                                if self.model.config_data["deshabilitar_altura"]["tool1"] == False:
                                    self.model.altura_zone["tool1"] = False
                            print("emit zone de tool1 por altura")
                            self.zone_tool1.emit()

                    else:
                        print("No entró porque self.model.estado_candados: ",self.model.estado_candados)

                if "TOOL2_ALTURA" in payload:
                    #si no se encuentra activado el modo de revisión de candados (funcionamiento normal)
                    if self.model.estado_candados == False:

                        caja = self.model.torque_data["tool2"]["current_trq"][0]
                        tuerca = self.model.torque_data["tool2"]["current_trq"][1]
                            
                        print("caja: ",caja)
                        print("tuerca: ",tuerca)

                        if caja == "BATTERY" or caja == "BATTERY-2" or caja == "BATTERY-3":
                            pass
                        else:
                            if payload["TOOL2_ALTURA"] == True:
                                self.model.altura_zone["tool2"] = True
                            else:
                                if self.model.config_data["deshabilitar_altura"]["tool2"] == False:
                                    self.model.altura_zone["tool2"] = False
                            print("emit zone de tool2 por altura")
                            self.zone_tool2.emit()

                    else:
                        print("No entró porque self.model.estado_candados: ",self.model.estado_candados)

                if "MFBP2_candado_limit" in payload:
                    if payload["MFBP2_candado_limit"] == True:
                        self.model.candados_limit_inductivos["MFB-P2"] = True
                        if self.model.en_ciclo:
                            command = {
                            #"lbl_boxEmergente1" : {"text": "TAPA MFB-P2 detectada \n Continue con el Torque", "color": "green"},
                            "lbl_boxEmergente1" : {"text": "", "color": "green"},
                            }
                        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                    else:
                        self.model.candados_limit_inductivos["MFB-P2"] = False
                        if self.model.en_ciclo and (len(self.model.torque_data["tool1"]["queue"])>0 or len(self.model.torque_data["tool3"]["queue"])>0):
                            if 'MFB-P2' in str(self.model.torque_data["tool1"]["queue"]) or 'MFB-P2' in str(self.model.torque_data["tool3"]["queue"]):
                            
                                command = {
                                    "lbl_boxEmergente1" : {"text": "TAPA MFB-P2 detectada", "color": "green"},
                                    
                                    }
                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

                if "MFBP1_candado_limit" in payload:
                    print("self.model.torque_data[self.tool][queue] =",self.model.torque_data["tool2"]["queue"])
                    if payload["MFBP1_candado_limit"] == True :
                        self.model.candados_limit_inductivos["MFB-P1"] = True
                        self.model.tapaAbiertaMFBP1=False
                        if self.model.en_ciclo and  self.model.tapaAbiertaMFBS==False:
                            command = {
                            
                            "lbl_boxEmergente1" : {"text": ""},
                            }
                            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        elif self.model.en_ciclo and self.model.tapaAbiertaMFBS==True:
                            if 'MFB-S' in str(self.model.torque_data["tool2"]["queue"]) or 'MFB-S' in str(self.model.torque_data["tool3"]["queue"]):
                             
                                command = {
                                "lbl_boxEmergente1" : {"text": "TAPA MFBS detectada"},
                                
                                }
                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    
                    else:
                        self.model.candados_limit_inductivos["MFB-P1"] = False
                        
                        if self.model.en_ciclo and (len(self.model.torque_data["tool2"]["queue"])>0 or len(self.model.torque_data["tool3"]["queue"])>0):
                            if 'MFB-P1' in str(self.model.torque_data["tool2"]["queue"]) or 'MFB-P1' in str(self.model.torque_data["tool3"]["queue"]):
                                self.model.tapaAbiertaMFBP1=True
                                command = {
                                    "lbl_boxEmergente1" : {"text": "TAPA MFB-P1 detectada"},
                                    
                                    }
                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                if "MFBS_candado_limit" in payload:
                    if payload["MFBS_candado_limit"] == True:
                        self.model.tapaAbiertaMFBS=False
                        self.model.candados_limit_inductivos["MFB-S"] = True
                        if self.model.en_ciclo and  self.model.tapaAbiertaMFBP1==False:
                            command = {
                            #"lbl_boxEmergente1" : {"text": "TAPA MFB-S detectada \n Continue con el Torque ", "color": "green"},
                            "lbl_boxEmergente1" : {"text": "", "color": "green"},
                            
                            }
                            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        elif self.model.en_ciclo and self.model.tapaAbiertaMFBP1==True:
                            if 'MFB-P1' in str(self.model.torque_data["tool2"]["queue"]) or 'MFB-P1' in str(self.model.torque_data["tool3"]["queue"]):
                            
                                command = {
                                "lbl_boxEmergente1" : {"text": "TAPA MFBP1 detectada"},
                                
                                }
                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    else:
                        self.model.candados_limit_inductivos["MFB-S"] = False
                        
                        if self.model.en_ciclo and (len(self.model.torque_data["tool2"]["queue"])>0 or len(self.model.torque_data["tool3"]["queue"])>0):
                            if 'MFB-S' in str(self.model.torque_data["tool2"]["queue"]) or 'MFB-S' in str(self.model.torque_data["tool3"]["queue"]):
                                self.model.tapaAbiertaMFBS=True
                                command = {
                                    "lbl_boxEmergente1" : {"text": "TAPA MFB-S", "color": "green"},
                                    
                                    }
                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                if "MFBE_candado_limit" in payload:
                    if payload["MFBE_candado_limit"] == True:
                        self.model.candados_limit_inductivos["MFB-E"] = True
                    else:
                        self.model.candados_limit_inductivos["MFB-E"] = False

                #formato sensor inductivo: inductivo_caja_tuerca
                for inductivo in list(payload):
                    if "inductivo_" in inductivo:
                        
                        inductivo_array = inductivo.split("_") #inductivo_array = [inductivo,caja,tuerca]
                        print("inductivo_array: ",inductivo_array)

                        caja_inductivo = inductivo_array[1]
                        tuerca_inductivo = inductivo_array[2]
                        
                        #se obtienen los datos del inductivo_tool
                        inductivo_tool = self.model.torque_cycles[caja_inductivo][tuerca_inductivo][0]
                        
                        
                        
                        command = {
                            tuerca_inductivo :payload[inductivo]
                            }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        
                        print("self.model.config_data[sensores_inductivos][caja_inductivo][tuerca_inductivo]: ",self.model.config_data["sensores_inductivos"][caja_inductivo][tuerca_inductivo])

                        if self.model.config_data["sensores_inductivos"][caja_inductivo][tuerca_inductivo] == True:

                            #se obtienen los datos del inductivo_tool
                            inductivo_tool = self.model.torque_cycles[caja_inductivo][tuerca_inductivo][0]
                            print("self.model.torque_cycles[caja_inductivo][tuerca_inductivo]:",self.model.torque_cycles[caja_inductivo][tuerca_inductivo])
                            print("inductivo_tool: ",inductivo_tool)

                            if self.model.estado_candados == False or inductivo_tool == "tool1":
                            
                                #si current_trq no está vacío...
                                if self.model.torque_data[inductivo_tool]["current_trq"] != None:
                                    caja = self.model.torque_data[inductivo_tool]["current_trq"][0]
                                    tuerca = self.model.torque_data[inductivo_tool]["current_trq"][1]
                                    
                                    if caja == caja_inductivo:
                                        print("tuerca",tuerca)
                                        print("tuerca_inductivo",tuerca_inductivo)
                                        if tuerca!=tuerca_inductivo and self.model.candados_limit_inductivos[caja] == True:
                                          
                                          if payload[inductivo] == True:
                                              print("hay dos sensores activados de ",inductivo_tool)
                                              self.model.otra_cavidad_activa[inductivo_tool]=True
                                              #Se obtienen las cavidades sensadas
                                              self.model.cavidad_sensada[inductivo_tool][caja_inductivo].append(tuerca_inductivo)
                                              print("self.model.cavidad_sensada",self.model.cavidad_sensada)
                                          else:
                                              #Se obtienen las cavidades sensadas
                                              
                                              self.model.cavidad_sensada[inductivo_tool][caja_inductivo].pop(self.model.cavidad_sensada[inductivo_tool][caja_inductivo].index(tuerca_inductivo))
                                              print("self.model.cavidad_sensada drop",self.model.cavidad_sensada)
                                              if isinstance(self.model.cavidad_sensada[inductivo_tool][caja_inductivo],list) and len(self.model.cavidad_sensada[inductivo_tool][caja_inductivo])>1:
                                                  print("muchas tuercas detectadas")
                                                  self.model.otra_cavidad_activa[inductivo_tool]=True
                                              else:
                                                  print("Ya no hay herramienta en dos posiciones")
                                                  self.model.otra_cavidad_activa[inductivo_tool]=False
                                                  command = {
                                                        "lbl_steps" : {"text": f"Vuelve a colocar la herramienta"+inductivo_tool+" en posicion", "color": "green"},
                                                        "lbl_result" : {"text": "", "color": "black"},
                                                        }
                                                  self.client.publish(self.model.torque_data[inductivo_tool]["gui"],json.dumps(command), qos = 2)
                                                  
                                              
                                        #SI LA tuerca es diferente a tuerca_inductivo
                                        if tuerca == tuerca_inductivo and self.model.candados_limit_inductivos[caja] == True:

                                            encoder_inductivo = copy(inductivo_tool)
                                            encoder_inductivo = encoder_inductivo.replace("tool","encoder_")
                                            print("encoder_inductivo: ",encoder_inductivo)

                                            if payload[inductivo] == True:
                                                self.model.input_data["plc"][encoder_inductivo]["zone"] = '{"'+ caja_inductivo + '":"'+ tuerca_inductivo + '"}' #ejemplo: self.model.input_data["plc"][encoder_2]["zone"] = "{"PDC-D":"E1"}"
                                            else:
                                                self.model.input_data["plc"][encoder_inductivo]["zone"] = '{"'+ caja_inductivo + '":"0"}'
                                            print("self.model.input_data[plc][encoder][zone]", self.model.input_data["plc"][encoder_inductivo]["zone"])

                                            if encoder_inductivo == "encoder_1":
                                                print("self.model.otra_cavidad_activa[inductivo_tool] ya para enviar emit TOOL1",self.model.otra_cavidad_activa[inductivo_tool])
                                                if self.model.otra_cavidad_activa[inductivo_tool]==True:
                                                    print("debe mostrar mensaje de dos cavidades de ",inductivo_tool)
                                                    command = {
                                                        "lbl_steps" : {"text": f"Herramienta1 en dos Cavidades al mismo tiempo", "color": "red"},
                                                        "lbl_result" : {"text": "Verificar sensores de posicion de herramienta", "color": "black"},
                                                        }
                                                    self.client.publish(self.model.torque_data[inductivo_tool]["gui"],json.dumps(command), qos = 2)

                                                else:

                                                    print("emit zone de tool1")
                                                    self.zone_tool1.emit() 

                                            if encoder_inductivo == "encoder_2":
                                                print("self.model.otra_cavidad_activa[inductivo_tool] ya para enviar emit TOOL2",self.model.otra_cavidad_activa[inductivo_tool])
                                                if self.model.otra_cavidad_activa[inductivo_tool]==True:
                                                    
                                                    print("debe mostrar mensaje de dos cavidades de ",inductivo_tool)
                                                    command = {
                                                        "lbl_steps" : {"text": f"Herramienta2 en dos Cavidades al mismo tiempo", "color": "red"},
                                                        "lbl_result" : {"text": "Verificar sensores de posicion de herramienta", "color": "black"},
                                                        }
                                                    self.client.publish(self.model.torque_data[inductivo_tool]["gui"],json.dumps(command), qos = 2)

                                                else:
                                                    print("emit zone de tool2") 
                                                    self.zone_tool2.emit()

                                            if encoder_inductivo == "encoder_3":
                                                print("self.model.otra_cavidad_activa[inductivo_tool] ya para enviar emit TOOL3",self.model.otra_cavidad_activa[inductivo_tool])
                                                if self.model.otra_cavidad_activa[inductivo_tool]==True:
                                                    print("debe mostrar mensaje de dos cavidades de ",inductivo_tool)
                                                    command = {
                                                        "lbl_steps" : {"text": f"Herramienta3 en dos Cavidades al mismo tiempo", "color": "red"},
                                                        "lbl_result" : {"text": "Verificar sensores de posicion de herramienta", "color": "black"},
                                                        }
                                                    self.client.publish(self.model.torque_data[inductivo_tool]["gui"],json.dumps(command), qos = 2)

                                                else:
                                                    print("emit zone de tool3")
                                                    self.zone_tool3.emit()
                                        
                                        elif tuerca == tuerca_inductivo and self.model.candados_limit_inductivos[caja] == False:
                                            print("Cerrar Tapa para nido: ",caja)
                                            command = {
                                                "lbl_boxEmergente1" : {"text": f"Candado de caja {caja} abierto \n Cerrar Nido para continuar", "color": "black"},
                                                
                                                }
                                            self.client.publish(self.model.torque_data[inductivo_tool]["gui"],json.dumps(command), qos = 2)
                                            
                    #self.model.robot_data["v_queue"][box].pop(self.model.robot_data["v_queue"][box].index(self.model.robot_data["current_trig"]))
                    
                                          


                #encoder4
                if "encoder" in payload and "name" in payload and "value" in payload:

                    #obtener encoder_1, encoder_2, encoder_3, o encoder_4
                    encoder = "encoder_" + str(payload["encoder"])

                    #si se trata del encoder de altura
                    if encoder == "encoder_4":

                        print("encoder: ",encoder)

                        #si no se encuentra activado el modo de revisión de candados (funcionamiento normal)
                        if self.model.estado_candados == False:

                            #se convierte a tool3 para este caso porque el encoder 4 está en el eje Z sobre la tool3
                            current_tool = "tool3"

                            print("current_tool: ",current_tool)

                            #si current_trq no está vacío...
                            if self.model.torque_data[current_tool]["current_trq"] != None:
                                caja = self.model.torque_data[current_tool]["current_trq"][0]
                                tuerca = self.model.torque_data[current_tool]["current_trq"][1]
                            
                                print("caja: ",caja)
                                print("tuerca: ",tuerca)
                                print("payload[name]: ",payload["name"])
                                #si la caja coincide con la del encoder...
                                #PLC/1/status       {"encoder":4,"name":{"MFB-P2":"ALTURA"},"value":True}
                                if caja in payload["name"]:

                                    print("payload[value]: ",payload["value"])
                                    #se actualiza la variable que determina si está dentro de la zona de altura correcta o fuera para esa caja
                                    if payload["value"] == True:
                                        self.model.altura_zone[current_tool] = True
                                    else:
                                        self.model.altura_zone[current_tool] = False
                                    print("self.model.altura_zone[" + current_tool + "]: " + str(self.model.altura_zone[current_tool]))
                                    print("emit zone de tool3")
                                    self.zone_tool3.emit()
                            else:
                                print("self.model.torque_data[current_tool][current_trq] == None")
                        else:
                            print("No entró porque self.model.estado_candados: ",self.model.estado_candados)

                #ejemplo de mensaje:
                #PLC/1/status       {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                #DESDE GDI SERÍA:   {"encoder": 2,"name": "{\"PDC-R\":\"E1\"}","value":true}
                # SI EL MENSAJE MQTT CONTIENE ENCODER, NAME y VALUE...
                if "encoder" in payload and "name" in payload and "value" in payload:

                    print("payload: ",payload)

                    #CAMBIAR {"PDC-R":"E1"} por {"PDC-RMID":"E1"} o {"PDC-RS":"E1"} según corresponda
                    if "PDC-R" in payload["name"] and "PDC-RMID" in self.model.input_data["database"]["modularity"]:
                        payload["name"] = payload["name"].replace("PDC-R", "PDC-RMID")
                    if "PDC-R" in payload["name"] and "PDC-RS" in self.model.input_data["database"]["modularity"]:
                        payload["name"] = payload["name"].replace("PDC-R", "PDC-RS")

                    #obtener encoder_1, encoder_2, encoder_3, o encoder_4
                    encoder = "encoder_" + str(payload["encoder"])

                    #si no se encuentra activado el modo de revisión de candados (funcionamiento normal)
                    if self.model.estado_candados == False:

                        #se obtienen los datos del current_trq
                        current_tool = encoder.replace("encoder_","tool")
                        #si current_trq no está vacío...
                        if current_tool != "tool4" and self.model.torque_data[current_tool]["current_trq"] != None:
                            caja = self.model.torque_data[current_tool]["current_trq"][0]
                            tuerca = self.model.torque_data[current_tool]["current_trq"][1]

                            #ejemplo de señal: {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                            #ejemplo de caja: "PDC-D"
                            #ejemplo de tuerca: "E1"
                            #si el encoder leído contiene la caja y la tuerca del torque que está en la tarea actual (current_trq)
                            if caja in payload["name"] and tuerca in payload["name"]:
                                print("caja: ",caja)
                                print("tuerca: ",tuerca)

                                iinductivos = False
                                if caja in self.model.config_data["sensores_inductivos"]: #se busca que la caja sea una MFB-P2, MFB-P1, MFB-S o MFB-E
                                    if tuerca in self.model.config_data["sensores_inductivos"][caja]: #se busca que sea una tuerca válida para esa caja
                                        print("self.model.config_data[sensores_inductivos][caja][tuerca]: ",self.model.config_data["sensores_inductivos"][caja][tuerca])
                                        if self.model.config_data["sensores_inductivos"][caja][tuerca] == True:
                                            iinductivos = True

                                if iinductivos == False:

                                    #aquí entra cuando "value = False"...
                                    if not(payload["value"]):
                                        #actualizar payload["name"] actual con 0, ejemplo: {"PDC-D":"0"}
                                        payload["name"] = payload["name"][:payload["name"].find(":") + 1] + '"0"}'

                                    #a este punto llegas con un payload["name"] que vale a la caja:terminal {"PDC-D":"E1"} o con un valor de 0 {"PDC-D":"0"}

                                    lista_encoders = ["encoder_1","encoder_2","encoder_3"]
                                    for i in lista_encoders:
                                        if i == encoder:
                                            #se actualiza la zona de este encoder
                                            self.model.input_data["plc"][i]["zone"] = payload["name"] #ejemplo: self.model.input_data["plc"][encoder_2]["zone"] = "{"PDC-D":"E1"}"


                                    print("encoder: ",encoder)
                                    print("self.model.input_data[plc][encoder][zone]", self.model.input_data["plc"][encoder]["zone"])

                                    if encoder == "encoder_1":
                                        print("emit zone de tool1")
                                        self.zone_tool1.emit() 

                                    if encoder == "encoder_2":
                                        print("emit zone de tool2")
                                        self.zone_tool2.emit()

                                    if encoder == "encoder_3":
                                        print("emit zone de tool3")
                                        self.zone_tool3.emit()


                    #si está en revisión de candados
                    else:
                        print('Para desactivar candados mandar PLC/1/status {"candados_finish":true}')
                        print("PAYLOAD: ",payload["name"])
                        print("VALUE: ",payload["value"])    
                        # {"encoder":3,"name":{"PDC-R":"S1"},"value":True}
                        # {"encoder":3,"name":{"PDC-R":"S1"},"value":False}
                        # {"encoder":3,"name":{"PDC-R":"S3"},"value":True}

                        payload_name = copy(payload["name"])
                        payload_name = payload_name.replace('{','')
                        payload_name = payload_name.replace('}','')
                        payload_name = payload_name.replace('"','')
                        payload_name = payload_name.replace('PDC-R:','')
                        payload_name = payload_name.replace('PDC-RMID:','')
                        payload_name = payload_name.replace('PDC-RSMALL:','')
                        print("copyPAYLOAD: ",payload_name)

                        if encoder == "encoder_4":
                            #funcionamiento cambia para s6 y s7 que esperan valores de height2
                            if self.model.current_task_candado=="s6" or self.model.current_task_candado=="s7":
                                if payload_name=="height2":
                                    if payload["value"] == False:
                                        self.model.input_data["plc"][encoder]["candado"] = "0"
                                    else:
                                        self.model.input_data["plc"][encoder]["candado"] = "height"
                                    print("emit zone de tool4")
                                    self.zone_tool4.emit()
                            else:
                                if payload_name=="height":
                                    if payload["value"] == False:
                                        self.model.input_data["plc"][encoder]["candado"] = "0"
                                    else:
                                        self.model.input_data["plc"][encoder]["candado"] = "height"
                                    print("emit zone de tool4")
                                    self.zone_tool4.emit()

                        if encoder == "encoder_3":

                            if payload_name in self.model.candados_zonas:
                                if payload["value"] == False:
                                    self.model.candados_zonas[payload_name]=False
                                    print("self.model.candados_zonas[payload_name]",self.model.candados_zonas)
                                else:
                                    self.model.candados_zonas[payload_name]=True
                                    print("self.model.candados_zonas[payload_name]",self.model.candados_zonas)

                            print("self.model.current_task_candado ==== ",self.model.current_task_candado)
                            if self.model.current_task_candado == payload_name:
                                if payload["value"] == False:
                                    self.model.input_data["plc"][encoder]["candado"] = "0"
                                    print("emit de zone tool3 CANDADO = FALSE")
                                    
                                else:
                                    self.model.input_data["plc"][encoder]["candado"] = payload_name
                                    print("emit zone de tool3 CANDADO = TRUE")
                                    
                                self.zone_tool3.emit()
                            else:
                                print("IGNORAR TRIGGER")
                                print("IGNORADO: ",payload_name)
                                
                        if encoder == "encoder_1":

                            #si current_trq no está vacío...
                            if self.model.torque_data["tool1"]["current_trq"] != None:
                                caja = self.model.torque_data["tool1"]["current_trq"][0]
                                tuerca = self.model.torque_data["tool1"]["current_trq"][1]

                                #ejemplo de señal: {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                                #ejemplo de caja: "PDC-D"
                                #ejemplo de tuerca: "E1"
                                #si el encoder leído contiene la caja y la tuerca del torque que está en la tarea actual (current_trq)
                                if caja in payload["name"] and tuerca in payload["name"]:
                                    print("caja: ",caja)
                                    print("tuerca: ",tuerca)

                                    iinductivos = False
                                    if caja in self.model.config_data["sensores_inductivos"]: #se busca que la caja sea una MFB-P2, MFB-P1, MFB-S o MFB-E
                                        if tuerca in self.model.config_data["sensores_inductivos"][caja]: #se busca que sea una tuerca válida para esa caja
                                            print("self.model.config_data[sensores_inductivos][caja][tuerca]: ",self.model.config_data["sensores_inductivos"][caja][tuerca])
                                            if self.model.config_data["sensores_inductivos"][caja][tuerca] == True:
                                                iinductivos = True

                                    if iinductivos == False:
                                        #aquí entra cuando "value = False"...
                                        if not(payload["value"]):
                                            #actualizar payload["name"] actual con 0, ejemplo: {"PDC-D":"0"}
                                            payload["name"] = payload["name"][:payload["name"].find(":") + 1] + '"0"}'

                                        #ejemplo: en self.model.input_data["plc"] ::::: [encoder_2]["zone"] = "{"PDC-D":"E1"}"
                                        self.model.input_data["plc"][encoder]["zone"] = payload["name"] #valores como "E1", "A22", "0", etc...
                                        print("self.model.input_data[plc][encoder][zone]", self.model.input_data["plc"][encoder]["zone"])
                                        print("emit zone de tool1")
                                        self.zone_tool1.emit()

                if "retry_btn" in payload:
                    self.model.input_data["plc"]["retry_btn"] = bool(payload["retry_btn"])
                    if payload["retry_btn"] == True:
                        self.retry_btn.emit()

                #se habilita la función mensajes_clamp cada que llega un mensaje del PLC
                for i in self.nido:
                    self.mensajes_clamp(i,payload)


            if message.topic == self.model.sub_topics["torque_1"]:

                payload_str = json.dumps(payload)
                tool = "tool1"

                #if "signal_start_button" in payload: 
                #    print("signal start button: ",payload["signal_start_button"])

                if "bin" in payload_str:
                    if "bin1" in payload:
                        if payload["bin1"]:
                            self.model.torque_bin[tool]["bin1"] = 1
                        else:
                            self.model.torque_bin[tool]["bin1"] = 0
                    if "bin2" in payload:
                        if payload["bin2"]:
                            self.model.torque_bin[tool]["bin2"] = 2
                        else:
                            self.model.torque_bin[tool]["bin2"] = 0
                    if "bin3" in payload:
                        if payload["bin3"]:
                            self.model.torque_bin[tool]["bin3"] = 4
                        else:
                            self.model.torque_bin[tool]["bin3"] = 0

                    self.model.torque_bin[tool]["current_profile"] = self.model.torque_bin[tool]["bin1"] + self.model.torque_bin[tool]["bin2"] + self.model.torque_bin[tool]["bin3"]


                if "result" in payload: 
                    #se convierten los valores leídos de string a float
                    
                    #converted_values = [self.convert_to_float_or_str(val) for val in payload]
                    for valor_torque in payload:
                        payload[valor_torque]=self.convert_to_float_or_str(payload[valor_torque])
                        self.model.info_torque[valor_torque]=payload[valor_torque]
                    if self.model.info_torque["result"]!=1:
                        self.model.herramienta_bloqueada[tool]=True
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : True}), qos = 2)
                    else:
                        self.model.herramienta_bloqueada[tool]=False
                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:

                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        ################################################
                        copy_CycleSelected_tool1 = ""
                        fecha_actual = self.model.get_currentTime()
                        try:
                            data = {
                                "HERRAMIENTA": tool,
                                "REGISTRO": payload,
                                "FECHA": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                                "CICLO_manager":str(self.model.torque_data[tool]["current_trq"]),
                                "estado_actual":self.model.estado_actual[tool],
                                "perfil_driver":self.model.info_torque["CycleSelected"],
                                "fase_driver":  self.model.info_torque["fase"],
                                "HM":           self.model.qr_codes["HM"],
                                "angulo_final": self.model.info_torque["angle"],
                                "torque_final": self.model.info_torque["torque"],
                                "torque_minimo": self.model.info_torque["torque_min"],
                                "torque_maximo": self.model.info_torque["torque_max"],
                                "angulo_minimo": self.model.info_torque["angle_min"],
                                "angulo_maximo": self.model.info_torque["angle_max"],
                                "angle_trend":   self.model.info_torque["angle_trend"],
                                "torque_trend":  self.model.info_torque["torque_trend"],
                                "angle_target":  self.model.info_torque["angle_target"],
                                "torque_target": self.model.info_torque["torque_target"],
                                "result":        self.model.info_torque["result"]
                                }
                            print("data to post torqueinfo",data)
                            copy_CycleSelected_tool1 = copy(self.model.info_torque["CycleSelected"])
                            copy_angulo_final1 = copy(self.model.info_torque["angle"])
                            copy_angulo_maximo1 = copy(self.model.info_torque["angle_max"])

                            endpoint = "http://{}/api/post/torque_info".format(self.model.server)
                            resp = requests.post(endpoint, data=json.dumps(data))
                            self.default_info_torque() #se reinicia el valor de las variables, pero se guarda el último CycleSelected
                        except Exception as ex:
                            print("post torque exception: ", ex)
                        #se emite la señal de que se hizo un torque con esta herramienta
                        
                        revversa1 = self.model.torque_data[tool]["backward_profile"]

                        print("revversa1: ",revversa1)
                        print("self.model.info_torque[CycleSelected]: ",copy_CycleSelected_tool1)
                        print("self.model.estado_actual[tool]: ",self.model.estado_actual[tool])

                        if (copy_CycleSelected_tool1 == revversa1 or copy_angulo_final1>4000 or copy_angulo_maximo1>4000 ) and self.model.estado_actual[tool] == "BACKWARD":
                            print("torque1_reversa emit()")
                            self.torque1_reversa.emit()
                        else:
                            self.model.asegurar_lectura[tool] = True
                            print("torque1 emit()")
                            self.torque1.emit()
                    else:
                        print("torque no emit, saliendo de reversa")
                    if self.model.herramienta_bloqueada[tool]==True:
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}), qos = 2)

            if message.topic == self.model.sub_topics["torque_2"]:

                payload_str = json.dumps(payload)
                tool = "tool2"

                #if "signal_start_button" in payload: 
                #    print("signal start button: ",payload["signal_start_button"])


                if "bin" in payload_str:
                    if "bin1" in payload:
                        if payload["bin1"]:
                            self.model.torque_bin[tool]["bin1"] = 1
                        else:
                            self.model.torque_bin[tool]["bin1"] = 0
                    if "bin2" in payload:
                        if payload["bin2"]:
                            self.model.torque_bin[tool]["bin2"] = 2
                        else:
                            self.model.torque_bin[tool]["bin2"] = 0
                    if "bin3" in payload:
                        if payload["bin3"]:
                            self.model.torque_bin[tool]["bin3"] = 4
                        else:
                            self.model.torque_bin[tool]["bin3"] = 0

                    self.model.torque_bin[tool]["current_profile"] = self.model.torque_bin[tool]["bin1"] + self.model.torque_bin[tool]["bin2"] + self.model.torque_bin[tool]["bin3"]


                if "result" in payload: 
                    #se convierten los valores leídos de string a float
                    for valor_torque in payload:
                        payload[valor_torque]=self.convert_to_float_or_str(payload[valor_torque])
                        self.model.info_torque[valor_torque]=payload[valor_torque]
                    if self.model.info_torque["result"]!=1:
                        self.model.herramienta_bloqueada[tool]=True
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : True}), qos = 2)
                    else:
                        self.model.herramienta_bloqueada[tool]=False
                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:

                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        ################################################
                        copy_CycleSelected_tool2 = ""
                        fecha_actual = self.model.get_currentTime()
                        try:
                            data = {
                                "HERRAMIENTA": tool,
                                "REGISTRO": payload,
                                "FECHA": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                                "CICLO_manager":str(self.model.torque_data[tool]["current_trq"]),
                                "estado_actual":self.model.estado_actual[tool],
                                "perfil_driver":self.model.info_torque["CycleSelected"],
                                "fase_driver":  self.model.info_torque["fase"],
                                "HM":           self.model.qr_codes["HM"],
                                "angulo_final": self.model.info_torque["angle"],
                                "torque_final": self.model.info_torque["torque"],
                                "torque_minimo": self.model.info_torque["torque_min"],
                                "torque_maximo": self.model.info_torque["torque_max"],
                                "angulo_minimo": self.model.info_torque["angle_min"],
                                "angulo_maximo": self.model.info_torque["angle_max"],
                                "angle_trend":   self.model.info_torque["angle_trend"],
                                "torque_trend":  self.model.info_torque["torque_trend"],
                                "angle_target":  self.model.info_torque["angle_target"],
                                "torque_target": self.model.info_torque["torque_target"],
                                "result":        self.model.info_torque["result"]
                                }
                            print("data to post torqueinfo",data)
                            copy_CycleSelected_tool2 = copy(self.model.info_torque["CycleSelected"])
                            copy_angulo_final2 = copy(self.model.info_torque["angle"])
                            copy_angulo_maximo2 = copy(self.model.info_torque["angle_max"])
                            endpoint = "http://{}/api/post/torque_info".format(self.model.server)
                            resp = requests.post(endpoint, data=json.dumps(data))
                            self.default_info_torque()
                        except Exception as ex:
                            print("post torque exception: ", ex)
                        #se emite la señal de que se hizo un torque con esta herramienta
                        
                        revversa2 = self.model.torque_data[tool]["backward_profile"]

                        print("revversa2: ",revversa2)
                        print("self.model.info_torque[CycleSelected]: ",copy_CycleSelected_tool2)
                        print("self.model.estado_actual[tool]: ",self.model.estado_actual[tool])

                        if (copy_CycleSelected_tool2 == revversa2 or copy_angulo_final2>4000 or copy_angulo_maximo2>4000 ) and self.model.estado_actual[tool] == "BACKWARD":
                            print("torque2_reversa emit()")
                            self.torque2_reversa.emit()
                        else:
                            self.model.asegurar_lectura[tool] = True
                            print("torque2 emit()")
                            self.torque2.emit()
                    else:
                        print("torque no emit, saliendo de reversa")
                    if self.model.herramienta_bloqueada[tool]==True:
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}), qos = 2)

            if message.topic == self.model.sub_topics["torque_3"]:

                payload_str = json.dumps(payload)
                tool = "tool3"

                #if "signal_start_button" in payload: 
                #    print("signal start button: ",payload["signal_start_button"])

                if "bin" in payload_str:
                    if "bin1" in payload:
                        if payload["bin1"]:
                            self.model.torque_bin[tool]["bin1"] = 1
                        else:
                            self.model.torque_bin[tool]["bin1"] = 0
                    if "bin2" in payload:
                        if payload["bin2"]:
                            self.model.torque_bin[tool]["bin2"] = 2
                        else:
                            self.model.torque_bin[tool]["bin2"] = 0
                    if "bin3" in payload:
                        if payload["bin3"]:
                            self.model.torque_bin[tool]["bin3"] = 4
                        else:
                            self.model.torque_bin[tool]["bin3"] = 0

                    self.model.torque_bin[tool]["current_profile"] = self.model.torque_bin[tool]["bin1"] + self.model.torque_bin[tool]["bin2"] + self.model.torque_bin[tool]["bin3"]

                if "result" in payload: 
                    #se convierten los valores leídos de string a float
                    for valor_torque in payload:
                        payload[valor_torque]=self.convert_to_float_or_str(payload[valor_torque])
                        self.model.info_torque[valor_torque]=payload[valor_torque]

                    if self.model.info_torque["result"]!=1:
                        self.model.herramienta_bloqueada[tool]=True
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : True}), qos = 2)
                    else:
                        self.model.herramienta_bloqueada[tool]=False
                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:
                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        ################################################
                        copy_CycleSelected_tool3 = ""
                        fecha_actual = self.model.get_currentTime()
                        try:
                            data = {
                                "HERRAMIENTA": tool,
                                "REGISTRO": payload,
                                "FECHA": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                                "CICLO_manager":str(self.model.torque_data[tool]["current_trq"]),
                                "estado_actual":self.model.estado_actual[tool],
                                "perfil_driver":self.model.info_torque["CycleSelected"],
                                "fase_driver":  self.model.info_torque["fase"],
                                "HM":           self.model.qr_codes["HM"],
                                "angulo_final": self.model.info_torque["angle"],
                                "torque_final": self.model.info_torque["torque"],
                                "torque_minimo": self.model.info_torque["torque_min"],
                                "torque_maximo": self.model.info_torque["torque_max"],
                                "angulo_minimo": self.model.info_torque["angle_min"],
                                "angulo_maximo": self.model.info_torque["angle_max"],
                                "angle_trend":   self.model.info_torque["angle_trend"],
                                "torque_trend":  self.model.info_torque["torque_trend"],
                                "angle_target":  self.model.info_torque["angle_target"],
                                "torque_target": self.model.info_torque["torque_target"],
                                "result":        self.model.info_torque["result"]
                                }
                            print("data to post torqueinfo",data)
                            copy_CycleSelected_tool3 = copy(self.model.info_torque["CycleSelected"])
                            copy_angulo_final3 = copy(self.model.info_torque["angle"])
                            copy_angulo_maximo3 = copy(self.model.info_torque["angle_max"])
                            endpoint = "http://{}/api/post/torque_info".format(self.model.server)
                            resp = requests.post(endpoint, data=json.dumps(data))
                            self.default_info_torque()
                        except Exception as ex:
                            print("post torque exception: ", ex)
                        #se emite la señal de que se hizo un torque con esta herramienta
                        
                        revversa3 = self.model.torque_data[tool]["backward_profile"]

                        print("revversa3: ",revversa3)
                        print("self.model.info_torque[CycleSelected]: ",copy_CycleSelected_tool3)
                        print("self.model.estado_actual[tool]: ",self.model.estado_actual[tool])

                        if (copy_CycleSelected_tool3 == revversa3 or copy_angulo_final3>4000 or copy_angulo_maximo3>4000 ) and self.model.estado_actual[tool] == "BACKWARD":
                            print("torque3_reversa emit()")
                            self.torque3_reversa.emit()
                        else:
                            self.model.asegurar_lectura[tool] = True
                            print("torque3 emit()")
                            self.torque3.emit()
                    else:
                        print("torque no emit, saliendo de reversa")
                    if self.model.herramienta_bloqueada[tool]==True:
                        tool_desbloqueada = tool+"_desbloqueada"
                        self.client.publish(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}), qos = 2)

            if message.topic == self.model.sub_topics["gui"]:
                 
                if self.model.llave == True:
                   if "keyboard_cancel" in payload:
                       command = {"message_pop":{"Visible":False}}
                       self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                       print("key no emit")
                       self.model.llave = False
                   if "keyboard_ok" in payload:
                       command = {"message_pop":{"Visible":False}}
                       self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                       self.key.emit()
                       print("key emit")
                       self.model.llave = False
                if "Mantenimiento" in payload:
                    print("la gui trae mantenimiento y llega al comm")
                    fecha_actual = self.model.get_currentTime()
                    command = {
                        "vision":"start_record",
                        "info":self.model.qr_codes["HM"]+" "+str(fecha_actual.strftime("%Y/%m/%d %H:%M:%S"))
                    }
                    self.client.publish(self.model.sub_topics["supervision"],json.dumps(command), qos = 2)
                
                if "request" in payload:
                    self.model.input_data["gui"]["request"] = payload["request"]
                    if payload["request"] == "login":
                        self.login.emit()
                    elif payload["request"] == "logout":
                        self.logout.emit()
                    elif payload["request"] == "config":
                        self.config.emit()
                    elif payload["request"] == "gdi":

                        print("USUARIO TIPO:", self.model.local_data["user"]["type"])
                        
                        #ya no se oculta desde aquí la GDI
                        #if self.model.local_data["user"]["type"] == "CALIDAD" or self.model.local_data["user"]["type"] == "SUPERUSUARIO":

                        #    if self.mostrar_gdi == True:
                        #        self.mostrar_gdi = False
                        #        self.client.publish("GDI",json.dumps({"Esconder":"window"}), qos = 2)
                        #        print("Escondiendo GDI")
                        #    elif self.mostrar_gdi == False:
                        #        self.mostrar_gdi = True
                        #        self.client.publish("GDI",json.dumps({"Mostrar":"window"}), qos = 2)
                        #        print("Mostrando GDI")
                if "MOSTRARGDI" in str(payload):
                        print("Mostrando GDI")
                        try:
                            #se oculta la GDI automáticamente:
                            self.client.publish("GDI",json.dumps({"Mostrar" : True}), qos = 2)
                        except Exception as ex:
                            print("Error al Mostrar GDI ", ex)
                if "ESCONDERGDI" in str(payload):
                        print("Escondiendo GDI")
                        try:
                            #se oculta la GDI automáticamente:
                            self.client.publish("GDI",json.dumps({"Esconder" : True}), qos = 2)
                        except Exception as ex:
                            print("Error al Esconder GDI ", ex)
                if "codeQR" in payload:
                    
                    if "MOSTRARGDI" in str(payload):
                        print("Mostrando GDI")
                        try:
                            #se oculta la GDI automáticamente:
                            self.client.publish("GDI",json.dumps({"Mostrar" : True}), qos = 2)
                        except Exception as ex:
                            print("Error al Mostrar GDI ", ex)
                    if "ESCONDERGDI" in str(payload):
                        print("Escondiendo GDI")
                        try:
                            #se oculta la GDI automáticamente:
                            self.client.publish("GDI",json.dumps({"Esconder" : True}), qos = 2)
                        except Exception as ex:
                            print("Error al Esconder GDI ", ex)
                    usuario = str(payload["codeQR"])
                    try:
                        endpoint = ("http://{}/api/get/usuarios/GAFET/=/{}/ACTIVE/=/1".format(self.model.server, usuario))
                        response = requests.get(endpoint).json()
                        print(response)
                        if (self.model.key_calidad_caja_repetida== True  or self.model.key_calidad_caja_sin_FET==True) and response["TYPE"] == "CALIDAD":
                            master_qr_boxes = json.loads(self.model.input_data["database"]["pedido"]["QR_BOXES"])
                            for box in master_qr_boxes:
                                if master_qr_boxes[box][0] in self.model.qr_box_actual and master_qr_boxes[box][1]:
                                    if not(box in self.model.input_data["plc"]["clamps"]) and box in self.model.input_data["database"]["modularity"]:
                                        
                                        if "TYPE" in response:
                                            if response["TYPE"] == "SUPERUSUARIO" or response["TYPE"] == "AMTC" or response["TYPE"] == "CALIDAD":
                                                fecha_actual = self.model.get_currentTime()
                                                data = {
                                                    "NAME": response["NAME"],
                                                    "GAFET":  usuario,
                                                    "TYPE": response["TYPE"],
                                                    "LOG": "torque_KEY",
                                                    "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                                                    }
                                        
                                        print("porque está mal")
                                        data["LOG"]="CAJA_"+self.model.caja_por_validar+"_Validada"
                                        data["HM"]=self.model.qr_codes["HM"]
                                        data["FET"]=self.model.name_FET
                                        data["QR_FET"]=self.model.qr_FET
                                        data["QR_VALIDADO"]=self.model.qr_box_actual
                                        self.model.key_calidad_caja_repetida=False
                                        
                                        print("QR ACEPTADO validado calidad: ",self.model.qr_box_actual)
                                        print("colocar caja para clampear: ",self.model.caja_por_validar)
                                        if self.model.caja_por_validar=="PDC-P":
                                            self.model.validacion_conectores_pdcp=True
                                            if self.model.caja_por_validar in self.model.boxPos1:
                                                command = {
                                                    "lbl_steps" : {"text": f"Coloca la caja PDC-P para validar CONECTORES", "color": "green"},
                                                    "img_center" : "PDCP_CANDADOS.JPG",
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                                command = {
                                                    "lbl_steps" : {"text": "", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                            if self.model.caja_por_validar in self.model.boxPos2:

                                                command = {
                                                    "lbl_steps" : {"text": f"Coloca la caja PDC-P para validar CONECTORES", "color": "green"},
                                                    "img_center" : "PDCP_CANDADOS.JPG",
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                                command = {
                                                    "lbl_steps" : {"text": f" ", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                
                                                }
                                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                                            self.model.qr_validado.append(copy(self.model.qr_box_actual))
                                            endpoint = "http://{}/api/post/login".format(self.model.server)
                                            resp = requests.post(endpoint, data=json.dumps(data))
                                        else:
                                            self.client.publish(self.model.pub_topics["plc"],json.dumps({self.model.caja_por_validar: True}), qos = 2)

                                            if self.model.caja_por_validar in self.model.boxPos1:
                                                command = {
                                                    "lbl_steps" : {"text": f"Coloca la caja {self.model.caja_por_validar} en su lugar", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                                command = {
                                                    "lbl_steps" : {"text": "", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                            if self.model.caja_por_validar in self.model.boxPos2:

                                                command = {
                                                    "lbl_steps" : {"text": f"Coloca la caja {self.model.caja_por_validar} en su lugar", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                    }
                                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                                command = {
                                                    "lbl_steps" : {"text": f" ", "color": "black"},
                                                    "lbl_result" : {"text": "", "color": "red"},
                                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                                
                                                }
                                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                                            self.model.qr_validado.append(copy(self.model.qr_box_actual))
                                            endpoint = "http://{}/api/post/login".format(self.model.server)
                                            resp = requests.post(endpoint, data=json.dumps(data))
                                            Timer(10, self.boxTimeout, args = (self.model.caja_por_validar, self.model.qr_box_actual)).start()

                                #elif self.model.reintento_torque == True:
                                #    print("key_process!!!!!!!!!!!!!!!!!!!!!!")
                                #    print("key_process!!!!!!!!!!!!!!!!!!!!!!")
                                #    print("key_process!!!!!!!!!!!!!!!!!!!!!!")
                                #
                                #    endpoint = "http://{}/api/post/login".format(self.model.server)
                                #    resp = requests.post(endpoint, data=json.dumps(data))
                                #    
                                #    self.key_process.emit()
                                ## si la variable es False, quiere decir que estás en otra parte del proceso y la llave reiniciará el ciclo
                                #else:
                                #    endpoint = "http://{}/api/post/login".format(self.model.server)
                                #    resp = requests.post(endpoint, data=json.dumps(data))
                                #    
                                #    command = {"popOut":"¿Seguro que desea dar llave?\n Presione Esc. para salir, click derecho para continuar..."}
                                #    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                #    self.model.llave = True

                    except Exception as ex:
                        print("QR exception:", ex)
                    print("llego un codigo qr")
                    if "CENTERLLAVE" in str(payload):
                        self.key.emit()

                    if "CENTERKEY" in str(payload):

                        for tool in self.model.estado_actual:
                            if self.model.estado_actual[tool]=="BACKWARD":
                                
                                command = {
                                    "lbl_steps" : {"text": "Completa reversa para finalizar ciclo", "color": "black"},
                                    "lbl_result" : {"text": "Llave detectada", "color": "red"},
                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                    }
                                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                command = {
                                    "lbl_steps" : {"text": "Completa reversa para finalizar ciclo", "color": "black"},
                                    "lbl_result" : {"text": "Llave detectada", "color": "red"},
                                    "lbl_boxNEW" : {"text":"", "color": "green"},
                                    }
                                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                #self.client.publish(self.model.torque_data[tool]["gui"],json.dumps(command), qos = 2)
                        # si la variable es True, quiere decir que hubo un mal torqueo y se requiere llave para habilitar la reversa
                        if self.model.reintento_torque == True:
                            #esta llave solo es para proceso
                            print("key_process.emit()")
                            self.key_process.emit()
                        # si la variable es False, quiere decir que estás en otra parte del proceso y la llave reiniciará el ciclo
                        elif self.model.reintento_torque == False:
                            command = {"message_pop":{"text":"¿Seguro que desea dar llave?\n  Presione Esc. para salir, Click Derecho para continuar...",
                                               "Visible":True},}
                            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                            self.model.llave = True


                if "ID" in payload:
                    self.model.input_data["gui"]["ID"] = payload["ID"]
                    self.ID.emit()
                if "code" in payload:
                    self.model.input_data["gui"]["code"] = payload["code"]
                    self.code.emit()
                if "visible" in payload:
                    self.model.input_data["gui"]["visible"] = payload["visible"]
                    self.visible.emit()

            if message.topic == self.model.sub_topics["config"]:
                if "finish" in payload:
                    if payload["finish"] == True:
                        self.config_ok.emit()
                if "shutdown" in payload:
                    if payload["shutdown"] == True:
                        self.model.shutdown = True

            if message.topic == self.model.sub_topics["gui"] or message.topic == self.model.sub_topics["gui_2"]:
                if "MTTOuser" in payload:
                    user_mantenimiento = payload["MTTOuser"]
                    endpoint = ("http://{}/api/get/usuarios/GAFET/=/{}/ACTIVE/=/1".format(self.model.server, user_mantenimiento))
                    response = requests.get(endpoint).json()
                    print(response)
                    if "TYPE" in response:
                        if response["TYPE"] == "SUPERUSUARIO" or response["TYPE"] == "AMTC" or response["TYPE"] == "MANTENIMIENTO":
                            fecha_actual = self.model.get_currentTime()
                            data = {
                                "NAME": response["NAME"],
                                "GAFET":  user_mantenimiento,
                                "TYPE": response["TYPE"],
                                "LOG": "torque_KEY",
                                "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                                }
                            print("dataaa mtto",data)
                            command = {
                                "userOK" : True,
                                "login_mtto": False
                                }
                            
                            self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        else:
                            self.client.publish(self.model.pub_topics["gui"],json.dumps({"userOK": False}), qos = 2)
                if "PDC-R" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-R": payload["PDC-R"]}), qos = 2)
                if "PDC-RMID" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": payload["PDC-RMID"]}), qos = 2) 
                if "PDC-D" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-P": payload["PDC-P"]}), qos = 2)  
                if "PDC-P" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-D": payload["PDC-D"]}), qos = 2)  
                if "MFB-P1" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"MFB-P1": payload["MFB-P1"]}), qos = 2)
                if "MFB-P2" in payload:
                    self.client.publish(self.model.pub_topics["plc"],json.dumps({"MFB-P2": payload["MFB-P1"]}), qos = 2)        

                if "Mantenimiento" in payload:
                    if payload["Mantenimiento"]==True:
                        if self.model.en_ciclo==False:
                            print("la gui trae mantenimiento y llega al comm")
                            fecha_actual = self.model.get_currentTime()
                            command = {
                                "vision":"start_record",
                                "info":self.model.qr_codes["HM"]+" "+str(fecha_actual.strftime("%Y/%m/%d %H:%M:%S"))
                            }
                            self.client.publish(self.model.sub_topics["supervision"],json.dumps(command), qos = 2)
                        #else:
                    else:
                        if self.model.en_ciclo==False:
                            command = {
                                "vision":"stop_record"                        }
                            self.client.publish(self.model.sub_topics["supervision"],json.dumps(command), qos = 2)
                        #else:
                if "qr_box" in payload:
                    string_qr_box = str(payload["qr_box"])
                    string_qr_box = string_qr_box.replace(" ","") #se eliminan los espacios de los QRs

                    if self.model.config_data["trazabilidad"] == False:
                        if string_qr_box == "004":
                            self.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-P": True}), qos = 2)
                        elif string_qr_box == "009":
                            self.client.publish(self.model.pub_topics["plc"],json.dumps({"MFB-E": True}), qos = 2)
                        else:
                            self.qr_box.emit(string_qr_box)
                    elif "BYPASSTOOL" in payload["qr_box"]:
                        if payload["qr_box"]=="BYPASSTOOL1":
                            if "MFB-P1" in self.model.torque_data["tool1"]["current_trq"] and self.model.torque_data["tool1"]["current_trq"][1]== self.model.zona_actual[1]:
                                print("es la caja MFBP1, se encuentra dentro de las tareas actuales y ya esta en la zona")
                                self.model.altura_zone["tool1"] = True
                        "vamos a hacer algo"
                    else:
                        self.qr_box.emit(string_qr_box)

        except Exception as ex:
            print("input exception", ex)
    
    def convert_to_float_or_str(self,value):
        try:
            return float(value)
        except ValueError:
            return str(value)

    def default_info_torque(self):
        self.model.info_torque={"AngularTreshold":0,
                          "CurrentMonitor":0,
                          "CycleSelected":0,
                          "FinalSpeed":0,
                          "PostSeatingRealTorque":0,
                          "PostSeatingTorque":0,
                          "RundownSpeed":0,
                          "SeatingTorque":0,
                          "SetErrorcode":0,
                          "ToolCount":0,
                          "TorqueCorrection":0,
                          "angle":0,
                          "angle_max":0,
                          "angle_min":0,
                          "angle_target":0,
                          "angle_trend":"",
                          "fase":0,
                          "result":0,
                          "torque":0,
                          "torque_max":0,
                          "torque_min":0,
                          "torque_target":0,
                          "torque_trend":"",
            }
    
    def closePopout (self):
        command = {
            "popOut":"close"
            }
        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
        self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

    def boxTimeout(self, i, qr_box):

        #if self.model.bandera_mfbe_nueva == True:
        #        self.model.bandera_mfbe_nueva = False
        #        qr_box = qr_box.replace("12975407416","12975408030") #se regresa qr orgiginal 
        #                                                             #para que quede registrado como su qr en self.model.qr_codes[i]
        #                                                             #que es la varable que guarda los QRs en el registro

        if not(i in self.model.input_data["plc"]["clamps"]):
            print("tiempo terminado... caja desclampeada: ",i)
            self.client.publish(self.model.pub_topics["plc"],json.dumps({i: False}), qos = 2)
            

            if self.model.caja_por_validar in self.model.boxPos1:
                command = {
                "lbl_steps" : {"text": f"Vuelve a escanear la caja {self.model.caja_por_validar}", "color": "red"},
                "img_center" : "logo.jpg",
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                command = {
                "lbl_steps" : {"text": f" ", "color": "black"},
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
            if self.model.caja_por_validar in self.model.boxPos2:

                command = {
                "lbl_steps" : {"text": f"Vuelve a escanear la caja {self.model.caja_por_validar}", "color": "red"},
                "img_center" : "logo.jpg",
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                command = {
                "lbl_steps" : {"text": f" ", "color": "black"},

                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},

                }
                self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)



            for item in self.model.torque_data:
                if not(len(self.model.torque_data[item]["queue"])):
                    #self.client.client.publish(self.model.torque_data[item]["gui"],json.dumps(command), qos = 2)
                    pass
        else:
            self.model.qr_codes[i] = qr_box

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from manager.model import model
    import sys
    app = QApplication(sys.argv)
    model = model.manager()
    client = mqttClient(model)
    sys.exit(app.exec_())

