"""Scrutini Database Functions."""
import sqlite3
import os
import csv
import datetime
import classes as sc
from sWidgets import today


class SCDatabase:
    """Control access to the database."""

    def __init__(self, settings):
        """Access the database."""
        self.settings = settings
        self.competition = None
        if self.settings.verbose:
            print("Connecting to DB...")
        if not os.path.exists(self.settings.db_file):
            if self.settings.verbose:
                print("DB Not Found")
            self.conn = self.create_connection()
            self.cursor = self.conn.cursor()
            self.create_schema()
            self.tables = Tables(self)
            self.t = self.tables
            # self.insert_initial_data()
        else:
            self.conn = self.create_connection()
            self.cursor = self.conn.cursor()
            self.tables = Tables(self)
            self.t = self.tables
        self.s = self.settings
        self.get_competition()

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

    def get_competition(self):
        if self.competition is not None:
            if self.s.verbose:
                print(f"Already Set Competition {self.competition.iid}")
            return self.competition
        competitions_list = self.get_all_ids("competition")
        if self.s.verbose:
            print(f"All competitions: {competitions_list}")
        if self.s.last_comp in competitions_list:
            self.competition = self.t.competition.get(self.settings.last_comp)
            if self.s.verbose:
                print(f"Found Competition: {self.competition.iid}")
            return self.competition
        else:
            if self.s.verbose:
                print("No competition found.")
            return None

    def get_all_ids(self, table):
        """Return a list of all IDs"""
        self.cursor.execute('select id from %s' % table)
        result = self.cursor.fetchall()
        if result is not None:
            ids = []
            for iid in result:
                ids.append(iid[0])
            return ids
        else:
            return []

    def get_all(self, table, datatype):
        """Return a list of all from a table"""
        self.cursor.execute('select * from %s' % table)
        result = self.cursor.fetchall()
        if result is not None:
            items = []
            for item in result:
                items.append(datatype(*item))
            return items
        else:
            return []

    def get(self, table, datatype, iid):
        """Return a single item"""
        self.cursor.execute(f"select * from {table} where id = {iid}")
        result = self.cursor.fetchone()
        if result is not None:
            return datatype(*result)
        else:
            return None

    def save(self):
        self.conn.commit()
        if self.s.verbose:
            print("DB Saved")


class Tables:
    def __init__(self, db):
        self.competition_type = TableCompetitionTypes(db)
        self.competition = TableCompetitions(db)
        self.category = TableCategories(db)
        self.judge = TableJudges(db)
        self.dancer = TableDancers(db)
        self.group = TableGroups(db)
        self.dance = TableDances(db)
        self.event = TableEvents(db)
        self.place_value = TablePlaceValues(db)
        self.score = TableScores(db)


class TableCompetitionTypes:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        self.table = "competition_type"
        self.datatype = sc.CompetitionType

    def get_all(self):
        """Return a list of CompetitionTypes"""
        self.cursor.execute('select * from %s' % self.table)
        result = self.cursor.fetchall()
        if result is not None:
            competition_types = []
            for comp_type in result:
                competition_types.append(sc.CompetitionType(*comp_type))
            return competition_types
        else:
            return None

    def get(self, iid):
        """Return a single specified CompetitionType by id"""
        self.cursor.execute('select * from competition_type where id = %d' %
                            int(iid))
        return sc.CompetitionType(*self.cursor.fetchone())

    def new(self):
        new_type = sc.CompetitionType(0, '', '')
        return self.insert(new_type)

    def insert(self, c_type):
        self.cursor.execute(f"insert into competition_type (name, abbrev,\
                            championship, protected) values\
                            (\"{c_type.name}\", \"{c_type.abbrev}\",\
                            {c_type.championship}, {c_type.protected})")
        c_type.iid = self.cursor.lastrowid
        return c_type

    def update(self, c_type):
        self.cursor.execute('update competition_type set name = \"%s\", abbrev\
                             = \"%s\", championship = %d, protected = %d\
                             where id = %d' %
                            (c_type.name, c_type.abbrev, c_type.championship,
                             c_type.protected, c_type.iid))
        self.conn.commit()
        return type


