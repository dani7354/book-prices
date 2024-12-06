from flask import blueprints, render_template, Response, jsonify, request, Blueprint
from flask_login import login_required

from bookprices.shared.api.job import JobApiClient
from bookprices.shared.db.database import Database
from bookprices.web.service.job_service import JobService
from bookprices.web.shared.enum import HttpMethod, JobTemplate, HttpStatusCode
from bookprices.web.mapper.job import map_job_list
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    JOB_API_BASE_URL,
    JOB_API_USERNAME,
    JOB_API_PASSWORD)

db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
job_service = JobService(JobApiClient(JOB_API_BASE_URL, JOB_API_USERNAME, JOB_API_PASSWORD, db.api_key_db))


job_blueprint = Blueprint("job", __name__)


@job_blueprint.route("/", methods=[HttpMethod.GET.value])
@login_required
def  index() -> str:
    return render_template(JobTemplate.INDEX.value)

@job_blueprint.route("/job-list", methods=[HttpMethod.GET.value])
@login_required
def job_list() -> tuple[Response, int]:
    jobs = job_service.get_job_list()
    job_list_view_model = map_job_list(jobs)
    return jsonify(job_list_view_model), HttpStatusCode.OK
