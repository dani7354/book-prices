const msgContainer = $("#msg-container");
const jobRunContainer = $("#job-run-container");

const jobRunModal = $("#job-run-modal");
const jobRunModalForm = $("#form-create-edit-job-run");
const jobRunModalBodyDiv = $("#div-job-run-modal-body");
const jobIdInput = "job-id";

const jobRunsFieldName = "job_runs";
const jobRunIdFieldName = "id";


function handleClickDeleteJobRun(e) {
    e.preventDefault();
    if (confirm("Er du sikker på at du vil slette denne jobkørsel?")) {
        let jobId = $(e.target).closest("tr").data("id");
        deleteJobRun(jobId);
    }
}

function deleteJobRun(jobRunId) {
    let url = `${baseUrl}/job-run/delete/${jobRunId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function (data, status, xhr) {
            showAlert(data[messageFieldName], "success", msgContainer);
            refreshJobRuns();
        },
        "error": function (xhr, status, error) {
            showAlert(xhr[messageFieldName], "danger", msgContainer);
            refreshJobRuns();
        }
    });
}

function initializeJobRunTable(columns, rows, translations) {
    let table = $("<table></table>")
        .attr("class", "table")
    jobRunContainer.append(table);

    let tableHeader = $("<thead></thead>");
    let tableBody = $("<tbody></tbody>")
    let tableHeaderRow = $("<tr></tr>");
    tableHeader.append(tableHeaderRow);
    table.append(tableHeader);

    $.each(columns, (index, columnKey) => {
        tableHeaderRow.append($("<th></th>")
            .attr("scope", "col")
            .text(translations[columnKey]));
    });

    tableHeaderRow.append($("<th></th>").text("Status"));
    tableHeaderRow.append($("<th></th>")); // For buttons

    $.each(rows, (index, row) => {
        let tableRow = $("<tr></tr>").attr("data-id", row[jobRunIdFieldName]);
        $.each(columns, (index, columnName) => {
            tableRow.append($("<td></td>").text(row[columnName]));
        });

        let statusCell = $("<td></td>")
            .attr("class", `text-${row["status_color"]}`)
            .text(row["status"]);
        tableRow.append(statusCell);

        let actionCell = $("<td></td>");
        let showButton = $("<a></a>")
            .attr("id", "btn-delete-job-run")
            .attr("class", "btn btn-secondary mb-1")
            .attr("data-bs-toggle", "modal")
            .attr("data-bs-target", "#job-run-modal")
            .attr("data-job-run-id", row[jobRunIdFieldName])
            .text("Vis");
        actionCell.append(showButton);
        actionCell.append(" ");

        let deleteButton = $("<a></a>")
            .attr("id", "btn-delete-job-run")
            .attr("class", "btn btn-secondary mb-1")
            .click(handleClickDeleteJobRun)
            .text("Slet");
        actionCell.append(deleteButton);
        tableRow.append(actionCell);
        tableBody.append(tableRow);
    });

    table.append(tableBody);
}

function getJobRuns(jobId) {
    let url = `${baseUrl}/job-run-list`;
    if (jobId !== undefined) {
        url = `${url}?jobId=${jobId}`;
    }
    $.ajax(url, {
            "method" : "GET",
            "dataType": "json",
            "success" : function (data, status, xhr) {
                jobRunContainer.empty();
                if (data[jobRunsFieldName].length === 0) {
                    jobRunContainer.text("Ingen kørsler oprettet for dette job.");
                    return;
                }
                initializeJobRunTable(
                    data["columns"],
                    data[jobRunsFieldName],
                    data["translations"]
                );
            },
            "error" : function (xhr, status, error) {
                showAlert(xhr["message"], "danger", msgContainer);
            }
        });
}

function refreshJobRuns() {
    let jobIdNode = $(`#${jobIdInput}`);
    if (jobIdNode.length > 0) {
        getJobRuns(jobIdNode.val());
    }
    else {
        getJobRuns();
    }
}

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
    let priorityInput = $("#input-priority");
    $.each(priorities, (value, translation) => {
        priorityInput.append(
            $("<option></option>")
                .attr("value", value)
                .text(translation)
        );
    });
}

function loadJobRunModal(event) {
    let jobRunId = $(event.relatedTarget).data("job-run-id");
    let jobId = $(`#${jobIdInput}`).val();
    $("#input-job-id").val(jobId);

    if (jobRunId === undefined) {
        toggleSpinnerInJobRunModal(true);
        let url = `${baseUrl}/job-run/create-model?jobId=${jobId}`;
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data, status, xhr) {
                loadPriorityOptions(data["priorities"]);
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
                $("#input-status").val(data["status"]);
                loadPriorityOptions(data["priorities"]);
                $("#input-priority").val(data["priority"]);
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

function hideModal(event) {
    jobRunModalForm.hide();
    $("#input-priority").val("");
    $("#input-status").val("");
    $("#input-priority").empty();
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

$(document).ready(function () {
    refreshJobRuns();
    jobRunModal.on("show.bs.modal", loadJobRunModal);
    jobRunModal.on("hidden.bs.modal", hideModal);
    jobRunModalForm.on("submit", sendJobRunForm);
});