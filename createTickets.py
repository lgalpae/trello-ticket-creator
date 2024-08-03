import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
from colorama import Fore

class TrelloTicketCreator:
    BASE_URL = "https://api.trello.com/1"

    def __init__(self):
        load_dotenv()
        self.api_key = self.get_user_input("TRELLO_API_KEY", "Ingresa tu TRELLO_API_KEY: ")
        self.token = self.get_user_input("TRELLO_TOKEN", "Ingresa tu TRELLO_TOKEN: ")
        self.board_id = self.get_user_input("TRELLO_BOARD", "Ingresa tu TRELLO_BOARD: ")
        self.fetch_board_lists()  # Llamar a fetch_board_lists antes de solicitar el ID de la lista
        self.list_id = self.get_user_input("TRELLO_LIST", "Indica el ID de la lista donde quieres crear los tickets: ")
        self.json_file_path = input("\nIntroduce la ruta del archivo JSON de tickets:\n").strip()

    def get_user_input(self, env_var, prompt):
        if env_var == "TRELLO_LIST":
            default_list_id = os.getenv('TRELLO_LIST')
            use_default = input(f"¿Deseas usar el TRELLO_LIST ('{default_list_id}') definido en .env? (Y/n): ").strip().lower()
        else:
            use_default = input(f"¿Deseas usar el {env_var} definido en .env? (Y/n): ").strip().lower()

        if use_default == 'n':
            return input(prompt).strip()
        else:
            return os.getenv(env_var)

    def fetch_board_lists(self):
        url = f"{self.BASE_URL}/boards/{self.board_id}/lists?key={self.api_key}&token={self.token}"
        response = requests.get(url)
        if response.status_code == 200:
            listas = response.json()
            print("\n - Estas son las listas de tu tablero: ")
            for lista in listas:
                print(f"Lista: {lista['name']} - ID: {lista['id']}")
        else:
            print(Fore.RED + f"Error al obtener las listas del tablero: {response.text}")
            sys.exit(1)

    def obtener_id_etiqueta(self, etiqueta_nombre):
        url = f"{self.BASE_URL}/boards/{self.board_id}/labels?key={self.api_key}&token={self.token}"
        response = requests.get(url)
        if response.status_code == 200:
            etiquetas = response.json()
            for etiqueta in etiquetas:
                if etiqueta['name'] == etiqueta_nombre:
                    return etiqueta['id']
        url = f"{self.BASE_URL}/boards/{self.board_id}/labels?key={self.api_key}&token={self.token}&name={etiqueta_nombre}"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()['id']
        else:
            print(Fore.RED + f"Error al crear la etiqueta '{etiqueta_nombre}': {response.text}")
            return None

    def validar_estructura_json(self, data):
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
            if not self.validar_estructura_ticket(ticket, estructura_esperada):
                return False, "La estructura del archivo JSON no es válida."
        return True, ""

    def validar_estructura_ticket(self, ticket, estructura):
        if not isinstance(ticket, dict):
            return False
        for key, tipo in estructura.items():
            if key not in ticket:
                return False
            if isinstance(tipo, dict):
                if not self.validar_estructura_ticket(ticket[key], tipo):
                    return False
            elif not isinstance(ticket[key], tipo):
                return False
        return True

    def procesar_tickets(self):
        try:
            with open(self.json_file_path, encoding='utf-8') as f:
                data = json.load(f)
            es_valido, mensaje_error = self.validar_estructura_json(data)
            if not es_valido:
                print(Fore.RED + f"Error: {mensaje_error}")
                sys.exit(1)
            print("\nIniciando la creación de tickets en Trello...\n")
            for ticket_data in data:
                self.crear_ticket_en_trello(ticket_data)
        except FileNotFoundError:
            print(Fore.RED + f"Error: No se pudo encontrar el archivo '{self.json_file_path}'. Por favor, verifica la ruta e inténtalo de nuevo.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(Fore.RED + f"Error: El archivo '{self.json_file_path}' no es un JSON válido. Por favor, verifica el contenido e inténtalo de nuevo.")
            sys.exit(1)

    def crear_ticket_en_trello(self, ticket_data):
        descripcion = self.construir_descripcion(ticket_data)
        etiquetas_ids = [self.obtener_id_etiqueta(f"Team: {ticket_data['asignado_a']}")] + [self.obtener_id_etiqueta(etiqueta) for etiqueta in ticket_data['etiquetas'] if self.obtener_id_etiqueta(etiqueta)]
        etiquetas = ",".join(filter(None, etiquetas_ids))
        fecha_entrega = datetime.strptime(ticket_data['fecha_entrega'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        url = f"{self.BASE_URL}/cards?key={self.api_key}&token={self.token}&idList={self.list_id}&name={ticket_data['nombre_tarea']}&desc={descripcion}&idLabels={etiquetas}&due={fecha_entrega}"
        response = requests.post(url)
        if response.status_code == 200:
            print(Fore.GREEN + f"Ticket creado: {ticket_data['nombre_tarea']}")
        else:
            print(Fore.RED + f"Error al crear el ticket: {response.text}")

    def construir_descripcion(self, ticket_data):
        return f"{ticket_data['descripcion']}\n\n" \
               f"**Historia de Usuario:** {ticket_data['detalles']['historia_usuario']}\n\n" \
               f"**Valor de Impacto:** {ticket_data['detalles']['valor_impacto']}\n\n" \
               f"**Esfuerzo Estimado:** {ticket_data['detalles']['esfuerzo_estimado']}\n\n" \
               f"**Dependencias:** {ticket_data['detalles']['dependencias']}\n\n" \
               f"**Notas Adicionales:** {ticket_data['detalles']['notas_adicionales']}"

    def main(self):
        self.procesar_tickets()

if __name__ == "__main__":
    trello_ticket_creator = TrelloTicketCreator()
    trello_ticket_creator.main()
