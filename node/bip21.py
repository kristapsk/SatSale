# https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki
# bitcoin:<address>[?amount=<amount>][?label=<label>][?message=<message>]

from decimal import Decimal
from typing import Union
from urllib.parse import parse_qs, quote, unquote_plus, urlencode, urlparse
import re

from utils import btc_amount_format


def _is_bip21_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    return parsed.scheme.lower() == "bitcoin" and parsed.path != ""


def _is_bip21_amount_str(amount: str) -> bool:
    return re.compile(r"^[0-9]{1,8}(\.[0-9]{1,8})?$").match(
        amount) is not None


def _validate_bip21_amount(amount: Union[Decimal, float, int, str]) -> None:
    if not _is_bip21_amount_str(str(amount)):
        raise ValueError("Invalid BTC amount " + str(amount))


def decode_bip21_uri(uri: str) -> dict:
    if not _is_bip21_uri(uri):
        raise ValueError("not a valid BIP21 URI: " + uri)
    result = {}
    parsed = urlparse(uri)
    result["address"] = parsed.path
    params = parse_qs(parsed.query)
    for key in params:
        if key.startswith("req-"):
            raise ValueError("Unknown required parameter " + key +
                             " in BIP21 URI.")
        if key == "amount":
            _validate_bip21_amount(params[key][0])
            result["amount"] = btc_amount_format(params["amount"][0])
        else:
            result[key] = unquote_plus(params[key][0])
    return result


def encode_bip21_uri(address: str, params: Union[dict, list]) -> str:
    uri = "bitcoin:{}".format(address)
    if len(params) > 0:
        if "amount" in params:
            _validate_bip21_amount(params["amount"])
            # Format value effective way - never do more than 8 decimal
            # places, strip trailing zeroes, use integer for round values.
            flt_amt = float(params["amount"])
            int_amt = int(flt_amt)
            if int_amt == flt_amt:
                params["amount"] = int_amt
            else:
                params["amount"] = "{0:.8f}".format(
                    Decimal(params["amount"])).strip("0")
                if params["amount"][0] == ".":
                    params["amount"] = "0" + params["amount"]
        uri += "?" + urlencode(params, quote_via=quote)
    return uri
