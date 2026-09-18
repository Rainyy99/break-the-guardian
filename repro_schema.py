"""
Reproduce the exact "Could not load contract schema" error from Studio,
but with a FULL, non-truncated Python traceback — run this in Codespaces
(needs genlayer-py, which needs Rust/maturin, hence Codespaces not Termux).

Usage:
    pip install genlayer-py
    python3 repro_schema.py
"""
import traceback
from pathlib import Path

from genlayer_py import create_client
from eth_account import Account

CONTRACT_PATH = "contracts/honeypot.py"
STUDIO_ENDPOINT = "https://studio.genlayer.com/api"


def main():
    contract_code = Path(CONTRACT_PATH).read_text()
    print(f"Loaded {CONTRACT_PATH} ({len(contract_code)} chars)\n")

    throwaway_account = Account.create()

    client = create_client(
        endpoint=STUDIO_ENDPOINT,
        account=throwaway_account,
    )

    print(f"Calling get_contract_schema_for_code() against {STUDIO_ENDPOINT} ...\n")
    try:
        schema = client.get_contract_schema_for_code(contract_code=contract_code)
        print("SUCCESS — schema loaded fine:")
        print(schema)
    except Exception:
        print("FAILED — full traceback below:\n")
        traceback.print_exc()


if __name__ == "__main__":
    main()
