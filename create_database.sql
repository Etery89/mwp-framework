PRAGMA foreign_keys = on;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS learner;
CREATE TABLE learner (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    username VARCHAR (64),
    email VARCHAR (64),
    password VARCHAR (64),
    role VARCHAR (32)
);

DROP TABLE IF EXISTS course;
CREATE TABLE course (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (64),
    category VARCHAR (128),
    type VARCHAR (32)
);

DROP TABLE IF EXISTS course_learner;
CREATE TABLE course_learner (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    course_id INTEGER,
    learner_id INTEGER,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (learner_id) REFERENCES learner(id)
);

DROP TABLE IF EXISTS category;
CREATE TABLE category (
    id INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name VARCHAR (64),
    super_category VARCHAR (128)
);

COMMIT TRANSACTION;

