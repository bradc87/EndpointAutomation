drop table if exists TASK_DEPENDENCY;
drop table if exists SCHEDULE_DEFN;
drop table if exists ENDPOINT_USER;
drop table if exists ENDPOINT;
drop table if exists CALENDAR_DEFN;
drop table if exists CALENDAR;
drop table if exists TASK;
drop table if exists SCHEDULE_DEPEDENCY;
drop table if exists SCHEDULE;


CREATE TABLE SCHEDULE (
	ID SERIAL PRIMARY KEY,
	DISPLAY_NAME VARCHAR(100),
	ENABLED BOOLEAN );

CREATE TABLE SCHEDULE_DEPEDENCY (
	ID SERIAL PRIMARY KEY, 
	SCHEDULE_ID INT references SCHEDULE (ID), 
	ENABLED BOOLEAN, 
	DEP_STRING VARCHAR(100),
	DEP_INT INT );

CREATE TABLE TASK (
	ID SERIAL PRIMARY KEY,
	INSTANCE_ID INT, 
	SCHEDULE_ID INT, 
	STATUS VARCHAR(40),
	ENDPOINT_USER_ID INT,
	WORKING_DIR VARCHAR(200),
	SERVER_COMMAND VARCHAR(200),
	SERVER_COMMAND_ARGS VARCHAR(200) );

CREATE TABLE CALENDAR (
	ID SERIAL PRIMARY KEY, 
	DISPLAY_NAME VARCHAR(100) );

CREATE TABLE CALENDAR_DEFN (
	ID SERIAL PRIMARY KEY, 
	CALENDAR_ID INT references CALENDAR (ID), 
	DAY_OF_MONTH INT, 
	ENABLED BOOLEAN );

CREATE TABLE ENDPOINT (
	ID SERIAL PRIMARY KEY,
	DISPLAY_NAME VARCHAR(100),
	ADDRESS VARCHAR(200),
	STATUS VARCHAR(40), 
	ENABLED BOOLEAN,
	LAST_HEARTBEAT DATE, 
	LAST_ACTION DATE );

CREATE TABLE ENDPOINT_USER (
	ID SERIAL PRIMARY KEY,
	DISPLAY_NAME VARCHAR(100),
	USER_NAME VARCHAR(100),
	CREDENTIAL_TYPE VARCHAR(40), 
	CREDENTIAL VARCHAR(1000));

CREATE TABLE SCHEDULE_DEFN (
	ID SERIAL PRIMARY KEY,
	SCHEDULE_ID INT references SCHEDULE(ID), 
	SERVER_COMMAND VARCHAR(200),
	SERVER_COMMAND_ARGS VARCHAR(200),
	RUN_USER_ID INT references ENDPOINT_USER (ID), 
	WORKING_DIR VARCHAR(200),
	CALENDAR_ID INT references CALENDAR (ID), 
	ENDPOINT_ID INT references ENDPOINT (ID),
    ENABLED BOOLEAN );

CREATE TABLE TASK_DEPENDENCY (
	ID SERIAL PRIMARY KEY, 
 	DEPENDENCY_ID INT references SCHEDULE_DEPEDENCY (ID), 
	ENABLED BOOLEAN,
	STATUS VARCHAR(40) );

INSERT INTO endpoint (DISPLAY_NAME, ADDRESS, STATUS, ENABLED)
VALUES ('skyfall', 'localhost:5000', 'UNKNOWN', TRUE);


