import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Preguntar al usuario si desea usar las credenciales definidas en .env o ingresar otras
use_default_api_key = input("¿Deseas usar la TRELLO_API_KEY definida en .env? (Y/n): ").strip().lower()
if use_default_api_key == 'n':
    api_key = input("Ingresa tu TRELLO_API_KEY: ").strip()
else:
    api_key = os.getenv('TRELLO_API_KEY')

use_default_token = input("¿Deseas usar el TRELLO_TOKEN definido en .env? (Y/n): ").strip().lower()
if use_default_token == 'n':
    token = input("Ingresa tu TRELLO_TOKEN: ").strip()
else:
    token = os.getenv('TRELLO_TOKEN')

use_default_board = input("¿Deseas usar el TRELLO_BOARD definido en .env? (Y/n): ").strip().lower()
if use_default_board == 'n':
    board_id = input("Ingresa tu TRELLO_BOARD: ").strip()
else:
    board_id = os.getenv('TRELLO_BOARD')

# Consultamos las listas de ese tablero para que se indique en cuál se quieren crear los tickets

# Configura la URL para obtener las listas del tablero
url = f"https://api.trello.com/1/boards/{board_id}/lists?key={api_key}&token={token}"

# Realiza la solicitud GET para obtener las listas del tablero
response = requests.get(url)

if response.status_code == 200:
    # Convierte la respuesta JSON en un diccionario de Python
    listas = response.json()

    # Imprime el nombre de cada lista en el tablero
    print(f"\n - Estas son las listas de tu tablero: ")
    for lista in listas:
        print(f"Lista: {lista['name']} - ID: {lista['id']}")
else:
    print(f"Error al obtener las listas del tablero: {response.text}")
    sys.exit(1)  # Termina el script con un código de estado 1 indicando un error

default_list_id = os.getenv('TRELLO_LIST')
use_default_list = input(f"¿Deseas usar el TRELLO_LIST ('{default_list_id}') definido en .env? (Y/n): ").strip().lower()
if use_default_list == 'n':
    lista_id = input("\nIndica el ID de la lista donde quieres crear los tickets: ").strip().lower()
else:
    lista_id = os.getenv('TRELLO_LIST')


# Solicitar al usuario la ruta del archivo JSON
json_file_path = input("\nIntroduce la ruta del archivo JSON de tickets:\n").strip()


# Función para obtener el ID de una etiqueta existente o crearla si no existe
def obtener_id_etiqueta(etiqueta_nombre):
    # Buscar si la etiqueta ya existe en el tablero
    url = f"https://api.trello.com/1/boards/{board_id}/labels?key={api_key}&token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        etiquetas = response.json()
        for etiqueta in etiquetas:
            if etiqueta['name'] == etiqueta_nombre:
                return etiqueta['id']
    
    # Si la etiqueta no existe, crearla
    url = f"https://api.trello.com/1/boards/{board_id}/labels?key={api_key}&token={token}&name={etiqueta_nombre}"
    response = requests.post(url)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Error al crear la etiqueta '{etiqueta_nombre}': {response.text}")
        return None


def validar_estructura_json(data):
    # Definimos la estructura esperada
    estructura_esperada = {
        "nombre_tarea": str,
        "descripcion": str,
        "detalles": {
            "historia_usuario": str,
            "valor_impacto": str,
            "esfuerzo_estimado": str,
            "dependencias": str,
            "notas_adicionales": str
        },
        "checklist": list,
        "asignado_a": str,
        "etiquetas": list,
        "fecha_entrega": str,
        "comentarios": str
    }
    
    if not isinstance(data, list) or len(data) == 0:
        return False, "El archivo JSON debe contener una lista con al menos un elemento."

    for ticket in data:
        if not validar_estructura_ticket(ticket, estructura_esperada):
            return False, "La estructura del archivo JSON no es válida."

    return True, ""

def validar_estructura_ticket(ticket, estructura):
    if not isinstance(ticket, dict):
        return False

    for key, tipo in estructura.items():
        if key not in ticket:
            return False
        if isinstance(tipo, dict):
            if not validar_estructura_ticket(ticket[key], tipo):
                return False
        elif not isinstance(ticket[key], tipo):
            return False
        
    return True


