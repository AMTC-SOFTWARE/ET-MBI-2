
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from paho.mqtt.client import Client
from threading import Timer
from time import sleep              # Para usar la función sleep(segundos)
from copy import copy
import json

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
    
    nido = ["PDC-P","PDC-D","MFB-P1","MFB-P2","PDC-R","PDC-RMID","BATTERY","BATTERY-2","MFB-S","MFB-E"]
    nido_pub = ""
    color_nido = "blue"


    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.client = Client()
        QTimer.singleShot(5000, self.setup)

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
                            "popOut":"Paro de emergencia activado"
                            }
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    else:
                        #QTimer.singleShot(1000, self.closePopout)
                        self.closePopout()

            if self.model.input_data["plc"]["emergency"] == False:
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
                if self.keyboard_key == "keyboard_space":
                    print("se presionó el palpador de teclado")
                    self.model.pin_pressed = True
                    self.pin.emit()
                if self.keyboard_key == "keyboard_esc":
                    command = {"popOut":"close"}
                    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    print("key no emit")

                if self.model.llave == True:

                    if self.keyboard_key == "keyboard_esc":
                        command = {"popOut":"close"}
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        print("key no emit")
                        self.model.llave = False
                    elif self.keyboard_key == "click_derecho":
                        command = {"popOut":"close"}
                        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                        self.key.emit()
                        print("key emit")
                        self.model.llave = False
                    #else:
                    #    command = {"popOut":"Mensaje no recibido, gire la llave nuevamente"}
                    #    self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    #    print("AQUI HAY REMOVER EL MENSAJE PARA EVITAR QUE ESTE TODO EL TIEMPO")
                        

                
                    

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

                if "candados_finish" in payload:
                    if payload["candados_finish"] == True:
                        self.model.estado_candados = False
                        #regresa variable que permite escanear otra caja
                        self.model.pdcr_iniciada=False
                    if payload["candados_finish"] == False:
                        self.model.estado_candados = True

                #ejemplo de mensaje:
                #PLC/1/status       {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                #DESDE GDI SERÍA:   {"encoder": 2,"name": "{\"PDC-R\":\"E1\"}","value":true}
                # SI EL MENSAJE MQTT CONTIENE ENCODER, NAME y VALUE...
                if "encoder" in payload and "name" in payload and "value" in payload:

                    #CAMBIAR {"PDC-R":"E1"} por {"PDC-RMID":"E1"} o {"PDC-RS":"E1"} según corresponda
                    if "PDC-R" in payload["name"] and "PDC-RMID" in self.model.input_data["database"]["modularity"]:
                        payload["name"] = payload["name"].replace("PDC-R", "PDC-RMID")
                    if "PDC-R" in payload["name"] and "PDC-RS" in self.model.input_data["database"]["modularity"]:
                        payload["name"] = payload["name"].replace("PDC-R", "PDC-RS")

                    #obtener encoder_1, encoder_2, encoder_3, o encoder_4
                    encoder = "encoder_" + str(payload["encoder"])

                    #si no se encuentra activado el modo de revisión de candados (funcionamiento normal)
                    if self.model.estado_candados == False:
                        print('Para activar candados mandar{"candados_finish":false}')

                        #se obtienen los datos del current_trq
                        current_tool = encoder.replace("encoder_","tool")
                        #si current_trq no está vacío...
                        if self.model.torque_data[current_tool]["current_trq"] != None:
                            caja = self.model.torque_data[current_tool]["current_trq"][0]
                            tuerca = self.model.torque_data[current_tool]["current_trq"][1]
                            
                            #ejemplo de señal: {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                            #ejemplo de caja: "PDC-D"
                            #ejemplo de tuerca: "E1"
                            #si el encoder leído contiene la caja y la tuerca del torque que está en la tarea actual (current_trq)
                            if caja in payload["name"] and tuerca in payload["name"]:

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

                            if self.model.torque_data["tool1"]["current_trq"] != None:
                                caja = self.model.torque_data["tool1"]["current_trq"][0]
                                tuerca = self.model.torque_data["tool1"]["current_trq"][1]
                            
                                #ejemplo de señal: {"encoder":1,"name":{"PDC-D":"E1"},"value":True}
                                #ejemplo de caja: "PDC-D"
                                #ejemplo de tuerca: "E1"
                                if caja in payload["name"] and tuerca in payload["name"]:

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
                    for item in payload:
                        payload[item] = float(payload[item])

                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:

                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        print("torque1 emit()")
                        #se emite la señal de que se hizo un torque con esta herramienta
                        self.torque1.emit()
                    else:
                        print("torque no emit, saliendo de reversa")

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
                    for item in payload:
                        payload[item] = float(payload[item])

                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:

                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        print("torque2 emit()")
                        #se emite la señal de que se hizo un torque con esta herramienta
                        self.torque2.emit()
                    else:
                        print("torque no emit, saliendo de reversa")


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
                    for item in payload:
                        payload[item] = float(payload[item])

                    #si no está bloqueada la señal (por estar transicionando al salir de backward)
                    if self.model.lock_backward[tool] == False:
                        #se copia la información del arreglo recibido del torque por esta herramienta
                        self.model.input_data["torque"][tool] = copy(payload)
                        print("torque3 emit()")
                        #se emite la señal de que se hizo un torque con esta herramienta
                        self.torque3.emit()
                    else:
                        print("torque no emit, saliendo de reversa")
                

            if message.topic == self.model.sub_topics["gui"]:
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
                        
                        if self.model.local_data["user"]["type"] == "CALIDAD" or self.model.local_data["user"]["type"] == "SUPERUSUARIO":

                            if self.mostrar_gdi == True:
                                self.mostrar_gdi = False
                                self.client.publish("GDI",json.dumps({"Esconder":"window"}), qos = 2)
                                print("Escondiendo GDI")
                            elif self.mostrar_gdi == False:
                                self.mostrar_gdi = True
                                self.client.publish("GDI",json.dumps({"Mostrar":"window"}), qos = 2)
                                print("Mostrando GDI")

                if "codeQR" in payload:

                    print("llego un codigo qr")
                    if "CENTERLLAVE" in str(payload):
                        self.key.emit()

                    if "CENTERKEY" in str(payload):

                        print("es una llave del AMTC")

                        # si la variable es True, quiere decir que hubo un mal torqueo y se requiere llave para habilitar la reversa
                        if self.model.reintento_torque == True:
                            #esta llave solo es para proceso
                            print("key_process.emit()")
                            self.key_process.emit()
                        # si la variable es False, quiere decir que estás en otra parte del proceso y la llave reiniciará el ciclo
                        elif self.model.reintento_torque == False:
                            command = {"popOut":"¿Seguro que desea dar llave?\n Presione Esc. para salir, Click Derecho para continuar..."}
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
                if "qr_box" in payload:
                    string_qr_box = str(payload["qr_box"])
                    string_qr_box = string_qr_box.replace(" ","") #se eliminan los espacios de los QRs
                    self.qr_box.emit(string_qr_box)    

        except Exception as ex:
            print("input exception", ex)

    def closePopout (self):
        command = {
            "popOut":"close"
            }
        self.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from manager.model import model
    import sys
    app = QApplication(sys.argv)
    model = model.manager()
    client = mqttClient(model)
    sys.exit(app.exec_())

