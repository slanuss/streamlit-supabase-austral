# app_pages.py
# Este archivo auxiliar importa las funciones de tus páginas desde la carpeta 'pages'

# Importa las funciones principales de las páginas renombradas
# Asegúrate de que los archivos existan en 'pages/' y estén renombrados con un guion bajo
from pages._donante import donante_page
from pages._beneficiario import beneficiario_page
# from pages._hospital import hospital_page # Descomentar cuando la crees

# Puedes definir aquí una función que contenga un diccionario de las páginas
# Esto facilita el manejo en Inicio.py
def get_pages_dict():
    return {
        "Donante": donante_page,
        "Beneficiario": beneficiario_page,
        # "Hospital": hospital_page, # Descomentar cuando la crees
    }