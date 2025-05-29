"""
@authors: MS. Marco Rutiaga Quezada
          MS. Aarón Castillo Tobías
          Ing. Rogelio García

###############################################################################
command to exe generation:
        pyinstaller --noconsole --icon=icon.ico --add-data data;data --noconfirm app.py
        pyinstaller --icon=icon.ico --add-data data;data --noconfirm app.py
        pyinstaller --onedir --icon=icon.ico --contents-directory "." --add-data data;data app.py
commands for User Experience:
        Reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableTaskMgr /t REG_DWORD /d 1 /f
        taskkill /f /im explorer.exe
        start explorer.exe
###############################################################################
"""

from gui import MainWindow
from manager import Controller
import os

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from time import sleep
    import sys

    #Este ajuste de sys.stdout asegura que los print() se vuelquen inmediatamente al archivo de salida, resolviendo el problema del búfer al correr la aplicación con un BAT para poder acceder a la información de los print() y poder guardar la información de consola.
    sys.stdout.reconfigure(line_buffering=True)

    #os.startfile('C:\\WINDOWS\\system32\\cmd.exe')

    app = QApplication(sys.argv)
    gui_1 = MainWindow(name = "Interior 1.1", topic = "gui")
    gui_2 = MainWindow(name = "Interior 1.2", topic = "gui_2", parent = gui_1)
    manager = Controller(gui_1)

    gui_2.allow_close = False
    gui_2.show()
    gui_2.move(-1920,0)
    gui_1.showMaximized()
    gui_2.showMaximized()
    
    
    ###import numpy as np
    ###from scipy.optimize import least_squares

    #### Datos de los puntos (X, Y, X', Y')
    ###puntoA_X_old = -513.749
    ###puntoA_Y_old = -151.868
    ###puntoA_X_new = -540.132
    ###puntoA_Y_new = -116.757

    ###puntoB_X_old = -420.692
    ###puntoB_Y_old = -382.611
    ###puntoB_X_new = -458.968
    ###puntoB_Y_new = -358.509

    ###puntoC_X_old = 610.697
    ###puntoC_Y_old = -58.363
    ###puntoC_X_new = 602.936
    ###puntoC_Y_new = 11.449

    ###points = [
    ###    (puntoA_X_old, puntoA_Y_old, puntoA_X_new, puntoA_Y_new),  # Punto A
    ###    (puntoB_X_old, puntoB_Y_old, puntoB_X_new, puntoB_Y_new),  # Punto B
    ###    (puntoC_X_old, puntoC_Y_old, puntoC_X_new, puntoC_Y_new)   # Punto C
    ###]

    #### Función de residuos
    ###def residuals(params):
    ###    theta, delta_X, delta_Y = params
    ###    residuals = []
    ###    for X, Y, X_new_obs, Y_new_obs in points:
    ###        X_new_calc = X * np.cos(theta) - Y * np.sin(theta) + delta_X
    ###        Y_new_calc = X * np.sin(theta) + Y * np.cos(theta) + delta_Y
    ###        residuals.append(X_new_calc - X_new_obs)
    ###        residuals.append(Y_new_calc - Y_new_obs)
    ###    return residuals

    #### Valores iniciales para theta, delta_X, delta_Y
    ###initial_guess = [np.radians(1.574), -29.607, 45.897]

    #### Optimización con least_squares
    ###result = least_squares(residuals, initial_guess, method='lm', max_nfev=1000)

    #### Resultados
    ###theta_opt = np.degrees(result.x[0])  # Convertir a grados
    ###delta_X_opt = result.x[1]
    ###delta_Y_opt = result.x[2]

    ###print(f"Ángulo de rotación (θ): {theta_opt:.3f}°")
    ###print(f"Traslación en X (ΔX): {delta_X_opt:.3f}")
    ###print(f"Traslación en Y (ΔY): {delta_Y_opt:.3f}")

    #### Validación
    ###def apply_transform(X, Y, theta, delta_X, delta_Y):
    ###    X_new = X * np.cos(theta) - Y * np.sin(theta) + delta_X
    ###    Y_new = X * np.sin(theta) + Y * np.cos(theta) + delta_Y
    ###    return X_new, Y_new

    ###print("\nValidación:")
    ###for X, Y, X_obs, Y_obs in points:
    ###    X_calc, Y_calc = apply_transform(X, Y, result.x[0], result.x[1], result.x[2])
    ###    print(f"Punto ({X}, {Y}): Calculado = ({X_calc:.3f}, {Y_calc:.3f}), Observado = ({X_obs}, {Y_obs})")
    
    sys.exit(app.exec_())

