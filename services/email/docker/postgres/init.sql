CREATE USER email_user WITH PASSWORD 'email_user';

CREATE DATABASE email_db;
GRANT ALL PRIVILEGES ON DATABASE email_db TO email_user;
