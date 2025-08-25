#include <iostream>
#include <windows.h>
#include <string>
#include <sstream>
#include <cstdlib> // Para std::atoi

// Definiciones
#define MAESTRO_ADDRESS 0x0C // Dirección por defecto de la Maestro (puede variar)

// Función para convertir microsegundos a unidades de target de la Maestro (0.25 µs)
unsigned short usATarget(unsigned short microsegundos) {
    return static_cast<unsigned short>(microsegundos * 4);
}

// Función para abrir el puerto serial
HANDLE abrirPuertoSerial(const std::string& nombrePuerto) {
    HANDLE hSerial = CreateFileA(nombrePuerto.c_str(),
                               GENERIC_READ | GENERIC_WRITE,
                               0,
                               NULL,
                               OPEN_EXISTING,
                               0, // No overlapped I/O
                               NULL);

    if (hSerial == INVALID_HANDLE_VALUE) {
        std::cerr << "Error al abrir el puerto " << nombrePuerto << ". Error: " << GetLastError() << std::endl;
    }
    return hSerial;
}

// Función para configurar los parámetros del puerto serial
bool configurarPuertoSerial(HANDLE hSerial) {
    DCB dcbSerialParams = {0};
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);

    if (!GetCommState(hSerial, &dcbSerialParams)) {
        std::cerr << "Error al obtener el estado del puerto. Error: " << GetLastError() << std::endl;
        return false;
    }

    dcbSerialParams.BaudRate = CBR_115200; // Velocidad de baudios por defecto de la Maestro
    dcbSerialParams.ByteSize = 8;
    dcbSerialParams.Parity = NOPARITY;
    dcbSerialParams.StopBits = ONESTOPBIT;

    if (!SetCommState(hSerial, &dcbSerialParams)) {
        std::cerr << "Error al establecer el estado del puerto. Error: " << GetLastError() << std::endl;
        return false;
    }
    return true;
}

// Función para enviar un comando a la Maestro
bool enviarComando(HANDLE hSerial, const unsigned char* comando, int longitud) {
    DWORD bytesEscritos;
    if (!WriteFile(hSerial, comando, longitud, &bytesEscritos, NULL)) {
        std::cerr << "Error al escribir en el puerto. Error: " << GetLastError() << std::endl;
        return false;
    }
    return true;
}

// Función para establecer el objetivo de un servo
bool setTarget(HANDLE hSerial, unsigned char canal, unsigned short objetivo) {
    unsigned char comando[] = {
        0x84, // Comando Set Target
        canal,
        static_cast<unsigned char>(objetivo & 0x7F),       // 7 bits menos significativos
        static_cast<unsigned char>((objetivo >> 7) & 0x7F) // 7 bits más significativos
    };
    return enviarComando(hSerial, comando, sizeof(comando));
}

int main(int argc, char *argv[]) {
    std::string puertoCOM = "\\\\.\\COM5"; // **¡VERIFICA ESTE PUERTO!**
    HANDLE hSerial = abrirPuertoSerial(puertoCOM);

    if (hSerial == INVALID_HANDLE_VALUE) {
        return 1;
    }

    if (!configurarPuertoSerial(hSerial)) {
        CloseHandle(hSerial);
        return 1;
    }

    if (argc != 3) {
        std::cerr << "Uso: " << argv[0] << " <numero_servo> <posicion_us>" << std::endl;
        CloseHandle(hSerial);
        return 1;
    }

    int numeroServo = std::atoi(argv[1]);
    int posicionUS = std::atoi(argv[2]);

    if (numeroServo < 0 || numeroServo > 11 || posicionUS < 250 || posicionUS > 2500) {
        std::cerr << "Error: Numero de servo debe estar entre 0 y 11, y la posicion entre 500 y 2500 us." << std::endl;
        CloseHandle(hSerial);
        return 1;
    }

    std::cout << "Moviendo servo " << numeroServo << " a " << posicionUS << " us..." << std::endl;

    if (setTarget(hSerial, static_cast<unsigned char>(numeroServo), usATarget(static_cast<unsigned short>(posicionUS)))) {
        std::cout << "Servo " << numeroServo << " movido a: " << posicionUS << " us" << std::endl;
    } else {
        std::cerr << "Error al mover el servo " << numeroServo << "." << std::endl;
    }

    CloseHandle(hSerial); // Cierra el puerto serial al finalizar
    std::cout << "Puerto serial cerrado." << std::endl;

    return 0;
}