"""Scrutini Database Functions."""
import sqlite3
import os
# from scruclasses import *
import scruclasses as sc
import csv


class SCDatabase:
    def __init__(self, db_file, schema_file, app_version, schema_version,
                 settings='current'):
        self.db_file = db_file
        self.schema_file = schema_file
        self.app_version = app_version
        self.schema_version = schema_version
        print("Connecting to DB...")
        self.settings = sc.Settings('current', self.app_version, self.schema_version,
                    0, 0, 1)
        if not os.path.exists(self.db_file):
            self.dbconn = self.create_connection(self.db_file)
            self.create_schema()
            self.tables = Tables(self)
            self.insert_initial_data()
        else:
            self.dbconn = self.create_connection(self.db_file)
            self.tables = Tables(self)
        # self.check()
        self.cursor = self.dbconn.cursor()
        self.settings = self.tables.settings.get(settings)
        # self.tables = Tables(self)

    def open_connection(self):
        """Open a DB connection."""
        self.dbconn = self.create_connection(self.db_file)

    def close_connection(self):
        """Close the DB connection."""
        self.dbconn.close()

    def create_connection(self, db_file):
        """Create a database connection to the SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
        return conn

    def create_schema(self):
        """Load the schema into the DB"""
        print('Setting up database')
        with open(self.schema_file, 'rt') as f:
            schema = f.read()
        # self.dbconn = self.create_connection(self.db_file)
        self.dbconn.executescript(schema)
        self.dbconn.commit()

    def check(self):
        """Check whether the DB is new, and create schema and load defaults"""
        if os.path.exists(self.db_file):
            print(f'Database {self.db_file} exists; check version')
            if self.settings.version == self.app_version:
                print("App Version %f is current version" %
                      self.settings.version)
            elif (self.settings.version < self.app_version):
                print("Settings need updated to version %f" % self.app_version)
            else:
                print("App needs updated to version %f to use this data" %
                      self.settings.version)
            if self.settings.schema == self.schema_version:
                print("Schema version %f is current version" %
                      self.schema_version)
            elif self.settings.schema < self.schema_version:
                print("Schema version %f need updated to %f" %
                      (self.settings.schema, self.schema_version))
            else:
                print("App needs updated to schema version %f to use this data"
                      % self.settings.schema)
        else:
            print('Need to create schema')
            self.create_schema()
            self.insert_initial_data()

    def insert_initial_data(self):
        """Preload the DB with some necessary data"""
        print('Inserting initial data')
        categories = [sc.DancerCat(0, '', '', 1),
                      sc.DancerCat(0, 'Primary', 'P', 1),
                      sc.DancerCat(0, 'Beginner', 'B', 1),
                      sc.DancerCat(0, 'Novice', 'N', 1),
                      sc.DancerCat(0, 'Intermediate', 'I', 1),
                      sc.DancerCat(0, 'Premier', 'X', 1),
                      sc.DancerCat(0, 'Choreography', 'C', 1),
                      sc.DancerCat(0, 'Special Award', 'S', 1)]
        for c in categories:
            self.tables.categories.insert(c)
        types = [sc.CompetitionType(0, 'Regular', 'Reg', 0, 1),
                 sc.CompetitionType(0, 'Championship', 'Champ', 1, 1),
                 sc.CompetitionType(0, 'Premiership', 'Prem', 1, 1)]
        for t in types:
            self.tables.competition_types.insert(t)
        self.tables.settings.insert(
            sc.Settings('current', self.app_version, self.schema_version,
                        0, 0, 1))

        place_values = [sc.PlaceValue(1, 137), sc.PlaceValue(2, 91),
                        sc.PlaceValue(3, 71), sc.PlaceValue(4, 53),
                        sc.PlaceValue(5, 37), sc.PlaceValue(6, 23)]
        for pv in place_values:
            self.tables.place_values.insert(pv)
        self.tables.judges.insert(sc.Judge(0, '', '', 9999999999))
        print('Loading dances...')
        dances = ['Dance/Award', 'Highland Fling', 'Sword Dance',
                  'Sean Triubhas', 'Reel', 'Flora', 'Scottish Lilt', 'Jig',
                  'Sailor\'s Hornpipe', 'Highland Laddie', 'Village Maid',
                  'Blue Bonnets', 'Earl of Erroll', 'Scotch Measure',
                  'Barracks Johnnie', 'Pas de Basques',
                  'Pas de Basques and High Cuts', 'Scholarship',
                  'Most Promising', 'Special Award', 'Dancer of the Day',
                  'Choreography', 'Special/Trophy Fling', 'Broadswords',
                  'Cake Walk', 'Reel Team']
        for d in dances:
            self.tables.dances.insert(sc.Dance(0, d))
        self.dbconn.commit()

    def retrieve_csv_dict(self, csv_filename):
        if os.path.exists(csv_filename):
            with open(csv_filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                return reader
        else:
            print('File not found.')
            return None

    def retrieve_csv_keys(self, csv_filename):
        if os.path.exists(csv_filename):
            with open(csv_filename, newline='') as csvfile:
                reader = csv.reader(csvfile)
                return next(reader)
        else:
            print('File not found.')
            return None


class Tables:
    def __init__(self, db):
        self.settings = TableSettings(db)
        self.competition_types = TableCompetitionTypes(db)
        self.competitions = TableCompetitions(db)
        self.categories = TableCategories(db)
        self.judges = TableJudges(db)
        self.dancers = TableDancers(db)
        self.groups = TableGroups(db)
        self.dances = TableDances(db)
        self.events = TableEvents(db)
        self.place_values = TablePlaceValues(db)


class TableSettings:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get(self, choice='current'):
        """Retrieve settings from DB

        Arguments:
        choice -- String; which settings to retrieve (default 'current')
        """
        self.cursor.execute(
            'SELECT * FROM settings WHERE name = \"%s\"' % choice)
        return sc.Settings(*self.cursor.fetchone())

    def insert(self, settings):
        """Create a new type of Settings"""
        self.cursor.execute('insert into settings(name, version, schema,\
                             interface, lastComp, orderPlaces) values(\"%s\",\
                             %f, %f, %d, %d, %d)' %
                            (settings.name, settings.version, settings.schema,
                             settings.interface, settings.lastComp,
                             settings.orderOfPlacings))
        self.dbconn.commit()

    def update(self, settings):
        """Save Settings"""
        self.cursor.execute('update settings set name = \"%s\", version = %f,\
                            schema = %f, interface = %d, lastComp = %d,\
                            orderPlaces=%d where name = \"%s\"' %
                            (settings.name, settings.version, settings.schema,
                             settings.interface, settings.lastComp,
                             settings.orderOfPlacings, settings.name))
        self.dbconn.commit()


class TableCompetitionTypes:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_all(self):
        """Return a list of CompetitionTypes"""
        self.cursor.execute('select * from competitionTypes')
        result = self.cursor.fetchall()
        if result is not None:
            competitionTypes = []
            for ct in result:
                competitionTypes.append(sc.CompetitionType(*ct))
            return competitionTypes
        else:
            return None

    def get(self, id):
        """Return a single specified CompetitionType by id"""
        self.cursor.execute('select * from competitionTypes where id = %d' %
                            int(id))
        return sc.CompetitionType(*self.cursor.fetchone())

    def insert(self, type):
        self.cursor.execute(f"insert into competitionTypes (name, abbrev,\
                            isChampionship, protected) values (\"{type.name}\",\
                            \"{type.abbrev}\", {type.isChampionship},\
                            {type.isProtected})")
        type.id = self.cursor.lastrowid
        return type

    def update(self, type):
        self.cursor.execute('update competitionTypes set name = \"%s\", abbrev\
                             = \"%s\", isChampionship = %d, protected = %d\
                             where id = %d' %
                            (type.name, type.abbrev, type.isChampionship,
                             type.isProtected, type.id))
        self.dbconn.commit()
        return type


class TableCompetitions:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()
        self.db = db

    def get_all(self):
        """Return a list of Competitions"""
        self.cursor.execute('select * from competitions')
        result = self.cursor.fetchall()
        if result is not None:
            competitions = []
            for c in result:
                competitions.append(sc.Competition(*c))
            return competitions
        else:
            return None

    def get(self, id):
        """Return a single Competition specified by id"""
        self.cursor.execute(f"select * from competitions where id = {int(id)}")
        return sc.Competition(*self.cursor.fetchone())

    def insert(self, comp):
        """Create a new Competition"""
        self.cursor.execute('insert into competitions(name, description,\
                            eventDate, deadline, location, competitionType,\
                            isChampionship)\
                            values (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,%d)'
                            % (comp.name, comp.description, comp.eventDate,
                               comp.deadline, comp.location,
                               comp.competitionType, comp.isChampionship))
        comp.id = self.cursor.lastrowid
        return comp

    def update(self, comp):
        """Save values for the selected Competition"""
        self.cursor.execute(f"update competitions set name='{comp.name}',\
                            description='{comp.description}',\
                            eventDate='{comp.eventDate}',\
                            deadline='{comp.deadline}',\
                            location='{comp.location}',\
                            competitionType={comp.competitionType},\
                            isChampionship={comp.isChampionship}\
                            where id={comp.id}")
        self.dbconn.commit()  # This should probably be handled elsewhere
        return comp

    def remove(self, id):
        """Delete the Competition specified by id and associated objects"""
        self.cursor.execute('delete from competitions where id = %d' % int(id))
        self.db.tables.judges.remove_by_competition(id)
        self.db.tables.groups.remove_by_competition(id)
        self.db.tables.dancers.remove_by_competition(id)
        self.db.tables.events.remove_by_competition(id)
        self.dbconn.commit()  # Right place?


class TableJudges:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_by_competition(self, id):
        """Return a list of all Judges in a Competition specified by
        Competition.id
        """
        self.cursor.execute(f"select * from judges where competition =\
                             {int(id)}")
        result = self.cursor.fetchall()
        if result is not None:
            judges = []
            for j in result:
                judges.append(sc.Judge(*j))
            return judges
        else:
            return None

    def get(self, id):
        """Return a single Judge specified by id"""
        self.cursor.execute('select * from judges where id = %d' % int(id))
        result = self.cursor.fetchone()
        return sc.Judge(*result)

    def insert(self, judge):
        """Create a new Judge"""
        self.cursor.execute(f"insert into judges\
                            (firstName, lastName, competition) values\
                            ('{judge.firstName}','{judge.lastName}',\
                            {judge.competition})")
        judge.id = self.cursor.lastrowid
        return judge

    def update(self, judge):
        """Save the specified Judge"""
        self.cursor.execute('update judges set firstName = \"%s\",\
                            lastName = \"%s\", competition = %d where id =%d'
                            % (judge.firstName, judge.lastName,
                               judge.competition, judge.id))
        self.dbconn.commit()  # Right place?
        return judge

    def remove(self, id):
        """Delete a selected Judge specified by id"""
        self.cursor.execute('delete from judges where id = %d' % int(id))
        self.dbconn.commit()  # Right place?

    def remove_by_competition(self, id):
        """Delete all Judges in a Competition specified by Competition.id"""
        self.cursor.execute(f"delete from judges where\
                             competition = {int(id)}")
        self.dbconn.commit()


class TableGroups:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_by_competition(self, id):
        """Return a list of all DancerGroups in a Competition"""
        self.cursor.execute(f"select * from dancerGroups where competition =\
                            {int(id)}")
        results = self.cursor.fetchall()
        if results is not None:
            groups = []
            for dg in results:
                groups.append(sc.DancerGroup(*dg))
            return groups
        else:
            return None

    def get(self, id):
        """Return a single DancerGroup specified by id"""
        self.cursor.execute(f"select * from dancerGroups where id = {int(id)}")
        return sc.DancerGroup(*self.cursor.fetchone())

    def get_by_abbrev(self, abbrev):
        """Return a single DancerGroup specified by abbrev"""
        self.cursor.execute('select * from dancerGroups where abbrev = \"%s\"'
                            % abbrev)
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerGroup(*result)
        else:
            return None

    def get_by_dancer(self, id):
        """Return a list of all DancerGroups a Dancer is in"""
        self.cursor.execute('select dancer, dancerGroup from dancerGroupJoin\
                             where dancer = %d' % id)
        results = self.cursor.fetchall()
        if results is not None:
            groups = []
            if len(results) > 0:
                for dg in results:
                    groups.append(self.get(dg[1]))
            return groups
        else:
            return None

    def insert(self, group):
        """Create a new DancerGroup"""
        self.cursor.execute(f"insert into dancerGroups(name, abbrev, ageMin,\
                            ageMax, dancerCat, competition) values\
                            ('{group.name}', '{group.abbrev}', {group.ageMin},\
                            {group.ageMax}, {group.dancerCat},\
                            {group.competition})")
        group.id = self.cursor.lastrowid
        return group

    def update(self, group):
        """Save a DancerGroup"""
        self.cursor.execute('update dancerGroups set name = \"%s\", abbrev =\
                             \"%s\", ageMin = %d, ageMax = %d, dancerCat = %d,\
                             competition = %d where id =%d' %
                            (group.name, group.abbrev, group.ageMin,
                             group.ageMax, group.dancerCat, group.competition,
                             group.id))
        self.dbconn.commit()
        return group

    def remove(self, id):
        """Delete a DancerGroup specified by id"""
        self.cursor.execute('delete from dancerGroups where id = %d' % int(id))
        # Now disconnect this DG from any dancers:
        self.unjoin_by_group(id)
        self.dbconn.commit()

    def remove_by_competition(self, id):
        """Delete all DancerGroups in a Competition"""
        groups = self.get_by_competition(id)
        for dg in groups:
            self.remove(dg.id)

    def join(self, dancer_id, group_id):
        check = self.get_by_dancer(dancer_id)
        if check is not None:
            for dg in check:
                if dg.id == group_id:
                    # Already in group
                    return
        self.cursor.execute('insert into dancerGroupJoin (dancer, dancerGroup)\
                            values(%d, %d)' % (dancer_id, group_id))
        self.dbconn.commit()

    def unjoin(self, dancer_id, group_id):
        """Remove the connection between Dancer and DancerGroup"""
        self.cursor.execute('delete from dancerGroupJoin where (dancer = %d\
                             and dancerGroup = %d)' %
                            (int(dancer_id), int(group_id)))
        self.dbconn.commit()

    def unjoin_by_dancer(self, id):
        """Remove all DancerGroups from a Dancer"""
        self.cursor.execute('delete from dancerGroupJoin where dancer = %d'
                            % int(id))
        self.dbconn.commit()

    def unjoin_by_group(self, id):
        """Remove all Dancers from a DancerGroup"""
        self.cursor.execute('delete from dancerGroupJoin where dancerGroup =\
                             %d' % int(id))
        self.dbconn.commit()


class TableDancers:
    def __init__(self, db):
        self.db = db
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def find(self, dancer):
        """Return the Dancer number for sorting"""
        return dancer.number

    def get_ordered_by_number(self, group_id):
        """Return all Dancers in a DancerGroup, sorted by Dancer number"""
        dancers = self.get_by_group(group_id)
        if len(dancers) > 0:
            dancers.sort(key=self.find)
        return dancers

    def get_by_group(self, id):
        """Return all Dancers in a DancerGroup"""
        self.cursor.execute('select dancer, dancerGroup from dancerGroupJoin\
                             where dancerGroup = %d' % id)
        results = self.cursor.fetchall()
        if results is not None:
            dancers = []
            for d in results:
                dancers.append(self.get(d[0]))
            return dancers
        else:
            return []

    def get_by_competition(self, id):
        """Return all Dancers in a Competition"""
        self.cursor.execute(f"select * from dancers where competition = {id}")
        results = self.cursor.fetchall()
        if results is not None:
            dancers = []
            for d in results:
                dancers.append(sc.Dancer(*d))
            return dancers
        else:
            return []

    def get(self, id):
        """Select a single Dancer by id"""
        self.cursor.execute('select * from dancers where id = %d' % int(id))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.Dancer(*result)
        else:
            return None

    def insert(self, dancer):
        """Create a new Dancer"""
        self.cursor.execute('insert into dancers (firstName, lastName,\
                             scotDanceNum, street, city, state, zip,\
                             birthdate, age, registeredDate, number, phonenum,\
                             email, teacher, teacherEmail, dancerCat,\
                             dancerGroup, competition) values (\"%s\", \"%s\",\
                             \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\",\
                             %d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\",\
                             \"%s\",%d,%d,%d)' %
                            (dancer.firstName, dancer.lastName,
                             dancer.scotDanceNum, dancer.street, dancer.city,
                             dancer.state, dancer.zipCode, dancer.birthdate,
                             dancer.age, dancer.registeredDate, dancer.number,
                             dancer.phonenum, dancer.email, dancer.teacher,
                             dancer.teacherEmail, dancer.dancerCat,
                             dancer.dancerGroup, dancer.competition))
        dancer.id = self.cursor.lastrowid
        return dancer

    def update(self, dancer):
        """Save a Dancer"""
        self.cursor.execute('update dancers set firstName = \"%s\", lastName =\
                             \"%s\", scotDanceNum = \"%s\", street  = \"%s\",\
                             city = \"%s\", state = \"%s\", zip = \"%s\",\
                             birthdate = \"%s\", age = %d, registeredDate =\
                             \"%s\", number = \"%s\", phonenum = \"%s\",\
                             email = \"%s\", teacher = \"%s\", teacherEmail =\
                             \"%s\", dancerCat = %d, dancerGroup = %d,\
                             competition = %d where id = %d' %
                            (dancer.firstName, dancer.lastName,
                             dancer.scotDanceNum, dancer.street, dancer.city,
                             dancer.state, dancer.zipCode, dancer.birthdate,
                             dancer.age, dancer.registeredDate, dancer.number,
                             dancer.phonenum, dancer.email, dancer.teacher,
                             dancer.teacherEmail, dancer.dancerCat,
                             dancer.dancerGroup, dancer.competition,
                             dancer.id))
        self.dbconn.commit()
        return dancer

    def remove_by_competition(self, id):
        """Delete all Dancers in a Competition"""
        self.cursor.execute(f"delete from dancers where competition = {id}")
        self.dbconn.commit()

    def remove(self, id):
        """Delete a single Dancer by id"""
        self.cursor.execute('delete from dancers where id = %d' % int(id))
        self.db.tables.groups.unjoin_by_dancer(id)
        self.dbconn.commit()


class TableDances:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_all(self):
        """Return all Dances"""
        self.cursor.execute('select * from dances')
        results = self.cursor.fetchall()
        if results is not None:
            dances = []
            for d in results:
                dances.append(sc.Dance(*d))
            return dances
        else:
            return []

    def get(self, id):
        """Return a single Dance by id"""
        self.cursor.execute('select * from dances where id = %d' % int(id))
        return sc.Dance(*self.cursor.fetchone())

    def insert(self, dance):
        """Create a new Dance"""
        self.cursor.execute(f"insert into dances (name) values\
                            (\"{dance.name}\")")
        dance.id = self.cursor.lastrowid
        return dance

    def update(self, dance):
        """Save a Dance"""
        self.cursor.execute('update dances set name = \"%s\" where id = %d' %
                            (dance.name, dance.id))
        self.dbconn.commit()
        return dance


class TableScores:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get(self, id):
        """Get a single Score item"""
        self.cursor.execute('select * from scores where id = %d' % int(id))
        result = self.cursor.fetchone()
        return sc.Score(*result)

    def get_by_event_dancer(self, event_id, dancer_id):
        """Return a Dancer's Score in an Event"""
        self.cursor.execute('select * from scores where event = %d and dancer\
                             = %d' % (int(event_id), int(dancer_id)))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.Score(*result)
        else:
            return None

    def get_by_event(self, id):
        """Return a list of all Scores from an Event"""
        self.cursor.execute('select * from scores where event = %d' % id)
        results = self.cursor.fetchall()
        scores = []
        for s in results:
            scores.append(sc.Score(*s))
        return scores

    def exists_for_event(self, id):
        """Verify if there are any Scores for an Event"""
        scores = self.get_by_event(id)
        if scores is None or scores == []:
            return False
        else:
            return True

    def insert(self, score):
        """Create a new Score item"""
        self.cursor.execute(f"insert into scores (dancer, event, judge,\
                            competition, score) values ({score.dancer},\
                            {score.event}, {score.judge}, {score.competition},\
                            {score.score})")
        score.id = self.cursor.lastrowid
        return score

    def update(self, score):
        """Save a Score"""
        self.cursor.execute('update scores set dancer = %d, event = %d, judge\
                             = %d, competition = %d, score = %f where id = %d'
                            % (score.dancer, score.event, score.judge,
                               score.competition, score.score, score.id))
        self.dbconn.commit()
        return score

    def remove_by_event(self, id):
        """Delete all Scores in an Event"""
        self.cursor.execute('delete from scores where event = %d' % id)
        self.dbconn.commit()

    def remove_by_event_judge(self, event_id, judge_id):
        """Remove every Score that has been entered for a Judge in an Event"""
        self.cursor.execute('delete from scores where event = %d and judge =\
                             %d' % (event_id, judge_id))
        self.dbconn.commit()


