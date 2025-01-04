const msgContainer = $("#msg-container");
const jobRunContainer = $("#job-run-container");

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

$(document).ready(function () {
    refreshJobRuns();
});