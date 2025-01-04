const jobRunModal = $("#job-run-modal");
const jobRunModalForm = $("#form-create-edit-job-run");
const jobRunModalBodyDiv = $("#div-job-run-modal-body");
const inputPriority = $("#input-priority");
const inputJobId = $("#input-job-id");
const jobIdInput = "job-id";


function toggleSpinnerInJobRunModal(showSpinner) {
    let spinner = jobRunModalBodyDiv.find(".spinner-border");
    if (showSpinner && spinner.length === 0) {
        spinner = $("<div></div>")
            .attr("class", "spinner-border text-primary")
            .attr("role", "status");
        spinner.append($("<span></span>")
            .attr("class", "visually-hidden")
            .text("Loading..."));

        jobRunModalBodyDiv.prepend(spinner);
    }
    else if (!showSpinner && spinner.length > 0) {
        spinner.remove();
    }
    else {
        console.log("Spinner already in modal. Something is wrong!");
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
}

function loadJobRunModal(event) {
    let jobRunId = $(event.relatedTarget).data("job-run-id");
    let jobId = $(`#${jobIdInput}`).val();
    inputPriority.val(jobId);

    if (jobRunId === undefined) {
        toggleSpinnerInJobRunModal(true);
        let url = `${baseUrl}/job-run/create-model?jobId=${jobId}`;
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data, status, xhr) {
                loadPriorityOptions(data["priorities"]);
                inputJobId.val(jobId);
                toggleSpinnerInJobRunModal(false);
                jobRunModalForm.attr("action", data["form_action_url"]);
                jobRunModalForm.show();
            },
            "error": function (xhr, status, error) {
                let modalBody = jobRunModal.find(".modal-body");
                modalBody.empty();
                modalBody.append($("<p></p>").text(xhr["message"]));
            }
        });
    }
    else {
        toggleSpinnerInJobRunModal(true);
        let url = `${baseUrl}/job-run/${jobRunId}`;
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data, status, xhr) {
                console.log(data);
                loadPriorityOptions(data["priorities"]);
                inputPriority.val(data["priority"]);
                jobRunModalForm.attr("action", data["form_action_url"]);
                jobRunModalForm.show();
                toggleSpinnerInJobRunModal(false);
            },
            "error": function (xhr, status, error) {
                let modalBody = jobRunModal.find(".modal-body");
                modalBody.empty();
                modalBody.append($("<p></p>").text(xhr["message"]));
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
        "success": function (data, status, xhr) {
            jobRunModal.modal("hide");
            showAlert(data[messageFieldName], "success", msgContainer);
            refreshJobRuns();
        },
        "error": function (xhr, status, error) {
            jobRunModalBodyDiv.prepend(
                $("<div></div>")
                    .attr("class", "text-danger")
                    .prepend($("<p></p>")
                        .text(xhr[messageFieldName])));
        }
    });
}


$(document).ready(function() {
    jobRunModal.on("show.bs.modal", loadJobRunModal);
    jobRunModal.on("hidden.bs.modal", hideModal);
    jobRunModalForm.on("submit", sendJobRunForm);
});