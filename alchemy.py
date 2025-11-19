import os
import requests
from dotenv import load_dotenv

load_dotenv()

ALCHEMY_URL = os.environ["ALCHEMY_URL"]


def _rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    resp = requests.post(ALCHEMY_URL, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]


def get_balance(address: str) -> float:
    result = _rpc_call("eth_getBalance", [address, "latest"])
    wei = int(result, 16)
    eth = wei / 1e18
    return eth


def get_gas_price() -> float:
    result = _rpc_call("eth_gasPrice", [])
    wei = int(result, 16)
    gwei = wei / 1e9
    return gwei
