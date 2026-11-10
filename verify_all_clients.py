from opensooq_client import OpenSooqClient
from syarah_client import SyarahClient
from haraj_market_engine import HarajMarketEngine

def test_all():
    print("1. Running OpenSooq Client Test...")
    os_client = OpenSooqClient()
    os_items = os_client.search('ايفون')
    print(f"   OpenSooq OK: {len(os_items)} listings fetched.")
    assert len(os_items) > 0, "OpenSooq failed"

    print("\n2. Running Syarah Client Test...")
    sy_client = SyarahClient()
    sy_cars = sy_client.get_inventory()
    print(f"   Syarah OK: {len(sy_cars)} cars fetched.")
    assert len(sy_cars) > 0, "Syarah failed"

    print("\n3. Running Haraj Market Engine Test...")
    engine = HarajMarketEngine()
    res = engine.sync_keyword('RTX 3060')
    deals = engine.detect_anomalies()
    print(f"   Haraj OK: {res['fetched']} listings processed, {len(deals)} anomalies detected.")
    assert res['fetched'] > 0, "Haraj failed"

    print("\n>>> ALL PRODUCTION MARKETPLACE CLIENTS FULLY VERIFIED! <<<")

if __name__ == "__main__":
    test_all()
