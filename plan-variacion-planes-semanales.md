# Plan: Variación automática de planes semanales — DietaMex 45+

## Objetivo
Evitar que el cliente reciba el mismo menú semana tras semana. El sistema debe detectar la semana actual y alternar entre al menos 2 versiones del plan, y en el futuro poder escalar a 4 o más.

## Alcance (fase 1)
1. Detectar la semana actual del año automáticamente.
2. Seleccionar el plan corresponds a la semana (A / B) usando una regla predecible.
3. Generar el PDF correspondiente al plan seleccionado.
4. Enviar el PDF al correo del usuario automáticamente al suscribirse o solicitarlo.
5. Permitir que, si el usuario ya tiene la landing cargada un martes, vea el plan correcto sin intervención humana.

## Regla de selección de plan
- Semanas pares → Plan Semanal A  
- Semanas impares → Plan Semanal B

Esto asegura una alternancia perfecta sin repetir menús en semanas consecutivas y sin necesidad de base de datos ni sistema de turnos complejo.

## Estructura del plan semanal (2 versiones)

### Plan A (semana par)
| Día       | Enfoque          |
|-----------|------------------|
| Lunes     | Frijoles         |
| Martes    | Pescado          |
| Miércoles | Lentejas         |
| Jueves    | Res magra        |
| Viernes   | Pavo             |
| Sábado    | Hidratación      |
| Domingo   | Descanso         |

### Plan B (semana impar)
| Día       | Enfoque          |
|-----------|------------------|
| Lunes     | Pollo            |
| Martes    | Vegetariano      |
| Miércoles | Pescado blanco   |
| Jueves    | Cerdo magro      |
| Viernes   | Pavo             |
| Sábado    | Frutas           |
| Domingo   | Descanso         |

> Ambas versiones respetan 1.500 kcal, estándares mexicanos, < 2 g de sal, 4-6 comidas por día.

## Plan de implementación

### Backend (Python)
1. Endpoint `api/current-plan` que reciba `email` y devuelva el PDF según la semana actual.
2. Función `get_week_number()` para determinar semana par/impar.
3. Diccionario de planes A y B con recetas, macros y etiquetas.
4. Generación dinámica de PDF con ReportLab (ya tenemos el script base).
5. Envío automático por correo (usar skill AgentMail existente).

### Frontend (landing)
1. Botón "Descargar plan de esta semana" → consulta a `/api/current-plan`.
2. Si el usuario ya tenía el PDF guardado, el backend devuelve el archivo actualizado.
3. Si el usuario se suscribe, se envía el PDF correspondiente a la semana en curso.

### Email automático
- Al suscribirse, el sistema envía el PDF del plan correspondiente.
- Asunto: `Tu plan semanal DietaMex 45+ — Semana {N}`
- Cuerpo breve recordando los 4-6 tiempos de comida y la caminata.

## Consideraciones futuras
- Escalar a 4 planes (A, B, C, D) para rotar cada 4 semanas.
- Permitir al usuario cambiar sus preferencias (ej. sin pescado) y regenerar su plan personalizado.
- Agregar recordatorios por Telegram/correo: “Mañana cambia el plan, ya tienes la nueva versión lista”.
