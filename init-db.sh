#!/bin/bash
set -e

# Create the game_ctrl_user role if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'game_ctrl_user') THEN
            CREATE USER game_ctrl_user WITH PASSWORD 'GameCtrl!2828';
        END IF;
    END
    \$\$;

    -- Create database if it doesn't exist
    SELECT 'CREATE DATABASE game_ctrl'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'game_ctrl')\gexec

    GRANT ALL PRIVILEGES ON DATABASE game_ctrl TO game_ctrl_user;
    
    -- Connect to game_ctrl database and set up permissions
    \c game_ctrl
    GRANT ALL ON SCHEMA public TO game_ctrl_user;
EOSQL
