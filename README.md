# SHOEBOX Modbus - Script de pruebas

Script de pruebas por Modbus TCP para el dispositivo SHOEBOX (firmware STM32F207VET6).
Permite leer/escribir entradas y salidas digitales, salidas y entrada analógica, manejar
el watchdog y la configuración de red, todo desde un menú por consola.

## Requisitos

```
pip install pyModbusTCP
```

Pensado para correr en **Windows** (usa `msvcrt` para detectar teclas sin bloquear un loop).

## Cómo correrlo

```
python shoebox_modbus.py
```

Al arrancar se conecta a la IP definida en `DEFAULT_HOST` (por defecto `10.0.0.10`, la
misma que trae el firmware de fábrica). El menú se repite indefinidamente hasta que se
elige la opción `0` para salir.

## Menú

| Opción | Qué hace |
|---|---|
| 1 | Lee las 13 entradas digitales (DI_0 a DI_12). **Lógica activa-baja**: `1` = pin en bajo (activado), `0` = pin en alto. |
| 2 | Pregunta qué salidas digitales (DO_0 a DO_7) prender (ej: `0,2,5`) y apaga el resto. **Lógica directa**: `1` = salida en alto. |
| 3 | Apaga todas las salidas digitales. |
| 4 | Rampa en A0 (holding register 0) de 0 al máximo, en escalones de a 5000 cada 0.5 s. |
| 5 | Igual que la 4, pero además baja de nuevo a 0 (rampa triangular). |
| 6 | Lee en loop la entrada analógica (convertida a voltios) y el contador de pulsos de DI_0. Se corta apretando cualquier tecla. |
| 7 | Habilita o deshabilita el watchdog (pregunta cuál de las dos). |
| 8 | Lee el estado actual del watchdog (límite de tiempo, habilitado, LED). |
| 9 | Lee la configuración de red actual del dispositivo (IP, máscara, gateway, tipo). |
| 10 | Cambia la IP **del dispositivo** a `192.168.0.100` (se escribe en la EEPROM del equipo). |
| 11 | Cambia a qué IP se conecta **este script**, sin reiniciar la consola (útil si hay que probar otra placa). |

## Mapa Modbus (de `definitions.h`)

**Coils**
- `0-12`: entradas digitales (DI_0 a DI_12), solo lectura
- `16-23`: salidas digitales (DO_0 a DO_7), escritura
- `24`: habilitar/deshabilitar watchdog
- `25`: watchdog LED enable
- `26`: watchdog LED clear

**Holding registers**
- `0-2`: salidas analógicas A0, A1, A2 (0-65535), escritura
- `4`: entrada analógica (única, ADC ADS8866), solo lectura
- `5`: contador de pulsos en DI_0, solo lectura
- `20+`: configuración de red (IP, máscara, gateway)
- `27`: límite de tiempo del watchdog
- `29`: fecha guardada en NVM

## Notas importantes

- **Watchdog**: si está habilitado y no hay tráfico Modbus durante el tiempo límite
  configurado (por defecto 30 × 100 ms = 3 s), el firmware apaga solo todas las salidas
  digitales y analógicas. Para pruebas manuales largas, conviene deshabilitarlo (opción 7)
  o mantener alguna lectura periódica corriendo.
- **Calibración de las salidas analógicas**: el valor escrito no sale igual al DAC; el
  firmware aplica una constante de calibración por canal (`CALIBRATION_ADC`, distinta para
  A0/A1/A2) antes de mandarlo al DAC8551.
- **Entrada analógica**: hay un solo canal físico (ADS8866, ADC de un solo canal), no tres
  como en otros modelos de la misma familia de dispositivos (DIO/AI/AO/AIO). El rango
  0-65535 crudo se asume equivalente a 0-4 V; si el rango real de la placa es otro, ajustar
  la constante `ADC_MAX_VOLTAGE` en el script.