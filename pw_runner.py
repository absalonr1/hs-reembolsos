import time
from playwright.sync_api import sync_playwright
from datetime import datetime
import locale
from s3_path import build_s3_base
import boto3
import os
from dotenv import load_dotenv
import uuid
import pytz
from datetime import datetime,timezone

load_dotenv()

contador = 1
bucket_name = os.environ.get("S3_BUCKET")


def takescreenshot(page, error=None,s3_save=False,basePath=None):
    global contador
    timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    fileName = ""
    
    if error is None:
        fileName = f"paso_{contador}_{timestamp}.jpeg"        
    else:
        fileName = f"error_{contador}_{timestamp}_ERROR.jpeg"

    page.screenshot(path=fileName, type="jpeg" ,quality=50, full_page=True)
    
    contador += 1
    if s3_save:
        #  base = (
        #     f"synthetic/"
        #     f"env={env}/app={app}/journey={journey}/region={region}/"
        #     f"year={year}/month={month}/day={day}/hour={hour}/minute={minute}/"
        #     f"run_id={run_id}/"
        # )
        s3save(fileName, basePath + fileName)

def s3save(fileName, key):
    s3 = boto3.client('s3')
    
    try:
        s3.upload_file(fileName, bucket_name, key)
        print(f"DEBUG: Archivo {fileName} guardado en S3 en {key}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar {fileName} en S3. Detalle: {e}")
    finally:
        print("DEBUG: Finalizó intento de guardar archivo en S3.")
        

def run_playwright() -> bool:

    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    mes = datetime.now().strftime("%B")
    anio = datetime.now().year

    # Identificador único de la ejecución
    santiago = pytz.timezone('America/Santiago')
    now = datetime.now(tz=santiago)#timezone.utc)  # UTC-4
    run_id = f"{now.strftime('%Y-%m-%dT%H-%M-%SZ')}_{uuid.uuid4().hex[:8]}"
    

    basePath = build_s3_base(
            env="prod",
            app="afiliados-help",
            journey="reembolso",
            region="us-east-1",
            now=now,
            run_id=run_id
        )
    
    browser = None
    context = None
    try:
        with sync_playwright() as playwright:
            print("Iniciando navegador...")
            browser = playwright.firefox.launch(headless=True)
            print("Navegador iniciado.")

            """
                "omit" : no guarda cuerpos de respuesta, solo las cabeceras y la traza de requests (HAR liviano).
                "attach" : adjunta los cuerpos pequeños directamente en el HAR.
                "embed" : embebe los cuerpos directamente en el JSON del HAR (lo que lo infla bastante).
            """
            
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_har_path="trafico-firefox.har",
                record_har_content="omit"
                
            )
            # Tracing de playwright
            #context.tracing.start(screenshots=True, snapshots=True, sources=True)
            print("Contexto creado.")
            page = context.new_page()
            page.set_default_timeout(30000)
            page.goto("https://login.helpseguros.cl/login")
            #time.sleep(3)
            rut = os.environ.get("RUT")
            page.get_by_label("RUT").fill(rut)
            page.get_by_label("Contraseña").click()
            password = os.environ.get("PASS")
            page.get_by_label("Contraseña").fill(password)
            takescreenshot(page, s3_save=True,basePath=basePath)
            page.get_by_role("button", name="INGRESAR").click()
            #time.sleep(20)
            
            iframe_locator = page.frame_locator("iframe#pandoraBox")
            # Esperar hasta que el elemento <strong> esté disponible            
            xpath = f"//html/body/app-root/div/app-home/div/div[1]/div[1]/div/div/div[1]/div/h2/span[1]/strong[contains(text(), 'Absalon')]"
            
            # Esperar hasta que el elemento esté visible
            iframe_locator.locator(f"xpath={xpath}").wait_for(state="visible", timeout=30000)
            time.sleep(2)
            takescreenshot(page, s3_save=True,basePath=basePath)
            page.get_by_role("link", name="Mis reembolsos").click()
            page.get_by_role("link", name="Solicitar reembolso").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Open calendar").click()
            page.locator("#pandoraBox").content_frame.get_by_label(f"1 de {mes} de {anio}", exact=True).click()
            page.locator("#pandoraBox").content_frame.get_by_text("arrow_drop_down").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Absalon Luis Opazo Garcia").click()
            takescreenshot(page, s3_save=True,basePath=basePath)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Iniciar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Consulta Médica").click()
            frame = page.frame_locator("#pandoraBox")
            upload = frame.locator("app-upload-file", has_text="cloud_upload Liquidación o")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.pdf")
            time.sleep(2)
            takescreenshot(page, s3_save=True,basePath=basePath)
            upload = frame.locator("app-upload-file", has_text="cloud_upload Boleta - Voucher")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.png")
            time.sleep(2)
            takescreenshot(page, s3_save=True,basePath=basePath)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("ABSALON LUIS OPAZO GARCIA", exact=True).click()
            takescreenshot(page, s3_save=True,basePath=basePath)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Acepto los Términos y").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Close").click()
            time.sleep(2)            
            takescreenshot(page, s3_save=True,basePath=basePath)
            context.close()
            browser.close()
            print("Navegador cerrado.")
            s3save("trafico-firefox.har", basePath + "trafico-firefox.har")
            # Fin tracing de playwright
            #context.tracing.stop(path="trace.zip")
        return True
    except Exception as e:
        print(f"Error: {e}")
        if 'page' in locals():
            takescreenshot(page,error=True, s3_save=True,basePath=basePath)
        return False
    #finally:
        #if context:
        #    context.close()
        #if browser:
        #    browser.close()

if __name__ == "__main__":
    run_playwright()