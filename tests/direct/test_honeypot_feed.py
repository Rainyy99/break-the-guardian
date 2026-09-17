import json


def test_recent_attempts_empty_when_none(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    result = json.loads(contract.get_recent_attempts(10))
    assert result == []


def test_recent_attempts_newest_first(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa 1"))
    contract.attempt_hack(1, "percobaan pertama")

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa 2"))
    contract.attempt_hack(1, "percobaan kedua")

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*", json.dumps("ACCESS GRANTED"))
    contract.attempt_hack(1, "percobaan ketiga - berhasil")

    result = json.loads(contract.get_recent_attempts(10))
    assert len(result) == 3
    # terbaru harus di depan
    assert result[0]["prompt"] == "percobaan ketiga - berhasil"
    assert result[0]["leaked"] is True
    assert result[2]["prompt"] == "percobaan pertama"


def test_recent_attempts_respects_limit(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    for i in range(5):
        direct_vm.clear_mocks()
        direct_vm.mock_llm(r".*", json.dumps(f"Tidak bisa {i}"))
        contract.attempt_hack(1, f"percobaan ke-{i}")

    result = json.loads(contract.get_recent_attempts(2))
    assert len(result) == 2
    assert result[0]["prompt"] == "percobaan ke-4"
    assert result[1]["prompt"] == "percobaan ke-3"


def test_recent_attempts_limit_bigger_than_total(direct_deploy, direct_vm):
    contract = direct_deploy("contracts/honeypot.py")
    direct_vm.mock_llm(r".*", json.dumps("Tidak bisa"))
    contract.attempt_hack(1, "cuma 1 percobaan")

    result = json.loads(contract.get_recent_attempts(50))
    assert len(result) == 1