class TableCompetitions:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        self.db = db
        self.table = "competition"
        self.datatype = sc.Competition

    def get_all(self):
        """Return a list of Competitions"""
        self.cursor.execute('select * from %s' % self.table)
        result = self.cursor.fetchall()
        if result is not None:
            competitions = []
            for comp in result:
                competitions.append(self.datatype(*comp))
            return competitions
        else:
            return None

    def get_all_ids(self):
        """Return a list of all IDs"""
        self.cursor.execute('select id from %s' % self.table)
        result = self.cursor.fetchall()
        if result is not None:
            ids = []
            for iid in result:
                ids.append(id)
            return ids
        else:
            return []

    def get(self, iid):
        """Return a single Competition specified by id"""
        self.cursor.execute(f"select * from competition where id = {int(iid)}")
        return sc.Competition(*self.cursor.fetchone())

    def new(self):
        competition = sc.Competition(0, '', '')
        return self.insert(competition)

    def insert(self, comp):
        """Create a new Competition"""
        self.cursor.execute(('insert into competition (name, description, '\
                            'event_date, deadline, location, competition_type)'\
                            'values (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d)'
                            % (comp.name, comp.description, comp.event_date,
                               comp.deadline, comp.location,
                               comp.competition_type)))
        comp.iid = self.cursor.lastrowid
        return comp

    def update(self, comp):
        """Save values for the selected Competition"""
        # Why doesn't this vvv work?
        # self.cursor.execute('update competition set name=%(name)s, '\
        #                     'description=%(description)s, '\
        #                     'event_date=%(event_date)s, '\
        #                     'deadline=%(deadline)s, '\
        #                     'location=%(location)s, '\
        #                     'competition_type=%(competition_type)s '\
        #                     'where id=%(iid)d' % {'name': comp.name,
        #                         'description': comp.description,
        #                         'event_date': comp.event_date,
        #                         'deadline': comp.deadline,
        #                         'location': comp.location,
        #                         'competition_type': comp.competition_type,
        #                         'iid': comp.iid
        #                     })
        self.cursor.execute(f"update competition set name='{comp.name}',"\
                            f"description='{comp.description}',"\
                            f"event_date='{comp.event_date}',"\
                            f"deadline='{comp.deadline}',"\
                            f"location='{comp.location}',"\
                            f"competition_type={comp.competition_type} "\
                            f"where id={comp.iid}")
        self.conn.commit()  # This should probably be handled elsewhere
        return comp

    def remove(self, iid):
        """Delete the Competition specified by id and associated objects"""
        self.cursor.execute('delete from competition where id = %d' % int(iid))
        self.db.tables.judge.remove_by_competition(iid)
        self.db.tables.group.remove_by_competition(iid)
        self.db.tables.dancer.remove_by_competition(iid)
        self.db.tables.event.remove_by_competition(iid)
        self.conn.commit()  # Right place?


class TableJudges:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_by_competition(self, c_id):
        """Return a list of all Judges in a Competition specified by
        Competition.id
        """
        self.cursor.execute(f"select * from judge where competition =\
                             {int(c_id)}")
        result = self.cursor.fetchall()
        if result is not None:
            judges = []
            for judge in result:
                judges.append(sc.Judge(*judge))
            return judges
        else:
            return None

    def get(self, iid):
        """Return a single Judge specified by id"""
        self.cursor.execute('select * from judge where id = %d' % int(iid))
        result = self.cursor.fetchone()
        return sc.Judge(*result)

    def new(self, comp_id):
        judge = sc.Judge(0, '', '', comp_id)
        return self.insert(judge)

    def insert(self, judge):
        """Create a new Judge"""
        self.cursor.execute(f"insert into judge\
                            (first_name, last_name, competition) values\
                            ('{judge.first_name}','{judge.last_name}',\
                            {judge.competition})")
        judge.iid = self.cursor.lastrowid
        return judge

    def update(self, judge):
        """Save the specified Judge"""
        self.cursor.execute('update judge set first_name = \"%s\",\
                            last_name = \"%s\", competition = %d where id =%d'
                            % (judge.first_name, judge.last_name,
                               judge.competition, judge.iid))
        self.conn.commit()  # Right place?
        return judge

    def remove(self, iid):
        """Delete a selected Judge specified by id"""
        self.cursor.execute('delete from judge where id = %d' % int(iid))
        self.conn.commit()  # Right place?

    def remove_by_competition(self, c_id):
        """Delete all Judges in a Competition specified by Competition.id"""
        self.cursor.execute(f"delete from judge where\
                             competition = {int(c_id)}")
        self.conn.commit()


