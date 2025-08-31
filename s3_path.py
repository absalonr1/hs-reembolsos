import uuid
import pytz
from datetime import datetime,timezone

def build_s3_key(env, app, journey, region):
    """
    Genera un key S3 con la estructura definida para synthetic monitoring.
    """
    # Fecha/hora actual en UTC
     # Get a timezone object
    santiago = pytz.timezone('America/Santiago')
    now = datetime.now(tz=santiago)#timezone.utc)  # UTC-4
    year   = now.strftime("%Y")
    month  = now.strftime("%m")
    day    = now.strftime("%d")
    hour   = now.strftime("%H")
    minute = now.strftime("%M")

    # Identificador único de la ejecución
    run_id = f"{now.strftime('%Y-%m-%dT%H-%M-%SZ')}_{uuid.uuid4().hex[:8]}"

    # Construcción del path
    base = (
        f"synthetic/"
        f"env={env}/app={app}/journey={journey}/region={region}/"
        f"year={year}/month={month}/day={day}/hour={hour}/minute={minute}/"
        f"run_id={run_id}/"
    )

    return base




if __name__ == "__main__":
    # Ejemplo de uso
    keys = build_s3_key(
        env="prod",
        app="afiliados-help",
        journey="reembolso",
        region="us-east-1"
    )
    print(keys)