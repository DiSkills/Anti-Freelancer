CREATE USER messenger_user WITH PASSWORD 'messenger_user';

CREATE DATABASE messenger_db;
GRANT ALL PRIVILEGES ON DATABASE messenger_db TO messenger_user;
