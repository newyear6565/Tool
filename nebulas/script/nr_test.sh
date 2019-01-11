curl -i -H 'Content-Type: application/json' -X POST http://47.92.203.173:9685/v1/user/getNrHash -d '{"start":1, "end":1000, "version":1}'
curl -i -H 'Content-Type: application/json' -X POST http://47.92.203.173:9685/v1/user/getNrList -d '{"hash":"000000000000000100000000000003e80000000000000001"}'
curl -i -H 'Content-Type: application/json' -X POST http://47.92.203.173:9685/v1/user/getDipList -d '{}'
