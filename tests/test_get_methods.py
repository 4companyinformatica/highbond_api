import sys
import os

sys.path.append(f"{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}\\src")

from highbond_api_class import Highbond_API
from dotenv import load_dotenv
import os
import pathlib


d1 = Highbond_API(
    token=os.environ.get("HB_TOKEN"),
    organization_id=os.environ.get("HB_ORGID"),
    server=os.environ.get("HB_SERVER")
)

script_root = pathlib.Path(__file__)

load_dotenv(".env")

def test_getAgents():
    response = d1.getAgents()

    assert bool(response)

def test_getOrganization():
    response = d1.getOrganization()
    print(response)

    assert bool(response)