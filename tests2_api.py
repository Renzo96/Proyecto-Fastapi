from fastapi import FastAPI, Request, Response,Depends, HTTPException
from tests2 import *
from fastapi.responses import PlainTextResponse, FileResponse,HTMLResponse, JSONResponse
from fastapi import Response,Depends,HTTPException, FastAPI, Form 
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
import pandas as pd
import pymysql
from starlette import responses

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# users = {
#     "Admin": "password123",
#     "Silvana": "password456"
# }


@app.get("/")
def home():
    html = leer_html('home.html')
    return responses.HTMLResponse(content=html, status_code=200)

sessions = {}

@app.get("/login")
async def login_form():
    return """
        <form method="post">
        <input type="text" name="username" placeholder="Enter your username"><br>
        <input type="password" name="password" placeholder="Enter your password"><br>
        <button type="submit">Login</button>
        </form>
    """

@app.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    conexion = pymysql.connect(
        host='localhost',
        database='database_silvana',
        user='root',
        password='root'
    )
    cursor = conexion.cursor()

    query = 'SELECT * FROM USUARIOS'
    cursor.execute(query)

    df = pd.read_sql_query(query, conexion)

    
    conexion.commit()
    conexion.close()

    username = credentials.username
    password = credentials.password


    if username in df['usuario'].values and password == df.loc[df['usuario'] == username, 'contraseña'].values[0]:
        sessions[username] = True
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.get("/scan_puertos")
def scan_puertos(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username

    if username not in sessions:
        return {"message": "You need to log in to execute this request."}
    #Fragmento del 68-70 es para txt, de no quererlo así descomentar línea 77 y comentar las mencionadas
    scan_info = port_scan(get_local_ip())
    scan_info_str = "\n".join([f"{k}: {v}" for k, v in scan_info.items()])

    response = Response(content=scan_info_str, media_type="text")
    response.headers["Content-Disposition"] = "attachment; filename=información_interfaz.txt"
    
    return response
    
    #return port_scan(get_local_ip())




# @app.get("/scan_puertos.txt")
# def scan_puertos(response:Response,credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     if username not in sessions:
#         return {"message": "You need to log in to execute this request."}
    
#     scan_info = port_scan(get_local_ip())
#     scan_info_str = "\n".join([f"{k}: {v}" for k, v in scan_info.items()])

#     response = Response(content=scan_info_str, media_type="text")
#     response.headers["Content-Disposition"] = "attachment; filename=información_interfaz.txt"
    
#     return response

@app.get("/informacion_interfaz")
def informacion_interfaz(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    
    if username not in sessions:
        return {"message": "You need to log in to execute this request."}
    
    #Fragmento del 105-108 es para txt, de no quererlo así descomentar línea 112 y comentar las mencionadas

    interfaz_info = get_interface_info()
    interfaz_info_str = "\n".join([f"{k}: {v}" for k, v in interfaz_info.items()])
    response = Response(content=interfaz_info_str, media_type="text")
    response.headers["Content-Disposition"] = "attachment; filename=información_interfaz.txt"
    
    return response
    
    #return get_interface_info()


# @app.get("/informacion_interfaz.txt")
# def informacion_interfaz(request:Request,response: Response, credentials : HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     if username not in sessions:
#         return {"message": "You need to log in to execute this request."}
    
#     interfaz_info = get_interface_info()
#     interfaz_info_str = "\n".join([f"{k}: {v}" for k, v in interfaz_info.items()])
#     response = Response(content=interfaz_info_str, media_type="text")
#     response.headers["Content-Disposition"] = "attachment; filename=información_interfaz.txt"
    
#     return response


# @app.get("/informacion_antivirus")
# def informacion_antivirus(request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     if username not in sessions:
#         return {"message": "You need to log in to execute this request."}
    
#     antivirus_info = get_antivirus()
#     if get_antivirus() == {'antivirus_software': []}:
#         message = "Antivirus_software: No posee un sistema de antivirus instalado.\nRecomendación: Debería instalar un sistema de antivirus en su ordenador para tener protección en tiempo real contra ataques de virus.\nPuede descargar su sitema de antivirus de las siguientes páginas:\nAvast: https://www.avast.com/es-ar/lp-ppc-free-av-brand?ppc_code=012&ppc=a&gad=1&gclid=CjwKCAjwjMiiB"
#         response=Response(content=message, media_type="text")
#         response.headers["Content-Disposition"] = "attachment; filename=informacion_antivirus.txt"
#         return response
#     elif  get_antivirus() == {'antivirus_software': result['is_up_to_date'] != True}:
#         message2 = "Su antivirus se encuentra desactualizado, proceda a actualizarlo"
#         response=Response(content=message2, media_type="text")
#         response.headers["Content-Disposition"] = "attachment; filename=informacion_antivirus.txt"
#         return response
#     else:
#         antivirus_info_str = "\n".join([f"{k}: {v}" for k, v in antivirus_info.items()])
#         response = Response(content=antivirus_info_str, media_type="text")
#         response.headers["Content-Disposition"] = "attachment; filename=información_antivirus.txt"
#         return response
    
@app.get("/informacion_antivirus")
def informacion_antivirus(request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if username not in sessions:
        return {"message": "You need to log in to execute this request."}
    
    antivirus_info = get_antivirus()
    if not antivirus_info['antivirus_software']:
        message = "Antivirus_software: No posee un sistema de antivirus instalado.\nRecomendación: Debería instalar un sistema de antivirus en su ordenador para tener protección en tiempo real contra ataques de virus.\nPuede descargar su sitema de antivirus de las siguientes páginas:\nAvast: https://www.avast.com/es-ar/lp-ppc-free-av-brand?ppc_code=012&ppc=a&gad=1&gclid=CjwKCAjwjMiiB"
        response = Response(content=message, media_type="text")
        response.headers["Content-Disposition"] = "attachment; filename=informacion_antivirus.txt"
        return response
    else:
        is_up_to_date = all(av['is_up_to_date'] for av in antivirus_info['antivirus_software'])
        if not is_up_to_date:
            message2 = "Su antivirus se encuentra desactualizado, proceda a actualizarlo"
            response = Response(content=message2, media_type="text")
            response.headers["Content-Disposition"] = "attachment; filename=informacion_antivirus.txt"
            return {"mensaje": message2, "antivirus_info": antivirus_info}
        else:
            antivirus_info_str = "\n".join([f"{k}: {v}" for k, v in antivirus_info.items()])
            response = Response(content=antivirus_info_str, media_type="text")
            response.headers["Content-Disposition"] = "attachment; filename=información_antivirus.txt"
            return response


# @app.get("/informacion_antivirus.txt")
# def informacion_antivirus(response:Response,credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     if username not in sessions:
#         return {"message": "You need to log in to execute this request."}
#     antivirus_info =  get_antivirus()
#     antivirus_info_str = "\n".join([f"{k}: {v}" for k, v in antivirus_info.items()])
#     response = Response(content=antivirus_info_str, media_type="text")
#     response.headers["Content-Disposition"] = "attachment; filename=información_antivirus.txt"
    
#     return response

@app.get("/informacion_sistema")
def informacion_sistema(request: Request,response: Response,credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if username not in sessions:
        return {"message": "You need to log in to execute this request."}
    
    #Fragmento del 172-175 es para txt, de no quererlo así descomentar línea 178 y comentar las mencionadas

    system_info = get_system_info()
    system_info_str = "\n".join([f"{k}: {v}" for k, v in system_info.items()])
    response = Response(content=system_info_str, media_type="text")
    response.headers["Content-Disposition"] = "attachment; filename=información_sistema.txt"
    
    return response
    #return get_system_info()

# @app.get("/informacion_sistema.txt")
# def informacion_sistema(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     if username not in sessions:
#         return {"message": "You need to log in to execute this request."}
    
#     system_info = get_system_info()
#     system_info_str = "\n".join([f"{k}: {v}" for k, v in system_info.items()])
    
#     response = Response(content=system_info_str, media_type="text")
#     response.headers["Content-Disposition"] = "attachment; filename=información_sistema.txt"
    
#     return response




@app.post("/logout")
async def logout(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if username in sessions:
        del sessions[username]
    return {"message": "Logged out successfully."}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)