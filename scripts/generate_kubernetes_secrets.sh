#! /bin/bash

SECRET_NAME=forum-secret
PATH_TO_ENV=.env

echo "[+] Generate secret '$SECRET_NAME' from '$PATH_TO_ENV' file..."

kubectl get secret $SECRET_NAME &> /dev/null
if [[ "$?" == 0 ]]; then
    echo "[+] Secret already exists. Deleting it..."
    kubectl delete secret $SECRET_NAME
fi

echo "[+] Creating secret..."
kubectl create secret generic $SECRET_NAME --from-env-file=$PATH_TO_ENV
