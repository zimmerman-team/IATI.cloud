#!/bin/sh
PGPASSWORD="$1" pg_dump --no-owner -h $2 -p $3 -U $4 $5 > $6.dump