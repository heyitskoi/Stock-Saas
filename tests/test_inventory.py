import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from stock.inventory import Inventory
from stock import storage


def setup_function(function):
    # ensure clean inventory file
    if os.path.exists(storage.DATA_FILE):
        os.remove(storage.DATA_FILE)


def test_add_issue_return_cycle():
    inv = Inventory()
    inv.add_item('headphones', 5)
    assert inv.get_status('headphones')['headphones']['available'] == 5

    assert inv.issue_item('headphones', 2)
    status = inv.get_status('headphones')['headphones']
    assert status['available'] == 3 and status['in_use'] == 2

    assert inv.return_item('headphones', 2)
    status = inv.get_status('headphones')['headphones']
    assert status['available'] == 5 and status['in_use'] == 0

