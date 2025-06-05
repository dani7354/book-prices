from flask import render_template, Response, jsonify, request, Blueprint, redirect, url_for, abort
from flask_login import login_required

from bookprices.shared.api.job import JobApiClient
from bookprices.shared.db.database import Database
from bookprices.web.service.auth_service import require_admin, require_job_manager
from bookprices.web.service.csrf import get_csrf_token
from bookprices.shared.service.job_service import (
    JobService,
    AlreadyExistError,
    DeletionFailedError,
    UpdateFailedError, FailedToGetJobRunsError, CreationFailedError)
from bookprices.web.shared.enum import HttpMethod, JobTemplate, HttpStatusCode, Endpoint
from bookprices.web.mapper.job import map_job_list, map_job_edit_view_model, map_job_run_list, \
    map_job_run_edit_view_model, map_job_run_create_view_model
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    JOB_API_BASE_URL,
    JOB_API_USERNAME,
    JOB_API_PASSWORD,
    JOB_API_CLIENT_ID)
from bookprices.web.viewmodels.job import CreateJobViewModel
from bookprices.web.viewmodels.job_run import JobRunPriority, JobRunCreateViewModel, JobRunEditViewModel

MESSAGE_FIELD_NAME = "message"
JOB_ID_URL_PARAMETER = "jobId"

db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
job_service = JobService(JobApiClient(JOB_API_BASE_URL, JOB_API_USERNAME, JOB_API_PASSWORD, JOB_API_CLIENT_ID, db.api_key_db))


job_blueprint = Blueprint("job", __name__)


@job_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@job_blueprint.route("/", methods=[HttpMethod.GET.value])
@login_required
@require_job_manager
def  index() -> str:
    return render_template(JobTemplate.INDEX.value)


@job_blueprint.route("/create", methods=[HttpMethod.POST.value, HttpMethod.GET.value])
@login_required
@require_job_manager
def create() -> str | Response:
    if request.method == HttpMethod.POST.value:
        name = request.form.get(CreateJobViewModel.name_field_name) or ""
        description = request.form.get(CreateJobViewModel.description_field_name) or ""
        active = bool(request.form.get(CreateJobViewModel.active_field_name)) or False

        view_model = CreateJobViewModel(
            name=name, description=description, version="", active=active, form_action_url=url_for("job.create"))
        if not view_model.is_valid():
            return render_template(JobTemplate.CREATE.value, view_model=view_model)

        try:
            job_service.create_job(
                name=view_model.name,
                description=view_model.description,
                is_active=view_model.active)
        except AlreadyExistError as ex:
            view_model.add_error(CreateJobViewModel.name_field_name, str(ex))
            return render_template(JobTemplate.CREATE.value, view_model=view_model)

        return redirect(url_for(Endpoint.JOB_INDEX.value))

    return render_template(JobTemplate.CREATE.value, view_model=CreateJobViewModel.empty(url_for("job.create")))


