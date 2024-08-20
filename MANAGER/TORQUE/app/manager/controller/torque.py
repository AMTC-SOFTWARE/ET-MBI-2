from PyQt5.QtCore import QState, pyqtSignal, QObject, pyqtSlot
from paho.mqtt import publish
from datetime import datetime
from threading import Timer
from time import sleep
from cv2 import imread, imwrite
from copy import copy
import json
import requests
import threading

class Torquing (QState):
    finish  = pyqtSignal()
    reset   = pyqtSignal()
    def __init__(self, model = None):
        super().__init__(QState.ParallelStates)
        self.model = model

        #model.transitions son las señales del cliente .. self.client = MqttClient(self.model, parent = self)

        self.chkReset   = ChkReset(model = self.model, parent = self)
        self.manager    = ToolsManager(model = self.model, parent = self)
        self.tool1      = NewTool1(tool = "tool1", model = self.model, parent = self)
        self.tool2      = NewTool2(tool = "tool2", model = self.model, parent = self)
        self.tool3      = NewTool3(tool = "tool3", model = self.model, parent = self)

        #transición al clampear una caja regresas a clase de ToolsManager
        self.manager.addTransition(self.model.transitions.clamp, self.manager)

        #cada que finalizas una herramienta de todas sus terminales, regresas a clase de ToolsManager
        self.manager.addTransition(self.tool1.finish, self.manager)
        self.manager.addTransition(self.tool2.finish, self.manager)
        self.manager.addTransition(self.tool3.finish, self.manager)

        #señales emitidas por ToolsManager que afectan a los objetos de NewTool
        self.manager.ok1.connect(self.tool1.trigger.emit)
        self.manager.ok2.connect(self.tool2.trigger.emit)
        self.manager.ok3.connect(self.tool3.trigger.emit)

        #señal de finish de que finaliza el ciclo (viene desde la clase ToolsManager)
        self.manager.finish.connect(self.finish.emit)

        #se manda un reset de la clase Torquing, pero no está conectado a nada (NO HACE NADA)
        self.chkReset.reset.connect(self.reset.emit)

    #método clean que (cuando sea llamado) llama al método clean dentro de NewTool para cada objeto de esta clase
    def clean(self):
        self.tool1.clean()
        self.tool2.clean()
        self.tool3.clean()

class NewTool1 (QState):
    finish  = pyqtSignal()
    trigger = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

        self.standby        = QState(parent = self)
        self.zone           = CheckZone(tool = self.tool, model = self.model, parent = self)
        self.chk_response   = CheckResponse(tool = self.tool, model = self.model, parent = self)
        self.NOK            = Error(tool = self.tool, model = self.model, parent = self)
        self.qintervention  = QualityIntervention(tool = self.tool, model = self.model, parent = self)
        self.qgafet         = gafetQuality(tool = self.tool, model = self.model, parent = self)
        self.backward       = Backward(tool = self.tool, model = self.model, parent = self)
        #self.raffi_active   = RaffiActive(tool = self.tool, model = self.model, parent = self)
        self.raffi_key      = RaffiKey(tool = self.tool, model = self.model, parent = self)
        self.raffi_message  = RaffiMessage(tool = self.tool, model = self.model, parent = self)
        self.chk_profile    = CheckProfile(tool = self.tool, model = self.model, parent = self)
        self.holding_time   = HoldingTime(tool = self.tool, model = self.model, parent = self)
        self.activar_tool   = ActivarHerramienta(tool = self.tool, model = self.model, parent = self)
        self.chk_ALARMA     = Check_data_alarm(tool = self.tool, model = self.model, parent = self)

        #si se está en zone y la variable self.model.estado_actual[self.tool] vale "ERRORNOK" se va directamente a ese estado en el que se había quedado
        self.zone.addTransition(self.zone.ERRORNOK, self.NOK)
        #si se está en zone y la variable self.model.estado_actual[self.tool] vale "BACKWARD" se va directamente a ese estado en el que se había quedado
        self.zone.addTransition(self.zone.BACKWARD, self.backward)
        #si se está en zone y la variable self.model.estado_actual[self.tool] vale "QINTERVENTION" se va directamente a ese estado en el que se había quedado
        self.zone.addTransition(self.zone.QINTERVENTION, self.qintervention)
        #si se está en zone y la variable self.model.estado_actual[self.tool] vale "CHECKPROFILE" se va directamente a ese estado en el que se había quedado
        self.zone.addTransition(self.zone.CHECKPROFILE, self.chk_profile)

        #variable para regresar a zone estando en zone, se usa para bypass solamente
        self.zone.addTransition(self.zone.retry_zone, self.zone)

        #si se está en zone y la variable de activación de herramienta está en false para esa tool, se va a un estado holding_time para comenzar un timer
        self.zone.addTransition(self.zone.enable_time, self.holding_time)
        #si se mueve la herramienta estándo en posición de holding_time se cancela el timer, no se activa la herramienta y se vuelve a self.zone
        self.holding_time.addTransition(self.model.transitions.zone_tool1, self.zone)
        #si se cumple el tiempo de holding_time sin sacar la tool de la posición de la zona se manda la señal activar_signal y se va a un estado que habilitará la variable de activación
        self.holding_time.addTransition(self.holding_time.activar_signal, self.activar_tool)
        #en este estado la variable de activación de esta herramienta se hace true y se vuelve a self.zone, donde si es true se habilita la herramienta
        self.activar_tool.addTransition(self.activar_tool.continuar, self.zone)
        #si ya se había habilitado la herramienta y solo se está esperando la respuesta del torque debe poder ir aunque esté en estos estados nuevamete 
        #(esto porque la herramienta al momento de estar torqueando puede salir de la zona una vez que ya fue activada por su movimiento de torqueo y a causa de las zonas en el encoder)
        self.holding_time.addTransition(self.model.transitions.torque1, self.chk_response)
        self.activar_tool.addTransition(self.model.transitions.torque1, self.chk_response)

        #presionar un raffi, te lleva a este estado solo si estás en self.zone
        self.zone.addTransition(self.model.transitions.raffi_on, self.raffi_message)
        #para continúar la operación normal si el raffi que se presionó no afecta a esta herramienta
        self.raffi_message.addTransition(self.raffi_message.process_continue, self.zone)
        #al estar en raffi messsage, y dar llave vas a raffi_key
        self.raffi_message.addTransition(self.model.transitions.key_process, self.raffi_key)
        #para salir de raffi message sin habilitar raffi...
        self.raffi_message.addTransition(self.model.transitions.raffi_off, self.zone)
        #para salir debes deshabilitar el raffi, y vuelves a self.zone
        self.raffi_key.addTransition(self.model.transitions.raffi_off,self.zone)

        #self.trigger emitida por ToolsManager para ir a estado zone
        self.standby.addTransition(self.trigger, self.zone)

        #cuando la zona es nok emitida por zone, vas a standby
        self.zone.addTransition(self.zone.nok, self.standby)

        #la señal de estar sobre una zona te manda al estado zone
        self.zone.addTransition(self.model.transitions.zone_tool1, self.zone)

        #cuando estas en zone y llega el resultado del torque se va a chk_response
        self.zone.addTransition(self.model.transitions.torque1, self.chk_response)

        #cuando se había peridido un torque que llegó y tal vez por ToolManager no se revisó, se manda a chk_response
        self.zone.addTransition(self.zone.chck_response, self.chk_response)

        #al recibir un torque con result OK regresas al estado de zone
        self.chk_response.addTransition(self.chk_response.ok, self.zone)

        #al recibir un torque con result NOK vas al estado de error
        self.chk_response.addTransition(self.chk_response.nok, self.NOK)

        self.NOK.addTransition(self.NOK.reintento, self.backward)
        #al recibir más de ciertos reintentos pedirá acceso de calidad para continuar o cambio de caja
        self.NOK.addTransition(self.NOK.quality, self.qintervention)
        #al dar una llave key_process() (que solo se puede mandar si self.model.reintento_torque = True, vas al estado de reversa
        self.NOK.addTransition(self.model.transitions.key_process, self.backward)

        #al dar una llave key_process() (que solo se puede mandar si self.model.reintento_torque = True, vas al estado de reversa
        self.qintervention.addTransition(self.model.transitions.ID, self.qgafet)
        self.qgafet.addTransition(self.qgafet.ok, self.backward)
        self.qgafet.addTransition(self.qgafet.nok, self.qintervention)


        #si estás en backward llave te lleva a mensaje de backward
        #self.backward.addTransition(self.model.transitions.key_process, self.backward)

        #para que al enviarse una señal de zona de la misma herramienta no te saque de el estado backward, sino que vuelvas a este mismo
        self.backward.addTransition(self.model.transitions.zone_tool1, self.backward)

        #si la señal que llega es torque pero no es torque1_reversa, significa que fue un torque aún con el profile de la tuerca, falta poner en reversa la herramienta
        self.backward.addTransition(self.model.transitions.torque1, self.backward)

        #un torque te saca de la reversa, y regresas a zone
        #self.backward.addTransition(self.model.transitions.torque1, self.zone)
        #self.backward.addTransition(self.model.transitions.torque1, self.chk_profile)
        
        self.backward.addTransition(self.model.transitions.torque1_reversa, self.chk_ALARMA)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.ok, self.chk_profile)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.nok, self.qintervention)
        self.qgafet.addTransition(self.qgafet.ok_alarma, self.chk_profile)


        self.chk_profile.addTransition(self.chk_profile.ok, self.zone)
        self.chk_profile.addTransition(self.chk_profile.retry, self.chk_profile)
        self.chk_profile.addTransition(self.model.transitions.key_process, self.zone)

        #al mandar una señal de finish de la misma clase de NewTool cuando ya no se tienen tareas, se va a standby
        self.addTransition(self.finish, self.standby)

        #se va a la función finished de Newtool al enviarse una señal ok proveniente del estado zone (se conecta la señal ok de zone para entrara a este método "def finished(self)" de Newtool)
        self.zone.ok.connect(self.finished)

        self.setInitialState(self.standby)
    
    # cuando a la clase Torquing le llaman a su método clean para cada objeto (cada herramienta en Newtool) se llama a esta función que limpia estas variables
    def clean(self):
        self.zone.img_name = ""
        self.zone.flex_BB_drawed = False

    def finished(self):
        self.clean()
        self.finish.emit()

class NewTool2 (QState):
    finish          = pyqtSignal()
    trigger         = pyqtSignal()
    triggerPalpador = pyqtSignal()

    def __init__(self, tool = "tool2", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

        self.standby        = QState(parent = self)
        self.zone           = CheckZone(tool = self.tool, model = self.model, parent = self)
        self.chk_response   = CheckResponse(tool = self.tool, model = self.model, parent = self)
        self.NOK            = Error(tool = self.tool, model = self.model, parent = self)
        self.qintervention  = QualityIntervention(tool = self.tool, model = self.model, parent = self)
        self.qgafet         = gafetQuality(tool = self.tool, model = self.model, parent = self)
        self.backward       = Backward(tool = self.tool, model = self.model, parent = self)
        #self.raffi_active   = RaffiActive(tool = self.tool, model = self.model, parent = self)
        self.raffi_key      = RaffiKey(tool = self.tool, model = self.model, parent = self)
        self.raffi_message  = RaffiMessage(tool = self.tool, model = self.model, parent = self)
        self.raffi_key_palpador     = RaffiKey(tool = self.tool, model = self.model, parent = self)
        self.raffi_message_palpador = RaffiMessage(tool = self.tool, model = self.model, parent = self)
        self.chk_profile    = CheckProfile(tool = self.tool, model = self.model, parent = self)
        self.holding_time   = HoldingTime(tool = self.tool, model = self.model, parent = self)
        self.activar_tool   = ActivarHerramienta(tool = self.tool, model = self.model, parent = self)
        self.chk_ALARMA     = Check_data_alarm(tool = self.tool, model = self.model, parent = self)

        self.zone.addTransition(self.zone.ERRORNOK, self.NOK)
        self.zone.addTransition(self.zone.BACKWARD, self.backward)
        self.zone.addTransition(self.zone.QINTERVENTION, self.qintervention)
        self.zone.addTransition(self.zone.CHECKPROFILE, self.chk_profile)
        self.zone.addTransition(self.zone.retry_zone, self.zone)

        self.zone.addTransition(self.zone.enable_time, self.holding_time)
        self.holding_time.addTransition(self.model.transitions.zone_tool2, self.zone)
        self.holding_time.addTransition(self.holding_time.activar_signal, self.activar_tool)
        self.activar_tool.addTransition(self.activar_tool.continuar, self.zone)
        self.holding_time.addTransition(self.model.transitions.torque2, self.chk_response)
        self.activar_tool.addTransition(self.model.transitions.torque2, self.chk_response)
        

        self.zone.addTransition(self.model.transitions.raffi_on, self.raffi_message)
        self.raffi_message.addTransition(self.raffi_message.process_continue, self.zone)
        self.raffi_message.addTransition(self.model.transitions.key_process, self.raffi_key)
        self.raffi_message.addTransition(self.model.transitions.raffi_off, self.zone)
        self.raffi_key.addTransition(self.model.transitions.raffi_off,self.zone)

        self.standby.addTransition(self.trigger, self.zone)
        
        self.zone.addTransition(self.zone.nok, self.standby)
        self.zone.addTransition(self.model.transitions.zone_tool2, self.zone)
        self.zone.addTransition(self.model.transitions.torque2, self.chk_response)
        self.zone.addTransition(self.zone.chck_response, self.chk_response)

        self.chk_response.addTransition(self.chk_response.ok, self.zone)
        #al recibir un torque con result NOK vas al estado de error
        self.chk_response.addTransition(self.chk_response.nok, self.NOK)

        #cuando estás en el estado de la clase error, te manda a el estado de reversa si el reintento es menor al maximo de reintentos permitidos
        self.NOK.addTransition(self.NOK.reintento, self.backward)
        self.NOK.addTransition(self.NOK.quality, self.qintervention)
        #al dar una llave key_process() (que solo se puede mandar si self.model.reintento_torque = True, vas al estado de reversa
        self.NOK.addTransition(self.model.transitions.key_process, self.backward)
        
        self.qintervention.addTransition(self.model.transitions.ID, self.qgafet)
        self.qgafet.addTransition(self.qgafet.ok, self.backward)
        self.qgafet.addTransition(self.qgafet.nok, self.qintervention)

        #self.backward.addTransition(self.model.transitions.key_process, self.backward)
        self.backward.addTransition(self.model.transitions.zone_tool2, self.backward)
        self.backward.addTransition(self.model.transitions.torque2, self.backward)
        #self.backward.addTransition(self.model.transitions.torque2, self.zone)
        #self.backward.addTransition(self.model.transitions.torque2, self.chk_profile)

        self.backward.addTransition(self.model.transitions.torque2_reversa, self.chk_ALARMA)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.ok, self.chk_profile)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.nok, self.qintervention)
        self.qgafet.addTransition(self.qgafet.ok_alarma, self.chk_profile)


        self.chk_profile.addTransition(self.chk_profile.ok, self.zone)
        self.chk_profile.addTransition(self.chk_profile.retry, self.chk_profile)
        self.chk_profile.addTransition(self.model.transitions.key_process, self.zone)

        self.addTransition(self.finish, self.standby)

        self.zone.ok.connect(self.finished)

        self.setInitialState(self.standby)

    def clean(self):
        self.zone.img_name = ""
        self.zone.flex_BB_drawed = False

    def finished(self):
        self.clean()
        self.finish.emit()

