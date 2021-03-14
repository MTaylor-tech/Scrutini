/*  Schema for Scrutini
    Schema Version 0.03
*/

-- Competition Types include Regular, Championship, and Premiership and defines how scoring is done and number of judges
create table competitionTypes (
	id			integer primary key	autoincrement not null,
	name		text,
	abbrev		text,
	championship	integer,
	protected 	integer
);

insert into competitionTypes (
	name, abbrev, championship, protected
) values ('Regular', 'Reg', 0, 1), (
					'Championship', 'Champ', 1, 1), (
					'Premiership', 'Prem', 1, 1);

-- Competitions
create table competitions (
    id          integer primary key autoincrement not null,
    name        text,
    description text,
    eventDate   date,
    deadline    date,
    location    text,
    competitionType		integer,
    isChampionship integer
);

-- Dance Categories are groups of dances to help organize what dances each competition includes
create table categories (
    id           integer primary key autoincrement not null,
    name         text
);

-- Dances are names of dances and special trophies that can be chosen for an event
create table dances (
    id          integer primary key autoincrement not null,
    name        text
);

insert into dances (name) values
	('Dance/Award'), ('Highland Fling'), ('Sword Dance'), ('Sean Triubhas'),
	('Reel'), ('Flora'), ('Scottish Lilt'), ('Jig'), ("Sailor's Hornpipe"),
	('Highland Laddie'), ('Village Maid'), ('Blue Bonnets'),
	('Earl of Erroll'), ('Scotch Measure'), ('Barracks Johnnie'),
	('Pas de Basques'), ('Pas de Basques and High Cuts'), ('Scholarship'),
	('Most Promising'), ('Special Award'), ('Dancer of the Day'),
	('Choreography'), ('Special/Trophy Fling'), ('Broadswords'),
	('Cake Walk'), ('Reel Team');

--PlaceValues are the point values of different places in an event
create table placeValues (
	place		integer primary key not null,
	points		integer
);

insert into placeValues (
	place, points
) values (1, 137), (2, 91), (3, 71), (4, 53), (5,37), (6, 23);

-- Events are dances and special trophies at a particular competition which can award medals
create table events (
    id          integer primary key autoincrement not null,
    name        text,
    dancerGroup integer,
    dance       integer,
    competition integer,
    countsForOverall integer,
    numPlaces   integer,
    earnsStamp  integer
);

-- This join table is used to link Dances with Dance Categories so that there can be many
-- Dances in each Category and a Dance can be in many Categories
create table danceCatJoin (
    id          integer primary key autoincrement not null,
    dance       integer,
    category    integer
);

-- Dancer Categories are Primary, Beginner, Novice, Intermediate, Premier
create table dancerCats (
    id          integer primary key autoincrement not null,
    name        text,
    abbrev      text,
    protected   integer
);

insert into dancerCats (
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
create table dancerGroups (
    id          integer primary key autoincrement not null,
    name        text,
		abbrev      text,
    ageMin      integer,
    ageMax      integer,
    dancerCat   integer,
    competition integer
);

-- This join table is used to link Dancers with DancerGroups so that there can be many
-- Dancers in each Group and a Dancer can be in many Groups
create table dancerGroupJoin (
    dancer       integer,
    dancerGroup    integer
);

-- This join table is used to group Events with Dancer Groups
create table eventGroupJoin (
    id          integer primary key autoincrement not null,
    event       integer,
    dancerGroup integer,
    competition integer
);

-- Dancers are individual competitors
create table dancers (
    id          integer primary key autoincrement not null,
    firstName   text,
    lastName    text,
    scotDanceNum    text,
    street      text,
    city        text,
    state       text,
    zip         text,
    birthdate   date,
    age         integer,
    registeredDate  date,
    number      text,
    phonenum    text,
    email       text,
    teacher		text,
    teacherEmail text,
    dancerCat   integer,
    dancerGroup integer,
    competition integer
);

-- Scores
create table scores (
    id          integer primary key autoincrement not null,
    dancer      integer,
    event       integer,
    judge       integer,
    competition integer,
    score		real
);

-- Judges
create table judges (
    id          integer primary key autoincrement not null,
    firstName   text,
    lastName    text,
    competition integer
);

insert into judges (
	firstName, lastName, competition
) values ('', '', 9999999999);

-- Placing Values are the points awarded for placing in regular events
create table placingValues (
    place       integer,
    value       integer
);
