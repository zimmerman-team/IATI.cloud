#!/bin/bash

# ========== CONFIG ==========
LEADER_HOST=91.99.48.74
CORE_NAME="transaction"                  # The Solr core to replicate
CORE_PATH="/mnt/HC_Volume_102717161/solr_follower_data/solr/server/solr/$CORE_NAME"
LEADER_CORE_PATH="/mnt/HC_Volume_102420500/solr_data/solr/server/solr/$CORE_NAME"
SSH_USER="zim"                       # Or solr / your SSH user
RSYNC_FLAGS="-aP --delete"             # Add --dry-run to test first  Add -z (-aPz) to compress during transfer

# ========== RSYNC ==========
echo "Starting rsync of core '$CORE_NAME' from $LEADER_HOST..."
rsync $RSYNC_FLAGS "$SSH_USER@$LEADER_HOST:$LEADER_CORE_PATH/data/index/" "$CORE_PATH/data/index/"

# Dry run:
# rsync -aP --dry-run "$SSH_USER@$LEADER_HOST:$LEADER_CORE_PATH/data/index/" "$CORE_PATH/data/index/"

# ========== SET PERMISSIONS ==========
echo "Fixing permissions..."
sudo chown -R 1001:root "$CORE_PATH/data/index"

echo "Done syncing core '$CORE_NAME'."

cd /home/zim/IATI.cloud
sudo docker compose down
sudo docker compose up -d solr-replication
echo "Restarted Solr Replication service."
