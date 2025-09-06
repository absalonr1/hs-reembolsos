
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
brew install sops
brew install age
brew install yq

age-keygen -o ~/.config/age/key.txt
export SOPS_AGE_KEY_FILE=~/.config/age/key.txt

#crear en la raiz  archivo llamado .sops.yaml con la public key:
#creation_rules:
#  - age: "age1x5w2lq0w2r9..."   #  public key de age
```


```
sops --encrypt secrets.yaml > secrets.enc.yaml
sops --decrypt secrets.enc.yaml > secrets.yaml

yq -r '.stringData | to_entries | .[] | "\(.key)=\(.value)"' secrets.yaml > .env
```