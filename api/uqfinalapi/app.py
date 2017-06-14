"""
UQFinal API Webapp
"""
from flask import Flask, make_response

from helpers import APIFailureException, APINotFoundException, APIException, api_response, NoResultFound
import models
import scraper


webapp = Flask(__name__)


# CORS
@webapp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@webapp.route('/')
def home():
    return make_response("No resource specified. See the API Docs", 404)


@webapp.route('/favicon.ico')
def favicon():
    # When running on lambda, invalid requests for a favicon polute the logs with exceptions
    return make_response("Not Found", 404)


@webapp.route('/semesters', methods=['GET'])
@api_response
def get_semesters():
    return {
        'semesters': [
            semester.serialise()
            for semester in models.SEMESTERS
        ]
    }


@webapp.route('/course/<int:semester_uq_id>/<string:course_code>', methods=['GET'])
@api_response
def get_offering(semester_uq_id, course_code):
    try:
        offering = models.Offering.fetch(
            semester_id=semester_uq_id,
            course_code=course_code,
        )

        return offering.serialise()
    except NoResultFound:
        # Didn't find anything existing, try scraping it
        offering = models.Offering(
            semester_id=semester_uq_id,
            course_code=course_code,
        )

        try:
            # Accessing assessment items is a good way to test if it loaded correctly
            _ = offering.assessment_items
            offering.save()
            return offering.serialise()
        except (scraper.ScraperException, APIException):
            # Scraping failed, probably just a bad request
            raise APINotFoundException("No offering for that course code and semester")


@webapp.route('/course/<int:semester_uq_id>/<string:course_code>/invalidate', methods=['GET'])
@api_response
def invalidate_offering(semester_uq_id, course_code):
    try:
        offering = _attempt_scrape(semester_uq_id, course_code)
        return offering.serialise()
    except scraper.ScraperInvalidCourseProfileException:
        raise APIFailureException("Course profile is invalid")
    except scraper.ScraperNoCourseProfileException:
        raise APIFailureException("There is no course profile for that course code and semester. Course might not be listed as being offered")
    except scraper.ScraperUnavailableCourseProfileException:
        raise APIFailureException("Course profile is listed as unavailable. Try again after the course profile becomes available")
