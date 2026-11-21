# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

Proyecto colaborativo desarrollado para la **Fase 4 (Prácticas Simuladas)** del curso **Programación (213023)** de la **Universidad Nacional Abierta y a Distancia (UNAD)** – Programa de Ingeniería de Sistemas.

## Descripción del Proyecto
Aplicación orientada a objetos desarrollada en **Python** (sin motores de bases de datos) que gestiona clientes, servicios especializados y reservas en memoria mediante listas internas y objetos, registrando todos los eventos y errores en un archivo de logs (`software_fj.log`) para garantizar estabilidad continua ante fallos.

## Arquitectura y Características Implementadas
- **Programación Orientada a Objetos (POO):**
  - Clase abstracta base `EntidadSistema` y clase abstracta `Servicio`.
  - Encapsulación y validaciones estrictas en `Cliente`.
  - Herencia y polimorfismo en tres servicios especializados: `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`.
  - Sobrecarga de métodos en `calcular_costo()` con parámetros opcionales (`impuesto` y `descuento`).
  - Clase `Reserva` con gestión de estados (`PENDIENTE`, `CONFIRMADA`, `PROCESADA`, `CANCELADA`).
- **Manejo Avanzado de Excepciones:**
  - Jerarquía de excepciones personalizadas (`ErrorSoftwareFJ`, `DatosInvalidosError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `CalculoInconsistenteError`).
  - Uso de bloques `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from ...`).
  - Registro automático en `software_fj.log` mediante el módulo `logging`.
- **Simulaciones:** Más de 10 operaciones completas (válidas e inválidas) ejecutadas sin interrumpir la aplicación.

## Estructura del Repositorio
```text
Fase4-SoftwareFJ-213023/
├── main.py              # Código fuente completo y documentado
├── software_fj.log      # Registro de eventos y errores generado al ejecutar
└── README.md            # Documentación del proyecto
