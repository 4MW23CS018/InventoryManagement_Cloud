#!/bin/bash
echo "Stopping and removing inventory-db container..."
docker stop inventory-db
docker rm inventory-db
echo "Cleanup done."
