"""Scrutini Class Definitions"""
import os
import json


class Settings:
    def __init__(self, filename, verbose=False):
        """Settings includes the info in settings."""
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
        self.read()

    def __str__(self):
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
        return f"Settings \'{self.name}\' for version {self.version}:\n\
                Database: {self.db_file}, \
                Schema version \'{self.schema}\' from {self.schema_file}\n\
                Interface: {self.interface} ({iface}), Verbose logging?\
                {vbose}\nLast Competition: {self.last_comp}"

    def read(self):
        if self.verbose:
            print(f"Loading settings from {self.settings_file}")
        with open(self.settings_file) as f:
            s = json.load(f)
        self.name = s['name']
        self.version = s['version']
        self.schema = s['schema']
        self.schema_file = s['schema_file']
        self.db_file = s['db_file']
        self.interface = s['interface']
        self.last_comp = s['last_comp']
        self.placings_order = s['placings_order']

    def write(self):
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
            "placings_order": self.placings_order
        }
        if self.verbose:
            print(settings)
        with open(self.settings_file, 'w') as outfile:
            json.dump(settings, outfile)


class CompetitionType:
    def __init__(self, id, name, abbrev, isChampionship=False,
                 isProtected=True):
        """Competition Types

        include Regular, Championship, and Premiership
        defines how scoring is done and number of judges
        """
        self.id = id
        self.name = name
        self.abbrev = abbrev
        self.isChampionship = isChampionship
        self.isProtected = isProtected


class Competition:
    def __init__(self, id, name, description, eventDate, deadline, location,
                 competitionType, isChampionship=False):
        """Competitions cover whole event and all the dances at the event"""
        self.id = id
        self.name = name
        self.description = description
        self.eventDate = eventDate
        self.deadline = deadline
        self.location = location
        self.competitionType = competitionType
        self.isChampionship = isChampionship


# Dance Categories are groups of dances to help organize what dances each competition includes
class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Dances are names of dances and special trophies that can be chosen for an event
class Dance:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Events are dances and special trophies at a particular competition which can award medals
class Event:
    def __init__(self, id, name, dancerGroup, dance, competition, countsForOverall, numPlaces, earnsStamp):
        self.id = id
        self.name = name
        self.dancerGroup = dancerGroup
        self.dance = dance
        self.competition = competition
        self.countsForOverall = countsForOverall
        self.numPlaces = numPlaces
        self.earnsStamp = earnsStamp

# Dancer Categories are Primary, Beginner, Novice, Intermediate, Premier
class DancerCat:
    def __init__(self, id, name, abbrev, protected=True):
        self.id = id
        self.abbrev = abbrev
        self.name = name
        self.protected = protected


# PlaceValues are the point values of placing in a dance
class PlaceValue:
    def __init__(self, place, points):
        self.place = place
        self.points = points

# Dancer Groups are age groupings within the Dancer Categories
# Additional Dancer Groups can be made that are for special awards
class DancerGroup:
    def __init__(self, id, name, abbrev, ageMin, ageMax, dancerCat, competition):
        self.id = id
        self.name = name
        self.ageMin = ageMin
        self.ageMax = ageMax
        self.dancerCat = dancerCat
        self.competition = competition
        self.abbrev = abbrev

# Dancers are individual competitors


class Dancer:
    def __init__(self, id, firstName, lastName, scotDanceNum, street, city, state, zipCode, birthdate, age, registeredDate, number, phonenum, email, teacher, teacherEmail, dancerCat, dancerGroup, competition):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.scotDanceNum = scotDanceNum
        self.street = street
        self.city = city
        self.state = state
        self.zipCode = zipCode
        self.birthdate = birthdate
        self.age = age
        self.registeredDate = registeredDate
        self.number = number
        self.phonenum = phonenum
        self.email = email
        self.teacher = teacher
        self.teacherEmail = teacherEmail
        self.dancerCat = dancerCat
        self.dancerGroup = dancerGroup
        self.competition = competition

# Judges
class Judge:
    def __init__(self, id, firstName, lastName, competition):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.competition = competition


# Scores are individual scores for individual competitors in individual events from individual judges
class Score:
    def __init__(self, id, dancer, event, judge, competition, score):
        self.id = id
        self.dancer = dancer
        self.event = event
        self.judge = judge
        self.competition = competition
        self.score = score
