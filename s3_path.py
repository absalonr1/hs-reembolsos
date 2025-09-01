

def build_s3_base(env, app, journey, region, run_id, now):
    """
    Genera un key S3 con la estructura definida para synthetic monitoring.
    """
    # Fecha/hora actual en UTC
     # Get a timezone object
    
    year   = now.strftime("%Y")
    month  = now.strftime("%m")
    day    = now.strftime("%d")
    hour   = now.strftime("%H")
    minute = now.strftime("%M")

    

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
    keys = build_s3_base(
        env="prod",
        app="afiliados-help",
        journey="reembolso",
        region="us-east-1"
    )
    print(keys)