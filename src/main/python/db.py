"""Scrutini Database Functions."""
import sqlite3
import os
import csv
import datetime
import classes as sc


class SCDatabase:
    """Control access to the database."""

    def __init__(self, settings):
        """Access the database."""
        self.settings = settings
        if self.settings.verbose:
            print("Connecting to DB...")
        if not os.path.exists(self.settings.db_file):
            if self.settings.verbose:
                print("")
            self.conn = self.create_connection()
            self.create_schema()
            self.tables = Tables(self)
            # self.insert_initial_data()
        else:
            self.conn = self.create_connection()
            self.tables = Tables(self)
        self.cursor = self.conn.cursor()

    def open_connection(self):
        """Open a DB connection."""
        self.conn = self.create_connection()

    def close_connection(self):
        """Close the DB connection."""
        self.conn.close()

    def create_connection(self):
        """Create a database connection to the SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(self.settings.db_file)
        except sqlite3.Error as error:
            print(error)
        return conn

    def create_schema(self):
        """Load the schema into the DB."""
        print('Setting up database')
        with open(self.settings.schema_file, 'rt') as file:
            schema = file.read()
        self.conn.executescript(schema)
        self.conn.commit()

    # def check(self):
    #     """Check whether the DB is new, and create schema and load defaults."""
    #     if os.path.exists(self.settings.db_file):
    #         print(f'Database {self.settings.db_file} exists.')
    #     else:
    #         print(f'{self.settings.db_file} is a new database.')
    #         self.create_schema()
            # self.insert_initial_data()

    # def insert_initial_data(self):
    #     """Preload the DB with some necessary data."""
    #     print('Inserting initial data')
        # categories = [sc.DancerCat(0, '', '', 1),
        #               sc.DancerCat(0, 'Primary', 'P', 1),
        #               sc.DancerCat(0, 'Beginner', 'B', 1),
        #               sc.DancerCat(0, 'Novice', 'N', 1),
        #               sc.DancerCat(0, 'Intermediate', 'I', 1),
        #               sc.DancerCat(0, 'Premier', 'X', 1),
        #               sc.DancerCat(0, 'Choreography', 'C', 1),
        #               sc.DancerCat(0, 'Special Award', 'S', 1)]
        # for category in categories:
        #     self.tables.categories.insert(category)
        # types = [sc.CompetitionType(0, 'Regular', 'Reg', 0, 1),
        #          sc.CompetitionType(0, 'Championship', 'Champ', 1, 1),
        #          sc.CompetitionType(0, 'Premiership', 'Prem', 1, 1)]
        # for tp in types:
        #     self.tables.competition_types.insert(tp)
        # place_values = [sc.PlaceValue(1, 137), sc.PlaceValue(2, 91),
        #                 sc.PlaceValue(3, 71), sc.PlaceValue(4, 53),
        #                 sc.PlaceValue(5, 37), sc.PlaceValue(6, 23)]
        # for pv in place_values:
        #     self.tables.place_values.insert(pv)
        # self.tables.judges.insert(sc.Judge(0, '', '', 9999999999))
        # print('Loading dances...')
        # dances = ['Dance/Award', 'Highland Fling', 'Sword Dance',
        #           'Sean Triubhas', 'Reel', 'Flora', 'Scottish Lilt', 'Jig',
        #           'Sailor\'s Hornpipe', 'Highland Laddie', 'Village Maid',
        #           'Blue Bonnets', 'Earl of Erroll', 'Scotch Measure',
        #           'Barracks Johnnie', 'Pas de Basques',
        #           'Pas de Basques and High Cuts', 'Scholarship',
        #           'Most Promising', 'Special Award', 'Dancer of the Day',
        #           'Choreography', 'Special/Trophy Fling', 'Broadswords',
        #           'Cake Walk', 'Reel Team']
        # for d in dances:
        #     self.tables.dances.insert(sc.Dance(0, d))
        # self.conn.commit()

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
        self.competition_types = TableCompetitionTypes(db)
        self.competitions = TableCompetitions(db)
        self.categories = TableCategories(db)
        self.judges = TableJudges(db)
        self.dancers = TableDancers(db)
        self.groups = TableGroups(db)
        self.dances = TableDances(db)
        self.events = TableEvents(db)
        self.place_values = TablePlaceValues(db)
        self.scores = TableScores(db)


class TableCompetitionTypes:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self):
        new_type = sc.CompetitionType(0, '', '', 0, 0)
        return self.insert(new_type)

    def insert(self, type):
        self.cursor.execute(f"insert into competitionTypes (name, abbrev,\
                            isChampionship, protected) values\
                            (\"{type.name}\", \"{type.abbrev}\",\
                            {type.isChampionship}, {type.isProtected})")
        type.id = self.cursor.lastrowid
        return type

    def update(self, type):
        self.cursor.execute('update competitionTypes set name = \"%s\", abbrev\
                             = \"%s\", isChampionship = %d, protected = %d\
                             where id = %d' %
                            (type.name, type.abbrev, type.isChampionship,
                             type.isProtected, type.id))
        self.conn.commit()
        return type


class TableCompetitions:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()
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

    def new(self):
        today = datetime.date.today()
        competition = sc.Competition(0, '', '', today, today, '', 0, 0)
        return self.insert(competition)

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
        self.conn.commit()  # This should probably be handled elsewhere
        return comp

    def remove(self, id):
        """Delete the Competition specified by id and associated objects"""
        self.cursor.execute('delete from competitions where id = %d' % int(id))
        self.db.tables.judges.remove_by_competition(id)
        self.db.tables.groups.remove_by_competition(id)
        self.db.tables.dancers.remove_by_competition(id)
        self.db.tables.events.remove_by_competition(id)
        self.conn.commit()  # Right place?


class TableJudges:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self, comp_id):
        judge = sc.Judge(0, '', '', comp_id)
        return self.insert(judge)

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
        self.conn.commit()  # Right place?
        return judge

    def remove(self, id):
        """Delete a selected Judge specified by id"""
        self.cursor.execute('delete from judges where id = %d' % int(id))
        self.conn.commit()  # Right place?

    def remove_by_competition(self, id):
        """Delete all Judges in a Competition specified by Competition.id"""
        self.cursor.execute(f"delete from judges where\
                             competition = {int(id)}")
        self.conn.commit()


class TableGroups:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def get_by_name(self, name):
        """Return a single DancerGroup specified by name"""
        self.cursor.execute('select * from dancerGroups where name = \"%s\"'
                            % name)
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

    def get_or_new(self, comp_id, g_string):
        """Look for an existing DancerGroup, but make a new one if not found"""
        if self.get_by_abbrev(g_string) is not None:
            return self.get_by_abbrev(g_string)
        elif self.get_by_name(g_string) is not None:
            return self.get_by_name(g_string)
        else:
            dancer_group = self.new(comp_id)
            dancer_group.name = g_string
            a_string = g_string[:3]
            got_it = False
            i = 0
            while not got_it:
                if self.get_by_abbrev(a_string) is None:
                    got_it = True
                else:
                    if i < 1:
                        i = 1
                        a_string = f"{a_string}{i}"
                    else:
                        i += 1
                        a_string = f"{a_string[:-1]}{i}"
            dancer_group.abbrev = a_string
            return self.update(dancer_group)

    def new(self, comp_id):
        dancerGroup = sc.DancerGroup(0, '', '', 4, 99, 0, comp_id)
        return self.insert(dancerGroup)

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
        self.conn.commit()
        return group

    def remove(self, id):
        """Delete a DancerGroup specified by id"""
        self.cursor.execute('delete from dancerGroups where id = %d' % int(id))
        # Now disconnect this DG from any dancers:
        self.unjoin_by_group(id)
        self.conn.commit()

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
        self.conn.commit()

    def unjoin(self, dancer_id, group_id):
        """Remove the connection between Dancer and DancerGroup"""
        self.cursor.execute('delete from dancerGroupJoin where (dancer = %d\
                             and dancerGroup = %d)' %
                            (int(dancer_id), int(group_id)))
        self.conn.commit()

    def unjoin_by_dancer(self, id):
        """Remove all DancerGroups from a Dancer"""
        self.cursor.execute('delete from dancerGroupJoin where dancer = %d'
                            % int(id))
        self.conn.commit()

    def unjoin_by_group(self, id):
        """Remove all Dancers from a DancerGroup"""
        self.cursor.execute('delete from dancerGroupJoin where dancerGroup =\
                             %d' % int(id))
        self.conn.commit()


class TableDancers:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self, comp_id):
        dancer = sc.Dancer(0,'','','','','','','','',0,'','','','','','',0,0,comp_id)
        return self.insert(dancer)

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
        self.conn.commit()
        return dancer

    def remove_by_competition(self, id):
        """Delete all Dancers in a Competition"""
        self.cursor.execute(f"delete from dancers where competition = {id}")
        self.conn.commit()

    def remove(self, id):
        """Delete a single Dancer by id"""
        self.cursor.execute('delete from dancers where id = %d' % int(id))
        self.db.tables.groups.unjoin_by_dancer(id)
        self.conn.commit()


class TableDances:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self):
        dance = sc.Dance(0,'')
        return self.insert(dance)

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
        self.conn.commit()
        return dance


class TableScores:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self):
        score = sc.Score(0, None, None, None, None, 0.0)
        return self.insert(score)

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
        self.conn.commit()
        return score

    def remove_by_event(self, id):
        """Delete all Scores in an Event"""
        self.cursor.execute('delete from scores where event = %d' % id)
        self.conn.commit()

    def remove_by_event_judge(self, event_id, judge_id):
        """Remove every Score that has been entered for a Judge in an Event"""
        self.cursor.execute('delete from scores where event = %d and judge =\
                             %d' % (event_id, judge_id))
        self.conn.commit()


class TableEvents:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_by_competition(self, id):
        self.cursor.execute(f"select * from events where competition = {id}")
        results = self.cursor.fetchall()
        events = []
        for e in results:
            if self.db.settings.verbose:
                print(*e)
            events.append(sc.Event(*e))
        return events

    def get_by_group(self, id):
        self.cursor.execute(f"select * from events where dancerGroup = {id}")
        results = self.cursor.fetchall()
        events = []
        for e in results:
            if self.db.settings.verbose:
                print(*e)
            events.append(sc.Event(*e))
        return events

    def get(self, id):
        self.cursor.execute('select * from events where id = %d' % int(id))
        return sc.Event(*self.cursor.fetchone())

    def new(self, dancerGroup_id=0, comp_id=0):
        event = sc.Event(0, '', dancerGroup_id, 0, comp_id, 1, 6, 1)
        return self.insert(event)

    def insert(self, event):
        self.cursor.execute(f"insert into events (name, dancerGroup, dance,\
                            competition, countsForOverall, numPlaces,\
                            earnsStamp) values (\'{event.name}\',\
                            {event.dancerGroup}, {event.dance},\
                            {event.competition}, {event.countsForOverall},\
                            {event.numPlaces}, {event.earnsStamp})")
        event.id = self.cursor.lastrowid
        return event

    def update(self, event):
        if self.db.settings.verbose:
            print(f"DB TableEvents Update: {event.name}")
        self.cursor.execute('update events set name = \"%s\", dancerGroup =\
                             %d, dance = %d, competition = %d,\
                             countsForOverall = %d, numPlaces = %d,\
                             earnsStamp = %d where id = %d' %
                            (event.name, event.dancerGroup, event.dance,
                             event.competition, event.countsForOverall,
                             event.numPlaces, event.earnsStamp, event.id))
        self.conn.commit()
        return event

    def remove(self, id):
        self.cursor.execute('delete from events where id = %d' % id)
        self.db.tables.scores.remove_by_event(id)
        self.conn.commit()

    def remove_by_competition(self, id):
        events = self.get_by_competition(id)
        for e in events:
            self.remove(e.id)


class TableCategories:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def get_by_name(self, cname):
        self.cursor.execute('select * from dancerCats where name like \"%%%s\"'
                            % cname)
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerCat(*result)
        else:
            return None

    def new(self):
        category = sc.DancerCat(0, '', '', 0)
        return self.insert(category)

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
        self.conn.commit()
        return category

    def remove(self, id):
        self.cursor.execute('delete from dancerCats where id = %d' % id)
        self.conn.commit()


class TablePlaceValues:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

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

    def new(self):
        place_value = sc.PlaceValue(0, 0)
        return self.insert(place_value)

    def insert(self, placeValue):
        self.cursor.execute('insert into placeValues (place, points) values\
                            (%d,%d)' % (placeValue.place, placeValue.points))
        return placeValue

    def insert_table(self):
        self.cursor.execute('create table if not exists placeValues (place\
                            integer primary key not null, points integer);')