class NewTool3 (QState):
    finish      = pyqtSignal()
    trigger     = pyqtSignal()
    goPalpador  = pyqtSignal()

    def __init__(self, tool = "tool3", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

        self.standby                = QState(parent = self)
        self.zone                   = CheckZone(tool = self.tool, model = self.model, parent = self)
        self.chk_response           = CheckResponse(tool = self.tool, model = self.model, parent = self)
        self.NOK                    = Error(tool = self.tool, model = self.model, parent = self)
        self.qintervention          = QualityIntervention(tool = self.tool, model = self.model, parent = self)
        self.qgafet                 = gafetQuality(tool = self.tool, model = self.model, parent = self)
        self.backward               = Backward(tool = self.tool, model = self.model, parent = self)
        #self.raffi_active           = RaffiActive(tool = self.tool, model = self.model, parent = self)
        self.raffi_key              = RaffiKey(tool = self.tool, model = self.model, parent = self)
        self.raffi_message          = RaffiMessage(tool = self.tool, model = self.model, parent = self)
        self.chk_profile            = CheckProfile(tool = self.tool, model = self.model, parent = self)
        
        self.palpador               = Palpador(tool = self.tool, model = self.model, parent = self)
        self.zone_palpador          = CheckZonePalpador(tool = self.tool, model = self.model, parent = self)
        self.delay_pin              = DelayPin(tool = self.tool, model = self.model, parent = self)
        self.waiting_pin            = WaitingPin(tool = self.tool, model = self.model, parent = self)
        self.raffi_key_palpador     = RaffiKey(tool = self.tool, model = self.model, parent = self)
        self.raffi_message_palpador = RaffiMessage(tool = self.tool, model = self.model, parent = self)

        self.holding_time   = HoldingTime(tool = self.tool, model = self.model, parent = self)
        self.activar_tool   = ActivarHerramienta(tool = self.tool, model = self.model, parent = self)
        self.chk_ALARMA     = Check_data_alarm(tool = self.tool, model = self.model, parent = self)
        #SEÑALES PARA REGRESAR A REVERSA DESPUES DE UN CLAMPEO DE OTRA CAJA
        self.zone.addTransition(self.zone.ERRORNOK, self.NOK)
        self.zone.addTransition(self.zone.BACKWARD, self.backward)
        self.zone.addTransition(self.zone.QINTERVENTION, self.qintervention)
        self.zone.addTransition(self.zone.CHECKPROFILE, self.chk_profile)
        self.zone.addTransition(self.zone.retry_zone, self.zone)

        #HOLDING TIME PARA ACTIVAR HERRAMIENTA
        self.zone.addTransition(self.zone.enable_time, self.holding_time)
        self.holding_time.addTransition(self.model.transitions.zone_tool3, self.zone)
        self.holding_time.addTransition(self.holding_time.activar_signal, self.activar_tool)
        self.activar_tool.addTransition(self.activar_tool.continuar, self.zone)
        self.holding_time.addTransition(self.model.transitions.torque3, self.chk_response)
        self.activar_tool.addTransition(self.model.transitions.torque3, self.chk_response)

        #RAFFI EN ZONE
        self.zone.addTransition(self.model.transitions.raffi_on, self.raffi_message)
        self.raffi_message.addTransition(self.raffi_message.process_continue, self.zone)
        self.raffi_message.addTransition(self.model.transitions.key_process, self.raffi_key)
        self.raffi_message.addTransition(self.model.transitions.raffi_off, self.zone)
        self.raffi_key.addTransition(self.model.transitions.raffi_off,self.zone)        

        #FUNCIONAMIENTO PRINCIPALE DE ZONAS Y TORQUES
        self.standby.addTransition(self.trigger, self.zone)
        self.zone.addTransition(self.zone.nok, self.standby)
        self.zone.addTransition(self.model.transitions.zone_tool3, self.zone)
        self.zone.addTransition(self.model.transitions.torque3, self.chk_response)
        self.zone.addTransition(self.zone.chck_response, self.chk_response)
        self.chk_response.addTransition(self.chk_response.ok, self.zone)
        self.chk_response.addTransition(self.chk_response.nok, self.NOK)
        
        #PALPADOR
        self.zone.addTransition(self.zone.chk_candados, self.palpador)
        self.palpador.addTransition(self.palpador.continuar, self.zone_palpador)
        self.zone_palpador.addTransition(self.model.transitions.zone_tool3, self.zone_palpador)
        self.zone_palpador.addTransition(self.model.transitions.zone_tool4, self.zone_palpador)
        self.zone_palpador.addTransition(self.zone_palpador.wait_pin, self.waiting_pin)
        self.waiting_pin.addTransition(self.model.transitions.pin,self.delay_pin)
        self.waiting_pin.addTransition(self.model.transitions.zone_tool3,self.delay_pin)
        self.waiting_pin.addTransition(self.model.transitions.zone_tool4,self.delay_pin)
        self.waiting_pin.addTransition(self.waiting_pin.pin_already_pressed,self.delay_pin)
        self.delay_pin.addTransition(self.delay_pin.continuar,self.zone_palpador)

        #RAFFI EN ZONE_PALPADOR
        self.zone_palpador.addTransition(self.model.transitions.raffi_on, self.raffi_message_palpador)
        self.raffi_message_palpador.addTransition(self.raffi_message_palpador.process_continue, self.zone_palpador)
        self.raffi_message_palpador.addTransition(self.model.transitions.key_process, self.raffi_key_palpador)
        self.raffi_message_palpador.addTransition(self.model.transitions.raffi_off, self.zone_palpador)
        self.raffi_key_palpador.addTransition(self.model.transitions.raffi_off,self.zone_palpador)
        
        self.zone_palpador.addTransition(self.zone_palpador.end,self.zone)
        
        #cuando estás en el estado de la clase error, te manda a el estado de reversa si el reintento es menor al maximo de reintentos permitidos
        self.NOK.addTransition(self.NOK.reintento, self.backward)
        self.NOK.addTransition(self.NOK.quality, self.qintervention)
        self.NOK.addTransition(self.model.transitions.key_process, self.backward)

        #VALIDACION DE 4to INTENTO
        self.qintervention.addTransition(self.model.transitions.ID, self.qgafet)
        self.qgafet.addTransition(self.qgafet.ok, self.backward)
        self.qgafet.addTransition(self.qgafet.nok, self.qintervention)

        #REVERSA DE HERRAMIENTA
        #self.backward.addTransition(self.model.transitions.key_process, self.backward)
        self.backward.addTransition(self.model.transitions.zone_tool3, self.backward)
        self.backward.addTransition(self.model.transitions.torque3, self.backward)
        
        #SALIDA DE LA REVERSA
        #self.backward.addTransition(self.model.transitions.torque3, self.zone)
        #self.backward.addTransition(self.model.transitions.torque3, self.chk_profile)

        self.backward.addTransition(self.model.transitions.torque3_reversa, self.chk_ALARMA)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.ok, self.chk_profile)
        self.chk_ALARMA.addTransition(self.chk_ALARMA.nok, self.qintervention)
        self.qgafet.addTransition(self.qgafet.ok_alarma, self.chk_profile)


        self.chk_profile.addTransition(self.chk_profile.ok, self.zone)
        self.chk_profile.addTransition(self.chk_profile.retry, self.chk_profile)
        self.chk_profile.addTransition(self.model.transitions.key_process, self.zone)

        #CONNECT DE SEÑALES DE FINISH
        self.addTransition(self.finish, self.standby)
        self.zone.ok.connect(self.finished)
        self.zone.chk_candados.connect(self.palpadorTool2)

        self.setInitialState(self.standby)


    def clean(self):
        self.zone.img_name = ""
        self.zone.flex_BB_drawed = False

    def finished(self):
        self.clean()
        self.finish.emit()

    def palpadorTool2(self):
        self.clean()
        self.goPalpador.emit()

