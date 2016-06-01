CREATE DATABASE IF NOT EXISTS gfonts 
CHARACTER SET = 'utf8'
COLLATE = 'utf8_general_ci';

CREATE USER 'gfontapp'@'localhost' 
IDENTIFIED BY '';

GRANT USAGE ON gfonts.* TO gfontapp;
GRANT ALL ON TABLE gfonts.* TO gfontapp;
SHOW GRANTS;
