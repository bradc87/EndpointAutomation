drop table if exists TASK_DEPENDENCY;
drop table if exists SCHEDULE_DEFN;
drop table if exists ENDPOINT_USER;
drop table if exists ENDPOINT;
drop table if exists CALENDAR_DEFN;
drop table if exists CALENDAR;
drop table if exists TASK;
drop table if exists SCHEDULE_DEPENDENCY;
drop table if exists SCHEDULE;

CREATE TABLE SCHEDULE (
	ID SERIAL PRIMARY KEY,
	DISPLAY_NAME VARCHAR(100),
	ENABLED BOOLEAN );

CREATE TABLE SCHEDULE_DEPENDENCY (
	ID SERIAL PRIMARY KEY, 
	SCHEDULE_ID INT references SCHEDULE (ID), 
	ENABLED BOOLEAN, 
	DEP_TYPE VARCHAR(40),
	DEP_STRING VARCHAR(100),
	DEP_INT INT );

CREATE TABLE TASK (
	ID SERIAL UNIQUE,
	INSTANCE_ID INT, 
	SCHEDULE_ID INT, 
	STATUS VARCHAR(40),
	ENDPOINT_ID INT, 
	ENDPOINT_USER_ID INT,
	WORKING_DIR VARCHAR(200),
	SERVER_COMMAND VARCHAR(200),
	SERVER_COMMAND_ARGS VARCHAR(200),
	EFFECTIVE_DATE DATE NOT NULL,
	PRIMARY KEY (SCHEDULE_ID, INSTANCE_ID, EFFECTIVE_DATE))

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
	ENDPOINT_TYPE VARCHAR(40),
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
	TASK_ID INT,
	TASK_SCHEDULE_ID INT, 
	TASK_INSTANCE_ID INT, 
 	DEPENDENCY_ID INT references SCHEDULE_DEPENDENCY(ID), 
	ENABLED BOOLEAN,
	STATUS VARCHAR(40),
	DEP_TYPE VARCHAR(40),
	DEP_STRING VARCHAR(100),
	DEP_INT INT );



INSERT INTO endpoint (DISPLAY_NAME, ADDRESS, STATUS, ENABLED)
VALUES ('skyfall', 'localhost:5000', 'UNKNOWN', TRUE);

INSERT INTO CALENDAR (DISPLAY_NAME) VALUES ('EveryDay');

insert into endpoint_user(display_name, user_name, credential_type, credential)
values('brad@skyfall', 'brad', 'sudo', 'none' );

insert into schedule(display_name, enabled) values ('TestSchedule1', True);

insert into SCHEDULE_DEFN(schedule_id, server_command, server_command_args, run_user_id, working_dir, calendar_id, endpoint_id)
values(1, 'date', '', 1, '/home/brad', 1,1);

INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 1, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 2, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 3, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 4, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 5, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 6, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 7, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 8, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 9, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 10, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 11, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 12, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 13, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 14, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 15, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 16, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 17, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 18, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 19, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 20, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 21, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 22, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 23, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 24, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 25, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 26, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 27, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 28, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 29, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 30, True);
INSERT INTO CALENDAR_DEFN (CALENDAR_ID, DAY_OF_MONTH, ENABLED) VALUES (1, 31, True);




