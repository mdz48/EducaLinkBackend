
import enum


class GroupType(enum.Enum):
    Privado = "Privado"
    Publico = "Publico"
    
class EducationLevel(enum.Enum):
    Primaria = "Primaria"
    Preescolar = "Preescolar"
    
class State(enum.Enum):
    Activo = "Activo"
    Bloqueado = "Bloqueado" 
    
class PostStatus(enum.Enum):
    Disponible = "Disponible"
    Vendido = "Vendido"
    
class FileType(enum.Enum):
    PDF = "PDF"
    Image = "Image"
    Document = "Document"
    
class SaleType(enum.Enum):
    Material_didactico = "Material didactico"
    Recursos_de_clase = "Recursos de clase"
    Libros = "Libros"
    Juguetes = "Juguetes"
    Mobiliario = "Mobiliario"
    Decoracion = "Decoracion"
    Electronica = "Electronica" 
    Uniformes = "Uniformes"
    Otros = "Otros" 
    