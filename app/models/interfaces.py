
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
    Recursos_de_clases = "Recursos de clases"
    Libros = "Libros"
    Jueguetes = "Jueguetes"
    Mobiliario = "Mobiliario"
    Decoracion = "Decoracion"
    Electronica = "Electronica"
    Otros = "Otros"
    