class TableGroups:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_by_competition(self, c_id):
        """Return a list of all DancerGroups in a Competition"""
        self.cursor.execute(f"select * from dancer_group where competition =\
                            {int(c_id)}")
        results = self.cursor.fetchall()
        if results is not None:
            groups = []
            for group in results:
                groups.append(sc.DancerGroup(*group))
            return groups
        else:
            return None

    def get(self, iid):
        """Return a single DancerGroup specified by id"""
        self.cursor.execute(f"select * from dancer_group where id = {int(iid)}")
        result = self.cursor.fetchone()
        group = None
        if result is not None:
            group = sc.DancerGroup(*result)
        return group

    def get_by_abbrev(self, abbrev, comp_id):
        """Return a single DancerGroup specified by abbrev"""
        self.cursor.execute('select * from dancer_group where abbrev = \"%s\"\
                            and competition = %d' % (abbrev, comp_id))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerGroup(*result)
        else:
            return None

    def get_by_name(self, name, comp_id):
        """Return a single DancerGroup specified by name"""
        self.cursor.execute('select * from dancer_group where name = \"%s\"\
                            and competition = %d' % (name, comp_id))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerGroup(*result)
        else:
            return None

    def get_by_dancer(self, id):
        """Return a list of all DancerGroups a Dancer is in"""
        self.cursor.execute('select dancer, dancer_group from\
                            dancer_dancer_group where dancer = %d' % id)
        results = self.cursor.fetchall()
        if results is not None:
            groups = []
            for group in results:
                groups.append(self.get(group[1]))
            return groups
        else:
            return []

    def get_or_new(self, comp_id, g_string):
        """Look for an existing DancerGroup, but make a new one if not found"""
        if self.get_by_abbrev(g_string, comp_id) is not None:
            return self.get_by_abbrev(g_string, comp_id)
        elif self.get_by_name(g_string, comp_id) is not None:
            return self.get_by_name(g_string, comp_id)
        else:
            dancer_group = self.new(comp_id)
            dancer_group.name = g_string
            a_string = g_string[:3]
            got_it = False
            i = 0
            while not got_it:
                if self.get_by_abbrev(a_string, comp_id) is None:
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
        group = sc.DancerGroup(0, '', '', 4, 99, 0, comp_id)
        return self.insert(group)

    def insert(self, group):
        """Create a new DancerGroup"""
        self.cursor.execute(f"insert into dancer_group (name, abbrev, age_min,\
                            age_max, dancer_category, competition) values\
                            ('{group.name}', '{group.abbrev}', {group.age_min},\
                            {group.age_max}, {group.dancer_category},\
                            {group.competition})")
        group.iid = self.cursor.lastrowid
        return group

    def update(self, group):
        """Save a DancerGroup"""
        self.cursor.execute('update dancer_group set name = \"%s\", abbrev =\
                             \"%s\", age_min = %d, age_max = %d, dancer_category = %d,\
                             competition = %d where id =%d' %
                            (group.name, group.abbrev, group.age_min,
                             group.age_max, group.dancer_category, group.competition,
                             group.iid))
        self.conn.commit()
        return group

    def remove(self, iid):
        """Delete a DancerGroup specified by id"""
        self.cursor.execute('delete from dancer_group where id = %d' % int(iid))
        # Now disconnect this DG from any dancers:
        self.unjoin_by_group(iid)
        self.conn.commit()

    def remove_by_competition(self, c_id):
        """Delete all DancerGroups in a Competition"""
        groups = self.get_by_competition(c_id)
        for group in groups:
            self.remove(group.iid)

    def join(self, dancer_id, group_id):
        if not self.dancer_in_group(dancer_id, group_id):
            self.cursor.execute('insert into dancer_dancer_group (dancer, dancer_group)\
                                values(%d, %d)' % (dancer_id, group_id))
            self.conn.commit()

    def unjoin(self, dancer_id, group_id):
        """Remove the connection between Dancer and DancerGroup"""
        self.cursor.execute('delete from dancer_dancer_group where (dancer = %d\
                             and dancer_group = %d)' %
                            (int(dancer_id), int(group_id)))
        self.conn.commit()

    def unjoin_by_dancer(self, dancer_id):
        """Remove all DancerGroups from a Dancer"""
        self.cursor.execute('delete from dancer_dancer_group where dancer = %d'
                            % int(dancer_id))
        self.conn.commit()

    def unjoin_by_group(self, group_id):
        """Remove all Dancers from a DancerGroup"""
        self.cursor.execute('delete from dancer_dancer_group where dancer_group =\
                             %d' % int(group_id))
        self.conn.commit()

    def dancer_in_group(self, dancer_id, group_id):
        """Check if a dancer is in a group"""
        result = self.cursor.execute(f"select * from dancer_dancer_group where dancer = {dancer_id} and dancer_group = {group_id}")
        if result is None:
            return False
        else:
            return True


