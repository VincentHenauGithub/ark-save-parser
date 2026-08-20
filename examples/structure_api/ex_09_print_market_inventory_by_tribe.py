from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory
from arkparse.parsing import GameObjectReaderConfiguration


SAVE_PATH = Path(r"C:\Path\To\Your\Genesis_WP\Genesis_WP.ark")
MAP = ArkMap.GENESIS1
MARKET_CLASS = "Market_C"
DEBUG_MARKET_DATA = False


def asv_class_name(obj: Any) -> str:
    short_name = obj.get_short_name() if hasattr(obj, "get_short_name") else None
    return f"{short_name}_C" if short_name else ""


def get_market_coords(market: StructureWithInventory) -> tuple[float, float, str]:
    if market.location is None:
        return 0.0, 0.0, "Unknown"

    coords = market.location.as_map_coords(MAP)
    if coords is None:
        return 0.0, 0.0, "Unknown"

    return coords.lat, coords.long, coords.sub_map_name or "Unknown"


def get_nested_property(container: Any, name: str, default: Any = None) -> Any:
    if not hasattr(container, "properties"):
        return default

    for prop in container.properties:
        if prop.name == name:
            return prop.value
    return default


def get_market_sell_orders(market: StructureWithInventory) -> Dict[str, Dict[str, Any]]:
    orders_by_item_uuid: Dict[str, Dict[str, Any]] = {}
    trade_data = market.object.get_property_value("MyTradeData")
    sell_orders = get_nested_property(trade_data, "SellOrders")
    if not hasattr(sell_orders, "properties"):
        return orders_by_item_uuid

    for order in sell_orders.properties:
        order_data = order.value
        item_ref = get_nested_property(order_data, "OrderItemRef")
        item_uuid = getattr(item_ref, "value", None)
        if not item_uuid:
            continue

        orders_by_item_uuid[str(item_uuid)] = {
            "order_id": order.name,
            "price_per_unit": get_nested_property(order_data, "PricePerUnit"),
            "quantity": get_nested_property(order_data, "ItemQuantity"),
            "owner_name": get_nested_property(order_data, "OwnerName"),
        }

    return orders_by_item_uuid


def debug_market_data(market: StructureWithInventory) -> None:
    print("  DEBUG MyTradeData:")
    trade_data = market.object.get_property_value("MyTradeData")
    if not hasattr(trade_data, "properties"):
        print(f"    {trade_data!r}")
        return

    for prop in trade_data.properties:
        print(f"    {prop.name}: {prop.type} = {prop.value!r}")
        if hasattr(prop.value, "properties"):
            for nested in prop.value.properties:
                print(f"      {nested.name}: {nested.type} = {nested.value!r}")


def get_inventory_items(market: StructureWithInventory) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if market.inventory is None:
        return items

    sell_orders = get_market_sell_orders(market)
    for item in market.inventory.items.values():
        item_class = asv_class_name(item)
        if not item_class:
            continue

        item_uuid = str(item.uuid)
        order = sell_orders.get(item_uuid, {})
        price_per_unit = order.get("price_per_unit")
        quantity = int(getattr(item, "quantity", 1) or 1)
        total_price = price_per_unit * quantity if isinstance(price_per_unit, int) else None

        items.append(
            {
                "item": item_class,
                "quantity": quantity,
                "price_per_unit": price_per_unit,
                "total_price": total_price,
                "order_owner": order.get("owner_name"),
            }
        )

    return sorted(items, key=lambda entry: (entry["item"], entry["price_per_unit"] or 0))


def main() -> None:
    save = AsaSave(SAVE_PATH)
    structure_api = StructureApi(save)
    config = GameObjectReaderConfiguration(
        blueprint_name_filter=lambda name: name is not None and "Market" in name
    )

    markets_by_tribe: Dict[tuple[int, str], List[StructureWithInventory]] = defaultdict(list)
    for structure in structure_api.get_all(config).values():
        if not isinstance(structure, StructureWithInventory):
            continue
        if asv_class_name(structure) != MARKET_CLASS:
            continue

        tribe_id = structure.owner.tribe_id
        tribe_name = structure.owner.tribe_name or "Unknown"
        markets_by_tribe[(tribe_id, tribe_name)].append(structure)

    if not markets_by_tribe:
        print(f"No {MARKET_CLASS} structures found.")
        return

    for (tribe_id, tribe_name), markets in sorted(markets_by_tribe.items(), key=lambda entry: (entry[0][1], entry[0][0] or 0)):
        print(f"Tribe {tribe_name} (ID: {tribe_id})")

        for market in sorted(markets, key=lambda m: str(m.uuid)):
            lat, lon, biome = get_market_coords(market)
            print(f"Market Lat: {lat:.2f} Lon: {lon:.2f} Biome: {biome}")
            if DEBUG_MARKET_DATA:
                debug_market_data(market)

            items = get_inventory_items(market)
            if not items:
                print("- No items")
            else:
                for item in items:
                    price = item["price_per_unit"]
                    if price is None:
                        print(f"- {item['item']} x{item['quantity']} - no sell order price found")
                    else:
                        seller = item["order_owner"] or "Unknown"
                        print(f"- {item['item']} x{item['quantity']} - {price} Hexagons each ({item['total_price']} total) - Seller: {seller}")

        print()


if __name__ == "__main__":
    main()
