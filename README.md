# Hypixel Skyblock Mutations Solver

A Python project designed to calculate the most profitable crop mutations in Hypixel Skyblock. This tool determines the best layout and highest revenue by evaluating live Bazaar prices, recipe requirements, growth time, drop tables, and mutation layout spaces.

## Features

- **Live Data:** Fetches real-time Bazaar data using the official Hypixel API.
- **Profit Calculation:** Calculates expected total plot profit and profit per hour for various mutated crops, considering both direct sales and drops (such as enchanted items).
- **Layout Solver:** Analyzes spatial constraints (`positions.py`) to maximize the efficient placement and number of crop spots on a plot.
- **Crop Rules:** Accounts for unique crop mechanics, including whether crops are destructive (do not regrow), have multiple harvest stages, or explode upon harvest.

## Files

- `main.py`: The entry point for calculating and sorting all potential mutations by profit per hour.
- `positions.py`: Contains algorithms for optimally placing mutated crops and predicting layout arrangements.
- `crop_revenue.py`: Helper script focusing specifically on analyzing instant sell revenue and drops calculation for single crops.
- `items.json`: Contains the detailed recipe dictionary, noting ingredients, drops, stages, and destructive traits of crops.

## Installation & Usage

1. **Clone the repository.**
2. **Install dependencies:**  
   The project primarily requires the `requests` library to query the Hypixel API.
   ```bash
   pip install requests
   ```
3. **Run the Solver:**
   Analyze all recipes and output the sorted profits:
   ```bash
   python main.py
   ```
4. **Targeted Crop Revenue:**
   To calculate revenue for specific crops (e.g., BLASTBERRY or SHELLFRUIT):
   ```bash
   python crop_revenue.py
   ```

## Disclaimer

This tool uses the Hypixel API. Bazaar prices are subject to rapid change, and calculated profits depend heavily on the provided data and recipe rules in `items.json`.