class TableDancers:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    # def find(self, dancer):
    #     """Return the Dancer number for sorting"""
    #     return dancer.competitor_num

    def get_ordered_by_number(self, group_id):
        """Return all Dancers in a DancerGroup, sorted by Dancer number"""
        dancers = self.get_by_group(group_id)
        if len(dancers) > 0:
            # dancers.sort(key=self.find)
            dancers.sort(key=lambda dancer: dancer.competitor_num)
        return dancers

    def get_by_group(self, group_id):
        """Return all Dancers in a DancerGroup"""
        self.cursor.execute('select dancer, dancer_group from dancer_dancer_group\
                             where dancer_group = %d' % group_id)
        results = self.cursor.fetchall()
        dancers = []
        if results is not None:
            for dancer in results:
                dancers.append(self.get(dancer[0]))
        return dancers

    def get_by_competition(self, c_id):
        """Return all Dancers in a Competition"""
        self.cursor.execute(f"select * from dancer where competition = {c_id}")
        results = self.cursor.fetchall()
        dancers = []
        if results is not None:
            for dancer in results:
                dancers.append(sc.Dancer(*dancer))
        return dancers

    def get(self, iid):
        """Select a single Dancer by id"""
        self.cursor.execute('select * from dancer where id = %d' % int(iid))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.Dancer(*result)
        else:
            return None

    def new(self, comp_id):
        dancer = sc.Dancer(0,'','','','','','','','',0,today(),'','','','','',0,comp_id)
        return self.insert(dancer)

    def insert(self, dancer):
        """Create a new Dancer"""
        self.cursor.execute('insert into dancer (first_name, last_name,\
                             scot_dance_num, street, city, state, zip,\
                             birthdate, age, registered_date, competitor_num,\
                             phone_num, email, teacher, teacher_email,\
                             dancer_category, competition) values\
                             (\"%s\", \"%s\",\
                             \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\",\
                             %d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\",\
                             \"%s\",%d,%d)' %
                            (dancer.first_name, dancer.last_name,
                             dancer.scot_dance_num, dancer.street, dancer.city,
                             dancer.state, dancer.zip, dancer.birthdate,
                             dancer.age, dancer.registered_date, dancer.competitor_num,
                             dancer.phone_num, dancer.email, dancer.teacher,
                             dancer.teacher_email, dancer.dancer_category,
                             dancer.competition))
        dancer.iid = self.cursor.lastrowid
        return dancer

    def update(self, dancer):
        """Save a Dancer"""
        self.cursor.execute('update dancer set first_name = \"%s\", last_name =\
                             \"%s\", scot_dance_num = \"%s\", street  = \"%s\",\
                             city = \"%s\", state = \"%s\", zip = \"%s\",\
                             birthdate = \"%s\", age = %d, registered_date =\
                             \"%s\", competitor_num = \"%s\", phone_num = \"%s\",\
                             email = \"%s\", teacher = \"%s\", teacher_email =\
                             \"%s\", dancer_category = %d,\
                             competition = %d where id = %d' %
                            (dancer.first_name, dancer.last_name,
                             dancer.scot_dance_num, dancer.street, dancer.city,
                             dancer.state, dancer.zip, dancer.birthdate,
                             dancer.age, dancer.registered_date, dancer.competitor_num,
                             dancer.phone_num, dancer.email, dancer.teacher,
                             dancer.teacher_email, dancer.dancer_category,
                             dancer.competition,
                             dancer.iid))
        self.conn.commit()
        return dancer

    def remove_by_competition(self, c_id):
        """Delete all Dancers in a Competition"""
        self.cursor.execute(f"delete from dancer where competition = {c_id}")
        self.conn.commit()

    def remove(self, iid):
        """Delete a single Dancer by id"""
        self.cursor.execute('delete from dancers where id = %d' % int(iid))
        self.db.tables.groups.unjoin_by_dancer(iid)
        self.conn.commit()


