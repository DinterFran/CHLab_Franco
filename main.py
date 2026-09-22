"""
shoebox_modbus.py

Script de pruebas Modbus TCP para el dispositivo SHOEBOX (STM32F207VET6).
Cada función implementa una prueba puntual; el menú al final elige cuál correr.
"""

from pyModbusTCP.client import ModbusClient
import time
import msvcrt  # Windows: para detectar tecla sin bloquear el loop

# --------------------------------------------------------------------------
# Configuración de conexión
# --------------------------------------------------------------------------
DEFAULT_HOST = "10.0.0.10"
PORT = 502
TIMEOUT = 1

current_host = DEFAULT_HOST  # se puede cambiar en tiempo de ejecución (ver change_host)

# --------------------------------------------------------------------------
# Mapa Modbus (según definitions.h)
# --------------------------------------------------------------------------
# Coils
COILS_MAPPED_AT = 0
NUM_DI = 13                 # DI_0 a DI_12 (coils 0-12)
COIL_WRITABLE_FROM = 16     # DO_0 a DO_7 (coils 16-23)
NUM_DO = 8
COIL_WD_ENABLE = 24
COIL_WD_LED = 25
COIL_WD_LED_CLEAR = 26

# Holding registers - IO local (SHOEBOX)
REG_AO_START = 0            # A0, A1, A2 (registros 0-2), escribibles
NUM_AO = 3
REG_HOLDING_AI_FROM = 4     # Entrada analógica (única, ADS8866)
REG_PULSE_VALUE_READ = 5    # Contador de pulsos en DI_0

# Holding registers - Config común (red / watchdog)
REG_COMMON_MAPPED_AT = 20
REG_WD_LIMIT_TIME = 27
REG_PULSE_VALUE_SET = 28
REG_DATE_1 = 29
REG_DEVICE_TYPE = 26

# Holdin registers - ADC VTC

REG_AI_MAPPED_AT = 0   # primer registro del bloque AI/AIO
REG_PV = 4
REG_RS = 5	# Range Selector pote
REG_SP1 = 6   #Set point pote
REG_SP2 = 7

# Calibración DAC (referencia, informativa)
CALIBRATION_ADC = {0: 62350, 1: 62340, 2: 62280}

# Rango de la entrada analógica: 0-65535 (crudo, 16 bits) representa 0-4 V
ADC_MAX_VOLTAGE = 4.0
ADC_MAX_RAW = 65535
def read_rs(c):
    """Lee el registro RS (Range Selector, dirección 4) una vez."""
    reg = c.read_holding_registers(REG_RS, 1)
    if reg is None:
        print("ERROR leyendo RS")
        return
    print(f"RS (raw): {reg[0]}")


def read_rs_loop(c, delay=0.5):
    """Lee RS en loop. Apretar cualquier tecla corta el loop."""
    print("Leyendo RS... apretá cualquier tecla para cortar")
    while True:
        if msvcrt.kbhit():
            msvcrt.getch()
            print("Lectura detenida")
            break
        reg = c.read_holding_registers(REG_RS, 1)
        if reg is None:
            print("ERROR leyendo RS")
        else:
            print(f"RS (raw): {reg[0]}")
        time.sleep(delay)

def read_pv_loop(c, delay=0.5):
    """Lee PV en loop. Apretar cualquier tecla corta el loop."""
    print("Leyendo PV... apretá cualquier tecla para cortar")
    while True:
        if msvcrt.kbhit():
            msvcrt.getch()
            print("Lectura detenida")
            break
        reg = c.read_holding_registers(REG_PV, 1)
        if reg is None:
            print(f"ERROR leyendo PV -> last_error={c.last_error}  "
                  f"last_except={c.last_except}  ({c.last_except_as_txt})")
        else:
            print(f"PV (raw): {reg[0]}")
        time.sleep(delay)
def read_rs_average(c, n=10, delay=0.5):
    """Lee RS n veces, imprime cada lectura y al final el promedio."""
    print(f"Leyendo RS ({n} consultas)...")
    valores = []
    for i in range(1, n + 1):
        reg = c.read_holding_registers(REG_RS, 1)
        if reg is None:
            print(f"[{i}/{n}] ERROR leyendo RS")
        else:
            valores.append(reg[0])
            print(f"[{i}/{n}] RS (raw): {reg[0]}")
        time.sleep(delay)

    print("--- Consultas ---")
    for i, v in enumerate(valores, start=1):
        print(f"Consulta {i}: {v}")

    if valores:
        promedio = sum(valores) / len(valores)
        print(f"--- Promedio ({len(valores)} lecturas válidas) ---")
        print(f"Promedio: {promedio:.2f}")
    else:
        print("No se obtuvo ninguna lectura válida, no se puede calcular el promedio")


