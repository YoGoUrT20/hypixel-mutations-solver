
import requests
import json
import sys
from positions import solve_layout

# Constants
HOURS_PER_STAGE = 2

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

def calculate_profits():
    # 1. Load recipes
    try:
        with open('items.json', 'r', encoding='utf-8') as f:
            recipes = json.load(f)
    except FileNotFoundError:
        print("items.json not found.")
        return

    # 2. Fetch bazaar prices
    products = get_bazaar_data()
    if not products:
        return

    profits = []
    skipped_items = []

    for item_name, data in recipes.items():
        made_of = data.get("made_of", {})
        stages = data.get("stages", 0)
        
        # Calculate time in hours
        # If stages is 0, it means instant or not growable? 
        # Usually crops take time. Assuming stages != 0 for growable crops.
        # If stages is 0, we avoid division by zero.
        hours_to_grow = stages * HOURS_PER_STAGE
        
        if not made_of:
            skipped_items.append(f"{item_name}: No recipe defined")
            continue

        # Get Sell Price of the crafted item (Revenue)
        product_data = products.get(item_name)
        if not product_data:
            skipped_items.append(f"{item_name}: Not found in Bazaar")
            continue

        sell_summary = product_data.get("sell_summary", [])
        if not sell_summary:
            skipped_items.append(f"{item_name}: No buy orders (cannot instasell)")
            continue
        
        instasell_price = sell_summary[0]["pricePerUnit"]
        
        # Calculate Drops Revenue
        drops_revenue = 0
        drops_data = data.get("drop", {})
        # Exceptions for Enchanted names
        enchanted_exceptions = {
            "INK_SACK:3": "ENCHANTED_COCOA",
            "CACTUS": "ENCHANTED_CACTUS_GREEN",
            "DOUBLE_PLANT": "ENCHANTED_SUNFLOWER",
            "SUGAR_CANE": "ENCHANTED_SUGAR",
            "POTATO_ITEM": "ENCHANTED_POTATO",
            "CARROT_ITEM": "ENCHANTED_CARROT",
        }

        for drop_item, drop_qty in drops_data.items():
            # Determine Enchanted Name
            enchanted_name = enchanted_exceptions.get(drop_item, f"ENCHANTED_{drop_item}")

            drop_unit_price = 0
            price_found = False

            # Try to get price from ENCHANTED form
            if enchanted_name in products:
                enchanted_summary = products[enchanted_name].get("sell_summary", [])
                if enchanted_summary:
                    # Found enchanted form, price is per 160 units
                    drop_unit_price = enchanted_summary[0]["pricePerUnit"]
                    price_found = True

            # Fallback to base item if Enchanted not found
            if not price_found:
                drop_product = products.get(drop_item)
                if not drop_product:
                    print(f"Warning: Drop item {drop_item} for {item_name} not found in Bazaar")
                    continue
                
                drop_sell_summary = drop_product.get("sell_summary", [])
                if not drop_sell_summary:
                    continue

                drop_unit_price = drop_sell_summary[0]["pricePerUnit"]
            # x38 based on testing, dk why so much
            drops_revenue += drop_qty / 160 * 38 * drop_unit_price

        revenue = instasell_price + drops_revenue

        # Calculate Cost of Ingredients (Insta-Buy)
        total_cost = 0
        possible = True
        
        for ing_name, qty in made_of.items():
            if ing_name == "FIRE":
                # Fire is free/block
                continue

            ing_data = products.get(ing_name)
            if not ing_data:
                 skipped_items.append(f"{item_name}: Ingredient '{ing_name}' not found")
                 possible = False
                 break
            
            buy_summary = ing_data.get("buy_summary", [])
            if not buy_summary:
                skipped_items.append(f"{item_name}: Ingredient '{ing_name}' has no sell offers")
                possible = False
                break
            
            unit_cost = buy_summary[0]["pricePerUnit"]
            cost = unit_cost * qty
            total_cost += cost

        if possible:
            # Adjust cost for non-destructive crops (Ingredients last 48h)
            # "the crops required for crop mutation are alive for 48 hours, so price should be 48/[stages]"
            is_destructive = data.get("destructive", False)
            explodes = data.get("explodes_on_harvest", False)
            
            if not is_destructive and not explodes and stages > 0:
                harvests_per_set = 48 / stages
                total_cost = total_cost / harvests_per_set

            profit = revenue - total_cost
            
            # Use positions algorithm to get max spots
            try:
                # solve_layout requires (item_name, item_data, all_items)
                _, spots, _ = solve_layout(item_name, data, recipes)
            except Exception as e:
                spots = 0
                print(f"Error solving layout for {item_name}: {e}")

            plot_profit = profit * spots
            
            # Profit PER HOUR (Total Plot Profit / Hours)
            if hours_to_grow > 0:
                profit_per_hour = plot_profit / hours_to_grow
            else:
                profit_per_hour = 0 # Or infinite? Technically instant growth.
                # If stage is 0, let's treat as 'Not a crop' or 'Instant'.
                # But typically these are just simple crafted items that don't grow?
                # The user added stages=0 to basic crops (Ashwreath).
                # Wait, Ashwreath isn't a crop?
                # "I added a new parameter stages...".
                # If stages=0, perhaps it doesn't grow and profit/hr is irrelevant (or just profit).
                # We will display 0 or N/A.

            profits.append({
                "item": item_name,
                "spots": spots,
                "unit_profit": profit,
                "total_profit": plot_profit,
                "hours": hours_to_grow,
                "profit_per_hour": profit_per_hour
            })

    # Sort by PROFIT PER HOUR descending
    profits.sort(key=lambda x: x['profit_per_hour'], reverse=True)

    sys.stdout.reconfigure(encoding='utf-8')

    print(f"Processed {len(profits)} items out of {len(recipes)} recipes.\n")
    
    # Header
    print(f"{'ITEM':<20} | {'SPOTS':<5} | {'HOURS':<6} | {'PLOT_PROFIT':<15} | {'PROFIT/HOUR':<15}")
    print("-" * 80)
    
    for p in profits:
        print(f"{p['item']:<20} | {p['spots']:<5} | {p['hours']:<6} | {p['total_profit']:<15.1f} | {p['profit_per_hour']:<15.1f}")

    if skipped_items:
        print("\nSkipped Items:")
        for skip in skipped_items:
            print(f" - {skip}")

if __name__ == "__main__":
    calculate_profits()
