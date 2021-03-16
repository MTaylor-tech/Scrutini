"""Scrutini Class Definitions.

These are intermediate classes that assist with moving data around the
application. The models are the same as in the database, but property
names may differ. Expected to move more utility to these.
"""
import json
from sWidgets import today


class Settings:
    """Settings

    Connect to the settings file and hold the settings for use by other
    classes.
    """

    def __init__(self, filename, verbose=False):
        """Set up settings variables and send to read()."""
        self.settings_file = filename
        self.name = None
        self.version = None
        self.schema = None
        self.schema_file = None
        self.db_file = None
        self.interface = None
        self.last_comp = None
        self.placings_order = None
        self.verbose = verbose
        self.x = {}
        self.read()

    def __str__(self):
        """Return a human-readable string explaining the settings."""
        if self.interface == 0:
            iface = 'CLI'
        elif self.interface == 1:
            iface = 'GUI'
        else:
            iface = '???'
        if self.verbose:
            vbose = 'Yes'
        else:
            vbose = 'No'
        return f"Settings \'{self.name}\' for version {self.version}:\n"\
               f"Database: {self.db_file}, "\
               f"Schema version \'{self.schema}\' from {self.schema_file}\n"\
               f"Interface: {self.interface} ({iface}), Verbose logging? "\
               f"{vbose}\nLast Competition: {self.last_comp}"

    def read(self):
        """Load settings from the specified settings file."""
        if self.verbose:
            print(f"Loading settings from {self.settings_file}")
        with open(self.settings_file) as file:
            setting = json.load(file)
        self.name = setting['name']
        self.version = setting['version']
        self.schema = setting['schema']
        self.schema_file = setting['schema_file']
        self.db_file = setting['db_file']
        self.interface = setting['interface']
        self.last_comp = setting['last_comp']
        self.placings_order = setting['placings_order']
        if setting.get('x') is not None:
            self.x = setting['x']

    def write(self):
        """Save settings to the specified settings file."""
        if self.verbose:
            print(f"Saving settings to {self.settings_file}")
        settings = {
            "name": self.name,
            "version": self.version,
            "schema": self.schema,
            "schema_file": self.schema_file,
            "db_file": self.db_file,
            "interface": self.interface,
            "last_comp": self.last_comp,
            "placings_order": self.placings_order,
            "x": self.x
        }
        if self.verbose:
            print(settings)
        with open(self.settings_file, 'w') as outfile:
            json.dump(settings, outfile)


class CompetitionType:
    """Competition Types.

    include Regular, Championship, and Premiership
    defines how scoring is done and number of judges.
    """

    def __init__(self, iid, name, abbrev, championship=False,
                 protected=False):
        """Create an instance with specified id, name, and abbreviation.

        Championship and protected status can also be specified.
        """
        self.iid = iid
        self.name = name
        self.abbrev = abbrev
        self.championship = championship
        self.protected = protected

    def __str__(self):
        """Return a human readable string of the details of the instance."""
        if self.championship:
            champ = "Yes"
        else:
            champ = "No"
        if self.protected:
            protect = "Yes"
        else:
            protect = "No"
        return f"{self.iid}: {self.name} [{self.abbrev}], Championship?\
                {champ}, Protected from Deletion? {protect}"


class Competition:
    """Competitions.

    cover whole event and all the dances at the event."""

    def __init__(self, iid, name, description='', event_date=None,
                 deadline=None, location='', competition_type=0):
        """Create a new instance."""
        self.iid = iid
        self.name = name
        self.description = description
        if event_date is not None:
            self.event_date = event_date
        else:
            self.event_date = today()
        if deadline is not None:
            self.deadline = deadline
        else:
            self.deadline = today()
        self.location = location
        self.competition_type = competition_type

    def __str__(self):
        """Return a human readable string of the details of the instance."""
        return f"{self.iid}: {self.name}, {self.location}, {self.event_date}"


class DanceCategory:
    """DanceCategory.

    Dance Categories are groups of dances to help organize what dances
    each competition includes.
    """

    def __init__(self, iid, name):
        """Create a new instance of Category."""
        self.iid = id
        self.name = name

    def __str__(self):
        """Return a human readable string of the id && name of the category."""
        return f"{self.iid}: {self.name}"


