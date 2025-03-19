const jobRunModal = $("#job-run-modal");
const jobRunModalForm = $("#form-create-edit-job-run");
const jobRunModalBodyDiv = $("#div-job-run-modal-body");
const inputPriority = $("#input-priority");
const inputVersion = $("#input-version");
const inputJobId = $("#input-job-id");
const divErrorMessage = $("#div-error-message");
const textErrorMessage = $("#text-error-message");


const jobIdInput = "job-id";


function toggleSpinnerInJobRunModal(showSpinner) {
    let spinner = jobRunModalBodyDiv.find(".spinner-border");
    if (showSpinner && spinner.length === 0) {
        spinner = $("<div></div>")
            .attr("class", "spinner-border text-secondary")
            .attr("role", "status");
        spinner.append($("<span></span>")
            .attr("class", "visually-hidden")
            .text("Loading..."));

        jobRunModalBodyDiv.prepend(spinner);
    }
    else if (!showSpinner && spinner.length > 0) {
        spinner.remove();
    }
}

function loadPriorityOptions(priorities) {
    $.each(priorities, (value, translation) => {
        inputPriority.append(
            $("<option></option>")
                .attr("value", value)
                .text(translation)
        );
    });
}

function hideModal(event) {
    jobRunModalForm.hide();
    inputPriority.val("");
    inputPriority.empty();
    inputVersion.val("");
    inputJobId.val("");
    divErrorMessage.hide();
    textErrorMessage.text("");
}

function loadJobRunModal(event) {
    let jobRunId = $(event.relatedTarget).data("job-run-id");
    let jobId = $(`#${jobIdInput}`).val();
    if (jobId === undefined) {
        jobId = $(event.relatedTarget).data("job-id");
    }
    inputPriority.val(jobId);

    if (jobRunId === undefined) {
        toggleSpinnerInJobRunModal(true);
        let url = `${baseUrl}/job-run/create-model?jobId=${jobId}`;
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data) {
                loadPriorityOptions(data[prioritiesFieldName]);
                inputJobId.val(jobId);
                toggleSpinnerInJobRunModal(false);
                jobRunModalForm.attr("action", data[formActionUrlFieldName]);
                jobRunModalForm.show();
            },
            "error": function (xhr) {
                let modalBody = jobRunModal.find(".modal-body");
                modalBody.empty();
                showAlert(xhr.responseJSON[messageFieldName], "danger", modalBody);
            }
        });
    }
    else {
        toggleSpinnerInJobRunModal(true);
        let url = `${baseUrl}/job-run/${jobRunId}`;
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data) {
                loadPriorityOptions(data[prioritiesFieldName]);
                inputPriority.val(data[priorityFieldName]);
                inputJobId.val(jobId);
                inputVersion.val(data[versionFieldName]);

                if (data[errorMessageFieldName] !== null) {
                    divErrorMessage.show();
                    textErrorMessage.text(data[errorMessageFieldName]);
                }

                jobRunModalForm.attr("action", data[formActionUrlFieldName]);
                jobRunModalForm.show();
                toggleSpinnerInJobRunModal(false);
            },
            "error": function (xhr) {
                let modalBody = jobRunModal.find(".modal-body");
                modalBody.empty();
                showAlert(xhr.responseJSON[messageFieldName], "danger", modalBody);
            }
        });
    }
}

function sendJobRunForm(event) {
    event.preventDefault();
    let form = $(event.target);
    let url = form.attr("action");
    let data = form.serialize();
    data += `&csrf_token=${$(csrfTokenNodeId).val()}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": data,
        "success": function (data) {
            jobRunModal.modal("hide");
            showAlert(data[messageFieldName], "success", msgContainer);
        },
        "error": function (xhr) {
            showAlert(xhr.responseJSON[messageFieldName], "danger", jobRunModalBodyDiv);
        }
    });
}


$(document).ready(function() {
    jobRunModal.on("show.bs.modal", loadJobRunModal);
    jobRunModal.on("hidden.bs.modal", hideModal);
    jobRunModalForm.on("submit", sendJobRunForm);
});