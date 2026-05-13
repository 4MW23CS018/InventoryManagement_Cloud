#!/bin/bash

echo "========================================="
echo "   CLI Inventory Manager - Setup"
echo "========================================="

# Start MySQL container
echo ""
echo "[1/3] Starting MySQL container..."
docker run --name inventory-db \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=inventorydb \
  -p 3306:3306 \
  -d mysql:8

# Wait for MySQL to be ready
echo ""
echo "[2/3] Waiting for MySQL to be ready (20 seconds)..."
sleep 20

# Create tables
echo ""
echo "[3/3] Creating tables..."
docker exec inventory-db mysql -uroot -proot inventorydb -e "
CREATE TABLE IF NOT EXISTS items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) DEFAULT 'General',
  quantity INT NOT NULL DEFAULT 0,
  price DECIMAL(10,2) NOT NULL,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT,
  type ENUM('IN', 'OUT') NOT NULL,
  quantity INT NOT NULL,
  note VARCHAR(100),
  done_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (item_id) REFERENCES items(id)
);
"

echo ""
echo "========================================="
echo "   Setup complete!"
echo "========================================="
echo ""
echo "Next step — install Python dependency:"
echo "  pip install mysql-connector-python --break-system-packages"
echo ""
echo "Then use the app:"
echo "  python3 inventory.py --help"
echo "========================================="
