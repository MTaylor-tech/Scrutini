/*  Schema for Scrutini
    Schema Version 0.01
*/

-- Competition Types include Regular, Championship, and Premiership and defines how scoring is done and number of judges
create table competition_types (
	id			integer primary key	autoincrement not null,
	name		text,
	abbrev		text,
	isChampionship	integer,
	protected 	integer
);

-- Competitions
create table competitions (
    id          integer primary key autoincrement not null,
    name        text,
    description text,
    eventDate   date,
    deadline    date,
    location    text,
    competition_type		integer,
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

--PlaceValues are the point values of different places in an event
create table placeValues (
	place		integer primary key not null,
	points		integer
);

-- Events are dances and special trophies at a particular competition which can award medals
create table events (
    id          integer primary key autoincrement not null,
    name        text,
    dancer_group integer,
    dance       integer,
    competition integer,
    counts_for_overall integer,
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

-- Dancer Groups are age groupings within the Dancer Categories
-- Additional Dancer Groups can be made that are for special awards
create table dancer_groups (
    id          integer primary key autoincrement not null,
    name        text,
    ageMin      integer,
    ageMax      integer,
    dancerCat   integer,
    competition integer,
    abbrev      text
);

-- This join table is used to link Dancers with DancerGroups so that there can be many
-- Dancers in each Group and a Dancer can be in many Groups
create table dancer_groupJoin (
    dancer       integer,
    dancer_group    integer
);

-- This join table is used to group Events with Dancer Groups
create table eventGroupJoin (
    id          integer primary key autoincrement not null,
    event       integer,
    dancer_group integer,
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
    dancer_group integer,
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

-- Settings stores information on the schema and app version as well as settings within the app
create table settings (
    name        text,
    version     real,
    schema      real,
    interface   integer,
    lastComp    integer,
    orderPlaces integer
);

-- Placing Values are the points awarded for placing in regular events
create table placingValues (
    place       integer,
    value       integer
);