class TableDances:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        self.table = "dance"
        self.datatype = sc.Dance

    def get_all(self):
        """Return all Dances"""
        self.cursor.execute('select * from dance')
        results = self.cursor.fetchall()
        dances = []
        if results is not None:
            for dance in results:
                dances.append(sc.Dance(*dance))
        return dances

    def get_all_ids(self):
        """Return a list of all IDs"""
        self.cursor.execute('select id from %s' % self.table)
        result = self.cursor.fetchall()
        if result is not None:
            ids = []
            for iid in result:
                ids.append(iid[0])
            return ids
        else:
            return []

    def get(self, iid):
        """Return a single Dance by id"""
        self.cursor.execute('select * from dance where id = %d' % int(iid))
        return sc.Dance(*self.cursor.fetchone())

    def new(self):
        dance = sc.Dance(0, '')
        return self.insert(dance)

    def insert(self, dance):
        """Create a new Dance"""
        self.cursor.execute(f"insert into dance (name) values\
                            (\"{dance.name}\")")
        dance.iid = self.cursor.lastrowid
        return dance

    def update(self, dance):
        """Save a Dance"""
        self.cursor.execute('update dance set name = \"%s\" where id = %d' %
                            (dance.name, dance.iid))
        self.conn.commit()
        return dance


class TableScores:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get(self, iid):
        """Get a single Score item"""
        self.cursor.execute('select * from score where id = %d' % int(iid))
        result = self.cursor.fetchone()
        return sc.Score(*result)

    def get_by_event_dancer(self, event_id, dancer_id):
        """Return a Dancer's Score in an Event"""
        self.cursor.execute('select * from score where event = %d and dancer\
                             = %d' % (int(event_id), int(dancer_id)))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.Score(*result)
        else:
            return None

    def get_by_event(self, event_id):
        """Return a list of all Scores from an Event"""
        self.cursor.execute('select * from score where event = %d' % event_id)
        results = self.cursor.fetchall()
        scores = []
        for s in results:
            scores.append(sc.Score(*s))
        return scores

    def exists_for_event(self, event_id):
        """Verify if there are any Scores for an Event"""
        scores = self.get_by_event(event_id)
        if scores is None or scores == []:
            return False
        else:
            return True

    def get_by_event_judge(self, event_id, judge_id):
        """Return a list of all Scores from an Event and judge by id"""
        self.cursor.execute('select * from score where event = %d and\
                            judge = %d' % (event_id, judge_id))
        results = self.cursor.fetchall()
        scores = []
        for s in results:
            scores.append(sc.Score(*s))
        return scores

    def exists_for_event_judge(self, event_id, judge_id):
        """Verify if there are any Scores for an Event and judge by Id"""
        scores = self.get_by_event_judge(event_id, judge_id)
        if scores is None or scores == []:
            return False
        else:
            return True

    def new(self):
        score = sc.Score(0, None, None, None, None, 0.0)
        return self.insert(score)

    def insert(self, score):
        """Create a new Score item"""
        self.cursor.execute(f"insert into score (dancer, event, judge,\
                            competition, score) values ({score.dancer},\
                            {score.event}, {score.judge}, {score.competition},\
                            {score.score})")
        score.iid = self.cursor.lastrowid
        return score

    def update(self, score):
        """Save a Score"""
        self.cursor.execute('update score set dancer = %d, event = %d, judge\
                             = %d, competition = %d, score = %f where id = %d'
                            % (score.dancer, score.event, score.judge,
                               score.competition, score.score, score.iid))
        self.conn.commit()
        return score

    def remove_by_event(self, event_id):
        """Delete all Scores in an Event"""
        self.cursor.execute('delete from score where event = %d' % event_id)
        self.conn.commit()

    def remove_by_event_judge(self, event_id, judge_id):
        """Remove every Score that has been entered for a Judge in an Event"""
        self.cursor.execute('delete from score where event = %d and judge =\
                             %d' % (event_id, judge_id))
        self.conn.commit()


