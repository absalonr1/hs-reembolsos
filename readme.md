
```
python3 -m venv myenv
source myenv/bin/activate 
pip install -r requirements.txt
playwright install firefox
uvicorn web-service:app --host 0.0.0.0 --port 8000 --reload
```

```
export AWS_PROFILE=<aws account>_AdministratorAccess
aws sts get-caller-identity
```

```
yq -r '.stringData | to_entries | .[] | "\(.key)=\(.value)"' secrets.yaml > .env
```