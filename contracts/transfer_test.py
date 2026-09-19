# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
# Throwaway utility contract — NOT part of the Break the Guardian submission.
# Sole purpose: verify emit_transfer() actually moves GEN to a plain wallet
# (EOA) address on real Studio/GenVM, before relying on the same pattern
# inside the real contract's claim_reward().
import json
from genlayer import *


@gl.evm.contract_interface
class _EoaRecipient:
    class View:
        pass

    class Write:
        pass


class TransferTest(gl.Contract):
    total_received: str
    total_sent: str

    def __init__(self):
        self.total_received = "0"
        self.total_sent = "0"

    @gl.public.write.payable
    def fund(self):
        amount = gl.message.value
        self.total_received = str(int(self.total_received) + amount)

    @gl.public.view
    def get_balance(self) -> int:
        return int(self.total_received) - int(self.total_sent)

    @gl.public.write
    def test_send(self, wallet_address: str, amount: int):
        if amount <= 0:
            raise ValueError("amount must be positive")
        available = int(self.total_received) - int(self.total_sent)
        if amount > available:
            raise ValueError("insufficient balance")

        self.total_sent = str(int(self.total_sent) + amount)

        recipient = _EoaRecipient(Address(wallet_address))
        recipient.emit_transfer(value=u256(amount))