class TableEvents:
    def __init__(self, db):
        self.db = db
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_by_competition(self, id):
        self.cursor.execute(f"select * from events where competition = {id}")
        results = self.cursor.fetchall()
        events = []
        for e in results:
            events.append(sc.Event(*e))
        return events

    def get_by_group(self, id):
        self.cursor.execute(f"select * from events where dancerGroup = {id}")
        results = self.cursor.fetchall()
        events = []
        for e in results:
            events.append(sc.Event(*e))
        return events

    def get(self, id):
        self.cursor.execute('select * from events where id = %d' % int(id))
        return sc.Event(*self.cursor.fetchone())

    def insert(self, event):
        self.cursor.execute(f"insert into events (name, dancerGroup, dance,\
                            competition, countsForOverall, numPlaces,\
                            earnsStamp) values ({event.name},\
                            {event.dancerGroup}, {event.dance},\
                            {event.competition}, {event.countsForOverall},\
                            {event.numPlaces}, {event.earnsStamp})")
        event.id = self.cursor.lastrowid
        return event

    def update(self, event):
        self.cursor.execute('update events set name = \"%s\", dancerGroup =\
                             %d, dance = %d, competition = %d,\
                             countsForOverall = %d, numPlaces = %d,\
                             earnsStamp = %d where id = %d' %
                            (event.name, event.dancerGroup, event.dance,
                             event.competition, event.countsForOverall,
                             event.numPlaces, event.earnsStamp, event.id))
        self.dbconn.commit()
        return event

    def remove(self, id):
        self.cursor.execute('delete from events where id = %d' % id)
        self.db.tables.scores.remove_by_event(id)
        self.dbconn.commit()

    def remove_by_competition(self, id):
        events = self.get_by_competition(id)
        for e in events:
            self.remove(e.id)


