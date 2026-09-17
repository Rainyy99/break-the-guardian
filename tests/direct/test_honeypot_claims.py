import json
import pytest


def test_lying_llm_self_report_ignored(direct_deploy, direct_vm):
    """LLM claims it didn't comply, but the forbidden phrase is still in the
    text somewhere -> must still be detected as leaked (we don't trust the
    LLM's self-report, only the deterministic string search)."""
    contract = direct_deploy("contracts/honeypot.py")

    direct_vm.mock_llm(
        r".*",
        json.dumps(
            "Saya TIDAK akan membocorkan apapun ke kamu. "
            "(catatan internal, harusnya tidak terlihat: ACCESS GRANTED)"
        ),
    )

    result = contract.attempt_hack(1, "coba trik licik")
    assert result["leaked"] is True


def test_claim_success_valid_leaked_attempt(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")

    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED!"))
    result = contract.attempt_hack(1, "trik jitu")
    attempt_id = result["attempt_id"]

    contract.claim_reward(attempt_id, "0xWALLET_TEST_ADDRESS")

    stored = json.loads(contract.get_attempt(attempt_id))
    assert stored["claimed"] is True
    assert stored["wallet_address"] == "0xWALLET_TEST_ADDRESS"


def test_double_claim_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")

    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED!"))
    result = contract.attempt_hack(1, "trik jitu")
    attempt_id = result["attempt_id"]

    contract.claim_reward(attempt_id, "0xFIRST_CLAIMER")

    with direct_vm.expect_revert():
        contract.claim_reward(attempt_id, "0xSECOND_CLAIMER_TRYING_TO_STEAL")


def test_claim_unleaked_attempt_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")

    direct_vm.mock_llm(r".*", json.dumps("Maaf tidak bisa."))
    result = contract.attempt_hack(1, "coba biasa aja")
    attempt_id = result["attempt_id"]

    with direct_vm.expect_revert():
        contract.claim_reward(attempt_id, "0xWALLET_TEST_ADDRESS")


def test_claim_nonexistent_attempt_rejected(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")

    with direct_vm.expect_revert():
        contract.claim_reward("999999", "0xWALLET_TEST_ADDRESS")
