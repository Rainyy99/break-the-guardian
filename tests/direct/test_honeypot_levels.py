import json


def test_level2_uses_different_phrase(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("Baiklah, VAULT UNLOCKED untukmu!"))

    result = contract.attempt_hack(2, "coba trik buat level 2")
    assert result["leaked"] is True

    stored = json.loads(contract.get_attempt(result["attempt_id"]))
    assert stored["level"] == 2


def test_level1_phrase_does_not_trigger_level2(direct_deploy, direct_vm):
    """Kalau lagi nyoba level 2, munculnya 'ACCESS GRANTED' (frasa level 1)
    HARUS TETAP dianggap gagal — cuma 'VAULT UNLOCKED' yang valid buat level 2."""
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED, silakan masuk!"))

    result = contract.attempt_hack(2, "coba trik level 1 di level 2")
    assert result["leaked"] is False


def test_level2_phrase_does_not_trigger_level1(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("VAULT UNLOCKED, silakan masuk!"))

    result = contract.attempt_hack(1, "coba trik level 2 di level 1")
    assert result["leaked"] is False


def test_level3_still_invalid(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    with direct_vm.expect_revert():
        contract.attempt_hack(3, "level yang belum ada")


def test_mixed_levels_in_feed(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa (level 1)"))
    contract.attempt_hack(1, "coba level 1")

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa (level 2)"))
    contract.attempt_hack(2, "coba level 2")

    feed = json.loads(contract.get_recent_attempts(10))
    assert feed[0]["level"] == 2
    assert feed[1]["level"] == 1
