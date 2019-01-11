
curl -i -H 'Accept: application/json' -X POST http://localhost:1785/v1/admin/transactionWithPassphrase -H 'Content-Type:application/json' -d '{"transaction":{"from":"n1HWE22w4DaE1gz6E9D9TGokrxfHBegoyB8","to":"n1yVTnA92dt6Kn1xuQKq79pSqsbefHhmqiD", "value":"100","nonce":86,"gasPrice":"1000000","gasLimit":"2000000","contract":{"function":"save","args":"[0]"}}, "passphrase": "samuel@nebulas"}'