class TableCategories:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get_all(self):
        """Return a list of all DancerCats"""
        self.cursor.execute('select * from dancerCats')
        result = self.cursor.fetchall()
        if result is not None:
            categories = []
            for c in result:
                categories.append(sc.DancerCat(*c))
            return categories
        else:
            return None

    def get(self, id):
        self.cursor.execute('select * from dancerCats where id = %d' % int(id))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerCat(*result)
        else:
            return None

    def insert(self, category):
        """Add a new DancerCat object into the DB"""
        self.cursor.execute(f"insert into dancerCats (name, abbrev, protected)\
                            values ('{category.name}', '{category.abbrev}',\
                            {category.protected})")
        category.id = self.cursor.lastrowid
        return category

    def update(self, category):
        self.cursor.execute('update dancerCats set name = \"%s\", abbrev =\
                            \"%s\", protected = %d where id =%d' %
                            (category.name, category.abbrev,
                             category.protected, category.id))
        self.dbconn.commit()
        return category

    def remove(self, id):
        self.cursor.execute('delete from dancerCats where id = %d' % id)
        self.dbconn.commit()


class TablePlaceValues:
    def __init__(self, db):
        self.dbconn = db.dbconn
        self.cursor = self.dbconn.cursor()

    def get(self, place):
        self.cursor.execute('select place, points from placeValues where\
                            place = %d' % int(place))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.PlaceValue(*result)
        else:
            return None

    def get_all(self):
        self.cursor.execute('select place, points from placeValues')
        results = self.cursor.fetchall()
        values = []
        for pv in results:
            values.append(sc.PlaceValue(*pv))
        return values

    def insert(self, placeValue):
        self.cursor.execute('insert into placeValues (place, points) values\
                            (%d,%d)' % (placeValue.place, placeValue.points))
        return placeValue

    def insert_table(self):
        self.cursor.execute('create table if not exists placeValues (place\
                            integer primary key not null, points integer);')