def read_sp_average(c, n=10, delay=0.5):
    """Lee PV n veces, imprime cada lectura y al final el promedio."""
    print(f"Leyendo PV ({n} consultas)...")
    valores = []    
    for i in range(1, n + 1):
        reg = c.read_holding_registers(REG_SP1, 1)
        if reg is None:
            print(f"[{i}/{n}] ERROR leyendo PV -> last_error={c.last_error}  "
                  f"last_except={c.last_except}  ({c.last_except_as_txt})")
        else:
            valores.append(reg[0])
            print(f"[{i}/{n}] PV (raw): {reg[0]}")
        time.sleep(delay)

    print("--- Consultas ---")
    for i, v in enumerate(valores, start=1):
        print(f"Consulta {i}: {v}")

    if valores:
        promedio = sum(valores) / len(valores)
        print(f"--- Promedio ({len(valores)} lecturas válidas) ---")
        print(f"Promedio: {promedio:.2f}")
    else:
        print("No se obtuvo ninguna lectura válida, no se puede calcular el promedio")


def read_pv_prom(c, delay=0.1):
    """Lee un promedio PV """
    print("Promediando PV")
    valores = []
    n = 10;
    for i in range(1, n + 1):
        reg = c.read_holding_registers(REG_PV, 1)
        if reg is None:
            print(f"[{i}/{n}] ERROR leyendo PV -> last_error={c.last_error}  "
                  f"last_except={c.last_except}  ({c.last_except_as_txt})")
        else:
            valores.append(reg[0])
            print(f"[{i}/{n}] PV (raw): {reg[0]}")
        time.sleep(delay)

    print("--- Consultas ---")
    for i, v in enumerate(valores, start=1):
        print(f"Consulta {i}: {v}")

    if valores:
        promedio = sum(valores) / len(valores)
        print(f"--- Promedio ({len(valores)} lecturas válidas) ---")
        print(f"Promedio: {promedio:.2f}")
    else:
        print("No se obtuvo ninguna lectura válida, no se puede calcular el promedio")

def read_rs_sp(c):
    """Lee RS, SP1 una vez."""
    regs = c.read_holding_registers(REG_RS, 2)
    if regs is None:
        print("ERROR leyendo RS/SP1")
        return
    print(f"RS (raw): {regs[0]}   SP1 (raw): {regs[1]}")


def read_rs_sp_loop(c, delay=0.1):
    """Lee RS, SP1 en loop. Apretar cualquier tecla corta el loop."""
    print("Leyendo RS/SP1 apretá cualquier tecla para cortar")
    while True:
        if msvcrt.kbhit():
            msvcrt.getch()
            print("Lectura detenida")
            break
        regs = c.read_holding_registers(REG_RS, 2)
        if regs is None:
            print("ERROR leyendo RS/SP1")
        else:
            print(f"RS (raw): {regs[0]}   SP1 (raw): {regs[1]}")
        time.sleep(delay)

def adc_raw_to_volts(raw):
    return raw * ADC_MAX_VOLTAGE / ADC_MAX_RAW


# --------------------------------------------------------------------------
# Conexión
# --------------------------------------------------------------------------
def connect():
    return ModbusClient(host=current_host, port=PORT, auto_open=True, auto_close=True, timeout=TIMEOUT)


def is_valid_ip(ip_str):
    parts = ip_str.split(".")
    if len(parts) != 4:
        return False
    return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def change_host(c):
    """Cambia la IP de conexión sin reiniciar el script."""
    global current_host
    new_ip = input(f"IP actual: {current_host}. Nueva IP (vacío = cancelar): ").strip()
    if not new_ip:
        print("Sin cambios")
        return
    if not is_valid_ip(new_ip):
        print("IP inválida, use el formato x.x.x.x")
        return
    current_host = new_ip
    c.host = current_host  # pyModbusTCP reconecta solo en el próximo request
    print(f"IP actualizada a {current_host}")


