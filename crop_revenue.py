import requests
import json

def get_bazaar_data():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            print("API request failed or returned success: false")
            return {}
        return data.get("products", {})
    except Exception as e:
        print(f"Error fetching bazaar data: {e}")
        return {}

def calculate_crop_revenue(item_name, data, products):
    product_data = products.get(item_name)
    if not product_data:
        print(f"{item_name}: Not found in Bazaar")
        return 0
    
    sell_summary = product_data.get("sell_summary", [])
    if not sell_summary:
        print(f"{item_name}: No buy orders (cannot instasell)")
        return 0
    
    instasell_price = sell_summary[0]["pricePerUnit"]
    
    drops_revenue = 0
    # drops_data = data.get("drop", {})
    drops_data = {}
    
    enchanted_exceptions = {
        "INK_SACK:3": "ENCHANTED_COCOA",
        "CACTUS": "ENCHANTED_CACTUS_GREEN",
        "DOUBLE_PLANT": "ENCHANTED_SUNFLOWER",
        "SUGAR_CANE": "ENCHANTED_SUGAR",
        "POTATO_ITEM": "ENCHANTED_POTATO",
        "CARROT_ITEM": "ENCHANTED_CARROT",
    }
    
    for drop_item, drop_qty in drops_data.items():
        enchanted_name = enchanted_exceptions.get(drop_item, f"ENCHANTED_{drop_item}")
        
        drop_unit_price = 0
        price_found = False
        
        if enchanted_name in products:
            enchanted_summary = products[enchanted_name].get("sell_summary", [])
            if enchanted_summary:
                drop_unit_price = enchanted_summary[0]["pricePerUnit"]
                price_found = True
        
        if not price_found:
            drop_product = products.get(drop_item)
            if not drop_product:
                print(f"Warning: Drop item {drop_item} for {item_name} not found in Bazaar")
                continue
            
            drop_sell_summary = drop_product.get("sell_summary", [])
            if not drop_sell_summary:
                continue
            
            drop_unit_price = drop_sell_summary[0]["pricePerUnit"]
        
        drops_revenue += drop_qty / 160 * 38 * drop_unit_price
    
    revenue = instasell_price + drops_revenue
    return revenue

with open('items.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

products = get_bazaar_data()

if products:
    x = calculate_crop_revenue("BLASTBERRY", recipes["BLASTBERRY"], products)
    shellfruit_revenue = calculate_crop_revenue("SHELLFRUIT", recipes["SHELLFRUIT"], products)
    
    print(f"BLASTBERRY crop revenue (x): {x:,.2f} coins")
    print(f"SHELLFRUIT crop revenue: {shellfruit_revenue:,.2f} coins")
