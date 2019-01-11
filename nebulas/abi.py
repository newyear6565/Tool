import sys
import os
import requests
import json
import time

def err(msg):
    print("Error: ", msg)
    exit(1)

class Neb(object):
    def __init__(self, vendor):
        self.mainnet = "https://mainnet.nebulas.io"
        self.testnet = "https://testnet.nebulas.io"
        self.internal = "http://47.92.203.173:9685"
        self.local = "http://localhost:9685"
        self.vendor = vendor
        if vendor == 'mainnet':
            self.host = self.mainnet
        elif vendor == 'testnet':
            self.host = self.testnet
        elif vendor == 'internal':
            self.host = self.internal
        else:
            self.host = self.local
        self.ACCT_FILE_NAME = "accounts.txt"
        self.REGISTER_APIS = [
            "transaction",
            "sendir",
            "create",
            "balance",
            "accounts",
            "check_accounts",
            "smartcontract"
        ]
        self.IR_POSTERS = {
            "internal":[
                {"addr":"n1HWE22w4DaE1gz6E9D9TGokrxfHBegoyB8", "passphrase":"samuel@nebulas"},
            ],
            "local":[
                {"addr":"n1R2E4Fo6ihQEptiFCgqcveY2vXEsWJAkfU", "passphrase":"samuel@nebulas"},
                # {"addr":"n1UodK5h3o7yHFLHe9Vq4N3WZGUthsWm6j7", "passphrase":"123456"},
            ],
            "testnet":[
                {"addr":"n1UodK5h3o7yHFLHe9Vq4N3WZGUthsWm6j7", "passphrase":"123456"},
            ],
        }

    def _load_accounts(self):
        # check existing accounts
        fp = open(self.ACCT_FILE_NAME, "r")
        info = {}
        try:
            lines = fp.readlines()
            for line in lines:
                addr_json = json.loads(line.strip())
                if addr_json['host'] not in info:
                    info[addr_json['host']] = []
                info[addr_json['host']].append({'address': addr_json['address'], 'value': addr_json['value']})
        except:
            pass
        finally:
            fp.close()
        return info[self.host] if self.host in info else []

    def check_accounts(self):
        accounts = self._load_accounts()
        for account in accounts:
            print(account['address'] + ": " + account['value'])

    def _append_accounts_raw(self, addr, value):
        fp = open(self.ACCT_FILE_NAME, "a")
        try:
            account_json = {'address':addr, 'value':value, 'host':self.host}
            fp.write(json.dumps(account_json)+"\n")
        except:
            pass
        finally:
            fp.close()

    def _append_accounts(self, account):
        fp = open(self.ACCT_FILE_NAME, "a")
        try:
            fp.write(json.dumps(account)+"\n")
        except:
            pass
        finally:
            fp.close()

    def request(self, url, data, request_mode=2):
        post_headers = {'Accept': 'application/json'}
        get_headers = {'Content-Type': 'application/json'}
        # print("start to send request, with data: ", json.dumps(data))
        if request_mode == 1:
            response = requests.get(url, headers=get_headers, data=json.dumps(data))
        elif request_mode == 2:
            response = requests.post(url, headers=post_headers, data=json.dumps(data))
        return json.loads(response.text)

    def get_register_methods(self):
        return self.REGISTER_APIS

    def balance(self, address):
        #cmd = "curl -i -H Accept:application/json -X POST %s/v1/user/accountstate -d '{\"address\":\"%s\"}'"%(self.host, address)
        url = "%s/v1/user/accountstate"%self.host
        data = {"address":address}
        res = self.request(url, data)
        balance = float(res['result']['balance'])
        print("Address: " + address + ", Balance: " + str(balance/pow(10, 18))
            + " NAS, " + "nonce: " + str(res['result']['nonce']) + ", type: " + str(res['result']['type']) + "\n")
        return balance

    def _check_nonce(self, address):
        url = "%s/v1/user/accountstate"%self.host
        data = {"address":address}
        try:
            res = self.request(url, data)
            return int(res['result']['nonce'])
        except:
            pass
        return -1

    def create_account(self, passphrase):
        url = '%s/v1/admin/account/new'%self.host
        data = {"passphrase":passphrase}
        res = self.request(url, data)
        res['result']['value'] = '0'
        res['result']['host'] = self.host
        self._append_accounts(res['result'])
        print("Created a new account: %s"%res['result']['address'])

    def show_accounts(self, curl=True):
        if curl:
            cmd = "curl -i -H Accept:application/json -X GET %s/v1/admin/accounts"%self.host
            os.system(cmd)
        else:
            url = '%s/v1/admin/accounts'%self.host
            res = self.request(url, {}, 1)
            print("Found following acccounts:\n")
            print(res)
            for addr in res['result']['addresses']:
                print(addr)

    def _sign_tx(self, data):
        url = '%s/v1/admin/sign'%self.host
        res = self.request(url, data)
        return res['result']

    def sendIR(self, ir_file_path):
        addr_info = self.IR_POSTERS[self.vendor][0]
        from_addr = addr_info['addr']
        to_addr = from_addr
        value="0.0"
        passphras = addr_info['passphrase']
        try:
            fp = open(ir_file_path, 'r')
            ir = fp.read()
            self.transaction(from_addr, to_addr, value, passphras, ir=ir.strip())
        except:
            pass
        finally:
            fp.close()

    def transaction(self, from_addr, to_addr, value, passphrase, nonce=0, ir=None):
        # sign the tx, then send the raw data
        url = '%s/v1/user/rawtransaction'%self.host
        tx_value = '{0:.0f}'.format(float(value)*pow(10, 18))

        # check nonce
        ex_nonce = self._check_nonce(from_addr)
        if ex_nonce < 0:
            err("failed to check from address nonce")
        if nonce != 0 and nonce != (ex_nonce + 1):
            err("wrong nonce value, previous is: " + str(ex_nonce))
        nonce = ex_nonce + 1

        # check balance
        balance = self.balance(from_addr)
        #TODO, calculate the gas here
        if balance <= 0.0:
            err("Insufficient balance!")

        gas_price = '1000000'
        gas_limit = '2000000'

        data = {"transaction":{"from":from_addr,"to":to_addr, "value":tx_value,
        "nonce":nonce,"gasPrice":gas_price,"gasLimit":gas_limit}, "passphrase":passphrase}

        if ir:
            data["transaction"]["protocol"] = ir

        raw_tx_data = self._sign_tx(data)
        res = self.request(url, raw_tx_data)

        self.check_tx_status(res['result']['txhash'])


    def check_tx_status(self, tx_hash):
        url = '%s/v1/user/getTransactionReceipt'%self.host
        data = {"hash":tx_hash}
        try:
            max = 6
            counter=0
            while counter<max:
                res = self.request(url, data)
                status = res['result']['status']
                if status == 1:
                    print(res)
                    print("\n[SUCCESS] Successfully send transaction!!\n")
                    break
                else:
                    print(">> Waiting for transaction to be onchain ...")
                time.sleep(5)
                counter+=1
            if counter >= max:
                print("\n[FAIL] Failed to send transaction!!\n")
        except:
            pass


    def deploy_sc(self, sc_fp):
        cmd = "ls"
        os.system(cmd)

    def driver(self, method, paras):
        if method == 'create':
            if len(paras) < 1:
                print("Please specify the new account passphrase!")
                exit(1)
            self.create_account(paras[0])
        elif method == 'check_accounts':
            self.check_accounts()
        elif method == 'accounts':
            self.show_accounts()
        elif method == 'balance':
            if len(paras) < 1:
                print("Please specify the address!")
                exit(1)
            self.balance(paras[0])
        elif method == 'transaction':
            if len(paras) < 3:
                print("Please specify the from addr, to addr, value, and nonce(optional)")
                exit(1)
            from_addr = paras[0]
            to_addr = paras[1]
            value = paras[2]
            passphrase = paras[3]
            nonce = int(paras[4]) if len(paras)>4 else 0
            self.transaction(from_addr, to_addr, value, passphrase, nonce)
        elif method == 'sendir':
            if len(paras)<1:
                print("Please specify the ir file path, should be base64 encoded")
                exit(1)
            self.sendIR(paras[0])
        elif method == 'create':
            inst = Neb(host)
            inst.create_account("samuel@nebulas")
        else:
            print("Invalid method!\nSupported methods are: \n")
            print(self.REGISTER_APIS)
            print("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python %s [mainnet | testnet | internal | ...] method([balance | tx | ...]) address ..."%__file__)
        exit(1)
    else:
        host = sys.argv[1]
        if host != 'mainnet' and host != 'testnet' and host != "local" and host != "internal":
            print("specify which net you wanna connect to, the value can be mainnet, testnet or local")
            exit(1)

        inst = Neb(host)
        methods = inst.get_register_methods()
        method = sys.argv[2]

        if method not in methods:
            print("invalid method: %s!"%method)
            exit(1)

        inst.driver(method, sys.argv[3:])

