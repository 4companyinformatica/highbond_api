import sys
import os

sys.path.append(f"{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}")

from src.highbond_api_class import Highbond_API
from dotenv import load_dotenv
import os
import pathlib


script_root = pathlib.Path(__file__).parent.resolve()

print(script_root)

if os.path.exists(".env"):
    load_dotenv(".env")

d1 = Highbond_API(
    token=os.environ.get("HB_TOKEN"),
    organization_id=os.environ.get("HB_ORGID"),
    server=os.environ.get("HB_SERVER")
)

def test_getAgents():
    response = d1.getAgents()

    assert bool(response)

def test_getOrganization():
    response = d1.getOrganization()
    print(response)

    assert bool(response)