class TableEvents:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_by_competition(self, c_id):
        self.cursor.execute(f"select * from event where competition = {c_id}")
        results = self.cursor.fetchall()
        events = []
        for event in results:
            event_obj = sc.Event(*event)
            if self.db.settings.verbose:
                print(event_obj)
            events.append(event_obj)
        return events

    def get_by_group(self, group_id):
        self.cursor.execute(f"select * from event where dancer_group = {group_id}")
        results = self.cursor.fetchall()
        events = []
        for event in results:
            event_obj = sc.Event(*event)
            if self.db.settings.verbose:
                print(event_obj)
            events.append(event_obj)
        return events

    def get(self, iid):
        self.cursor.execute('select * from event where id = %d' % int(iid))
        return sc.Event(*self.cursor.fetchone())

    def new(self, dancer_group_id=0, comp_id=0):
        event = sc.Event(0, '', dancer_group_id, 0, comp_id, 1, 6, 1)
        return self.insert(event)

    def insert(self, event):
        self.cursor.execute(f"insert into event (name, dancer_group, dance,\
                            competition, counts_for_overall, num_places,\
                            earns_stamp) values (\'{event.name}\',\
                            {event.dancer_group}, {event.dance},\
                            {event.competition}, {event.counts_for_overall},\
                            {event.num_places}, {event.earns_stamp})")
        event.iid = self.cursor.lastrowid
        return event

    def update(self, event):
        if self.db.settings.verbose:
            print(f"DB TableEvents Update: {event.name}")
        self.cursor.execute('update event set name = \"%s\", dancer_group =\
                             %d, dance = %d, competition = %d,\
                             counts_for_overall = %d, num_places = %d,\
                             earns_stamp = %d where id = %d' %
                            (event.name, event.dancer_group, event.dance,
                             event.competition, event.counts_for_overall,
                             event.num_places, event.earns_stamp, event.iid))
        self.conn.commit()
        return event

    def remove(self, iid):
        self.cursor.execute('delete from event where id = %d' % iid)
        self.db.tables.scores.remove_by_event(iid)
        self.conn.commit()

    def remove_by_competition(self, c_id):
        events = self.get_by_competition(c_id)
        for event in events:
            self.remove(event.iid)


class TableCategories:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_all(self):
        """Return a list of all DancerCategorys"""
        self.cursor.execute('select * from dancer_category')
        result = self.cursor.fetchall()
        categories = []
        if result is not None:
            for c in result:
                categories.append(sc.DancerCategory(*c))
        return categories

    def get(self, iid):
        self.cursor.execute('select * from dancer_category where id = %d'
                            % int(iid))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerCategory(*result)
        else:
            return None

    def get_by_name(self, cname):
        self.cursor.execute('select * from dancer_category where name like\
                            \"%%%s\"' % cname)
        result = self.cursor.fetchone()
        if result is not None:
            return sc.DancerCategory(*result)
        else:
            return None

    def new(self):
        category = sc.DancerCategory(0, '', '', 0)
        return self.insert(category)

    def insert(self, category):
        """Add a new DancerCategory object into the DB"""
        self.cursor.execute(f"insert into dancer_category\
                            (name, abbrev, protected)\
                            values ('{category.name}', '{category.abbrev}',\
                            {category.protected})")
        category.iid = self.cursor.lastrowid
        return category

    def update(self, category):
        self.cursor.execute('update dancer_category set name = \"%s\",\
                            abbrev = \"%s\", protected = %d where id =%d' %
                            (category.name, category.abbrev,
                             category.protected, category.iid))
        self.conn.commit()
        return category

    def remove(self, iid):
        self.cursor.execute('delete from dancer_category where id = %d' % iid)
        self.conn.commit()


class TablePlaceValues:
    def __init__(self, db):
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get(self, place):
        self.cursor.execute('select place, points from place_value where\
                            place = %d' % int(place))
        result = self.cursor.fetchone()
        if result is not None:
            return sc.PlaceValue(*result)
        else:
            return None

    def get_all(self):
        self.cursor.execute('select place, points from place_value')
        results = self.cursor.fetchall()
        values = []
        for pv in results:
            values.append(sc.PlaceValue(*pv))
        return values

    def new(self):
        place_value = sc.PlaceValue(0, 0)
        return self.insert(place_value)

    def insert(self, place_value):
        self.cursor.execute('insert into place_value (place, points) values\
                            (%d,%d)' % (place_value.place, place_value.points))
        return place_value

    def insert_table(self):
        self.cursor.execute('create table if not exists place_value (place\
                            integer primary key not null, points integer);')
