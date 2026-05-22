import json
import os
import sys
from base64 import b64encode
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from node import lnd as lnd_module
from node.lnd import lnd
from node.lndhub import lndhub


class FakeLNDClient:
    def __init__(self, invoice_response):
        self.invoice_response = invoice_response

    def lookup_invoice(self, r_hash_str):
        return self.invoice_response


class FakeLNDHubClient:
    def __init__(self, invoice_response):
        self.invoice_response = invoice_response

    def lookup_invoice(self, rhash):
        return self.invoice_response


def test_lnd_check_payment_does_not_add_extra_sat(monkeypatch):
    monkeypatch.setattr(
        lnd_module,
        "MessageToJson",
        lambda msg: json.dumps(msg),
    )

    lightning_node = lnd.__new__(lnd)
    lightning_node.lnd = FakeLNDClient({"amtPaidSat": "1000"})

    rhash = b64encode(b"test_hash").decode()
    conf_paid, unconf_paid = lightning_node.check_payment(rhash)

    assert conf_paid == Decimal("0.00001000")
    assert unconf_paid == Decimal(0)


def test_lnd_check_payment_returns_zero_for_unpaid_invoice(monkeypatch):
    monkeypatch.setattr(
        lnd_module,
        "MessageToJson",
        lambda msg: json.dumps(msg),
    )

    lightning_node = lnd.__new__(lnd)
    lightning_node.lnd = FakeLNDClient({})

    rhash = b64encode(b"test_hash").decode()
    conf_paid, unconf_paid = lightning_node.check_payment(rhash)

    assert conf_paid == Decimal(0)
    assert unconf_paid == Decimal(0)


def test_lndhub_check_payment_does_not_add_extra_sat():
    lightning_node = lndhub.__new__(lndhub)
    lightning_node.lndhub = FakeLNDHubClient({
        "ispaid": True,
        "amt": "1000",
    })

    conf_paid, unconf_paid = lightning_node.check_payment("test_rhash")

    assert conf_paid == Decimal("0.00001000")
    assert unconf_paid == Decimal(0)


def test_lndhub_check_payment_returns_zero_for_unpaid_invoice():
    lightning_node = lndhub.__new__(lndhub)
    lightning_node.lndhub = FakeLNDHubClient({
        "ispaid": False,
        "amt": "1000",
    })

    conf_paid, unconf_paid = lightning_node.check_payment("test_rhash")

    assert conf_paid == Decimal(0)
    assert unconf_paid == Decimal(0)