class CheckZone (QState):
    ok              = pyqtSignal()
    nok             = pyqtSignal()
    chk_candados    = pyqtSignal()
    enable_time     = pyqtSignal()

    chck_response   = pyqtSignal()
    retry_zone      = pyqtSignal()

    ERRORNOK        = pyqtSignal()
    BACKWARD        = pyqtSignal()
    QINTERVENTION   = pyqtSignal()
    CHECKPROFILE    = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.queue = self.model.torque_data[self.tool]["queue"]
        self.stop = self.model.torque_data[self.tool]["stop_profile"]
        self.backward = self.model.torque_data[self.tool]["backward_profile"] 
        self.delay1 = 0.1
        self.delay2 = 1
        self.delay3 = 0.3
        self.nut= ""
        self.oracle= ""
        self.currentTool= ""
        self.BB = self.model.BB
        self.img_name = ""
        self.start = True
        self.encoder = "encoder_" + self.tool[-1]
        self.flex_BB_drawed = False

    def onEntry(self, event):
        print("entrozone$%%$$$$$$$$$$%%%%%%%%%%%%%%%%%%%%%%%%%%$$$$$$$")
        #zone se inicializa con "0"
        zone = "0"
        
        #si algún clampeo de otra caja o terminar algún otro torque te lleva a ToolsManager y te quita tu actual reversa, se regresa a ese estado
        if self.model.estado_actual[self.tool] == "ERRORNOK":
            self.ERRORNOK.emit()
            return
        elif self.model.estado_actual[self.tool] == "BACKWARD":
            self.BACKWARD.emit()
            return
        elif self.model.estado_actual[self.tool] == "QINTERVENTION":
            self.QINTERVENTION.emit()
            return
        elif self.model.estado_actual[self.tool] == "CHECKPROFILE":
            self.CHECKPROFILE.emit()
            return

        if self.model.asegurar_lectura[self.tool] == True:
            print("señal se había perdido...")
            self.chck_response.emit()
            return

        #se revisa si hay alguna herramienta en reversa, o si está el raffi de la caja actual habilitado
        self.check_key_process_function()

        #en ToolsManager, en onEntry, se llega aquí al haber clampeado una caja nueva, (o cualquier señal que te lleve al estado self.manager)
        #si tiene tareas pendientes para esa herramienta self.model.torque_data[self.tool]["enable"] = True
        #si no se tienen tareas pendientes para esa herramienta, self.model.torque_data[self.tool]["enable"] = False
        #también se hace False cuando NO HAY TAREAS EN COLA PARA ESTA HERRAMIENTA (pero se pueden agregar más)
        #si self.model.torque_data[self.tool]["enable"] = False... entra a este if...
        if not(self.model.torque_data[self.tool]["enable"]):

            self.model.torque_data[self.tool]["rqst"] = False

            #se pone herramienta en stop
            Timer(self.delay1, self.profilePub, args = (self.stop,)).start()

            #se emite un NOK y esto hace que vuelva a esperar una señal del encoder
            Timer(0.05, self.nok.emit).start()

            return

        #################################### REVISAR MENSAJE DE ENCODER PARA LA ZONA ACTIVADA ############################
        #zone inicia valiendo "0"
        try:
            #temp = valor actual guardado de la zona para encoder 
            temp = self.model.input_data["plc"][self.encoder]["zone"] # {"caja": "torque_name"}

            #temp solo vale "0" al iniciar (se inicializa self.model.input_data["plc"][self.encoder]["zone"] = "0")
            #cuando los encoders no han modificado su valor
            if temp != "0":

                #UNA VEZ QUE SE MODIFICA EL VALOR INICIAL DE LOS ENCODERS...

                #guardas el json obtenido de self.model.input_data["plc"][self.encoder]["zone"]
                temp = json.loads(temp)

                #si el mensaje obtenido tiene una longitud (o sea que no es vacío el meensaje)
                if len(temp):
                    #zone toma el valor de la caja  y el torque que se detectó actual con el encoder
                    zone = [list(temp)[0], temp[list(temp)[0]]]  #  ["caja", "torque_name"]
                else:
                    zone = ""
 
        except Exception as ex:
            print (f"CheckZone {self.tool} Exception: ", ex)
            command = {
                "lbl_result" : {"text":f"CheckZone {self.tool} {ex.args}", "color": "red"},
                "lbl_steps" : {"text": "Verificar config. de encoders", "color": "black"}
                }
            #publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            #self.nok.emit()
            return
        #####################################################################################################################
        
        #se da el valor a current_trq de lo que está registrado en torque_data para esa herramienta en "current_trq"
        #si está vacío, obtiene nuevamente un valor desde self.queue[0] si es que aún quedan tareas por hacer
        current_trq = self.model.torque_data[self.tool]["current_trq"]

        print("||||||||||||||||||||||||||||||||||||||||||||||")
        print("self.queueeeeeeeee dentro de zone: ",self.queue)
        print("||||||||||||||||||||||||||||||||||||||||||||||")
        ########################## Funcionmiento Único para MFP1 y MFBP2 con tool3 ###################
        #self.model.current_queue[self.tool].clear()
        #if self.tool == "tool3":    
        #    if len(self.queue):
        #        for tarea in self.queue:

        #            print("Tarea: ",tarea)
        #            print("current zone[0]",zone[0])
        #            #si la zona actual está en la lista de tareas
        #            if zone[0] in tarea:
        #                #se agregan las tareas de queue que hay para esta caja
        #                self.model.current_queue[self.tool].append(tarea)
        #                print("tareas_actuales: ",self.model.current_queue[self.tool])
        #        if len(self.model.current_queue[self.tool]):
        #            print("len of self.model.current_queue[tool3]: ",len(self.model.current_queue[self.tool]))

        #            if zone[0] == "MFB-P1":
        #                print("zone 0 = MFB-P1")
        #                self.model.torque_data[self.tool]["current_trq"] = self.model.current_queue[self.tool][0]
        #                current_trq = self.model.current_queue[self.tool][0]
        #                #se utiliza la 1 primer pantalla
        #                self.model.torque_data[self.tool]["gui"] = self.model.pub_topics["gui"]
        #                #se llama al método draw con argumentos: caja y posición
        #                self.draw([current_trq[0], current_trq[1]])

        #                #se publica en la gui las instrucciones visuales
        #                command = {
        #                    "img_center" : self.tool + ".jpg"
        #                    }
        #                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        #            if zone[0]== "MFB-P2":
        #                print("zone 0 = MFB-P2")
        #                self.model.torque_data[self.tool]["current_trq"] = self.model.current_queue[self.tool][0]
        #                current_trq = self.model.current_queue[self.tool][0]
        #                #se utiliza la gui_2 la segunda pantalla
        #                self.model.torque_data[self.tool]["gui"] = self.model.pub_topics["gui_2"]
        #                #se llama al método draw con argumentos: caja y posición
        #                self.draw([current_trq[0], current_trq[1]])

        #                #se publica en la gui las instrucciones visuales
        #                command = {
        #                    "img_center" : self.tool + ".jpg"
        #                    }
        #                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        ################################################################################################

        #fechha_actual = self.model.get_currentTime()
        #fechha_inicio = datetime(2024,4,18,11,20,0)
        #fechha_fin = datetime(2024,4,19,10,0,0)
        #print("fechha_actual: ", fechha_actual)
        #print("fechha_inicio: ", fechha_inicio)
        #print("fechha_fin: ", fechha_fin)

        fecha_okk = False

        #if (fechha_actual > fechha_inicio and fechha_actual < fechha_fin) or self.model.config_data["sinTorquePDCR"]:
        if self.model.config_data["sinTorquePDCR"]:
            #print("fecha actual mayor que " + str(fechha_inicio) + " y menor que " + str(fechha_fin))
            print("self.model.config_data[sinTorquePDCR]: ", self.model.config_data["sinTorquePDCR"])
            print("valor de self.model.bypass_pdcr: ",self.model.bypass_pdcr)
            print("fecha_okk = True")
            fecha_okk = True

        if fecha_okk == True and self.model.bypass_pdcr != "Finalizado":
            if current_trq != None:
                if "PDC-R" in current_trq[0]:
                    if self.tool == "tool3":

                        #para después quitar la queue
                        self.model.save_box_candados = current_trq[0]
                        self.model.save_current_trq_candados = current_trq[1]
                        #para inicial el modo de revisión de candados
                        self.model.estado_candados = True
                        self.model.bypass_pdcr = "Inicio"

                        print("se emite la señal chk_candados.emit() para bypass PDC-R")
                        self.chk_candados.emit()
                        return
        else:
            #si se habilita el estado_candados porque ya es la última tarea de la caja PDCR entonces se va a finish para mandar la señal de PALPADOR
            if self.model.estado_candados == True:
                if self.tool == "tool3":
                    #variable para cuando entras a zone ir a estado palpador hasta que se haya finalizado
                    if self.model.contains_PDCR == True:
                        print("se emite la señal para palpador")
                        self.chk_candados.emit()
                        return

        #si el valor de current_trq es None (por el momento está vacío) o config_data está en True el flexible_mode
        if current_trq == None or self.model.config_data["flexible_mode"]:

            #si aún hay tareas en cola pendientes por hacer para esa herramienta (falta  torquear cosas)
            if len(self.queue):
                flex_BB_array = []

                #se iguala el current_trq a la tarea en cola (la ultima) con el valor de la caja , terminal, profile, y tuerca !!!!!!!!!!
                #SE ASIGNA LA ULTIMA TAREA DE ESTA HERRAMIENTA EN current_trq!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                current_trq = self.queue[0] # ["PDC-P", "E1", 2, "6mm Nut"]

                #si la herramienta es la 2
                if self.tool == "tool3":
                    #si la caja en la tarea en cola es MFB-P1...
                    if current_trq[0] == "MFB-P2":
                        #se utiliza la gui_2 la segunda pantalla
                        self.model.torque_data[self.tool]["gui"] = self.model.pub_topics["gui_2"]
                    else:
                        #de lo contrario se utiliza la 1 primer pantalla
                        self.model.torque_data[self.tool]["gui"] = self.model.pub_topics["gui"]


                #SI EL MODO ES FLEXIBLE
                if self.model.config_data["flexible_mode"]:
                    #se recorren las tareas en cola para ver si es igual a alguna de las tareas pendientes
                    for i in range(len(self.queue)):
                        if not(self.flex_BB_drawed):
                            #se agrega el bounding box para pintarlo
                            flex_BB_array.append([self.queue[i][0], self.queue[i][1]])

                        #si la caja que marca actualmente el encoder es igual a la caja de la tarea en cola actual...
                        if len(zone) and zone[0] == self.queue[i][0]:

                            #si la terminal actual por el encoder es igual a la terminal de la tarea en cola
                            if zone[1] == self.queue[i][1]:

                                #current trq es igual a esa tarea pendiente de la que es igual la caja y la terminal
                                current_trq = self.queue[i]
                                if self.flex_BB_drawed:
                                    break

                #SE GUARDA EN TORQUE_DATA el current_trq para esa herramienta!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.model.torque_data[self.tool]["current_trq"] = current_trq


                #se guarda valor de la tuerca
                self.nut = current_trq[3]
                #print("Self.Nut: ",self.nut)
                print("Self.Tool: ",self.tool)

                if self.nut == "8mm Nut":
                    self.oracle = "Oracle: 1033977"
                if self.nut == "6mm Nut":
                    self.oracle = "Oracle: 1033978"
                if self.nut == "Battery Nut":
                    self.oracle = "Oracle: 1021441"

                #Para mostrar en pantalla el nombre de la herramienta que está en este estado CheckZone
                if self.tool == "tool1":
                    self.currentTool = "HERRAMIENTA 1"
                if self.tool == "tool3":
                    self.currentTool = "HERRAMIENTA 2"
                if self.tool == "tool2":
                    self.currentTool = "HERRAMIENTA 3"

                if current_trq[0] == "MFB-P1" or current_trq[0] == "MFB-S":
                    #print("Mostrar imagen de 2 herramientas para MFB-P1 y S")
                    self.currentTool = "HERRAMIENTAS 2,3"
                    self.nut    = "8mm Grande - 6mm Chica"
                    self.oracle = "1033977       - 1033978   "

                if current_trq[0] == "MFB-P2":
                    #print("Mostrar imagen de 2 herramientas para MFB-P2")
                    self.currentTool = "HERRAMIENTAS 1,2"
                    self.nut    = "6mm Chica - 8mm Grande"
                    self.oracle = "1033978  - 1033977   "

                #se imprime la herramienta actual activa
                #print("Current Tool: ",self.currentTool)

                #img_name obtiene la dirección de la imagen de la caja para la tarea actual "current_trq"
                img_name = self.model.imgs_path + "boxes/"+ current_trq[0] + ".jpg"


                if self.model.config_data["flexible_mode"]:
                    if not(self.flex_BB_drawed):
                        self.draw(flex_BB_array)
                        self.flex_BB_drawed = True
                else:
                    #se llama al método draw con argumentos: caja y posición
                    self.draw([current_trq[0], current_trq[1]])


                #se publica en la gui las instrucciones visuales
                command = {
                    "lbl_instructions" : {"text": "||Instrucciones||", "color": "black"},
                    "img_nuts" : self.nut + ".jpg",
                    "lbl_nuts" : {"text": self.nut+"\n"+self.oracle, "color": "black"},
                    "img_toolCurrent" : self.currentTool+ ".jpg",
                    "lbl_toolCurrent" : {"text": "USAR "+self.currentTool, "color": "black"},
                    "img_center" : self.tool + ".jpg"
                    }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)


            #SI NO HAY TAREAS EN COLA PARA ESTA HERRAMIENTA (pero se pueden agregar más)
            else:
                #se emite un Finish de NewTool - FINISH!!!!!!!!!!!!!!!!!
                self.finish()
                return

        #############################################################################



        #si el string de zone está vacío: mandar profile a stop
        if not(len(zone)):
            if self.stop != self.model.torque_data[self.tool]["past_trq"]:
                command = {
                            "profile": self.stop
                          }
                print("TOPIC: ",self.pub_topic)
                print("STOP----------",command)
                publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.model.torque_data[self.tool]["past_trq"] = self.stop
            return

        ##si esta variable contiene elementos
        else:

            #se inicia profile como stop
            profile = self.stop
            command = {}

            #si lleva la caja PDC-R en esa queue de tareas, se hace true la variable para enviar la señal que te lleva al estado del palpador en lugar de finish
            if "PDC-R" in current_trq[0]:
                self.model.contains_PDCR = True            

            #print("zone[0] (ACTUAL - CAJA): ",zone[0])
            #print("zone[1] (ACTUAL - ZONA): ",zone[1])

            #print("current_trq[0] (TAREA): ",current_trq[0])
            #print("Valores de los raffi",self.model.raffi)
            #print("Valor actual del raffi para esta caja current_trq[0]: ",self.model.raffi[current_trq[0]])
            print("CUURRETN_TRQ",current_trq[0])
            if current_trq[0] == "PDC-RMID" or current_trq[0] == "PDC-R" or current_trq[0] == "PDC-RS":
                
                command = {
                    "lbl_boxNEW" : {"text": "RETIRE CUALQUIER\nCONTAMINANTE\nEN LOS CANDADOS\nQUE EXISTA", "color": "red"}
                    }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

            #si el raffi no está habilitado (su valor es 0)
            if self.model.raffi[current_trq[0]] == 0:

                #si la caja actual es igual a la solicitada de las tareas en cola...
                if zone[0] == current_trq[0]:   
                   
                    #si la terminal actual es igual a cero... (esto pasa en comm.py cada que llega una zona en "false")
                    if zone[1] == "0":
                        command = {
                            "lbl_result" : {"text":"Herramienta fuera de zona de torque", "color": "red"},
                            "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"},
                            }
                        profile = self.stop

                        #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                        self.check_lock_raffi_function(current_trq[0])

                    #si la terminal actual es igual a la terminal solicitada en la tarea actual en cola
                    elif zone[1] == current_trq[1]:

                        #if (fechha_actual > fechha_inicio and fechha_actual < fechha_fin) or self.model.config_data["sinTorquePDCR"]  cuando esto es true fecha_okk = true
                        if fecha_okk == True and current_trq[0] == "PDC-R":
                            print("avanzando con retry_zone para no habilitar herramienta en bypass")
                            self.retry_zone.emit()
                            return

                        #if caja == "PDC-P" or caja == "PDC-D":
                        #if caja == "BATTERY" or caja == "BATTERY-2":
                        #if (self.model.altura_zone[self.tool] == False) and (self.tool == "tool3") and (current_trq[0] == "MFB-P2"):
                        #if (self.model.altura_zone[self.tool] == False) and (self.tool == "tool3"):

                        condicion_tool1 = False
                        condicion_tool2 = False
                        condicion_tool3 = False

                        if (self.tool == "tool1") and (self.model.altura_zone[self.tool] == False) and (current_trq[0] != "PDC-P") and (current_trq[0] != "PDC-D"):
                            condicion_tool1 = True
                        if (self.tool == "tool2") and (self.model.altura_zone[self.tool] == False) and (current_trq[0] != "BATTERY") and (current_trq[0] != "BATTERY-2"):
                            condicion_tool2 = True
                        if (self.tool == "tool3") and (self.model.altura_zone[self.tool] == False) and (current_trq[0] != "PDC-R") and (current_trq[0] != "PDC-RMID") and (current_trq[0] != "PDC-RS"):
                            condicion_tool3 = True

                        if (condicion_tool1 or condicion_tool2 or condicion_tool3):
                            command = {
                                "lbl_result" : {"text":"Herramienta Altura Incorrecta", "color": "red"},
                                "lbl_steps" : {"text": "Mueve la herramienta a " + current_trq[0] + ": " + current_trq[1], "color": "red"}
                                }
                            profile = self.stop
                        
                            #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                            self.check_lock_raffi_function(current_trq[0])

                        else:
                            
                            if self.model.herramienta_bloqueada[self.tool]==True:
                                tool_desbloqueada = self.tool+"_desbloqueada"
                                publish.single(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}),hostname='127.0.0.1', qos = 2)
                                print("se hizo false")
                                sleep(0.4)
                                publish.single(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : True}),hostname='127.0.0.1', qos = 2)

                            #if (current_trq[1] == "A21" or current_trq[1] == "A22" or current_trq[1] == "A23" or current_trq[1] == "A24" or current_trq[1] == "A20" or current_trq[1] == "A25" or current_trq[1] == "A30") and self.model.activar_tool[self.tool] == False:
                            if self.model.activar_tool[self.tool] == False: #se debe mantener para todas las cavidades
                                print("se debe mantener la herramienta un tiempo en la zona para habilitarla")
                                command = {
                                    "lbl_result" : {"text": "Herramienta en " + zone[0] + ": " + zone[1], "color": "darkorange"},
                                    "lbl_steps" : {"text": "Mantenga en posición para activar...", "color": "navy"}
                                    }
                                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                print("enable_time emit")
                                self.enable_time.emit()
                                return
                            else:
                                
                                self.model.activar_tool[self.tool] = False #una vez habilitada, deshabilitar esto en la variable de modelo
                                print("tool: ",self.tool)
                                print("self.model.activar_tool[self.tool]: ",self.model.activar_tool[self.tool])

                                self.model.torque_data[self.tool]["rqst"] = True
                                command = {
                                    "lbl_result" : {"text": "Herramienta en " + zone[0] + ": " + zone[1], "color": "green"},
                                    "lbl_steps" : {"text": "Herramienta activada", "color": "black"}
                                    }
                                #se da a profile el valor del profile en cola solicitado para esa caja y esa terminal !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                profile = current_trq[2]
                                print("zone[1] (ACTUAL - ZONA): ",zone[1])
                                print("HERRAMIENTA ACTIVADA**********: ",self.tool)

                                #se bloquea el uso de este raffi
                                self.model.active_lock[current_trq[0]] = True
                                #se indica que la herramienta actual está bloqueando el raffi porque está activa
                                self.model.active_lock_tool[self.tool] = True

                                if self.model.config_data["untwist"]:
                                    profile = self.model.torque_data[self.tool]["backward_profile"]
                                self.model.torque_data[self.tool]["current_trq"] = current_trq

                    #si la terminal actual es diferente de cero y de la solicitada...
                    else:
                        command = {
                            "lbl_result" : {"text":"Herramienta en " + zone[0] + ": " + zone[1], "color": "red"},
                            "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"}
                            }
                        profile = self.stop
                        
                        #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                        self.check_lock_raffi_function(current_trq[0])

                #si la caja actual es diferente de la caja solicitada de las tareas en cola...
                else:
                    print("CUURRETN_TRQ",current_trq[0])
                    command = {
                        "lbl_result" : {"text":"Herramienta fuera de zona de torque", "color": "red"},
                        "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"},
                        }
                    profile = self.stop
                    
                    #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                    self.check_lock_raffi_function(current_trq[0])

            #si el raffi está habilitado (su valor es 1)
            elif self.model.raffi[current_trq[0]] == 1:
                command = {
                        "lbl_result" : {"text":"Raffi de caja "+ current_trq[0] +" Habilitado", "color": "red"},
                        "lbl_steps" : {"text": "Para continuar deshabilitar Raffi", "color": "black"}
                        }
                profile = self.stop
          
        #se guarda el valor del perfil que se quiera configurar en la herramienta: ya sea un perfil o un stop etc.
        self.model.torque_bin[self.tool]["send_profile"] = profile
        #finalmente haces un publish del mensaje y le mandas el profile a la herramienta (siempre y cuando sea diferente del profile anterior)
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(self.delay1, self.profilePub, args = (profile,)).start()

    def draw(self, BB):
        box = self.model.torque_data[self.tool]["current_trq"][0]
        self.model.imgs[box] = self.model.drawBB(
            img = self.model.imgs[box], BB = BB, color = (31, 186, 226))
        imwrite(self.model.imgs_path + self.tool + ".jpg", self.model.imgs[box])

    def check_lock_raffi_function(self, current_box):

        #print("check lock raffi function")
        print("currentbox: ",current_box)

        #se dehabilita el bloqueo de raffi para esta herramienta porque no está activa (tiene profile:stop)****
        self.model.active_lock_tool[self.tool] = False

        #se inicializa como False
        check_raffi_lock = False

        #se revisa si esta caja está en las tareas pendientes para cada herramienta
        #si alguna se usa en esta caja y su variable active_lock_tool es true, check_raffi_lock será true
        ###################################################################################
        if self.model.torque_data["tool1"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool1"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool1")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool1"] == True:
                    check_raffi_lock = True

        if self.model.torque_data["tool2"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool2"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool2")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool2"] == True:
                    check_raffi_lock = True

        if self.model.torque_data["tool3"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool3"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool3")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool3"] == True:
                    check_raffi_lock = True
        ###################################################################################

        #si ninguna tool de las que lleva esta caja, tiene habilitado su bloqueo de raffi (ninguna de las que lleva la caja está activa), entonces:
        if check_raffi_lock == False:
            #se hace false esta variable, para que se pueda volver a usar el raffi
            self.model.active_lock[current_box] = False
            #print("self.model.active_lock[",current_box,"] = False")

    def check_key_process_function (self):
        
        #se inicializa como False
        check_key_lock = False

        if self.model.backward_key_tool["tool1"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["tool2"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["tool3"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["raffi"] == True:
            check_key_lock = True

        if check_key_lock == False:
            #se hace false para permitir que aparezca el mensaje de confirmación de llave, solo si todas las herramientas NO están en reversa y no hay un raffi habilitado
            self.model.reintento_torque = False
            print("self.model.reintento_torque = False (todas las herramientas terminaron sus reversas y no hay raffi habilitado")

    def profilePub (self, profile):
        if profile != self.model.torque_data[self.tool]["past_trq"]:
            command = {
                        "profile": profile
                      }
            print("TOPIC: ",self.pub_topic)
            print("PROFILE--------",command)
            publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.model.torque_data[self.tool]["past_trq"] = profile

    def finish(self):
        command = {
            "lbl_instructions" : {"text": "", "color": "black"},
            "lbl_nuts" : {"text":"", "color": "black"},
            "lbl_toolCurrent" : {"text":"", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "img_toolCurrent" : "blanco.jpg",
            "lbl_result" : {"text": f"Torques {self.tool} aplicados correctamente", "color": "green"},
            "lbl_steps" : {"text": f"{self.tool} OK", "color": "black"}
            }
        #publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(self.delay1, self.profilePub, args = (self.stop,)).start()
        self.model.torque_data[self.tool]["enable"] = False

        #
        print("se emite finish de queue de caja")
        Timer(self.delay2, self.ok.emit).start()

class HoldingTime (QState):

    activar_signal    = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

    def onEntry(self, event):
        print("||||Dentro de Estado HoldingTime, tool: ",self.tool)

        #se manda señal para activar herramienta después de cierto tiempo
        self.model.tiempo[self.tool] = threading.Timer(1.0,self.activar_signal.emit)
        self.model.tiempo[self.tool].start()

    def onExit(self, event):
        print("||||||||||||||||||||||Saliendo de HoldingTime")
        print("tool: ",self.tool)
        print("self.model.tiempo[self.tool].cancel()")
        self.model.tiempo[self.tool].cancel()

class ActivarHerramienta (QState):

    continuar    = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

    def onEntry(self, event):
        print("||||Dentro de Estado ActivarHerramienta, tool: ",self.tool)

        self.model.activar_tool[self.tool] = True #variable para habilitar tool después de estar cierto tiempo en zona
        print("self.model.activar_tool: ",self.model.activar_tool)
        self.continuar.emit()

    def onExit(self, event):
        print("||||||||||||||||||||||Saliendo de ActivarHerramienta")

class CheckResponse (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()
    
    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.stop = self.model.torque_data[self.tool]["stop_profile"]
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.delay1 = 0.15
        self.delay2 = 1
        self.BB = self.model.BB
        self.queue = self.model.torque_data[self.tool]["queue"]

    def onEntry(self, event):
        print("chkresponse°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
        try:

            #variable para asegurar que se tomó en cuenta la respuesta de la herramienta
            if self.model.asegurar_lectura[self.tool] == True:
                print("se regresa asegurar_lectura a False: ",self.tool)
                self.model.asegurar_lectura[self.tool] = False

            if self.model.torque_data[self.tool]["rqst"] == False or self.model.input_data["torque"][self.tool] == {}:
                print("NO SE REVISA EL TORQUE PORQUE self.model.input_data[torque][self.tool] == {} o porque self.model.torque_data[self.tool][rqst] == False")
                self.ok.emit()
                return
            else:
                self.model.torque_data[self.tool]["rqst"] = False
                print("TOPIC: ",self.pub_topic)
                print("STOP--------\n profile: ",self.stop)

                publish.single(self.pub_topic,json.dumps({"profile": self.stop}),hostname='127.0.0.1', qos = 2)
                self.model.torque_data[self.tool]["past_trq"] = self.stop
                response = copy(self.model.input_data["torque"][self.tool])
                self.model.input_data["torque"][self.tool].clear()
                current_trq = self.model.torque_data[self.tool]["current_trq"]
                box = current_trq[0]
                #print("AQUI ESTÁ LA CAJA: ",box)
                self.model.tries[box][current_trq[1]] += 1
                
                if "2" in self.tool:
                    info1 = self.model.local_data["lbl_info1.2_text"]
                else:
                    info1 = self.model.local_data["lbl_info1_text"]

                if "torque_min" in response:
                    response["torque_min"] = round(response["torque_min"],2)
                else:
                    response["torque_min"] = 0.00

                print("response[torque]: ",response["torque"])
                #print("Tipo de dato response[torque]: ", type(response["torque"]))
                response["torque"] = "%.2f" % response["torque"]
                response["torque"] = float(response["torque"])
                #print("Tipo de dato Final a base de datos: ", type(response["torque"]))

                if "torque_max" in response:
                    response["torque_max"] = round(response["torque_max"],2)
                else:
                    response["torque_max"] = 0.00

                if "angle_min" in response:
                    response["angle_min"] = int(response["angle_min"])
                else:
                    response["angle_min"] = 0.00
                response["angle"] = round(response["angle"],2)
                if "angle_max" in response :
                    response["angle_max"] = int(response["angle_max"])
                else:
                    response["angle_max"] = 0.00

                trq_zone = box + ":" +  current_trq[1]
                trq_min = str(response["torque_min"])
                trq_applied = str(response["torque"]) + "Nm"
                trq_max = str(response["torque_max"])

                angle_min = str(response["angle_min"])
                angle_applied = str(response["angle"]) + "°"
                angle_max = str(response["angle_max"])

                trq_range = trq_min + "<" + trq_applied + "<" + trq_max
                angle_range = angle_min + "<" + angle_applied + "<" + angle_max

                info2 = trq_zone + "\n"
                info2 += "(" + trq_range + ")\n"
                info2 += "(" + angle_range +")"

                print("resultado::::::::::::::::: ",response["result"])

                resultado = "Malo"
                if response["result"] == 1:
                    tolerancia = 8
                    if self.tool == "tool3":
                        tolerancia = 16.0
                    if box == "BATTERY" or box == "BATTERY-2":
                        tolerancia = 6.5
                    tol_min = tolerancia - (10*tolerancia)/100
                    tol_max = tolerancia + (10*tolerancia)/100

                    print("tolerancia mínima: ",tol_min)
                    print("tolerancia máxima: ",tol_max)
                    print("resultado de torque: ",response["torque"])
                    if tol_min < response["torque"] and response["torque"] < tol_max:
                        resultado = "Bueno"

                print("resultado: ",resultado)
                #se reinicia variable de posición ok en zona de altura para esta herramienta 
                #después de un Torque ya sea OK o NOK
                if self.model.config_data["deshabilitar_altura"][self.tool] == False:
                    self.model.altura_zone[self.tool] = False
                    
                #Si el resultado del torque es correcto (OK) o está en modo reversa
                if resultado == "Bueno"  or self.model.config_data["untwist"]:
                    
                    
                    self.model.imgs[box] = self.model.drawBB(
                    img = self.model.imgs[box], BB =[box, current_trq[1]] , color = (0, 255, 0))
                    imwrite(self.model.imgs_path + self.tool + ".jpg", self.model.imgs[box])
                    #info1 += trq_zone + " ["+ trq_applied + "]\n"

                    command = {
                        #"lbl_info1" : {"text": info1, "color": "black"},
                        "lbl_info1" : {"text": info2, "color": "green"},
                        "lbl_result" : {"text": "Torque " + trq_zone + " OK", "color": "green"},
                        "lbl_steps" : {"text": "", "color": "black"},
                        "img_center" : self.tool + ".jpg"
                        }
                    publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                    self.model.result[box][current_trq[1]] = response["torque"]
                    self.model.resultAngle[box][current_trq[1]] = response["angle"]

                    if "2" in self.tool:
                        self.model.local_data["lbl_info1.2_text"] = info1
                    else:
                        self.model.local_data["lbl_info1_text"] = info1


                    #si la tarea que se realiza es la última de la caja PDCR
                    if len(self.queue) == 1:

                        if "PDC-R" in box:
                            print("||||||||||La caja Torqueada es una PDC-R: ",box)

                            print("QUEUEEEEEE:\n",self.queue)
                            print("BOXXXXXXXX: ",box)
                            print("current_trq[1]: ",current_trq[1])

                            #para después quitar la queue
                            self.model.save_box_candados = box
                            self.model.save_current_trq_candados = current_trq[1]
                            #para inicial el modo de revisión de candados
                            self.model.estado_candados = True
                        else:
                            self.remove_task(box, current_trq)
                    else:
                        self.remove_task(box, current_trq)

                    #se reinicia variable de posición OK en zona de altura para esta herramienta, después de un Torque OK
                    self.model.altura_zone[self.tool] = False

                    print("Torque OK!!!!!!!!!!!!")
                    #tiempo para mostrar en pantalla que se torqueó correctamente (se regresa al estado zone y si no hay más tareas para la herramienta se finaliza con un ok.emit() el estado zone)
                    Timer(self.delay2, self.ok.emit).start()

                #Si el resultado del torque no es correcto (NOK)
                else:
                    #imprime la imagen del cuadro en color rojo en la imagen de la caja
                    self.model.imgs[box] = self.model.drawBB(
                    img = self.model.imgs[box], BB =[box, current_trq[1]] , color = (0, 0, 255))
                    imwrite(self.model.imgs_path + self.tool + ".jpg", self.model.imgs[box])
                    #
                    command = {
                        "lbl_info1" : {"text": info2, "color": "red"},
                        "lbl_result" : {"text": "Torque " + trq_zone + " NOK", "color": "red"},
                        "lbl_steps" : {"text": "", "color": "black"},
                        "img_center" : self.tool + ".jpg",
                        }
                    publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                    #Aumenta el contador current_trq[1] en la caja actual
                    if self.model.tries[box][current_trq[1]] % 1 == 0:
                        if box in self.model.local_data["nuts_scrap"]:
                            if current_trq[1] in self.model.local_data["nuts_scrap"][box]:
                                self.model.local_data["nuts_scrap"][box][current_trq[1]] += 1
                            else:
                                self.model.local_data["nuts_scrap"][box][current_trq[1]] = 1
                        else:
                            self.model.local_data["nuts_scrap"][box] = {current_trq[1]: 1}

                    print("Torque NOK!!!!!!!!!!!!!!!!!!!!!")
                    Timer(self.delay1, self.nok.emit).start()

        except Exception as ex:
            print("Torque.CheckResponse() Exception:\n", ex)

    def remove_task(self, box, current_trq):

        modularity = self.model.input_data["database"]["modularity"]
        #se quita la tarea actual de modularity (la colección completa del arnés) una vez que ya se realizó correctamente
        modularity[box].pop(modularity[box].index(current_trq[1]))

        #se hace el pop de la tarea de la herramienta una vez que se realizó correctamente
        for i in range(len(self.queue)):
            if box == self.queue[i][0]:
                if current_trq[1] == self.queue[i][1]:
                    self.queue.pop(i)
                    break

        #si la caja ya no tiene terminales por torquear, se quita la caja de la colección y se libera la caja 
        if not(len(modularity[box])):
            modularity.pop(box)
            self.releaseTorqueClamp(box)
            #Timer(1, self.releaseTorqueClamp, args = (box,)).start()

        self.model.torque_data[self.tool]["current_trq"]  = None
        #se vuelve a habilitar la opción de activar el raffi de esa caja
        self.model.active_lock[box] = False
        self.model.active_lock_tool[self.tool] = False

    def releaseTorqueClamp (self, box):
        #aquí se liberan las cajas desúes de haber finalizado con alguna
        command = {
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts"  : {"text": "", "color": "black"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "img_center" : "logo.jpg"
            }
        if box in self.model.boxPos1:
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        if box in self.model.boxPos2:
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        print("Caja DESCLAMPEADA: ",box)
        if box == "PDC-RS":
            publish.single(self.model.pub_topics["plc"],json.dumps({"PDC-RMID" : False}),hostname='127.0.0.1', qos = 2)


        elif box == "MFB-S":
            if self.model.cajas_habilitadas["BATTERY-2"] == 3 or self.model.cajas_habilitadas["BATTERY-2"] == 0:
                print("La BT2 Ya se torqueó por lo que ambas cajas se liberan")
                publish.single(self.model.pub_topics["plc"],json.dumps({"BATTERY-2" : False, "MFB-S": False}),hostname='127.0.0.1', qos = 2)
            else:
                print("La BT2 aún no se ha torqueado por lo que no se puede liberar esta caja")
                command = {
                    "lbl_nuts" : {"text": "Para liberar la MFB-S\n es necesario completar:", "color": "red"},
                    "img_toolCurrent" : "boxpendiente2.jpg",
                    "lbl_toolCurrent" : {"text": "BATTERY-2", "color": "red"},
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        elif box == "BATTERY-2":

            if self.model.cajas_habilitadas["MFB-S"] == 3 or self.model.cajas_habilitadas["MFB-S"] == 0:
                print("La MFB-S Ya se torqueó por lo que ambas cajas se liberan")
                publish.single(self.model.pub_topics["plc"],json.dumps({"BATTERY-2" : False, "MFB-S": False}),hostname='127.0.0.1', qos = 2)
            else:
                print("La MFB-S aún no se ha torqueado por lo que no se puede liberar esta caja")
                print("directorio: ",self.model.imgs_path)
                print("directorio2: ",self.tool)
                command = {
                    "lbl_nuts" : {"text": "Para liberar la BATTERY-2\n es necesario completar:", "color": "red"},
                    "img_toolCurrent" : "boxpendiente1.jpg",
                    "lbl_toolCurrent" : {"text": "MFB-S", "color": "red"},
                    }

                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            
        else:            
            publish.single(self.model.pub_topics["plc"],json.dumps({box : False}),hostname='127.0.0.1', qos = 2)
        
        copy_box = box
        #caja adecuada:
        if "PDC-R" in box:
            if self.model.smallflag == True:
                copy_box = "PDC-RMID"
            if self.model.mediumflag == True:
                copy_box = "PDC-RMID"
            elif self.model.largeflag == True:
                copy_box = "PDC-R"
        #se avisa a la variable de cajas_habilitadas que ya se terminó esa caja
        self.model.cajas_habilitadas[copy_box] = 3
        print("|||||self.model.cajas_habilitadas: ",self.model.cajas_habilitadas)

class Check_data_alarm (QState):

    ok = pyqtSignal()
    nok=pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.stop = self.model.torque_data[self.tool]["stop_profile"]

    def onEntry(self, event):
        print("ESTADO ACTUAL Check_data_alarm")
        print("herramienta que entró a Check_data_alarm: ",self.tool)
        #si la inspección de alarma está habilitada desde la configuración...
        if self.model.config_data["checkAlarma"]==True:
            caja = self.model.torque_data[self.tool]["current_trq"][0]
            tuerca = self.model.torque_data[self.tool]["current_trq"][1]
            if caja == "MFB-P1" or caja == "MFB-P2" or caja == "MFB-S" or caja == "MFB-E":

                #Primeras tuercas de cada caja
                #MFB-S:  A51 8mm, A53 6mm
                #MFB-P1: A41 8mm, A42 6mm, | A46 8mm, A43 6mm
                #MFB-P2: A20 8mm, A29 6mm, | A24 6mm
                activar_alarma=False
                if tuerca != "A20" and tuerca != "A29" and tuerca != "A41" and tuerca != "A42" and tuerca != "A51" and tuerca != "A53": #and tuerca != "A43" and tuerca != "A46" and tuerca != "A24":
                    activar_alarma=self.consulta_eval_datos(self.tool)
                if activar_alarma:
                    fecha_actual = self.model.get_currentTime()
                    self.model.alarma_caja_tuerca=str(caja)+","+str(tuerca)
                    command = {
                        "info":self.model.qr_codes["HM"]+" "+str(fecha_actual.strftime("%Y/%m/%d %H:%M:%S")) + "-ALARMA"#+"-"+str(self.model.alarma_caja_tuerca)+str(fecha_actual.strftime("%Y/%m/%d %H:%M:%S"))
                        
                    }
                    publish.single(self.model.sub_topics["supervision"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    command = {
                        "save":"true"
                    }
                    publish.single(self.model.sub_topics["supervision"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.model.alarma_activada=True
                    print("ALARMA: activada!!")
                    self.model.ultima_imagen=self.tool
                    command = {
                        "lbl_boxTITLE" : {"text": "ALARMA TUERCA \n FALTANTE", "color": "red"},
                        "img_center" : "TuercaFaltante.jpg",
                        "alarma_emergencia": True
                        }
                    publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.pub_topic = self.model.pub_topics["torque"]["tool1"]
                    self.stop = self.model.torque_data["tool1"]["stop_profile"]
                    publish.single(self.pub_topic,json.dumps({"profile": self.stop}),hostname='127.0.0.1', qos = 2)

                    self.pub_topic = self.model.pub_topics["torque"]["tool2"]
                    self.stop = self.model.torque_data["tool2"]["stop_profile"]
                    publish.single(self.pub_topic,json.dumps({"profile": self.stop}),hostname='127.0.0.1', qos = 2)

                    self.pub_topic = self.model.pub_topics["torque"]["tool3"]
                    self.stop = self.model.torque_data["tool3"]["stop_profile"]
                    publish.single(self.pub_topic,json.dumps({"profile": self.stop}),hostname='127.0.0.1', qos = 2)
                    self.model.alarma_emergencia=True
                    self.nok.emit()

                else:
                    print("ALARMA: no se cumplen las condiciones para alarma")
                    self.ok.emit() #se trata de una primer tuerca de caja
            else:
                print("ALARMA: se trata de una caja con tuerca única")
                self.ok.emit() #se trata de una caja con tuerca única
            
        else:
            print("ALARMA: no está activada la alarma")
            self.ok.emit() #no está activada la alarma

    def onExit(self, event):
        print("Saliendo de Estado: Check_data_alarm")

    def consulta_eval_datos(self,tool):
        activar_alarma=False
        Fase1=False
        torque_alto=False
        torque_alto_reversa=False
        torque_alto_fase=False
        try:
            query="SELECT * FROM et_mbi_2.torque_info where HERRAMIENTA='"+tool+"' order by ID desc LIMIT 2;"""
            #query="SELECT INICIO, FIN FROM et_mbi_2.historial WHERE RESULTADO = 1 order by ID desc LIMIT 1;"
            endpoint = "http://{}/query/get/{}".format(self.model.server, query)
            resp_ultimos_torques = requests.get(endpoint).json()
            print("resp_ultimos_torques",resp_ultimos_torques)
            print("tool ",tool)
            if tool=="tool1":
                self.model.fase_torque=self.model.fase_torque_tool1
                self.model.reversa_torque=self.model.reversa_torque_tool1
            elif tool=="tool2":
                self.model.fase_torque=self.model.fase_torque_tool2
                self.model.reversa_torque=self.model.reversa_torque_tool2
            elif tool=="tool3":
                self.model.fase_torque=self.model.fase_torque_tool3
                self.model.reversa_torque=self.model.reversa_torque_tool3
            #Recopilar info de la reversa
            torque_final_reversa=resp_ultimos_torques["torque_final"][0]
            angulo_final_reveresa=resp_ultimos_torques["angulo_final"][0]

            #recopilar info de el torque anterior a la reversa
            angulo_minimo_torque=resp_ultimos_torques["angulo_minimo"][1]
            angulo_maximo_torque=resp_ultimos_torques["angulo_maximo"][1]
            torque_final_fase=resp_ultimos_torques["torque_final"][1]
            angulo_final_fase=resp_ultimos_torques["angulo_final"][1]
            
            HM_reversa=resp_ultimos_torques["HM"][0]
            HM_Fase=resp_ultimos_torques["HM"][1]
            #si los HM de los registros pertenecen al HM actual va a hacer la evaluacion, si no, la alarma no va a saltar
            if HM_reversa == HM_Fase and HM_Fase==self.model.qr_codes["HM"]:
                
                print("vamos a evaluar")
                if angulo_minimo_torque >= self.model.angulo_min_torq_down and angulo_minimo_torque <= self.model.angulo_min_torq_up: 
                    print("angulo minimo ok")
                    if angulo_maximo_torque >= self.model.angulo_max_torq_down and angulo_maximo_torque <= self.model.angulo_max_torq_up:
                        if resp_ultimos_torques["estado_actual"][1] != "BACKWARD":
                            Fase1=True
                        else:
                            print("doble registro en reversa, uno con profile aún activado")
                            Fase1=False
                    else:
                        Fase1=False
                        
                else:
                    Fase1=False
                #Solo si es fase 1 va a evaluar
                if Fase1==True:
                    if torque_final_fase >= self.model.fase_torque:
                        torque_alto_fase=True


                    if torque_final_reversa >= self.model.reversa_torque:
                        torque_alto_reversa=True

                    #Si hay un torque alto en la reversa y el anterior fue fase1, entonces enciende la alarma
                    if torque_alto_reversa==True: #and torque_alto_fase==False:
                        activar_alarma=True
                        
                    else:
                        activar_alarma=False
                        print("no hubo torque alto en la reversa o si hubo torque alto en la fase1")
                else:
                    activar_alarma=False
                    print("No es FASE1")
                
            else:
                activar_alarma=False
                
                print("HM no son los mismos")
        except Exception as ex:
            print("consulta datos torque info request exception: ", ex)
        return activar_alarma
    
class Error (QState):

    quality = pyqtSignal()
    reintento=pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

    def onEntry(self, event):
        print("ESTADO ACTUAL ERROR NOK")
        print("herramienta que entró a error: ",self.tool)

        self.model.estado_actual[self.tool] = "ERRORNOK" #se guarda el estado actual de esta tool

        current_trq = self.model.torque_data[self.tool]["current_trq"]
        box = current_trq[0]

        #################################
        print("self.model.reintento_torque = True")
        self.model.reintento_torque = True
        print("se hace true para no pedir el enter de la llave y así solo poder emitir la señal key_process() en lugar de key()")
        #para evitar que reintento_torque se haga true, hasta haber recibido un result de torque en reversa de cada herramienta que esté en reversa
        self.model.backward_key_tool[self.tool] = True
        #################################

        #si tiene menos de 2 reintentos, se habilita en automático la reversa sin necesidad de autorización
        if self.model.tries[box][current_trq[1]] <= 2:
            if self.model.tries[box][current_trq[1]] == 1:
                command = {
                        "show":{"img_popOut": "scrap.jpg"},
                        "lbl_steps" : {"text": "Mover Herramienta para continuar", "color": "black"},
                        "lbl_result" : {"text": "Reintento 1/2", "color": "red"}
                        }
            if self.model.tries[box][current_trq[1]] == 2:
                command = {
                        "show":{"img_popOut": "scrap.jpg"},
                        "lbl_steps" : {"text": "Mover Herramienta para continuar", "color": "black"},
                        "lbl_result" : {"text": "Reintento 2/2", "color": "red"}
                        }
            
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            print("reintento emit")
            Timer(3, self.reintento.emit).start()
            return
        #A los 4 reintentos emite el emit de calidad para mostrar el pop de calidad
        elif self.model.tries[box][current_trq[1]] == 5:
            print("||||||||5 REINTENTOS EN UNA POSICIÓN, CAMBIAR CAJA")
            #se emite la señal de que se requiere la intervención de Calidad para decidir si cancelar la pieza o continuar (quality)
            Timer(0.15, self.quality.emit).start()
            return
        #Si no son los 4 reintentos entonces emite el pop del cambio de tuerca
        else:           
            command = {
                "show":{"img_popOut": "scrap.jpg"},
                "lbl_steps" : {"text": "Gira la llave para reintentar", "color": "black"}
                }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            command = {
                "lineEditKey_focus":True #line edit de "QR Key"
                }
            #solo existe en gui, no en gui_2
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            #se espera la señal de la llave
            return

    def onExit(self, event):
        print("Saliendo de Estado: NOK")

        command = {
            "show":{"img_popOut": "close"}
            }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        command = {
            "lineEdit_focus":True #line edit de "Fuse boxes QR"
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2) #solo existe en gui, no en gui_2

class QualityIntervention (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

    def onEntry(self, event):
        #la variable contiene todas las cajas que se han clampeado hasta ese momento
        print("||||| En estado de QualityIntervention")

        self.model.estado_actual[self.tool] = "QINTERVENTION" #se guarda el estado actual de esta tool

        clamps = self.model.input_data["plc"]["clamps"]
        print("Clamps hasta el momento: ",clamps)

        #################################
        if self.model.alarma_activada==True:
            command = {
                "lbl_result" : {"text": f"Alarma Tuerca faltante en: "+self.model.alarma_caja_tuerca, "color": "red"},
                "lbl_steps" : {"text": "Se requiere intervención de Calidad\nIntroduzca gafete de CALIDAD para continuar", "color": "black", "font": "22pt"}
                }

            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        else:
            command = {
                "lbl_result" : {"text": "Demasiados reintentos en la misma posición", "color": "red"},
                "lbl_steps" : {"text": "Se requiere intervención de Calidad\nIntroduzca gafete de CALIDAD para continuar", "color": "black", "font": "22pt"}
                }

            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command = {
            "show":{"login": True},
            "allow_close": False,
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command = {
            "DISABLE_PDC-R":True,
            "DISABLE_PDC-RMID":True,
            "DISABLE_MFB-S":True,
            "DISABLE_MFB-P1":True,
            "DISABLE_MFB-P2":True,
            "DISABLE_PDC-P":True,
            "DISABLE_PDC-D":True,
            "DISABLE_MFB-E":True,
            "DISABLE_BATTERY":True,
            "DISABLE_BATTERY-2":True
            }
        for i in clamps:
            print("i",i)
            command[f"DISABLE_{i}"] = False
        print("Command Final: ",command)
        publish.single(self.model.pub_topics["plc"],json.dumps(command), qos = 2)

class gafetQuality (QState):

    ok      = pyqtSignal()
    nok     = pyqtSignal()
    ok_alarma= pyqtSignal()
    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool

    def onEntry(self, event):

        command = {
            "lbl_result" : {"text": "ID recibido", "color": "green"},
            "lbl_steps" : {"text": "Validando usuario de Calidad...", "color": "black"},
            }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command = {
            "alarma_emergencia": False,
            "show":{"login": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(0.05,self.API_requests).start()

    def API_requests (self):
        try:
            endpoint = ("http://{}/api/get/usuarios/GAFET/=/{}/ACTIVE/=/1".format(self.model.server, self.model.input_data["gui"]["ID"]))
            response = requests.get(endpoint).json()
            print("response: ",response)

            if "TYPE" in response:
                print("El usuario si existe en la DB")
                if response["TYPE"] == "CALIDAD" or response["NAME"] == "AMTC":
                    ################################################
                    print("se guarda registro de calidad y se emite un ok")
                    fecha_actual = self.model.get_currentTime()
                    try:
                        if self.model.alarma_activada==True:
                            Info_msg = "ALARMA DE CALIDAD, "+ self.model.qr_codes["HM"] +", " + str(self.model.torque_data[self.tool]["current_trq"])
                            
                        else:
                            Info_msg = "INTERVENCIÓN DE CALIDAD"

                        data = {
                            "NOMBRE": response["NAME"],
                            "TIPO": response["TYPE"],
                            "INFO": Info_msg,
                            "FECHA": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                            }
                        endpoint = "http://{}/api/post/quality_info".format(self.model.server)
                        resp = requests.post(endpoint, data=json.dumps(data))
                    except Exception as ex:
                        print("post quality exception: ", ex)

                    print("ocultando login: show:{login: False}")
                    command = {
                        "show":{"login": False}
                        }
                    publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    ################################################
                    if self.model.alarma_activada:
                        self.model.alarma_activada=False
                        self.model.alarma_caja_tuerca=""
                        self.ok_alarma.emit()
                        self.model.alarma_emergencia=False
                        #imcenter en la imagen principal
                        command = {
                            "lbl_boxTITLE" : {"text": "ALARMA TUERCA \n VERIFICADA", "color": "green"},
                            "img_center" : self.model.ultima_imagen+".jpg",
                            "alarma_emergencia": False,
                            "show":{"login": False}
                            }
                        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.model.ultima_imagen=""
                    else:
                        self.ok.emit()
                else:
                    print("El usuario NO pertenece a CALIDAD")
                    command = {
                        "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                        "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                        }
                    publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.nok.emit()
            else:
                 command = {
                    "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                    "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                    }
                 publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                 self.nok.emit()
        except Exception as ex:
            print("Login request exception: ", ex)
            command = {
                "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()
    
    def onExit(self, event):
        print("Saliendo de estado qgafet... aquí se colocan en FALSE los DISABLE_box")
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
        print("Command Final: ",command)
        publish.single(self.model.pub_topics["plc"],json.dumps(command), qos = 2)
        command = {
            "lbl_result" : {"text": "", "color": "green"},
            "lbl_steps" : {"text": "", "color": "black"},
            }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

class Backward (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.delay1 = 0.1
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.stop = self.model.torque_data[self.tool]["stop_profile"]
        self.backward = self.model.torque_data[self.tool]["backward_profile"]
        self.encoder = "encoder_" + self.tool[-1]

    def onEntry(self, event):
        

        print("ESTADO ACTUAL: REVERSA")

        self.model.estado_actual[self.tool] = "BACKWARD" #se guarda el estado actual de esta tool

        current_trq = self.model.torque_data[self.tool]["current_trq"] # ["PDC-P", "E1", 3, "tuerca_x"]
        try:
            zone = "0"
            temp = self.model.input_data["plc"][self.encoder]["zone"] # {"caja": "torque_name"}
            if temp != "0":
                temp = json.loads(temp)
                if len(temp):
                    zone = [list(temp)[0], temp[list(temp)[0]]]  #  ["caja", "torque_name"]
                else:
                    return
        except Exception as ex:
            print (f"CheckZone {self.tool} Exception: ", ex)
            command = {
                "lbl_result" : {"text":f"Backward Exception {self.tool} {ex.args}", "color": "red"},
                "lbl_steps" : {"text": "Verificar config. de encoders", "color": "black"}
                }
            #publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            return

    #if self.model.config_data["encoder_feedback"]["tool1"] == True:
        profile = self.stop
        command = {}
        if zone[0] == current_trq[0]:
            if self.model.herramienta_bloqueada[self.tool]==True:
                tool_desbloqueada = self.tool+"_desbloqueada"
                publish.single(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : False}),hostname='127.0.0.1', qos = 2)
                print("se hizo false")
                sleep(0.4)
                publish.single(self.model.pub_topics["plc"],json.dumps({tool_desbloqueada : True}),hostname='127.0.0.1', qos = 2)

            if zone[1] == "0":
                command = {
                    "lbl_result" : {"text":"Herramienta fuera de zona de torque", "color": "red"},
                    "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"}
                    }
                profile = self.stop
            elif zone[1] == current_trq[1]:
                
                command = {
                    "lbl_result" : {"text": "Herramienta en " + zone[0] + ": " + zone[1], "color": "green"},
                    "lbl_steps" : {"text": "Herramienta activada en REVERSA", "color": "black"}
                    }
                profile = self.backward
            else:
                command = {
                    "lbl_result" : {"text":"Herramienta en " + zone[0] + ": " + zone[1], "color": "red"},
                    "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"}
                    }
                profile = self.stop
        else:
            command = {
                "lbl_result" : {"text":"Herramienta fuera de zona de torque", "color": "red"},
                "lbl_steps" : {"text": "Coloca la herramienta en " + current_trq[0] + ": " + current_trq[1], "color": "black"}
                }
            profile = self.stop
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(self.delay1, self.profilePub, args = (profile,)).start()
    #else:
    #    self.ok.emit()

    def profilePub (self, profile):
        if profile != self.model.torque_data[self.tool]["past_trq"]:
            command = {
                        "profile": profile
                      }
            print("TOPIC: ",self.pub_topic)
            print("PROFILE BACKWARD--------",command)
            publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.model.torque_data[self.tool]["past_trq"] = profile
             
class ToolsManager (QState):

    ok1      = pyqtSignal()
    ok2      = pyqtSignal()
    ok3      = pyqtSignal()
    finish  = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.emty_tools = {}
        self.temporal1 = ""
        self.temporal2 = ""
        self.temporal3 = ""
    
    def onEntry(self, event):

        print("ESTADO: ToolsManager")

        command = {
                "lineEdit" : True,
                "lineEdit_focus" : True
                }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        print("Focus de lineEdit enviado")
        self.model.en_ciclo=True
        #Para saber si aún quedan cajas del lado izquierdo o derecho dependiendo de en que posición se hayan activado sus variables, se mantiene como true o se hace false
        Pos1Finished = False
        Pos2Finished = False
        #es la colección de todo el arnés
        modularity = self.model.input_data["database"]["modularity"]
        #Al clampear una caja esta se agrega a la variable self.model.input_data["plc"]["clamps"], después se manda la señal que te lleva a este estado ToolsManager
        #la variable contiene todas las cajas que se han clampeado hasta ese momento
        clamps = self.model.input_data["plc"]["clamps"]
        print("***modularityActual en ToolsManager: ",modularity)
        
        
        #se obtienen los valores para conocer si existen cajas por hacer para un lado de pantalla
        for boxModularity in modularity:
            print("boxModularity: ",boxModularity)
            if boxModularity in self.model.boxPos1:
                Pos1Finished = True
            if boxModularity in self.model.boxPos2:
                Pos2Finished = True

        print("*--*-*-*-*-*Pos1Finished: ",Pos1Finished)
        print("*--*-*-*-*-*Pos2Finished: ",Pos2Finished)

        #estos if entran hasta que se hayan terminado las cajas de un lado
        if Pos1Finished == False and Pos2Finished == True:
            print("Posición 1 Finished! Ya no quedan cajas, ESPERANDO POSICIÓN 2")
            command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
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
            "lbl_result" : {"text": "Cajas Terminadas", "color": "green"},
            "lbl_steps" : {"text": "Esperando Posición 2", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts"  : {"text": "", "color": "black"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "position" : {"text": "POSICIÓN 1", "color": "black"},
            "img_center" : "logo.jpg"
            }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        if Pos1Finished == True and Pos2Finished == False:
            print("Posición 2 Finished! Ya no quedan cajas, ESPERANDO POSICIÓN 1")
            command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
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
            "lbl_result" : {"text": "Cajas Terminadas", "color": "green"},
            "lbl_steps" : {"text": "Esperando Posición 1", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts"  : {"text": "", "color": "black"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "position" : {"text": "POSICIÓN 2", "color": "black"},
            "img_center" : "logo.jpg"
            }
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        #constraints = self.model.config_data["constraints"]["tools"]

        #se llama método checkTools (actualiza emty_tools para saber si tiene elementos en queue cada herramienta)
        self.checkTools()

        #SI YA NO QUEDAN ELEMENTOS EN LA COLECCIÓN..
        if not(len (modularity)):
            #se finaliza el ciclo
            Timer(0.05,self.finish.emit).start()
            return

        #A ESTE PUNTO DE ESTE ESTADO SOLO SE PUEDE LLEGAR SI QUEDAN ELEMENTOS EN LA COLECCIÓN YA QUE DE LO CONTRARIO LA SEÑAL FINISH EMITIDA TE SACARÁ DE ESTE ESTADO.

        #SI QUEDAN ELEMENTOS CLAMPEADOS...(Estos se van retirando de self.model.input_data["plc"]["clamps"] con un pop al momento en que llega un mensaje de clamp_box = False
        if len(clamps):

            #se convierte el mensaje de respuesta "clamp_PDC-R" a su respectiva caja que se clampeó según la modularity
            if "PDC-R" in clamps and "PDC-RMID" in modularity:
                    #index busca el indice del elemento de un arreglo, y después a este le cambias el valor
                    clamps[clamps.index("PDC-R")] = "PDC-RMID"
            if "PDC-R" in clamps and "PDC-RS" in modularity:
                    clamps[clamps.index("PDC-R")] = "PDC-RS"

            #recorrer lista de cajas clampeadas PARA ASIGNAR LAS TAREAS QUE DEBERÁN REALIZAR LAS HERRAMIENTAS ----------------------------------
            for i in clamps:
                #si la caja existe en la colección
                if i in modularity:
                    #recorres los elementos en la colección dentro de esa caja...
                    for j in modularity[i]:

                        #se copia la caja actual del for que se está revisando
                        caja = i
                        #se copia la terminal actual del for que se está revisando
                        terminal = j
                        #se obtiene el perfil correspondiente a cierta tarea según lo preestablecido en el model (configuración de torque que tendrá la tarea)
                        perfil = self.model.torque_cycles[caja][terminal][1]
                        #se obtiene la tuerca correspondiente a cierta tarea según lo preestablecido en el model (para manejo de datos y se pueda identificar si es una de 6mm u 8mm)
                        tuerca = self.model.torque_cycles[caja][terminal][2]
                        #se obtiene la tool correspondiente a cierta tarea según lo preestablecido en el model (para saber a qué tool se asignará la tarea)
                        herramienta = self.model.torque_cycles[caja][terminal][0]

                        #si la herramienta (self.model.torque_cycles[i][j][0]) correspondiente a esa caja y esa terminal no tiene tareas en cola AÚN!!...
                        #se llena self.model.torque_data[herramienta]["queue"] con las tareas para esa caja y se hace emty_tools[herramienta]=False para no agregar más tareas hasta terminar esas
                        if self.emty_tools[herramienta]:
                            #se asigna la caja con su posición, ciclo y herramienta correspondiente a torque_data, tool, queue (al queue de la herramienta)

                            self.model.torque_data[herramienta]["queue"].append([caja,terminal,perfil,tuerca])
                            #self.model.torque_data[self.model.torque_cycles[i][j][0]]["queue"].append([i, j, self.model.torque_cycles[i][j][1], self.model.torque_cycles[i][j][2]])



                #se llama método checkTools (actualiza emty_tools  para saber si tiene elementos en queue cada herramienta)
                #y solamente se llenan las tareas de una caja, después en checkTools se hace emty_tools False para que ya no se agreguen más tareas hasta haber completado esas
                #(una vez que se completan las tareas de una caja se regresa el ciclo a esta clase ToolsManager)
                self.checkTools()
            #---------------------------------- CADA VEZ QUE SE CLAMPEA UNA CAJA SE ASIGNAN TAREAS A LAS HERRAMIENTAS -------------------------------------


            #emty_tools vale True cuando la herramienta no tiene tareas, y False cuando aún tiene 
            #para recorrer las herramientas i = "tool1,tool2,tool3"
            for i in self.emty_tools:
                #si emty_tools no tiene tareas pendientes
                if self.emty_tools[i] == True:
                    tareas_pendientes = False
                #si tiene tareas pendientes
                else:
                    #se hace True la variable torque_data[tool1][enable] (dependiendo de la tool)   # para halllarlo rapido con crtl + F: self.model.torque_data[self.tool]["enable"] = True
                    #esto es para habilitar la herramienta al estar buscando zona con esa herramienta en la clase check_zone
                    self.model.torque_data[i]["enable"] = True
                    tareas_pendientes = True

                #si ya no hay tareas pendientes para ninguna herramienta...
                if tareas_pendientes == False:
                    print("//////////////////AQUI SE CAMBIA EL COMMAND, DENTRO DEL IF DE TAREAS PENDIENTES EN FALSE")
                    command = {
                        "lbl_result": {"text": ""},
                        "lbl_steps" : {"text": "Escanea código QR de alguna caja (Excepto las BATTERY'S)", "color": "black"},
                        "lbl_info2" : {"text": ""}
                        }
                    #Si ya no quedan cajas para la Posición 1 (Pos1Finished == False), sola/m actualizar GUI 2 con el command
                    if Pos1Finished == False:
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    #Si ya no quedan cajas para la Posición 2, sola/m actualizar GUI 1 con el command
                    elif Pos2Finished == False:
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    #Si ambas posiciones tienes cajas pendientes, actualizar las GUI's correspondientes según la Tool "i" (self.model.torque_data[i]["gui"])
                    else:
                        publish.single(self.model.torque_data[i]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)       
            
                    
            # Se activa la herramienta 1 (6mm,Izq)
            if self.temporal1 == "ok1":
                Timer(0.05, self.ok1.emit).start()
            # Se activa la herramienta 2 (6mm,Centro)
            if self.temporal2 == "ok2":
                Timer(0.05, self.ok2.emit).start()
            # Se activa la herramienta 3 (8mm,Der)
            if self.temporal3 == "ok3":
                Timer(0.05, self.ok3.emit).start()
            if self.temporal1 == "" and self.temporal2 == "" and self.temporal3 == "":
                print("Ninguna Tool se activa!")
        
        #NO HAY ELEMENTOS CLAMPEADOS
        else:
            command = {
                "lbl_result": {"text": ""},
                "lbl_steps" : {"text": "Escanea código QR de alguna caja (Excepto las BATTERY'S)", "color": "black"},
                "lbl_info2" : {"text": ""}
                }
            for i in self.model.torque_data:
                publish.single(self.model.torque_data[i]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
    
    def checkTools(self):
        clamps = self.model.input_data["plc"]["clamps"]
        print("*********CHECK TOOLS*********")

        #modo puntual o modo flexible activado (para empezar por cualquier tuerca)
        if self.model.config_data["flexible_mode"]:
            self.temporal1 = "ok1"
            self.temporal2 = "ok2"
            self.temporal3 = "ok3"
        else:

            if len(self.model.torque_data["tool1"]["queue"]):
                print("Aun hay elementos en tool1 para esta caja")
                self.temporal1 = "ok1"
            else:
                self.temporal1 = ""

            if len(self.model.torque_data["tool2"]["queue"]):
                print("Aun hay elementos en tool2 para esta caja")
                self.temporal2 = "ok2"
            else:
                self.temporal2 = ""

            if len(self.model.torque_data["tool3"]["queue"]):
                print("Aun hay elementos en tool3 para esta caja")
                self.temporal3 = "ok3"
            else:
                self.temporal3 = ""

        #se imprimen las tareas en cola de cada herramienta
        print("queue pendientes Tool 1",self.model.torque_data["tool1"]["queue"])
        print("queue pendientes Tool 2",self.model.torque_data["tool3"]["queue"])
        print("queue pendientes Tool 3",self.model.torque_data["tool2"]["queue"])

        #se recorre item: "tool1, tool2, tool3"
        for item in self.model.torque_data:

            #se revisa hay elementos en las tareas en cola de cada herramienta
            if not(len(self.model.torque_data[item]["queue"])):
                #si no quedan elementos en cola para esa herramienta, emty_tools se hace True, lo que permite asignarle más tareas
                self.emty_tools[item] = True
            else:
                #si ya se asignaron tareas a esa herramienta, emty_tools se hace False, por lo que no se le agregan más tareas (al menos hasta que termine las que tiene asignadas)
                self.emty_tools[item] = False

class ChkReset (QState):
    reset   = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        
        #self.standby = QState(parent = self)
        #self.chk_errors = CheckErrors(model = model, parent = self)

        #self.standby.addTransition(self.model.transitions.key, self.chk_errors)
        #self.chk_errors.addTransition(self.chk_errors.ok, self.standby)
        #self.chk_errors.addTransition(self.chk_errors.reset, self.standby)



        self.model.transitions.key.connect(self.reset.emit)

class CheckErrors (QState):
    ok      = pyqtSignal()
    reset   = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.errors = False
    def onEntry(self, event):
        self.errors = False
        for item in self.model.torque_data:
            if self.model.torque_data[item]["error"]:
                self.errors = True 
        if self.errors:
            self.errors = False
            self.ok.emit()
        else:
            self.reset.emit()

class RaffiActive (QState):

    ok      = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.queue = self.model.torque_data[self.tool]["queue"]
        self.stop = self.model.torque_data[self.tool]["stop_profile"]
        self.backward = self.model.torque_data[self.tool]["backward_profile"] 
        self.encoder = "encoder_" + self.tool[-1]

        self.model.transitions.raffi_enabled.connect(self.raffi_on)
        self.model.transitions.raffi_disabled.connect(self.raffi_off)

    

    @pyqtSlot(str)
    def raffi_on(self, raffi_enabled):


        current_trq = "not_found"
        if len(self.queue):
            current_trq = self.queue[0][0] #self.queue[0][0]: ["PDC-P"]
        
        self.model.current_box_raffi = str(raffi_enabled)

        print("tool: ",self.tool)
        print("current_trq: ", current_trq)
        print("self.model.current_box_raffi: ",self.model.current_box_raffi)


        if current_trq != "not_found":

            if current_trq == raffi_enabled:


                command_plc = {f"raffi_{self.model.current_box_raffi}": True}
                publish.single(self.model.pub_topics["plc"],json.dumps(command_plc),hostname='127.0.0.1', qos = 2)
                print("señal de raffi activado enviada a PLC")


                command = {
                        "lbl_result" : {"text":"Raffi de caja "+ self.model.current_box_raffi +" Habilitado", "color": "red"},
                        "lbl_steps" : {"text": "Para continuar deshabilitar Raffi", "color": "black"}
                        }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)



                profile = self.stop
                command = {"profile": profile}

                print("TOPIC: ",self.pub_topic)
                print("PROFILE: STOP")

                publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.model.torque_data[self.tool]["past_trq"] = profile

            else:

                print("no es una caja con tareas en cola")


    @pyqtSlot(str)
    def raffi_off(self, raffi_disabled):

        
        self.model.current_box_raffi = str(raffi_disabled)

        command_plc = {f"raffi_{self.model.current_box_raffi}": False}
        publish.single(self.model.pub_topics["plc"],json.dumps(command_plc),hostname='127.0.0.1', qos = 2)
        print("señal de raffi desactivado enviada a PLC")

class RaffiMessage (QState):

    process_continue      = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
    

    def onEntry(self, event):

        raffi_message = True

        #se manda señal para continuar con su máquina de estados, si esta herramienta no corresponde a el raffi activado para esta caja
        ###################################################################################
        #si la herramienta contiene un trigger diferente a None (tiene una tarea actual)
        if self.model.torque_data[self.tool]["current_trq"] != None:
            #si la caja actual para esta herramienta es igual a la caja solicitada por el raffi
            if self.model.torque_data[self.tool]["current_trq"][0] != self.model.current_raffi_key:
                print("se envía señal de que el raffi no es para esta herramienta: ",self.tool, " y continúa su operación normal")
                raffi_message = False
                self.process_continue.emit()
        ###################################################################################

        if raffi_message == True:

            #se hace true para no pedir el enter de la llave
            #################################
            print("self.model.reintento_torque = True, ", self.tool)
            self.model.reintento_torque = True
            #para que no se regrese reintento_torque a False en el estado "zone"
            self.model.backward_key_tool["raffi"] = True
            #################################

            command = {
                    "lbl_result" : {"text":"Raffi de caja "+ self.model.current_raffi_key +" Presionado, para habilitar", "color": "red"},
                    "lbl_steps" : {"text": "Raffi dar llave, para seguir ciclo vuelve a presionar el raffi: " + self.model.keyboard_raffi_pressed, "color": "red"}
                    }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def onExit(self, event):
        #Es necesario hacerse False en onExit para permitir llave otra vez, al tratarse de salir de este mensaje sin dar llave
        #para habilitar el raffi
        self.model.backward_key_tool["raffi"] = False
        command = {
                "lbl_result" : {"text":"Herramienta fuera de zona de torque", "color": "red"},
                "lbl_steps" : {"text": "Mueva la herramienta para continuar", "color": "black"}
                }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

class RaffiKey (QState):

    ok      = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.queue = self.model.torque_data[self.tool]["queue"]
        self.stop = self.model.torque_data[self.tool]["stop_profile"]
        self.backward = self.model.torque_data[self.tool]["backward_profile"] 
        self.encoder = "encoder_" + self.tool[-1]
    

    def onEntry(self, event):

        #se vuelve a hacer True porque el estado anterior en OnExit  es necesario hacerlo False
        self.model.backward_key_tool["raffi"] = True
        current_trq = "not_found"
        if len(self.queue):
            current_trq = self.queue[0][0] #self.queue[0][0]: ["PDC-P"]
       

        print("tool: ",self.tool)
        print("current_trq: ", current_trq)
        print("self.model.current_raffi_key: ",self.model.current_raffi_key)


        if current_trq != "not_found":

            if current_trq == self.model.current_raffi_key:


                command_plc = {f"raffi_{self.model.current_raffi_key}": True}
                publish.single(self.model.pub_topics["plc"],json.dumps(command_plc),hostname='127.0.0.1', qos = 2)
                print("señal de raffi activado enviada a PLC")

                command = {
                        "lbl_result" : {"text":"Raffi de caja "+ self.model.current_box_raffi +" Habilitado", "color": "red"},
                        "lbl_steps" : {"text": "Para continuar deshabilitar Raffi: "+ self.model.keyboard_raffi_pressed, "color": "black"}
                        }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)


                profile = self.stop
                command = {"profile": profile}

                print("TOPIC: ",self.pub_topic)
                print("PROFILE: STOP")

                publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.model.torque_data[self.tool]["past_trq"] = profile

            else:

                command = {
                        "lbl_result" : {"text":"Este Raffi no se puede habilitar", "color": "red"},
                        "lbl_steps" : {"text": f"Presiona nuevamente " + self.model.keyboard_raffi_pressed +" para continuar", "color": "red"}
                        }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                print("no es una caja con tareas en cola")
        else:
            command = {
                        "lbl_result" : {"text":"Este Raffi no se puede habilitar", "color": "red"},
                        "lbl_steps" : {"text": f"Presiona nuevamente " + self.model.keyboard_raffi_pressed +" para continuar", "color": "red"}
                        }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)


    def onExit(self, event):

        self.model.backward_key_tool["raffi"] = False
        command_plc = {f"raffi_{self.model.current_raffi_key}": False}
        publish.single(self.model.pub_topics["plc"],json.dumps(command_plc),hostname='127.0.0.1', qos = 2)
        print("señal de raffi desactivado enviada a PLC")

        command = {
                "lbl_result" : {"text":"Herramienta fuera de zona", "color": "red"},
                "lbl_steps" : {"text": "Mueva la herramienta para continuar", "color": "black"}
                }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

class CheckProfile (QState):
    ok      = pyqtSignal()
    retry   = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]

    def onEntry(self, event):

        #perfil esperado a tener en la herramienta (el que estaba antes de haber entrado a backward)
        #self.model.torque_bin[self.tool]["send_profile"]
        
        #perfil actual de la herramienta
        #self.model.torque_bin[self.tool]["current_profile"]
        print("current_profile: ",self.model.torque_bin[self.tool]["current_profile"])

        print("CHECKPROFILE-----------------------")

        self.model.estado_actual[self.tool] = "CHECKPROFILE"

        self.send_profile()
        #variable se hace true para dejar de recibir mensajes de torque falso proveniente de la reversa
        self.model.lock_backward[self.tool] = True

        command = {
                "lbl_result" : {"text":"Saliendo de modo REVERSA", "color": "red"},
                "lbl_steps" : {"text": "Espere a que se active la herramienta", "color": "black"}
                }
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        
        if self.model.torque_bin[self.tool]["current_profile"] != self.model.torque_data[self.tool]["stop_profile"]:
            if self.model.intentos_max_stop[self.tool] > 30:
                print("current profile = stop profile 30 intentos agotados para tool: ",self.tool)
                self.model.intentos_max_stop[self.tool] = 0
                self.send_profile()
                print("ok.emit() en 1 seg")
                
                self.model.estado_actual[self.tool] = "" #aquí ya terminó exitosamente la reversa de esa tuerca
                Timer(1.0, self.ok.emit).start()
            else:
                print("current profile != stop profile")
                self.model.intentos_max_stop[self.tool] += 1
                self.send_profile()
                Timer(0.1, self.retry.emit).start()
        else:
            self.model.intentos_max_stop[self.tool] = 0
            print("current profile = stop profile")
            self.send_profile()
            print("ok.emit() en 1 seg")
            
            self.model.estado_actual[self.tool] = "" #aquí ya terminó exitosamente la reversa de esa tuerca
            Timer(1.0, self.ok.emit).start()

    def send_profile(self):
        command = {"profile": self.model.torque_data[self.tool]["stop_profile"]}
        print("TOPIC: ",self.pub_topic)
        print("ENVIANDO NUEVAMENTE STOP")
        publish.single(self.pub_topic,json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.torque_data[self.tool]["past_trq"] = self.model.torque_data[self.tool]["stop_profile"]

    def onExit(self, event):
        #se hace false para permitir que aparezca el mensaje de confirmación de llave
        self.model.backward_key_tool[self.tool] = False
        #se hace false para permitir nuevamente mensajes provenientes del torque de la herramienta
        self.model.lock_backward[self.tool] = False

class Palpador (QState):

    continuar   = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]

    def onEntry(self, event):

        print("||||Dentro de Estado Palpador!")
        candados = self.model.input_data["database"]["candados"]
        print("Candados a Revisar: ",candados)

        command = {
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts"  : {"text": "", "color": "black"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "img_center" : "boxes/fuseconnvalidation.jpg",
            "lbl_result" : {"text": "Validación de Conectores PDC-R", "color": "blue"},
            "lbl_steps"  : {"text": "Coloque el Palpador sobre los candados", "color": "black"},
            }

        if self.model.palpador_iniciado == True:
            print("palpador ya había sido iniciado")
            command["img_center"] = self.tool + ".jpg"

        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        #se emite la señal para continuar a checar las zonas del Palpador
        Timer(0.5,self.continuar.emit).start()

    def onExit(self, event):
        print("||||Salida de Palpador")

class WaitingPin (QState):

    pin_already_pressed   = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.candadosQueue = self.model.input_data["database"]["candados"]

    def onEntry(self, event):
        print("||||Dentro de Estado WaitingPin!")

        #quiere decir que se presionó el pin antes de entrar correctamente en la zona encoder + zona altura y no se ha dejado de presionar el pin
        if self.model.pin_pressed == True:
            print("self.pin_already_pressed.emit()")
            self.pin_already_pressed.emit()

    def onExit(self, event):
        print("||||||||||||||||||||||Salida de WaitingPin")
        print("self.model.pin_pressed",self.model.pin_pressed)
        if self.model.pin_pressed == True:
            self.model.pin_pressed = False
            self.candadosQueue.pop(0)
            print("candados restantes: ",self.candadosQueue)
            
            print("Funcion Pintando Bounding Box en color Verde...")
            self.model.imgs["PDC-R"] = self.model.drawBB(
            img = self.model.imgs["PDC-R"], BB =["PDC-R", self.model.current_task_candado] , color = (0, 255, 0))
            imwrite(self.model.imgs_path + self.tool + ".jpg", self.model.imgs["PDC-R"])

            print("Y self.model.current_task_candado se iguala a NONE")
            #Se iguala a NONE la variable que contiene el candado actual en el modelo... si esto no se hace, el programa siempre pedirá el mismo candado aún después del "pop"
            self.model.current_task_candado = None

            command = {
                "lbl_result" : {"text": "Candado OK", "color": "green"},
                "lbl_steps" : {"text": "Mueva la herramienta para continuar", "color": "black"},
                "img_center" : self.tool + ".jpg"
                }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            
            #señal para avisar que acaba de finalizar un pin y dar un timer para antes de empezar a esperar el nuevo pin del siguiente candado
            self.model.nuevo_pin = True

class DelayPin (QState):

    continuar   = pyqtSignal()

    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        print("||||Dentro de Estado DelayPin!")

        if self.model.nuevo_pin == True:
            self.model.nuevo_pin = False
            Timer(0.7, self.continuar.emit).start()
        else:
            self.continuar.emit()
     
class CheckZonePalpador (QState):

    end                  = pyqtSignal()
    wait_pin             = pyqtSignal()
    
    def __init__(self, tool = "tool1", model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.tool = tool
        self.pub_topic = self.model.pub_topics["torque"][self.tool]
        self.candadosQueue = self.model.input_data["database"]["candados"]
        self.delay1 = 0.1
        self.delay2 = 2
        self.delay3 = 0.3
        self.oracle= ""
        self.currentTool= ""
        self.BB = self.model.BB
        self.img_name = ""
        self.start = True
        self.flex_BB_drawed = False

    def onEntry(self, event):
        print("|||| Dentro de Estado CheckZonePalpador!")
        #candado_encoder se inicializa con "0"
        candado_encoder = "0"
        current_height = "0"

        #se hace true al presionar el palpador, pero se debe mantener en False antes de llegar a ese estado (para prevenir que se haga true cuando se presione fuera de el estado waiting_pin)
        #self.model.pin_pressed = False

        #se revisa si hay alguna herramienta en reversa, o si está el raffi de la caja actual habilitado
        self.check_key_process_function()

        #################################### REVISAR MENSAJE DE ENCODER PARA LA ZONA ACTIVADA ############################
        #candado_encoder inicia valiendo "0"
        try:

            candado_encoder = self.model.input_data["plc"]["encoder_3"]["candado"]
            current_height = self.model.input_data["plc"]["encoder_4"]["candado"]

        except Exception as ex:
            print (f"CheckZone {self.tool} Exception: ", ex)
            command = {
                "lbl_result" : {"text":f"CheckZone {self.tool} {ex.args}", "color": "red"},
                "lbl_steps" : {"text": "Verificar config. de encoders", "color": "black"}
                }
            return
        #####################################################################################################################
        
        #se da el valor a current_task_candado de lo que está registrado en torque_data para esa herramienta en "current_task_candado"
        #si está vacío, obtiene nuevamente un valor desde self.candadosQueue[0] si es que aún quedan tareas por hacer
        current_task_candado = self.model.current_task_candado
        print("self.model.current_task_candado: ",self.model.current_task_candado)
        print("self.candadosQueue: ",self.candadosQueue)

        #si el valor de current_task_candado es None (por el momento está vacío)
        if current_task_candado == None:
            
            #si aún hay candados en cola pendientes por hacer para esa herramienta
            if len(self.candadosQueue):

                #se iguala el current_task_candado a la tarea en cola (la ultima) con el valor de la caja , terminal, profile, y tuerca !!!!!!!!!!
                #SE ASIGNA LA ULTIMA TAREA DE ESTA HERRAMIENTA EN current_task_candado!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                current_task_candado = self.candadosQueue[0] # ["s1","s2",...]

                #SE GUARDA EN self.model.current_task_candado el current_task_candado para esa herramienta!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.model.current_task_candado = current_task_candado


                #Para mostrar en pantalla la imagen del palpador (Cambiar el string por el del nombre de la imagen correspondiente al palpador; Cuando se tenga la foto)
                self.currentTool = "HERRAMIENTA 3"
                #img_name obtiene la dirección de la imagen de la caja para la validación de candados
                img_name = self.model.imgs_path + "boxes/fuseconnvalidation.jpg"

                #se llama al método draw con argumentos: caja y posición
                self.draw(["PDC-R", current_task_candado])


                #se publica en la gui las instrucciones visuales
                command = {
                    "img_nuts" : "/candados/"+current_task_candado+".png",
                    "lbl_nuts" : {"text":"Candado "+current_task_candado, "color": "black"},
                    "lbl_instructions" : {"text": "||Instrucciones||", "color": "black"},
                    "img_toolCurrent" : self.currentTool+ ".jpg",
                    "lbl_toolCurrent" : {"text": "USAR "+self.currentTool, "color": "black"},
                    "img_center" : self.tool + ".jpg"
                    }
                publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                #variable para indicar que ya inició el palpador y si se vuelve al estado inicial no borrar la imagen con fuseconnvalidation.jpg
                self.model.palpador_iniciado = True

            #SI NO HAY TAREAS EN COLA PARA ESTA HERRAMIENTA (pero se pueden agregar más)
            else:
                #se emite un Finish de CheckZonePalpador -  que se conecta a FINISH de NewTool3 ... FINISH!!!!!!!!!!!!!!!!!
                print("||||||| Se emite el Finish; PROCESO DEL PALPADOR COMPLETADO |||||||")
                self.finish()
                return

        #############################################################################

        ##si esta variable contiene elementos
        else:

            command = {}

            #si el raffi no está habilitado (su valor es 0)
            if self.model.raffi["PDC-R"] == 0:

                print("current_height: ",current_height)
                print("candado_encoder: ",candado_encoder)
 

                #si la zona de candado actual es igual a cero... (esto pasa en comm.py cada que llega una zona en "false")
                if candado_encoder == "0":
                    command = {
                        "lbl_result" : {"text":"Herramienta fuera de zona de candado", "color": "red"},
                        "lbl_steps" : {"text": "Coloca la herramienta en PDC-R: " + current_task_candado, "color": "black"}
                        }

                    #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                    self.check_lock_raffi_function("PDC-R")

                #si la zona de candado actual es igual a la zona de candado solicitada en la tarea actual en cola
                elif candado_encoder == current_task_candado or self.model.candados_zonas[current_task_candado]==True:
                        
                        #si es "0" quiere decir que no está en la zona de altura correcta
                        if current_height != "0":

                            #si current_height manda como resultado "height" significa que estás en posición de candado en altura
                            if current_height == "height":

                                command = {
                                    "lbl_result" : {"text": "Herramienta en PDC-R: " + candado_encoder, "color": "green"},
                                    "lbl_steps" : {"text": "Empuja la herramienta hacia el candado para validar", "color": "black"}
                                    }

                                #se bloquea el uso de este raffi
                                self.model.active_lock["PDC-R"] = True
                                #se indica que la herramienta actual está bloqueando el raffi porque está activa
                                self.model.active_lock_tool[self.tool] = True
                                self.wait_pin.emit()

                            else:
                                command = {
                                "lbl_result" : {"text": "Herramienta en PDC-R: " + candado_encoder, "color": "orange"},
                                "lbl_steps" : {"text": "Mueve la herramienta a la altura del candado", "color": "black"}
                                }                        
                                #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                                self.check_lock_raffi_function("PDC-R")

                        else:
                            command = {
                            "lbl_result" : {"text": "Herramienta en PDC-R: " + candado_encoder, "color": "orange"},
                            "lbl_steps" : {"text": "Mueve la herramienta a la altura del candado", "color": "black"}
                            }                        
                            #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                            self.check_lock_raffi_function("PDC-R")


                #si la terminal actual es diferente de cero y de la solicitada...
                else:
                    command = {
                        "lbl_result" : {"text": "Herramienta en PDC-R: " + candado_encoder, "color": "red"},
                        "lbl_steps" : {"text": "Coloca la herramienta en PDC-R: " + current_task_candado, "color": "black"}
                        }                        
                    #función para revisar si alguna herramienta que se use para las tareas de esta caja tiene los raffi bloqueados, si no, volver a habilitar el uso del raffi
                    self.check_lock_raffi_function("PDC-R")



            #si el raffi está habilitado (su valor es 1)
            elif self.model.raffi["PDC-R"] == 1:
                command = {
                        "lbl_result" : {"text":"Raffi de caja PDC-R Habilitado", "color": "red"},
                        "lbl_steps" : {"text": "Para continuar deshabilitar Raffi", "color": "black"}
                        }          
        #finalmente haces un publish del mensaje y le mandas el profile a la herramienta (siempre y cuando sea diferente del profile anterior)
        publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def draw(self, BB):
        box = "PDC-R"
        self.model.imgs[box] = self.model.drawBB(
            img = self.model.imgs[box], BB = BB, color = (31, 186, 226))
        imwrite(self.model.imgs_path + self.tool + ".jpg", self.model.imgs[box])

    def check_lock_raffi_function(self, current_box):

        #se dehabilita el bloqueo de raffi para esta herramienta porque no está activa (tiene profile:stop)****
        self.model.active_lock_tool[self.tool] = False
        #_____________________________________________

        #se inicializa como False
        check_raffi_lock = False

        #se revisa si esta caja está en las tareas pendientes para cada herramienta
        #si alguna se usa en esta caja y su variable active_lock_tool es true, check_raffi_lock será true
        ###################################################################################
        if self.model.torque_data["tool1"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool1"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool1")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool1"] == True:
                    check_raffi_lock = True

        if self.model.torque_data["tool2"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool2"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool2")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool2"] == True:
                    check_raffi_lock = True

        if self.model.torque_data["tool3"]["current_trq"] != None:
            if current_box == self.model.torque_data["tool3"]["current_trq"][0]:
                print("para esta caja: ",current_box," se tienen tareas con la tool3")
                #si esta tool tiene habilitado su bloqueo de raffi
                if self.model.active_lock_tool["tool3"] == True:
                    check_raffi_lock = True
        ###################################################################################

        #si ninguna tool de las que lleva esta caja, tiene habilitado su bloqueo de raffi (ninguna de las que lleva la caja está activa), entonces:
        if check_raffi_lock == False:
            #se hace false esta variable, para que se pueda volver a usar el raffi
            self.model.active_lock[current_box] = False
            #__________________________________________
            print("self.model.active_lock[",current_box,"] = False")

    def check_key_process_function (self):
        
        #se inicializa como False
        check_key_lock = False

        if self.model.backward_key_tool["tool1"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["tool2"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["tool3"] == True:
            check_key_lock = True

        if self.model.backward_key_tool["raffi"] == True:
            check_key_lock = True

        if check_key_lock == False:
            #se hace false para permitir que aparezca el mensaje de confirmación de llave, solo si todas las herramientas NO están en reversa y no hay un raffi habilitado
            self.model.reintento_torque = False
            print("self.model.reintento_torque = False (todas las herramientas terminaron sus reversas y no hay raffi habilitado")

    def finish(self): 
        
        if self.model.estado_candados == True:

            #regresar variables a False para finalizar con el palpador
            self.model.estado_candados = False
            self.model.contains_PDCR = False
            self.model.palpador_iniciado = False
            #regresa variable que permite escanear otra caja
            self.model.pdcr_iniciada=False
            ############################################## SE ELIMINA TAREA PENDIENTE DE ULTIMA TUERCA DE PDCR ########################################

            #se asigna la variable con la colección, la caja PDCR,PDCRMID o PDCRSMALL y el último torque que no se retiró antes de entrar a palpador
            modularity = self.model.input_data["database"]["modularity"]
            box = self.model.save_box_candados
            trq = self.model.save_current_trq_candados

            print("modularity[box]:\n",modularity[box])
            print("trq",trq)
            print("(modularity[box].index(trq)",(modularity[box].index(trq)))

            #se hace el pop del torque en modularity(la colección del arnés completo)
            modularity[box].pop(modularity[box].index(trq))

            #se hace el pop de la caja de la colección de larnés completo
            modularity.pop(box)

            print("se hace pop de la box\nmodularity:\n",modularity)

            queue3 = self.model.torque_data["tool3"]["queue"]

            print("queue tool3:\n",queue3)

            #se hace el pop de la tarea de la herramienta
            #(se busca el elemento i que contiene en i[0] a esa tarea y se elimina la tarea)
            for i in range(len(queue3)):
                print("i:",i)
                if box == queue3[i][0]:
                    print("Estamos Dentro")
                    print("i posible: ",i)
                    if trq == queue3[i][1]:
                        print("i encontrada UwU: ",i)
                        queue3.pop(i)
                        break
            
            print("se hace pop de tarea\nself.queue tool3:\n",queue3)

            #############################################################################################################################################
        
            print("|||||||||Finalizando PALPADOR y liberando variante de PDC-R")
            box = "PDC-R"
            command = {
                "lbl_instructions" : {"text": "", "color": "black"},
                "lbl_nuts" : {"text":"", "color": "black"},
                "lbl_toolCurrent" : {"text":"", "color": "black"},
                "img_nuts" : "blanco.jpg",
                "img_toolCurrent" : "blanco.jpg",
                "img_center" : "logo.jpg",
                "lbl_result" : {"text": f"Validación de candados finalizada con éxito", "color": "green"},
                "lbl_steps" : {"text": f"Candados OK", "color": "black"}
                }
            publish.single(self.model.torque_data[self.tool]["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.model.torque_data[self.tool]["enable"] = False
            #Se cambia el valor de "box" por la variante de la caja PDC-R correspondiente, en base a las banderas activadas desde el modelo:
            if self.model.smallflag == True:
                box = "PDC-RMID"
            if self.model.mediumflag == True:
                box = "PDC-RMID"
            elif self.model.largeflag == True:
                box = "PDC-R"
            #Se libera o desclampea la caja del nido
            publish.single(self.model.pub_topics["plc"],json.dumps({box : False}),hostname='127.0.0.1', qos = 2)
            #se avisa a la variable de cajas_habilitadas que ya se terminó esa caja
            self.model.cajas_habilitadas[box] = 3
            print("|||||self.model.cajas_habilitadas: ",self.model.cajas_habilitadas)

            #se vacía el current trq para que se agregue ahí la siguiente tarea para la herramienta
            self.model.torque_data["tool3"]["current_trq"]  = None

            #se vuelve a habilitar la opción de activar el raffi de esa caja
            self.model.active_lock[box] = False
            self.model.active_lock_tool["tool3"] = False

            print("variable self.model.bypass_pdcr = Finalizado para avisar que ya terminó los candados")
            self.model.bypass_pdcr = "Finalizado"

            Timer(self.delay2, self.end.emit).start()

        else:

            print("Pero el Hechicero ni se INMUTA")