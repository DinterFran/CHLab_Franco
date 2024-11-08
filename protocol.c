#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <math.h>

// Implementación del algoritmo de Goertzel
int16_t tone_45[] = {
0, 3536, -5000, 3536, 0, -3536, 5000, -3536, 0, 3536, 
-5000, 3536, 0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 
0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 
5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 5000, -3536, 
0, 3536, -5000, 3536, 0, -3536, 5000, -3536, 0, 3536, 
-5000, 3536, 0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 
0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 
5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 5000, -3536, 
0, 3536, -5000, 3536, 0, -3536, 5000, -3536, 0, 3536, 
-5000, 3536, 0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 
0, -3536, 5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 
5000, -3536, 0, 3536, -5000, 3536, 0, -3536, 5000, -3536

};
// Detecta la presencia de una frecuencia específica en una señal
float magnitud = 0;

typedef struct {
    float coeff;          // Coeficiente del algoritmo
    float q1;            // Estado previo 1
    float q2;            // Estado previo 2
    float sine;          // Valor del seno
    float cosine;        // Valor del coseno
    float magnitude;     // Magnitud de la frecuencia detectada
    int n;              // Contador de muestras
} goertzel_state_t;

void goertzel_init(goertzel_state_t *state, float frequency, float sampling_rate, int block_size) {
    float omega = 2.0f * 3.14159f * frequency / sampling_rate;
    state->coeff = 2.0f * cosf(omega);
    state->sine = sinf(omega);
    state->cosine = cosf(omega);
    state->q1 = 0;
    state->q2 = 0;
    state->n = 0;
}

void goertzel_process(goertzel_state_t *state, float sample) {
    float q0 = state->coeff * state->q1 - state->q2 + sample;
    state->q2 = state->q1;
    state->q1 = q0;
    state->n++;
}

float goertzel_magnitude(goertzel_state_t *state) {
    float real = state->q1 - state->q2 * state->cosine;
    float imag = state->q2 * state->sine;
    state->magnitude = sqrtf(real*real + imag*imag)/120;
    
    // Reiniciar estados
    state->q1 = 0;
    state->q2 = 0;
    state->n = 0;
    
    return state->magnitude;
}



int main() {
    // Inicializar el estado de Goertzel
    goertzel_state_t estado;
    float frecuencia = 6000.0f;  // 1kHz
    float tasa_muestreo = 16000.0f; // 16kHz
    int tamano_bloque = 0;

    goertzel_init(&estado, frecuencia, tasa_muestreo, tamano_bloque);

    // Generar datos de prueba (una señal simple)
    float muestras[120];
    for(int i = 0; i < 120; i++) {
        muestras[i] = sinf(2.0f * 3.14159f * frecuencia * i / tasa_muestreo);
    }

    // Medir el tiempo de procesamiento
    clock_t inicio = clock();

    // Procesar las muestras
    for(int j = 0; j < 100; j++) {

        goertzel_init(&estado, frecuencia, tasa_muestreo, tamano_bloque);
        
        for(int i = 0; i < 120; i++) {
            goertzel_process(&estado, tone_45[i]);
        }

        magnitud = goertzel_magnitude(&estado);
    }
    

    clock_t fin = clock();
    double tiempo_total = (double)(fin - inicio) / CLOCKS_PER_SEC;

    printf("Magnitud detectada: %f\n", magnitud);
    printf("Tiempo de procesamiento: %f microsegundos\n", tiempo_total * 1000000);

    return 0;
}
