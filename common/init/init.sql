CREATE USER 'mysql_user'@'localhost' IDENTIFIED BY 'Pass123';

GRANT ALL PRIVILEGES ON passport.* TO 'mysql_user'@'localhost';

USE passport;

CREATE TABLE user (
    chat_id INT NOT NULL,
    channel VARCHAR(30) NOT NULL,
    province VARCHAR(3) NOT NULL,
    join_time INT NOT NULL,
    primary key (chat_id, channel, province)
);

CREATE TABLE office (
    office_id INT NOT NULL PRIMARY KEY,
    cap VARCHAR(5) NOT NULL,
    city VARCHAR(64) NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(200) NOT NULL,
    province VARCHAR(64) NOT NULL,
    province_shortcut VARCHAR(2) NOT NULL,
    time VARCHAR(5) NOT NULL
);

CREATE TABLE availabilities (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    office_id INT NOT NULL,
    day VARCHAR(10) NOT NULL,
    hour VARCHAR(5) NOT NULL,
    slots INT NOT NULL,
    discovered_timestamp INT NOT NULL,
    available VARCHAR(1) NOT NULL,
    ended_timestamp INT
);

