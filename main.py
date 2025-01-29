from pyModbusTCP.client import ModbusClient
import time

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    c = ModbusClient(host="10.0.0.0", auto_open=True, auto_close=True, timeout=1)

    option = 1

    if option == 12:
        while True:
            print(c.read_holding_registers(0, 3))

    # set autofilter
    if option == 10:
        if not c.write_multiple_coils(16, [0]):
            print('ERROR')
        print("END")

    # Change ODR
    if option == 11:
        if not c.write_multiple_registers(4, [14]):
            print('ERROR')
        print("END")


    # Change IP
    if option == 1:
        IP = [192,168,0,100]
        message = [((IP[0] << 8) & 0xFF00) + (IP[1] & 0x00FF), ((IP[2] << 8) & 0xFF00) + (IP[3] & 0x00FF),0xFF00, 0, 0,0]

        regs = 0
        start_time = time.time()  # Captura el tiempo actual antes de ejecutar la instrucción
        if not c.write_multiple_registers(20, message):
            print("RETORNO ERROR")
        end_time = time.time()  # Captura el tiempo actual después de ejecutar la instrucción
        elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
        print(f"hasta acá: {elapsed_time} segundos")

        c = ModbusClient(host="10.0.0.15", auto_open=True, auto_close=True, timeout=1000)
        regs = c.read_holding_registers(20, 8)
        regs = c.read_holding_registers(20, 8)
        regs = c.read_holding_registers(20, 8)
        if regs is None:
            print("ERROR READING")
        else:
            print(regs)
            end_time = time.time()  # Captura el tiempo actual después de ejecutar la instrucción
            elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
            print(f"Tiempo de ejecución: {elapsed_time} segundos")

            regs = c.read_holding_registers(20, 8)
            print("IP: ", regs[0] >> 8, ".", regs[0] & 0xFF, ".", regs[1] >> 8, ".", regs[1] & 0xFF)
            print("NM: ", regs[2] >> 8, ".", regs[2] & 0xFF, ".", regs[3] >> 8, ".", regs[3] & 0xFF)
            print("GW: ", regs[4] >> 8, ".", regs[4] & 0xFF, ".", regs[5] >> 8, ".", regs[5] & 0xFF)
            print("Type: ", regs[6], ", Watchdog: ", regs[7])

    if option == 2:
        # print(c.write_multiple_registers(0, [0,0,10000,0]))
        #print(c.write_multiple_coils(16, [0]))
        #c.write_multiple_registers(4, [13])
       c.write_multiple_registers(5, [0])
        # Save filter & ODR setting

    if option == 3:  # Read values
        regs = c.read_holding_registers(20, 8)
        print("IP: ", regs[0] >> 8, ".", regs[0] & 0xFF, ".", regs[1] >> 8, ".", regs[1] & 0xFF)
        print("NM: ", regs[2] >> 8, ".", regs[2] & 0xFF, ".", regs[3] >> 8, ".", regs[3] & 0xFF)
        print("GW: ", regs[4] >> 8, ".", regs[4] & 0xFF, ".", regs[5] >> 8, ".", regs[5] & 0xFF)
        print("Type: ", regs[6], ", Watchdog: ", regs[7])
        c.close()

    if option == 4:
        message = [5, 4]
        start_time = time.time()  # Captura el tiempo actual antes de ejecutar la instrucción
        if not c.write_multiple_registers(4, message):
            print("RETORNO ERROR")
        end_time = time.time()  # Captura el tiempo actual después de ejecutar la instrucción
        elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
        print(f"hasta acá: {elapsed_time} segundos")

        c = ModbusClient(host="10.0.0.15", auto_open=True, auto_close=True, timeout=10)
        regs = c.read_holding_registers(5, 2)
        if regs is None:
            print("ERROR READING")
        else:
            print(regs)
            end_time = time.time()  # Captura el tiempo actual después de ejecutar la instrucción
            elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
            print(f"Tiempo de ejecución: {elapsed_time} segundos")
            print(regs)

    if option == 5:
        if not c.write_multiple_coils(26, [2]):
            print('ERROR')
        print("END")

    if option == 6:
        if not c.write_multiple_registers(0, [5698, 6352]):
            print('ERROR')
        reg=c.read_holding_registers(0, 3)
        print(reg)
        print("END")

    # Write Watchdog
    if option == 7:

        if not c.write_multiple_coils(24, [0,0]):
            print('ERROR COIL')
        print("END")
        if not c.write_multiple_registers(27, [100]):
            print('error register')

    # Read Watchdog
    if option == 8:
        limit = c.read_holding_registers(27, 1)
        wd_coils = c.read_coils(24, 2)
        wd_enable = wd_coils[0]
        wd_led_enable = wd_coils[1]
        print("Time limit: ", limit)
        print("WD enable: ", wd_enable, " WD LED enable: ", wd_led_enable)

    if option == 9:
        while True:
            if not print(c.read_holding_registers(0, 3)):
                print('ERROR REG')
            print("END")


