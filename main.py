from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definir el modelo de la base de datos
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    field_1 = Column(String, index=True)
    author = Column(String)
    description = Column(String)
    my_numeric_field = Column(Integer)

Base.metadata.create_all(bind=engine)

# Crear una instancia de FastAPI
app = FastAPI()

# Modelo de datos de entrada (POST)
class ItemCreate(BaseModel):
    field_1: str
    author: str
    description: str
    my_numeric_field: int

# Endpoint para recibir datos POST y guardarlos en la base de datos
@app.post("/input/{my_target_field}")
def create_item(
    my_target_field: str,
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    # Verificar si el campo objetivo es válido
    if my_target_field not in item.dict().keys():
        raise HTTPException(status_code=400, detail="Campo objetivo no válido")

    # Convertir el campo objetivo a mayúsculas
    setattr(item, my_target_field, getattr(item, my_target_field).upper())

    # Crear un nuevo objeto Item en la base de datos
    db_item = Item(**item.dict())

    # Guardar en la base de datos
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return {"id": db_item.id}

# Endpoint para obtener datos por ID
@app.get("/get_data/{id}")
def get_data(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

