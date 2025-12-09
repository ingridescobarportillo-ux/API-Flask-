import uuid

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from contextlib import contextmanager
from urllib.parse import quote

# ----------------------------------------------------
# Configuración de la Base de Datos y el Modelo
# ----------------------------------------------------

# ¡IMPORTANTE!: Reemplaza 'usuario', 'clave', 'host' y 'nombre_db' con tus credenciales reales de MySQL.
# Asegúrate de haber instalado 'PyMySQL' (pip install PyMySQL).
DATABASE_USER = "dbflaskinacap"
DATABASE_PASSWD = quote("1N@C@P_alumn05")
DATABASE_HOST = "mysql.flask.nogsus.org"
DATABASE_NAME = "api_alumnos"
DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWD}@{DATABASE_HOST}/{DATABASE_NAME}"
# DATABASE_URL = f"mysql+pymysql://dbflaskinacap:P_alumn05@mysql.flask.nogsus.org/api_alumnos"

# Inicializa el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Base declarativa que será la madre de todas nuestras clases de modelos
Base = declarative_base()

# ----------------------------------------------------
# Definición de la clase de la tabla (función que genera la tabla usuario)
# ----------------------------------------------------
class Usuario(Base):
    __tablename__ = 'imep_usuario'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text(100000), index=True)
    apellido = Column(String(150), index=True)
    usuario = Column(String(50), index=True)
    clave = Column(String(50), index=True)
    api_key = Column(String(250), index=True)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "apellido": self.apellido,
                "usuario": self.usuario, "clave": self.clave, "api_key": self.api_key}

class Mercado(Base):
    __tablename__ = 'imep_mercados'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), index=True)

    productos = relationship("Producto", back_populates="origen_mercado", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}

class Producto(Base):
    __tablename__ = 'imep_productos'

    id = Column(Integer, primary_key=True, index=True)
    idOrigen = Column(Integer, ForeignKey('imep_mercados.id'), nullable=False, index=True)
    nombre = Column(String(150), index=True)
    uMedida = Column(String(100), index=True)
    precio = Column(Integer, index=True)

    origen_mercado = relationship("Mercado", back_populates="productos")

    def to_dict(self):
        return {"id": self.id, "idOrigen": self.idOrigen, "nombre": self.nombre,
                "uMedida": self.uMedida, "precio": self.precio,
                # Incluimos el nombre del mercado para facilitar la lectura en el frontend
                "origen_mercado": self.origen_mercado.nombre if self.origen_mercado else None
                }


# ----------------------------------------------------
# Sesiones locales para interactuar con la DB
# ----------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ----------------------------------------------------
# Función de Control de Conexión (Context Manager)
# ----------------------------------------------------

@contextmanager
def get_db():
    """
    Función que controla la conexión a la base de datos (sesión).
    Garantiza que la sesión se cierre correctamente después de su uso.
    """
    db = SessionLocal()
    try:
        # Entrega la sesión de DB al bloque 'with'
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ----------------------------------------------------
# Función de Inicialización
# ----------------------------------------------------

"""
TODO(Función de Inicialización)
"""

# ----------------------------------------------------
# Funciones de consultas
# ----------------------------------------------------

def valida_usuario(usrname, passwd):
    try:
        with get_db() as db:
            user = db.query(Usuario).filter(Usuario.usuario == usrname, Usuario.clave == passwd).first()

            if user:
                user.api_key = uuid.uuid4().hex
                db.commit()
                db.refresh(user)
                return user

            return False

    except Exception as e:
        print(f"Lib: models.py. Func: valida_usuario. Lin(107). Error al listar el usuario: {e}")
        return {"error": "Error interno del servidor al listar usuarios. Verifique la DB."}