# --------------------------------------------------------------------------
# Pruebas: watchdog
# --------------------------------------------------------------------------
def watchdog_set(c, enable):
    """enable=True habilita el watchdog, enable=False lo deshabilita."""
    if c.write_single_coil(COIL_WD_ENABLE, 1 if enable else 0):
        print(f"Watchdog {'habilitado' if enable else 'deshabilitado'}")
    else:
        print("ERROR cambiando estado del watchdog")


def watchdog_toggle_menu(c):
    """Pregunta al usuario si quiere habilitar o deshabilitar el watchdog."""
    resp = input("Watchdog: (1) Habilitar / (0) Deshabilitar: ").strip()
    if resp == "1":
        watchdog_set(c, True)
    elif resp == "0":
        watchdog_set(c, False)
    else:
        print("Opción inválida, no se modificó el watchdog")


def watchdog_read_status(c):
    limit = c.read_holding_registers(REG_WD_LIMIT_TIME, 1)
    wd_coils = c.read_coils(COIL_WD_ENABLE, 2)
    if limit is None or wd_coils is None:
        print("ERROR leyendo estado del watchdog")
        return
    print(f"Time limit: {limit[0]}  WD enable: {wd_coils[0]}  WD LED enable: {wd_coils[1]}")

def watchdog_set_time_limit(c, value):
    """Escribe el tiempo límite del watchdog (holding register 27).
    'value' queda en las unidades que maneje el firmware (ver definitions.h)."""
    if c.write_single_register(REG_WD_LIMIT_TIME, value):
        print(f"OK: tiempo límite de watchdog = {value}")
    else:
        print("ERROR escribiendo tiempo límite del watchdog")


def watchdog_set_time_limit_menu(c):
    """Pide por consola el nuevo tiempo límite del watchdog y lo escribe."""
    resp = input("Nuevo tiempo límite del watchdog (0-65535): ").strip()
    try:
        value = int(resp)
    except ValueError:
        print("Entrada inválida, debe ser un número entero")
        return
    if not (0 <= value <= 65535):
        print("Valor fuera de rango (0-65535)")
        return
    watchdog_set_time_limit(c, value)

# --------------------------------------------------------------------------
# Pruebas: entradas / salidas digitales
# --------------------------------------------------------------------------
def read_digital_inputs(c):
    """Lee las 13 entradas digitales (lógica activa-baja: 1 = pin en bajo)."""
    coils = c.read_coils(COILS_MAPPED_AT, NUM_DI)
    if coils is None:
        print("ERROR leyendo coils de entrada")
        return
    for i, val in enumerate(coils):
        print(f"DI_{i}: {val}")


def write_digital_outputs(c, values):
    """values: lista de 8 valores (0/1) para DO_0..DO_7."""
    if len(values) != NUM_DO:
        print(f"ERROR: se esperaban {NUM_DO} valores, llegaron {len(values)}")
        return
    if c.write_multiple_coils(COIL_WRITABLE_FROM, values):
        print("OK escribiendo salidas digitales")
    else:
        print("ERROR escribiendo salidas digitales")


def clear_digital_outputs(c):
    write_digital_outputs(c, [0] * NUM_DO)


def write_digital_outputs_menu(c):
    """Pide por consola qué DO prender (ej: '0,2,5') y apaga el resto."""
    resp = input(f"DO a prender (0-{NUM_DO - 1}, separados por coma, vacío = ninguna): ").strip()
    values = [0] * NUM_DO
    if resp:
        try:
            indices = [int(x) for x in resp.split(",")]
        except ValueError:
            print("Entrada inválida, use números separados por coma (ej: 0,2,5)")
            return
        for i in indices:
            if 0 <= i < NUM_DO:
                values[i] = 1
            else:
                print(f"DO_{i} fuera de rango, se ignora")
    write_digital_outputs(c, values)


# --------------------------------------------------------------------------
# Pruebas: salidas analógicas (A0, A1, A2)
# --------------------------------------------------------------------------
def write_analog_outputs(c, values):
    """values: lista de hasta 3 valores (0-65535) para A0, A1, A2."""
    if c.write_multiple_registers(REG_AO_START, values):
        print(f"OK escribiendo salidas analógicas: {values}")
    else:
        print("ERROR escribiendo salidas analógicas")


