"""
Document Models

UQFinal is powered completely by AWS DynamoDB
"""
import urlparse
import time

import scraper
from helpers import NoResultFound
from caching import dynamodb_cached_property, DynamoDBCachedObject, dynamodb_cast_types_to_python

# Typing is for IDE only, doesn't matter at all
try:
    from typing import Optional, List
except ImportError:
    pass


class Semester(object):
    """
    A semester is a timeframe in which a course is offered
    A semester has an ID which is provided by UQ using some scheme they have
    """
    id = None  # type: int
    name = None  # type: str
    short_name = None  # type: str
    is_current = None  # type: bool

    def __init__(self, id, name, short_name, is_current=False):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.is_current = is_current

    def serialise(self):
        # type: () -> dict
        return {
            'uqId': self.id,
            'semester': self.name,
            'shortName': self.short_name,
            'isCurrent': self.is_current,
        }


SEMESTERS = [
    Semester(6560, "Semester 2, 2015", "Sem 2, 2015"),
    Semester(6620, "Semester 1, 2016", "Sem 1, 2016"),
    Semester(6660, "Semester 2, 2016", "Sem 2, 2016"),
    Semester(6720, "Semester 1, 2017", "Sem 1, 2017", True),
]


class Offering(DynamoDBCachedObject):
    """
    An Offering is a course being run in a Semester
    """
    @classmethod
    def get_table_name(self):
        return "uqfinal-offerings"

    # Table
    table = None

    # Key fields
    semester_id = None  # type: int
    course_code = None  # type: str

    @property
    def partition_key(self):
        return self.course_code

    @property
    def range_key(self):
        return self.course_code

    def __init__(self, table, semester_id, course_code):
        self.table = table
        self.semester_id = semester_id
        self.course_code = course_code
        super(Offering, self).__init__()

    @classmethod
    def fetch(cls, table, semester_id, course_code):
        query = table.get_item(
            Key={
                'course_code': course_code,
                'semester_id': semester_id,
            }
        )
        item = query.get('Item')

        if not item:
            raise NoResultFound()

        offering = cls(
            table=table,
            semester_id=item.pop('semester_id'),
            course_code=item.pop('course_code'),
        )

        for key, value in item.iteritems():
            if value is not None:
                setattr(offering, key, dynamodb_cast_types_to_python(value))

        return offering

    def delete(self):
        # type: () -> None
        self.table.delete_item(
            Key={
                'course_code': self.course_code,
                'semester_id': self.semester_id,
            }
        )

    def save(self):
        # type: () -> None
        """
        Save the state of this offering to DynamoDB
        """
        item = {
            attr_name: getattr(self, attr_name)
            for attr_name in dir(self)
            if type(getattr(self.__class__, attr_name)) == dynamodb_cached_property
        }

        item['course_code'] = self.course_code
        item['semester_id'] = self.semester_id

        self.table.put_item(
            Item=item,
        )

    # Semester lookup
    @property
    def semester(self):
        return (s for s in SEMESTERS if s.id == self.semester_id).next()

    # Data sources
    @dynamodb_cached_property
    def course_profile_id(self):
        # type: () -> int
        url = scraper.get_course_profile_url(self.semester.name, self.course_code)
        parsed_url = urlparse.urlparse(url)
        query_string = urlparse.parse_qs(parsed_url.query)
        return int(query_string['profileId'][0])

    @property
    def course_profile_assessment_url(self):
        # type: () -> str
        return "http://www.courses.uq.edu.au/student_section_loader.php?section=5&profileId={}".format(self.course_profile_id)

    @dynamodb_cached_property
    def scraped_timestamp(self):
        return int(time.time())

    # Data
    @dynamodb_cached_property
    def manually_modified(self):
        # type: () -> bool
        # If this is being called, there is no cached value, so we haven't modified anything
        return False

    @dynamodb_cached_property
    def is_linear(self):
        # type: () -> bool
        # This doesn't do anything yet
        return True

    @dynamodb_cached_property
    def calculable(self):
        # type: () -> bool
        # This doesn't do anything yet
        return True

    @dynamodb_cached_property
    def message(self):
        # type: () -> Optional[str]
        # This is only manually set if there is some special consideration for this course
        # Default value here
        return None

    @dynamodb_cached_property
    def cutoff_1(self):
        # type: () -> int
        # Default value
        return 0

    @dynamodb_cached_property
    def cutoff_2(self):
        # type: () -> int
        # Default value
        return 30

    @dynamodb_cached_property
    def cutoff_3(self):
        # type: () -> int
        # Default value
        return 45

    @dynamodb_cached_property
    def cutoff_4(self):
        # type: () -> int
        # Default value
        return 50

    @dynamodb_cached_property
    def cutoff_5(self):
        # type: () -> int
        # Default value
        return 65

    @dynamodb_cached_property
    def cutoff_6(self):
        # type: () -> int
        # Default value
        return 75

    @dynamodb_cached_property
    def cutoff_7(self):
        # type: () -> int
        # Default value
        return 85

    @dynamodb_cached_property
    def assessment_items(self):
        # type: () -> List[dict]
        # Load assessment items
        return scraper.get_assessment_items(self.course_profile_assessment_url)

    def serialise(self):
        return {
            'course': {
                'courseCode': self.course_code,
            },
            'courseProfileId': self.course_profile_id,
            'semester': self.semester.serialise(),
            'isLinear': self.is_linear,
            'manuallyModified': self.manually_modified,
            'calculable': self.calculable,
            'cutoff': {
                1: self.cutoff_1,
                2: self.cutoff_2,
                3: self.cutoff_3,
                4: self.cutoff_4,
                5: self.cutoff_5,
                6: self.cutoff_6,
                7: self.cutoff_7,
            },
            'assessment': [item for item in self.assessment_items],
            'lastUpdated': self.scraped_timestamp,
        }
