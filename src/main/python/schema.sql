/*  Schema for Scrutini
    Schema Version 0.1
*/

-- Competition Types include Regular, Championship, and Premiership and defines how scoring is done and number of judges
create table competition_type (
	id			integer primary key	autoincrement not null,
	name		text,
	abbrev		text,
	championship	integer,
	protected 	integer
);

insert into competition_type (
	name, abbrev, championship, protected
) values ('Regular', 'Reg', 0, 1), (
					'Championship', 'Champ', 1, 1), (
					'Premiership', 'Prem', 1, 1);

-- Competitions
create table competition (
    id          integer primary key autoincrement not null,
    name        text,
    description text,
    event_date  date,
    deadline    date,
    location    text,
    competition_type		integer
);

-- Dance Categories are groups of dances to help organize what dances each
-- competition includes, e.g. Highland, National, Primary
create table dance_category (
    id           integer primary key autoincrement not null,
    name         text
);

-- Dances are names of dances and special trophies that can be chosen for an event
create table dance (
    id          integer primary key autoincrement not null,
    name        text
);

insert into dance (name) values
	('Dance/Award'), ('Highland Fling'), ('Sword Dance'), ('Sean Triubhas'),
	('Reel'), ('Flora'), ('Scottish Lilt'), ('Jig'), ("Sailor's Hornpipe"),
	('Highland Laddie'), ('Village Maid'), ('Blue Bonnets'),
	('Earl of Erroll'), ('Scotch Measure'), ('Barracks Johnnie'),
	('Pas de Basques'), ('Pas de Basques and High Cuts'), ('Scholarship'),
	('Most Promising'), ('Special Award'), ('Dancer of the Day'),
	('Choreography'), ('Special/Trophy Fling'), ('Broadswords'),
	('Cake Walk'), ('Reel Team');

-- This join table is used to link Dances with Dance Categories so that there can be many
-- Dances in each Category and a Dance can be in many Categories
create table dance_dance_category (
    dance       integer,
    dance_category    integer
);

--PlaceValues are the point values of different places in an event
create table place_value (
	place		integer primary key not null,
	points		integer
);

insert into place_value (
	place, points
) values (1, 137), (2, 91), (3, 71), (4, 53), (5,37), (6, 23);

-- Events are dances and special trophies at a particular competition which can award medals
create table event (
    id          integer primary key autoincrement not null,
    name        text,
    dancer_group integer,
    dance       integer,
    competition integer,
    counts_for_overall integer,
    num_places   integer,
    earns_stamp  integer
);

-- Dancer Categories are Primary, Beginner, Novice, Intermediate, Premier
create table dancer_category (
    id          integer primary key autoincrement not null,
    name        text,
    abbrev      text,
    protected   integer
);

insert into dancer_category (
		name, abbrev, protected
) values ('', '', 1), (
		'Primary', 'P', 1), (
		'Beginner', 'B', 1), (
		'Novice', 'N', 1), (
		'Intermediate', 'I', 1), (
		'Premier', 'X', 1), (
		'Choreography', 'C', 1), (
		'Special Award', 'S', 1);

-- Dancer Groups are age groupings within the Dancer Categories
-- Additional Dancer Groups can be made that are for special awards
create table dancer_group (
    id          integer primary key autoincrement not null,
    name        text,
		abbrev      text,
    age_min      integer,
    age_max      integer,
    dancer_category   integer,
    competition integer
);

-- This join table is used to link Dancers with DancerGroups so that there can be many
-- Dancers in each Group and a Dancer can be in many Groups
create table dancer_dancer_group (
    dancer       integer,
    dancer_group    integer
);

-- This join table is used to group Events with Dancer Groups
create table event_dancer_group (
    event       integer,
    dancer_group integer
);

-- Dancers are individual competitors
create table dancer (
    id          integer primary key autoincrement not null,
    first_name   text,
    last_name    text,
    scot_dance_num    text,
    street      text,
    city        text,
    state       text,
    zip         text,
    birthdate   date,
    age         integer,
    registered_date  date,
    competitor_num      text,
    phone_num    text,
    email       text,
    teacher		text,
    teacher_email text,
    dancer_category   integer,
    competition integer
);

-- Scores
create table score (
    id          integer primary key autoincrement not null,
    dancer      integer,
    event       integer,
    judge       integer,
    competition integer,
    score		real
);

-- Judges
create table judge (
    id          integer primary key autoincrement not null,
    first_name   text,
    last_name    text,
    competition integer
);

insert into judge (
	first_name, last_name, competition
) values ('', '', 9999999999);
