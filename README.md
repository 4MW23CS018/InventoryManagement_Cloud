# # CLI Inventory Manager

A **terminal-only** inventory management system built with Python + Docker + MySQL.  
No browser, no UI. Everything runs from the command line.

Works on:
- **Killercoda** (Docker playground)
- **Google Cloud Console** (Cloud Shell)

---

## What It Does

- Add items with name, category, quantity, and price
- List inventory (filter by category)
- Restock or record sales (with full transaction log)
- Low stock warnings
- Inventory value report with category breakdown

---

## Project Structure

```
inventory-cli/
├── setup.sh          # Starts MySQL in Docker, creates tables
├── inventory.py      # Main CLI app
├── requirements.txt  # Python dependency
├── cleanup.sh        # Stops and removes the container
└── README.md
```

---

## Step-by-Step Guide

### Option A — Killercoda (Docker Playground)

> Go to https://killercoda.com → pick any Ubuntu playground

**Step 1 — Clone the project**
```bash
git clone https://github.com/YOUR_USERNAME/inventory-cli.git
cd inventory-cli
```

**Step 2 — Run setup**
```bash
chmod +x setup.sh
./setup.sh
```

**Step 3 — Install Python dependency**
```bash
pip install mysql-connector-python --break-system-packages
```

**Step 4 — Use the app**
```bash
python3 inventory.py --help
```

---

### Option B — Google Cloud Console (Cloud Shell)

> Open Google Cloud Console → click the Cloud Shell icon (top right)

**Step 1 — Clone the project**
```bash
git clone https://github.com/YOUR_USERNAME/inventory-cli.git
cd inventory-cli
```

**Step 2 — Start Docker (Cloud Shell has Docker)**
```bash
chmod +x setup.sh
./setup.sh
```

**Step 3 — Install Python dependency**
```bash
pip install mysql-connector-python --break-system-packages
```

**Step 4 — Use the app**
```bash
python3 inventory.py --help
```

---

## Commands & Examples

### Add items
```bash
python3 inventory.py add "Laptop" 10 999.99 --category Electronics
python3 inventory.py add "Mouse" 50 25.00 --category Electronics
python3 inventory.py add "Notebook" 100 3.50 --category Stationery
python3 inventory.py add "Pen" 200 1.20 --category Stationery
python3 inventory.py add "Desk Chair" 3 150.00 --category Furniture
```

### List all items
```bash
python3 inventory.py list
```

### List by category
```bash
python3 inventory.py list --category Electronics
```

### Restock an item
```bash
python3 inventory.py restock 1 5 --note "Supplier delivery"
```

### Record a sale
```bash
python3 inventory.py sell 1 2 --note "Online order"
python3 inventory.py sell 2 10
```

### View transaction history for an item
```bash
python3 inventory.py history 1
```

### Full inventory report
```bash
python3 inventory.py report
```

### Delete an item
```bash
python3 inventory.py delete 4
```

---

## Sample Output

### `list`
```
ID    Name                   Category        Qty      Price
────────────────────────────────────────────────────────────
1     Laptop                 Electronics     8        $999.99
2     Mouse                  Electronics     40       $25.00
3     Notebook               Stationery      100      $3.50
5     Desk Chair             Furniture       3        $150.00 ⚠ LOW
```

### `report`
```
═════════════════════════════════════════════
          INVENTORY REPORT
═════════════════════════════════════════════
  Total unique items : 4
  Total units        : 151
  Total stock value  : $9574.92

  By Category:
  Category        Items   Units   Value
  ────────────────────────────────────────
  Electronics     2       48      $9,099.92
  Stationery      1       100     $350.00
  Furniture       1       3       $450.00

  ⚠  Low Stock Alerts (< 5 units):
     - Desk Chair: 3 left

  Top Sold Items:
     - Mouse: 10 units sold
     - Laptop: 2 units sold
═════════════════════════════════════════════
```

---

## Cleanup

When you're done, remove the container:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

Or manually:
```bash
docker stop inventory-db && docker rm inventory-db
```

---

## Concepts Used

| Concept         | Where Used                                 |
|-----------------|--------------------------------------------|
| Docker          | MySQL runs inside a container              |
| MySQL           | Stores items and transactions              |
| Python + argparse | CLI with subcommands                    |
| Shell scripting | `setup.sh`, `cleanup.sh`                   |
| JOIN queries    | Report aggregates across two tables        |
| Foreign keys    | `transactions.item_id → items.id`          |
