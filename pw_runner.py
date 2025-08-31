import time
from playwright.sync_api import sync_playwright
from datetime import datetime
import locale
from s3_path import build_s3_key
import boto3
import os
from dotenv import load_dotenv

contador = 1

load_dotenv()


def takescreenshot(page, error=None,s3_save=False):
    global contador
    timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    if error is None:
        page.screenshot(path=f"paso_{contador}_{timestamp}.png")
    else:
        page.screenshot(path=f"error_{contador}_{timestamp}_ERROR.png")
    print(f"DEBUG: paso {contador}")
    contador += 1
    if s3_save:
        # Guardar en S3
        key = build_s3_key(
            env="prod",
            app="afiliados-help",
            journey="reembolso",
            region="us-east-1"
        )

        s3save(error, timestamp, key)

def s3save(error, timestamp, key):
    s3 = boto3.client('s3')
    filename = f"paso_{contador}_{timestamp}.png" if error is None else f"error_{contador}_{timestamp}_ERROR.png"
    bucket_name = "your-bucket-name"  # Reemplaza con el nombre de tu bucket
    try:
        s3.upload_file(filename, bucket_name, key)
        print(f"DEBUG: Archivo {filename} guardado en S3 en {key}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar {filename} en S3. Detalle: {e}")
    finally:
        print("DEBUG: Finalizó intento de guardar archivo en S3.")
        

def run_playwright() -> bool:

    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    mes = datetime.now().strftime("%B")
    anio = datetime.now().year

    base_path = build_s3_key(
        env="prod",
        app="afiliados-help",
        journey="reembolso",
        region="us-east-1"
    )

    browser = None
    context = None
    try:
        with sync_playwright() as playwright:
            print("Iniciando navegador...")
            browser = playwright.firefox.launch(headless=False)
            print("Navegador iniciado.")
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_har_path="trafico-firefox.har",
                record_har_content="embed"
            )
            # Tracing de playwright
            #context.tracing.start(screenshots=True, snapshots=True, sources=True)
            print("Contexto creado.")
            page = context.new_page()
            page.set_default_timeout(30000)
            page.goto("https://login.helpseguros.cl/login")
            time.sleep(3)
            rut = os.environ.get("RUT")
            page.get_by_label("RUT").fill(rut)
            page.get_by_label("Contraseña").click()
            password = os.environ.get("PASS")
            page.get_by_label("Contraseña").fill(password)
            takescreenshot(page)
            page.get_by_role("button", name="INGRESAR").click()
            time.sleep(20)
            takescreenshot(page)
            page.get_by_role("link", name="Mis reembolsos").click()
            page.get_by_role("link", name="Solicitar reembolso").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Open calendar").click()
            page.locator("#pandoraBox").content_frame.get_by_label(f"1 de {mes} de {anio}", exact=True).click()
            page.locator("#pandoraBox").content_frame.get_by_text("arrow_drop_down").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Absalon Luis Opazo Garcia").click()
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Iniciar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Consulta Médica").click()
            frame = page.frame_locator("#pandoraBox")
            upload = frame.locator("app-upload-file", has_text="cloud_upload Liquidación o")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.pdf")
            time.sleep(3)
            takescreenshot(page)
            upload = frame.locator("app-upload-file", has_text="cloud_upload Boleta - Voucher")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.png")
            time.sleep(3)
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("ABSALON LUIS OPAZO GARCIA", exact=True).click()
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Acepto los Términos y").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Close").click()
            time.sleep(3)
            takescreenshot(page)
            context.close()
            browser.close()
            print("Navegador cerrado.")
            # Fin tracing de playwright
            #context.tracing.stop(path="trace.zip")
        return True
    except Exception as e:
        print(f"Error: {e}")
        if 'page' in locals():
            takescreenshot(page, error=True)
        return False
    #finally:
        #if context:
        #    context.close()
        #if browser:
        #    browser.close()

if __name__ == "__main__":
    run_playwright()