def ramp_a0(c, step=5000, max_value=65535, delay=0.5, round_trip=False):
    """Rampa en A0 (holding register 0), sin tocar A1/A2."""
    value = 0
    while value <= max_value:
        if not c.write_single_register(REG_AO_START, value):
            print("ERROR escribiendo registro")
            return
        cal = value * CALIBRATION_ADC[0] // 65535
        print(f"A0 = {value}  (~{cal} en el DAC tras calibración)")
        value += step
        time.sleep(delay)
    c.write_single_register(REG_AO_START, max_value)
    print(f"A0 = {max_value} (final)")

    if round_trip:
        value = max_value
        while value >= 0:
            c.write_single_register(REG_AO_START, value)
            print(f"A0 = {value}")
            value -= step
            time.sleep(delay)
        c.write_single_register(REG_AO_START, 0)


# --------------------------------------------------------------------------
# Pruebas: entrada analógica y contador de pulsos
# --------------------------------------------------------------------------
def read_analog_input_loop(c, delay=0.5):
    """Lee AI (reg 4, convertido a voltios) y contador de pulsos (reg 5) en loop.
    Apretar cualquier tecla corta el loop y vuelve al menú."""
    print("Leyendo... apretá cualquier tecla para cortar")
    while True:
        if msvcrt.kbhit():
            msvcrt.getch()  # consume la tecla para que no quede en el buffer
            print("Lectura detenida")
            break

        regs = c.read_holding_registers(4, 1)
        if regs is None:
            print("ERROR leyendo registros")
        else:
            print(regs)
            volts = adc_raw_to_volts(regs[0])
            #print(f"AI: {regs[0]} ({volts:.3f} V)   Pulsos: {regs[1]}")
        time.sleep(delay)


# --------------------------------------------------------------------------
# Pruebas: configuración de red
# --------------------------------------------------------------------------
def change_ip(c, ip):
    """ip: lista de 4 octetos, ej [192, 168, 0, 100]."""
    message = [
        ((ip[0] << 8) & 0xFF00) + (ip[1] & 0x00FF),
        ((ip[2] << 8) & 0xFF00) + (ip[3] & 0x00FF),
        0xFF00, 0, 0, 0,
    ]
    if c.write_multiple_registers(REG_COMMON_MAPPED_AT, message):
        print(f"OK cambiando IP a {'.'.join(map(str, ip))}")
    else:
        print("ERROR cambiando IP")


def read_network_config(c):
    regs = c.read_holding_registers(REG_COMMON_MAPPED_AT, 8)
    if regs is None:
        print("ERROR leyendo config de red")
        return
    print("IP: ", regs[0] >> 8, ".", regs[0] & 0xFF, ".", regs[1] >> 8, ".", regs[1] & 0xFF)
    print("NM: ", regs[2] >> 8, ".", regs[2] & 0xFF, ".", regs[3] >> 8, ".", regs[3] & 0xFF)
    print("GW: ", regs[4] >> 8, ".", regs[4] & 0xFF, ".", regs[5] >> 8, ".", regs[5] & 0xFF)
    print("Type: ", regs[6], ", Watchdog: ", regs[7])

def led_clear(c):
    """Envía un pulso al coil de clear del LED de falla.
    El firmware apaga fault_flag y blink_error_flag, y limpia el coil solo."""
    if c.write_single_coil(COIL_WD_LED_CLEAR, 1):
        print("OK: LED de falla apagado")
    else:
        print("ERROR apagando el LED de falla")

def change_dr(c, dr):
    """dr: 0 a 10."""
    
    if c.write_multiple_registers(REG_AI_MAPPED_AT, [dr]):
        print(f"OK cambiando dr a {dr}")
    else:
        print("ERROR cambiando dr")

def change_sp(c, sp):
    """sp: 0 a 10."""
    
    if c.write_multiple_registers(1, [sp]):
        print(f"OK cambiando sp a {sp}")
    else:
        print("ERROR cambiando sp")

def read_status(c):
    """Lee el coil de status START/STOP (coil 16)."""
    coil = c.read_coils(COIL_WRITABLE_FROM, 1)
    if coil is None:
        print("ERROR leyendo status")
        return
    estado = "START" if coil[0] else "STOP"
    print(f"Status (raw): {coil[0]}  ({estado})")


def set_status(c, status):
    """status: True = START (1), False = STOP (0)."""
    if c.write_single_coil(COIL_WRITABLE_FROM, 1 if status else 0):
        print(f"OK: status = {'START' if status else 'STOP'}")
    else:
        print("ERROR cambiando status")


