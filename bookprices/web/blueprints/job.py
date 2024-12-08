from click import Tuple
from flask import blueprints, render_template, Response, jsonify, request, Blueprint, redirect, url_for
from flask_login import login_required

from bookprices.shared.api.job import JobApiClient
from bookprices.shared.db.database import Database
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.service.job_service import JobService, JobAlreadyExistError, DeletionFailedError
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
from bookprices.web.viewmodels.job import CreateJobViewModel

db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
job_service = JobService(JobApiClient(JOB_API_BASE_URL, JOB_API_USERNAME, JOB_API_PASSWORD, db.api_key_db))


job_blueprint = Blueprint("job", __name__)


@job_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@job_blueprint.route("/", methods=[HttpMethod.GET.value])
@login_required
def  index() -> str:
    return render_template(JobTemplate.INDEX.value)


@job_blueprint.route("/create", methods=[HttpMethod.POST.value, HttpMethod.GET.value])
@login_required
def create() -> str | Response:
    if request.method == HttpMethod.POST.value:
        name = request.form.get(CreateJobViewModel.name_field_name) or ""
        description = request.form.get(CreateJobViewModel.description_field_name) or ""
        active = bool(request.form.get(CreateJobViewModel.active_field_name)) or False

        view_model = CreateJobViewModel(name, description, active)
        if not view_model.is_valid():
            return render_template(JobTemplate.CREATE.value, view_model=view_model)

        try:
            job_service.create_job(
                name=view_model.name,
                description=view_model.description,
                is_active=view_model.active)
        except JobAlreadyExistError as ex:
            view_model.add_error(CreateJobViewModel.name_field_name, str(ex))
            return render_template(JobTemplate.CREATE.value, view_model=view_model)

        return redirect(url_for("job.index"))

    return render_template(JobTemplate.CREATE.value, view_model=CreateJobViewModel.empty())


@job_blueprint.route("/job-list", methods=[HttpMethod.GET.value])
@login_required
def job_list() -> tuple[Response, int]:
    jobs = job_service.get_job_list()
    job_list_view_model = map_job_list(jobs)

    return jsonify(job_list_view_model), HttpStatusCode.OK


@job_blueprint.route("/delete/<job_id>", methods=[HttpMethod.POST.value])
@login_required
def delete(job_id: str) -> tuple[Response, int]:
    try:
        job_service.delete_job(job_id)
        return jsonify({"message": "Job deleted"}), HttpStatusCode.OK
    except DeletionFailedError as ex:
        return jsonify({"message": str(ex)}), HttpStatusCode.BAD_REQUEST