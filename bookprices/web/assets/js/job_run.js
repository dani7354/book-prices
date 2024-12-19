const msgContainer = $("#msg-container");
const jobRunContainer = $("#job-run-container");
const jobIdInput = "job-id";

const baseUrl = "/job";
const messageFieldName = "message";


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
            msgContainer.text(data[messageFieldName]);
            refreshJobRuns();
        },
        "error": function (xhr, status, error) {
            msgContainer.text(xhr[messageFieldName]);
            refreshJobRuns();
        }
    });
}

function initializeJobRunTable(columns, rows, translations) {
    jobRunContainer.empty();
    let table = $("<table></table>")
        .attr("class", "table table-striped table-bordered")
    jobRunContainer.append(table);

    let tableHeader = $("<thead></thead>");
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
        let tableRow = $("<tr></tr>").attr("data-id", row["id"]);
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
            .attr("class", "btn btn-link btn-sm")
            .text("Vis");
        actionCell.append(showButton);

        let deleteButton = $("<a></a>")
            .attr("id", "btn-delete-job-run")
            .attr("class", "btn btn-link btn-sm")
            .click(handleClickDeleteJobRun)
            .text("Slet");
        actionCell.append(deleteButton);
        tableRow.append(actionCell);

        table.append(tableRow);
    });
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
                initializeJobRunTable(
                    data["columns"],
                    data["job_runs"],
                    data["translations"]
                );
            },
            "error" : function (xhr, status, error) {
                msgContainer.text(xhr["message"]);
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