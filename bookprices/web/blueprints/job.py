from flask import render_template, Response, jsonify, request, Blueprint, redirect, url_for, abort
from flask_login import login_required

from bookprices.shared.api.job import JobApiClient
from bookprices.shared.db.database import Database
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.service.job_service import (
    JobService,
    JobAlreadyExistError,
    JobDeletionFailedError,
    JobUpdateFailedError, FailedToGetJobRunsError)
from bookprices.web.shared.enum import HttpMethod, JobTemplate, HttpStatusCode
from bookprices.web.mapper.job import map_job_list, map_job_edit_view_model, map_job_run_list
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

MESSAGE_FIELD_NAME = "message"
JOB_ID_URL_PARAMETER = "jobId"

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

        view_model = CreateJobViewModel(name, description, active, form_action_url=url_for("job.create"))
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

    return render_template(JobTemplate.CREATE.value, view_model=CreateJobViewModel.empty(url_for("job.create")))


@job_blueprint.route("edit/<job_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
def edit(job_id: str) -> str | Response:
    if not (job := job_service.get_job(job_id)):
        abort(HttpStatusCode.NOT_FOUND, "Jobbet blev ikke fundet")

    if request.method == HttpMethod.POST.value:
        name = request.form.get(CreateJobViewModel.name_field_name) or ""
        description = request.form.get(CreateJobViewModel.description_field_name) or ""
        active = bool(request.form.get(CreateJobViewModel.active_field_name)) or False

        view_model = CreateJobViewModel(
            name,
            description,
            active,
            form_action_url=url_for("job.edit", job_id=job_id),
            id=job_id)
        if not view_model.is_valid():
            return render_template(JobTemplate.EDIT.value, view_model=view_model)

        try:
            job_service.update_job(
                job_id=job_id,
                name=view_model.name,
                description=view_model.description,
                is_active=view_model.active)
        except (JobAlreadyExistError, JobUpdateFailedError) as ex:
            view_model.add_error(CreateJobViewModel.name_field_name, str(ex))
            return render_template(JobTemplate.EDIT.value, view_model=view_model)

        return redirect(url_for("job.index"))

    return render_template(JobTemplate.EDIT.value, view_model=map_job_edit_view_model(job))


@job_blueprint.route("/job-list", methods=[HttpMethod.GET.value])
@login_required
def job_list() -> tuple[Response, int]:
    jobs = job_service.get_job_list()
    last_job_run_for_jobs = job_service.get_job_run_for_jobs([job["id"] for job in jobs])
    job_list_view_model = map_job_list(jobs, last_job_run_for_jobs)

    return jsonify(job_list_view_model), HttpStatusCode.OK


@job_blueprint.route("job-run-list", methods=[HttpMethod.GET.value])
@login_required
def job_run_list() -> tuple[Response, int]:
    try:
        job_id = request.args.get(JOB_ID_URL_PARAMETER)
        job_runs = job_service.get_job_runs(job_id)

        job_runs_view_model = map_job_run_list(job_runs)

        return jsonify(job_runs_view_model), HttpStatusCode.OK
    except FailedToGetJobRunsError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("/delete/<job_id>", methods=[HttpMethod.POST.value])
@login_required
def delete(job_id: str) -> tuple[Response, int]:
    try:
        if not job_service.get_job(job_id):
            return jsonify({MESSAGE_FIELD_NAME: "Job blev ikke fundet"}), HttpStatusCode.BAD_REQUEST
        job_service.delete_job(job_id)

        return jsonify({MESSAGE_FIELD_NAME: "Job slettet!"}), HttpStatusCode.OK
    except JobDeletionFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("/job-run/delete/<job_run_id>", methods=[HttpMethod.POST.value])
@login_required
def delete_job_run(job_run_id: str) -> tuple[Response, int]:
    try:
        if not job_service.get_job_run(job_run_id):
            return (jsonify({MESSAGE_FIELD_NAME: f"Jobkørsel med id {job_run_id} blev ikke fundet"}),
                    HttpStatusCode.BAD_REQUEST)
        job_service.delete_job_run(job_run_id)

        return jsonify({MESSAGE_FIELD_NAME: "Jobkørsel slettet!"}), HttpStatusCode.OK
    except JobDeletionFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST
