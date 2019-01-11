
sender="n1HrPpwwH5gTA2d7QCkVjMw14YbN1NNNXHc"
receiver="n1aNeW32iYqwdssGDR4zq2Ex3BLXE4BkUDA"

counter=0
max=0
value=0.0
passphrase="samuel@nebulas"

while [[ $counter -le $max ]]; do
    python3 api.py internal transaction $sender $receiver $value $passphrase
    (( counter++ ))
done
