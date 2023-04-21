import json
import random
import script

from flask import Flask, request

app = Flask(__name__)

### Responses ###


def success_response(body, code=200):
    """
    Return a JSON body with a default 200 response
    """
    return json.dumps(body), code


def failure_response(msg, code=404):
    """
    Return a failure message with a default 404 response
    """
    return json.dumps({"error": msg}), code

### Routes ###


@app.route("/")
def default():
    """
    Default route that returns a welcome message
    """
    return "Welcome to Vin's volume-cboard-backend"


@app.route("/api/flyers/trending/")
def fetch_trending_flyers():
    """
    This route fetches two flyers to be featured in trending
    """
    upcoming_flyers = script.get_upcoming_flyers()
    if upcoming_flyers is None:
        return failure_response("Unable to fetch flyers for trending")
    trending_flyers = random.sample(upcoming_flyers, 2)
    return success_response(trending_flyers)


@app.route("/api/flyers/weekly/")
def fetch_weekly_flyers():
    """
    This route fetches all weekly flyers
    """
    weekly_flyers = script.get_weekly_flyers()
    if weekly_flyers is None:
        return failure_response("Unable to fetch weekly flyers")
    return success_response(weekly_flyers)


@app.route("/api/flyers/past/")
def fetch_past_flyers():
    """
    This route fetches all past flyers
    """
    past_flyers = script.get_past_flyers()
    if past_flyers is None:
        return failure_response("Unable to fetch past flyers")
    return success_response(past_flyers)


@app.route("/api/flyers/upcoming/")
def fetch_upcoming_flyers():
    """
    This route fetches all upcoming flyers
    """
    upcoming_flyers = script.get_upcoming_flyers()
    if upcoming_flyers is None:
        return failure_response("Unable to fetch upcoming flyers")
    return success_response(upcoming_flyers)


@app.route("/api/organizations/<string:slug>/")
def fetch_specific_org(slug):
    """
    This route fetches a specific organization
    """
    org = script.get_org_from_slug(slug)
    if org is None or org == []:
        return failure_response("Unable to find organization from slug")
    return success_response(org)


@app.route("/api/organizations/")
def fetch_all_organizations():
    """
    This route fetches all organizations
    """
    orgs = script.get_organizations()
    if orgs is None:
        return failure_response("Unable to fetch all organizations")
    return success_response(orgs)


@app.route("/api/flyers/")
def fetch_all_flyers():
    """
    This route fetches all flyers
    """
    flyers = script.get_flyers()
    if flyers is None:
        return failure_response("Unable to fetch all flyers")
    return success_response(flyers)

### Main Script ###
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
