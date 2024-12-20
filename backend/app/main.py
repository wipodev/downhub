from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir CORS para que la extensión de Chrome pueda hacer solicitudes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar dominios específicos en lugar de '*'
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data")
async def get_data():
    return {"message": "¡Hola desde el backend en FastAPI!"}

# Ejecuta el servidor con: uvicorn main:app --reload
