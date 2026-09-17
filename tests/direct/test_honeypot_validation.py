import json


def test_claim_empty_wallet_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED"))
    result = contract.attempt_hack(1, "trik jitu")

    with direct_vm.expect_revert():
        contract.claim_reward(result["attempt_id"], "")


def test_claim_whitespace_only_wallet_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED"))
    result = contract.attempt_hack(1, "trik jitu")

    with direct_vm.expect_revert():
        contract.claim_reward(result["attempt_id"], "   ")


def test_recent_attempts_negative_limit_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    with direct_vm.expect_revert():
        contract.get_recent_attempts(-1)


def test_recent_attempts_zero_limit_returns_empty(direct_deploy, direct_vm):
    """limit=0 itu valid (bukan negatif), harus balikin list kosong tanpa error."""
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa"))
    contract.attempt_hack(1, "satu percobaan")

    result = json.loads(contract.get_recent_attempts(0))
    assert result == []


def test_challenge_level_zero_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    with direct_vm.expect_revert():
        contract.attempt_hack(0, "level nol")


def test_challenge_level_negative_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    with direct_vm.expect_revert():
        contract.attempt_hack(-1, "level negatif")
