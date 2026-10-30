import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# Crear el libro de Excel
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Lista de Alumnos"

# Definir los encabezados (deben coincidir con lo que lee tu sistema)
headers = ['Usuario (Username)', 'Nombres', 'Apellidos', 'Correo Electrónico']
ws.append(headers)

# Dar formato a los encabezados (Azul CITEN y letras blancas)
header_font = Font(color="FFFFFF", bold=True, size=12)
header_fill = PatternFill(start_color="0B2545", end_color="0B2545", fill_type="solid")
alignment = Alignment(horizontal="center", vertical="center")

for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = alignment

# Agregar 3 filas de ejemplo para que veas cómo llenarlo
alumnos_ejemplo = [
    ['alumno_juan', 'Juan Carlos', 'Pérez Gómez', 'juan.perez@citen.edu.pe'],
    ['alumno_maria', 'María Elena', 'Rodríguez Castro', 'maria.rodriguez@citen.edu.pe'],
    ['alumno_pedro', 'Pedro', 'Mendoza Ríos', 'pedro.mendoza@citen.edu.pe'],
]

for alumno in alumnos_ejemplo:
    ws.append(alumno)

# Ajustar el ancho de las columnas automáticamente
ws.column_dimensions['A'].width = 25
ws.column_dimensions['B'].width = 30
ws.column_dimensions['C'].width = 30
ws.column_dimensions['D'].width = 40

# Guardar el archivo
nombre_archivo = "Plantilla_Carga_Alumnos.xlsx"
wb.save(nombre_archivo)

print(f"¡Éxito! Se ha creado el archivo '{nombre_archivo}' en la carpeta de tu proyecto.")