@job_blueprint.route("edit/<job_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_job_manager
def edit(job_id: str) -> str | Response:
    if not (job := job_service.get_job(job_id)):
        abort(HttpStatusCode.NOT_FOUND, "Jobbet blev ikke fundet")

    if request.method == HttpMethod.POST.value:
        name = request.form.get(CreateJobViewModel.name_field_name) or ""
        description = request.form.get(CreateJobViewModel.description_field_name) or ""
        version = request.form.get(CreateJobViewModel.version_field_name) or ""
        active = bool(request.form.get(CreateJobViewModel.active_field_name)) or False

        view_model = CreateJobViewModel(
            name,
            description,
            version,
            active,
            form_action_url=url_for(Endpoint.JOB_EDIT.value, job_id=job_id),
            id=job_id)
        if not view_model.is_valid():
            return render_template(JobTemplate.EDIT.value, view_model=view_model)

        try:
            job_service.update_job(
                job_id=job_id,
                name=view_model.name,
                description=view_model.description,
                version=view_model.version,
                is_active=view_model.active)
        except (AlreadyExistError, UpdateFailedError) as ex:
            view_model.add_error(CreateJobViewModel.name_field_name, str(ex))
            return render_template(JobTemplate.EDIT.value, view_model=view_model)

        return redirect(url_for(Endpoint.JOB_INDEX.value))

    return render_template(JobTemplate.EDIT.value, view_model=map_job_edit_view_model(job))


@job_blueprint.route("job-run/create", methods=[HttpMethod.POST.value])
@login_required
@require_job_manager
def create_job_run() -> tuple[Response, int]:
    job_id = request.form.get(JobRunCreateViewModel.job_id_field_name)
    priority = request.form.get(JobRunCreateViewModel.priority_field_name)
    if not priority or priority not in JobRunPriority.get_values():
        return jsonify({MESSAGE_FIELD_NAME: "Prioritet ikke gyldig!"}), HttpStatusCode.BAD_REQUEST

    try:
        if not job_id or not job_service.get_job(job_id):
            return jsonify({MESSAGE_FIELD_NAME: "Job blev ikke fundet"}), HttpStatusCode.BAD_REQUEST

        job_service.create_job_run(job_id, priority)
        return jsonify({MESSAGE_FIELD_NAME: "Jobkørsel oprettet!"}), HttpStatusCode.OK
    except CreationFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("job-run/update/<job_run_id>", methods=[HttpMethod.POST.value])
@login_required
@require_job_manager
def update_job_run(job_run_id: str) -> tuple[Response, int]:
    job_id = request.form.get(JobRunEditViewModel.job_id_field_name)
    priority = request.form.get(JobRunEditViewModel.priority_field_name)
    version = request.form.get(JobRunEditViewModel.version_field_name)

    if not priority or priority not in JobRunPriority.get_values():
        return jsonify({MESSAGE_FIELD_NAME: "Prioritet ikke gyldig!"}), HttpStatusCode.BAD_REQUEST

    try:
        if not job_id or not job_service.get_job_run(job_run_id):
            return jsonify({MESSAGE_FIELD_NAME: f"Jobkørsel med id {job_run_id} blev ikke fundet"}), HttpStatusCode.BAD_REQUEST

        job_service.update_job_run(job_id, job_run_id, priority, version)
        return jsonify({MESSAGE_FIELD_NAME: "Jobkørsel opdateret!"}), HttpStatusCode.OK
    except UpdateFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("job-list", methods=[HttpMethod.GET.value])
@login_required
@require_job_manager
def job_list() -> tuple[Response, int]:
    jobs = job_service.get_job_list()
    last_job_run_for_jobs = job_service.get_job_run_for_jobs([job["id"] for job in jobs])
    job_list_view_model = map_job_list(jobs, last_job_run_for_jobs)

    return jsonify(job_list_view_model), HttpStatusCode.OK


@job_blueprint.route("job-run-list", methods=[HttpMethod.GET.value])
@login_required
@require_job_manager
def job_run_list() -> tuple[Response, int]:
    try:
        job_id = request.args.get(JOB_ID_URL_PARAMETER)
        job_runs = job_service.get_job_runs(job_id)
        job_runs_view_model = map_job_run_list(job_runs)

        return jsonify(job_runs_view_model), HttpStatusCode.OK
    except FailedToGetJobRunsError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("job-run/<job_run_id>", methods=[HttpMethod.GET.value])
@login_required
@require_job_manager
def job_run(job_run_id: str) -> tuple[Response, int]:
    if not (job_run_json := job_service.get_job_run(job_run_id)):
        return (jsonify({MESSAGE_FIELD_NAME: f"Jobkørsel med id {job_run_id} blev ikke fundet"}),
                HttpStatusCode.NOT_FOUND)

    job_run_view_model = map_job_run_edit_view_model(job_run_json)
    return jsonify(job_run_view_model), HttpStatusCode.OK


@job_blueprint.route("/delete/<job_id>", methods=[HttpMethod.POST.value])
@login_required
@require_job_manager
def delete(job_id: str) -> tuple[Response, int]:
    try:
        if not job_service.get_job(job_id):
            return jsonify({MESSAGE_FIELD_NAME: "Job blev ikke fundet"}), HttpStatusCode.BAD_REQUEST

        job_service.delete_job(job_id)
        return jsonify({MESSAGE_FIELD_NAME: "Job slettet!"}), HttpStatusCode.OK
    except DeletionFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST


@job_blueprint.route("/job-run/delete/<job_run_id>", methods=[HttpMethod.POST.value])
@login_required
@require_job_manager
def delete_job_run(job_run_id: str) -> tuple[Response, int]:
    try:
        if not job_service.get_job_run(job_run_id):
            return (jsonify({MESSAGE_FIELD_NAME: f"Jobkørsel med id {job_run_id} blev ikke fundet"}),
                    HttpStatusCode.BAD_REQUEST)

        job_service.delete_job_run(job_run_id)
        return jsonify({MESSAGE_FIELD_NAME: "Jobkørsel slettet!"}), HttpStatusCode.OK
    except DeletionFailedError as ex:
        return jsonify({MESSAGE_FIELD_NAME: str(ex)}), HttpStatusCode.BAD_REQUEST
