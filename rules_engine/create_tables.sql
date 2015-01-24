create table patients (
	id serial not null primary key,
	title varchar (20),
	first_name varchar (255),
	last_name varchar (255),
	nhs_number varchar (10),
	email varchar (255),
	tel_no varchar (20),
	fax_no varchar (20)
);

insert into patients values (0, 'Mr', 'John', 'Smith', '7876236676', 'j.smith@someemailhost.com', '01234 567890', NULL);
insert into patients values (0, 'Ms', 'Jane', 'Smith', '2536623652', 'j.smith@anothremailhost.com', '01234 567890', NULL);

create table professionals (
	id serial not null primary key,
	title varchar (20),
	first_name varchar (255),
	last_name varchar (255),
	email varchar (255),
	tel_no varchar (20),
	fax_no varchar (20)
);

insert into professionals values (0, 'Dr', 'A', 'Jones', 'a.jones@annhsemailaddress.com', '0872872882', NULL);

create table recipients (
	id serial not null primary key,
	patient_id integer,
	professional_id integer
);

insert into recipients values (0, 1, NULL);
insert into recipients values (0, 2, NULL);
insert into recipients values (0, NULL, 1);


create table actions (
	id serial not null primary key,
	action_code varchar(4)
	content_id integer,
	recipient_id integer not null,
);

create table action_content (
	id serial not null primary key,
	action_type varchar(4),
	content text
);
	
create table rules (
	id serial not null primary key,
	patient_id integer not null,
	recipient_id integer not null,
	event_code varchar(4),
	action_code varchar(4),
	action_content_id integer not null
);

create table char_codes (
	domain	varchar(4) not null primary key
	char_code varchar(4) not null primary key
	description varchar (255)
);

create table event_logs (
	id serial not null primary key,
	rule_id integer not null,
	reason varchar(255),
	event_time date,
	action_time date
);

insert into char_codes values ('DOM', 'ACTT', 'Action type');
insert into char_codes values ('DOM', 'EVTT', 'Event type');
insert into char_codes values ('EVTT', 'ADM', 'Admission');
insert into char_codes values ('EVTT', 'A&E', 'A & E');
insert into char_codes values ('EVTT', 'AMB', 'Ambulance');
insert into char_codes values ('ACTT', 'EML', 'Email');
insert into char_codes values ('ACTT', 'FAX', 'Fax');
insert into char_codes values ('ACTT', 'SMS', 'SMS message');
insert into char_codes values ('ACTT', 'LET', 'Letter');


