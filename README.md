# Trello Ticket Creator

![Python](https://img.shields.io/badge/language-Python-blue.svg)

Este proyecto permite crear tickets en Trello a partir de un archivo JSON. El script lee la información de las tareas desde el archivo JSON y crea las tarjetas correspondientes en Trello, incluyendo detalles como la descripción de la tarea, checklist, etiquetas y más.

## Requisitos Previos

Antes de ejecutar el script, asegúrate de tener los siguientes elementos configurados:

- Python 3.x instalado
- Una cuenta de Trello
- Un Personal Access Token de Trello (puedes generarlo desde [aquí](https://trello.com/app-key))
- Un archivo JSON con la estructura adecuada

## Instalación

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://github.com/tu-usuario/trello-ticket-creator.git
    cd trello-ticket-creator
    ```

2. Crea y activa un entorno virtual (opcional pero recomendado):

    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3. Instala las dependencias necesarias:

    ```bash
    pip install -r requirements.txt
    ```

4. Crea un archivo `.env` en la raíz del proyecto y define tus credenciales de Trello:

    ```plaintext
    TRELLO_API_KEY=your_trello_api_key
    TRELLO_TOKEN=your_trello_token
    TRELLO_BOARD=your_trello_board
    TRELLO_LIST=your_trello_list_id
    ```

## Formato del Archivo JSON

El archivo JSON debe tener la siguiente estructura:

```json
[
  {
    "nombre_tarea": "Nombre de la Tarea 1",
    "descripcion": "Breve descripción de la tarea 1, incluyendo contexto y objetivos",
    "detalles": {
      "historia_usuario": "",
      "valor_impacto": "",
      "esfuerzo_estimado": "",
      "dependencias": "",
      "notas_adicionales": ""
    },
    "checklist": [
      {"paso": "Paso 1", "completado": false},
      {"paso": "Paso 2", "completado": false},
      {"paso": "Paso 3", "completado": false}
    ],
    "asignado_a": "Nombre de la persona asignada",
    "etiquetas": ["prioridad-alta", "desarrollo"],
    "fecha_entrega": "YYYY-MM-DD",
    "comentarios": ""
  },
  {
    "nombre_tarea": "Nombre de la Tarea 2",
    "descripcion": "Breve descripción de la tarea 2, incluyendo contexto y objetivos",
    "detalles": {
      "historia_usuario": "",
      "valor_impacto": "",
      "esfuerzo_estimado": "",
      "dependencias": "",
      "notas_adicionales": ""
    },
    "checklist": [
      {"paso": "Paso 1", "completado": false},
      {"paso": "Paso 2", "completado": false},
      {"paso": "Paso 3", "completado": false}
    ],
    "asignado_a": "Nombre de la persona asignada",
    "etiquetas": ["prioridad-media", "diseño"],
    "fecha_entrega": "YYYY-MM-DD",
    "comentarios": ""
  }
]
```


## Ejecución del Script

Para ejecutar el script y crear los tickets en Trello, sigue estos pasos:

1.  Ejecuta el script:
    
    ```bash
    python create_trello_tickets.py
    ```
    
2.  Se te pedirá que ingreses si deseas usar las credenciales definidas en el archivo `.env`. Si no, podrás ingresar nuevas credenciales.
    
3.  Se te pedirá que ingreses la ruta del archivo JSON que contiene las tareas.
    

El script validará el archivo JSON y creará los tickets en la lista de Trello especificada.

## Notas

-   Asegúrate de que el archivo JSON tenga la estructura correcta.
-   Si hay errores en el JSON o en la creación de las tarjetas, el script mostrará mensajes de error adecuados.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para cualquier mejora o corrección.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.

