# Cosas el trabajo
forma de pasarle los datos al serial Ploter de VS
printf(">m:%d, w:%d pt: %d\r\n", mat_motor_value, system_status.actual_motor_value, poteTable[(system_status.actual_motor_value - MIN_F) / DELTA_F]);
