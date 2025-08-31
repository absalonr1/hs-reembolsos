from fastapi import FastAPI, Response, status
import uvicorn
from pw_runner import run_playwright    

app = FastAPI()

@app.get("/run-reembolso")

def run_reembolso(response: Response):
    success = run_playwright()
    if success:
        response.status_code = status.HTTP_200_OK
        return {"message": "Proceso completado correctamente"}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Error en el proceso"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