# Lee el JSON desde el archivo con codificación UTF-8
try:
    with open(json_file_path, encoding='utf-8') as f:
        data = json.load(f)
    
    # Validar la estructura del archivo JSON
    es_valido, mensaje_error = validar_estructura_json(data)
    if not es_valido:
        print(f"Error: {mensaje_error}")
        sys.exit(1)  # Termina el script con un código de estado 1 indicando un error
except FileNotFoundError:
    print(f"Error: No se pudo encontrar el archivo '{json_file_path}'. Por favor, verifica la ruta e inténtalo de nuevo.")
    sys.exit(1)  # Termina el script con un código de estado 1 indicando un error
except json.JSONDecodeError:
    print(f"Error: El archivo '{json_file_path}' no es un JSON válido. Por favor, verifica el contenido e inténtalo de nuevo.")
    sys.exit(1)  # Termina el script con un código de estado 1 indicando un error


# Itera sobre los datos y crea tickets en Trello
for ticket_data in data:
    # Construye la descripción del ticket
    descripcion = f"{ticket_data['descripcion']}\n\n"
    descripcion += f"**Historia de Usuario:** {ticket_data['detalles']['historia_usuario']}\n\n" \
                  f"**Valor de Impacto:** {ticket_data['detalles']['valor_impacto']}\n\n" \
                  f"**Esfuerzo Estimado:** {ticket_data['detalles']['esfuerzo_estimado']}\n\n" \
                  f"**Dependencias:** {ticket_data['detalles']['dependencias']}\n\n" \
                  f"**Notas Adicionales:** {ticket_data['detalles']['notas_adicionales']}"

    # Crear o obtener el ID de la etiqueta asignada al equipo
    etiqueta_asignado_a = obtener_id_etiqueta(f"Team: {ticket_data['asignado_a']}")

    # Crear o obtener el ID de cada etiqueta
    etiquetas_ids = []
    for etiqueta_nombre in ticket_data['etiquetas']:
        etiqueta_id = obtener_id_etiqueta(etiqueta_nombre)
        if etiqueta_id:
            etiquetas_ids.append(etiqueta_id)

    # Si existe una etiqueta para el asignado, añadirlo a la lista de etiquetas
    if etiqueta_asignado_a:
        etiquetas_ids.append(etiqueta_asignado_a)
        
    # Convertir la lista de IDs de etiquetas en una cadena separada por comas
    etiquetas = ",".join(etiquetas_ids)

     # Obtener la fecha de entrega
    fecha_entrega = datetime.strptime(ticket_data['fecha_entrega'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    # Crear la tarjeta en Trello
    url = f"https://api.trello.com/1/cards?key={api_key}&token={token}&idList={lista_id}&name={ticket_data['nombre_tarea']}&desc={descripcion}&idLabels={etiquetas}&due={fecha_entrega}"
    response = requests.post(url)
    if response.status_code == 200:
        card_id = response.json()['id']

        # Construir la lista de verificación "TODO" con todos los items
        checklist_items = []
        for paso in ticket_data['checklist']:
            checklist_items.append({"name": paso['paso'], "pos": "bottom"})

        # Crear la lista de verificación "TODO" en la tarjeta
        url = f"https://api.trello.com/1/checklists?key={api_key}&token={token}&idCard={card_id}&name=TODO&pos=bottom"
        response = requests.post(url)
        if response.status_code == 200:
            checklist_id = response.json()['id']

            # Agregar los items a la lista de verificación "TODO"
            for item in checklist_items:
                url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems?key={api_key}&token={token}"
                response = requests.post(url, data=item)
                if response.status_code != 200:
                    print(f"Error al agregar item a la lista de verificación 'TODO': {response.text}")

            print(f"Ticket creado: {ticket_data['nombre_tarea']}")
        else:
            print(f"Error al crear la lista de verificación 'TODO': {response.text}")
    else:
        print(f"Error al crear el ticket: {response.text}")