class Dance:
    def __init__(self, iid, name):
        """Dance

        Dances are names of dances and special trophies that can be chosen for
        an event.
        """
        self.iid = iid
        self.name = name

    def __str__(self):
        return f"{self.iid}: {self.name}"


class Event:
    def __init__(self, iid, name, dancer_group, dance, competition,
                 counts_for_overall, num_places, earns_stamp):
        """Event

        Events are dances and special trophies at a particular competition
        which can award medals
        """
        self.iid = iid
        self.name = name
        self.dancer_group = dancer_group
        self.dance = dance
        self.competition = competition
        self.counts_for_overall = counts_for_overall
        self.num_places = num_places
        self.earns_stamp = earns_stamp

    def __str__(self):
        if self.earns_stamp:
            stamp = "Yes"
        else:
            stamp = "No"
        if self.counts_for_overall:
            overall = "Yes"
        else:
            overall = "No"
        return f"{self.iid}: {self.name}, Counts for overall? {overall},"\
               f"Earns a Stamp? {stamp}"


class DancerCategory:
    def __init__(self, iid, name, abbrev, protected=True):
        """DancerCategory

        Dancer Categories are Primary, Beginner, Novice, Intermediate, Premier
        """
        self.iid = iid
        self.abbrev = abbrev
        self.name = name
        self.protected = protected

    def __str__(self):
        if self.protected:
            protect = "Yes"
        else:
            protect = "No"
        return f"{self.iid}: {self.name} [{self.abbrev}], Protected from\
                deletion? {protect}"


class PlaceValue:
    def __init__(self, place, points):
        """PlaceValue.

        PlaceValues are the point values of placing in a dance.
        """
        self.place = place
        self.points = points

    def __str__(self):
        return f"Place: {self.place}, worth {self.points} points"


class DancerGroup:
    def __init__(self, iid, name, abbrev, age_min, age_max,
                 dancer_category, competition):
        """DancerGroup.

        Dancer Groups are age groupings within the Dancer Categories
        Additional Dancer Groups can be made that are for special awards
        """
        self.iid = iid
        self.name = name
        self.age_min = age_min
        self.age_max = age_max
        self.dancer_category = dancer_category
        self.competition = competition
        self.abbrev = abbrev

    def __str__(self):
        return f"{self.iid}: {self.name} [{self.abbrev}], Ages:\
                {self.age_min}-{self.age_max}"


class Dancer:
    def __init__(self, iid, first_name, last_name, scot_dance_num, street, city,
                 state, zip, birthdate, age, registered_date, competitor_num,
                 phone_num, email, teacher, teacher_email, dancer_category,
                 competition):
        """Dancer.

        Dancers are individual competitors.
        """
        self.iid = iid
        self.first_name = first_name
        self.last_name = last_name
        self.scot_dance_num = scot_dance_num
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.birthdate = birthdate
        self.age = age
        self.registered_date = registered_date
        self.competitor_num = competitor_num
        self.phone_num = phone_num
        self.email = email
        self.teacher = teacher
        self.teacher_email = teacher_email
        self.dancer_category = dancer_category
        self.competition = competition

    def __str__(self):
        return f"{self.iid}: [#{self.competitor_num}] {self.first_name} "\
               f"{self.last_name}"


class Judge:
    def __init__(self, iid, first_name, last_name, competition):
        """Judge

        Just the name of the Judge and the connection to the competition
        """
        self.iid = iid
        self.first_name = first_name
        self.last_name = last_name
        self.competition = competition

    def __str__(self):
        return f"{self.iid}: {self.first_name} {self.last_name}"


class Score:
    def __init__(self, iid, dancer, event, judge, competition, score):
        """Score

        Scores are individual scores for individual competitors in
        individual events from individual judges
        """
        self.iid = iid
        self.dancer = dancer
        self.event = event
        self.judge = judge
        self.competition = competition
        self.score = score

    def __str__(self):
        return f"{self.iid}: Dancer ID: {self.dancer} in Event: {self.event}\
                Earned a score of {self.score} from Judge ID: {self.judge}"