def set_status_menu(c):
    """Pregunta al usuario si quiere poner START o STOP."""
    resp = input("Status: (1) START / (0) STOP: ").strip()
    if resp == "1":
        set_status(c, True)
    elif resp == "0":
        set_status(c, False)
    else:
        print("Opción inválida, no se modificó el status")



def set_mode(c, status):
    """status: True = ModBus (1), False = MANUAL (0)."""
    if c.write_single_coil(17, 1 if status else 0):
        print(f"OK: status = {'MB' if status else 'MANUAL'}")
    else:
        print("ERROR cambiando status")

def set_mode_menu(c):
    """Pregunta al usuario si quiere poner START o STOP."""
    resp = input("Status: (1) MB / (0) MANUAL: ").strip()
    if resp == "1":
        set_mode(c, True)
    elif resp == "0":
        set_mode(c, False)
    else:
        print("Opción inválida, no se modificó el status")
# --------------------------------------------------------------------------
# Menú
# --------------------------------------------------------------------------
MENU = {
    "1": ("Leer entradas digitales (una vez)", lambda c: read_digital_inputs(c)),
    "2": ("Prender salidas digitales a elección", lambda c: write_digital_outputs_menu(c)),
    "3": ("Apagar todas las salidas digitales", lambda c: clear_digital_outputs(c)),
    "4": ("Rampa en A0 (0 a máximo)", lambda c: ramp_a0(c)),
    "5": ("Rampa triangular en A0 (0 -> máximo -> 0)", lambda c: ramp_a0(c, round_trip=True)),
    "6": ("Leer entrada analógica (V) ", lambda c: read_analog_input_loop(c)),
    "7": ("Habilitar/deshabilitar watchdog", lambda c: watchdog_toggle_menu(c)),
    "8": ("Leer estado del watchdog", lambda c: watchdog_read_status(c)),
    "9": ("Leer configuración de red", lambda c: read_network_config(c)),
    "10": ("Cambiar IP DEL DISPOSITIVO a 192.168.0.100 (EEPROM)", lambda c: change_ip(c, [192, 168, 0, 100])),    
    "11": ("Cambiar a qué IP se conecta este script (sin reiniciar)", lambda c: change_host(c)),
    "12": ("Cambiar IP DEL DISPOSITIVO a 10.0.0.13 (EEPROM)", lambda c: change_ip(c, [10, 0, 0, 13])),
    "13": ("Apagar LED de falla (watchdog)", lambda c: led_clear(c)),
    "14": ("Cambiar tiempo límite del watchdog", lambda c: watchdog_set_time_limit_menu(c)),
    ## Para la VTC
    "15": ("Leer RS (una vez)", lambda c: read_rs(c)),
    "16": ("Leer RS en loop", lambda c: read_rs_loop(c)),
    "17": ("Leer RS/SP (una vez)", lambda c: read_rs_sp(c)),
    "18": ("Leer RS/SP en loop", lambda c: read_rs_sp_loop(c)),
    "19": ("Leer PV en loop", lambda c: read_pv_loop(c)),
    "20": ("Promedio de  PV", lambda c: read_pv_prom(c)),
    "21": ("Promedio de  RS", lambda c: read_rs_average(c)),
    "22": ("Promedio de  SP", lambda c: read_sp_average(c)),
    "23": ("Cambiar Drive Range", lambda c: change_dr(c, int(input("Ingrese drive range (0-10): ")))),
    "24": ("Leer status (START/STOP)", lambda c: read_status(c)),
    "25": ("Cambiar status (START/STOP)", lambda c: set_status_menu(c)),
    "26": ("Cambiar Set Point ", lambda c: change_sp(c, int(input("Ingrese drive range (0-10): ")))),
    "27": ("Cambiar mode (MB/MANUAL)", lambda c: set_mode_menu(c)),
}


def print_menu():
    print(f"\n=== SHOEBOX Modbus - Menú de pruebas (conectado a {current_host}) ===")
    for key, (desc, _) in MENU.items():
        print(f"  {key}: {desc}")
    print("  0: Salir")


def main():
    c = connect()
    while True:
        print_menu()
        choice = input("Opción: ").strip()
        if choice == "0":
            break
        entry = MENU.get(choice)
        if entry is None:
            print("Opción inválida")
            continue
        try:
            entry[1](c)
        except KeyboardInterrupt:
            print("\nInterrumpido")


if __name__ == "__main__":
    main()