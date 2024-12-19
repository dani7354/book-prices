const msgContainer = $("#msg-container");
const jobRunContainer = $("#job-run-container");
const jobIdInput = "job-id";

const baseUrl = "/job";
const messageFieldName = "message";


function deleteJobRun(jobRunId) {
    let url = `${baseUrl}/job-run/${jobRunId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "success": function (data, status, xhr) {
            msgContainer.text(data[messageFieldName]);
            getJobRuns();
        },
        "error": function (xhr, status, error) {
            msgContainer.text(xhr["message"]);
        }
    });
}

function initializeJobRunTable(columns, rows, translations) {
    console.log("Create table...");
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

    $.each(rows, (index, row) => {
        let tableRow = $("<tr></tr>").attr("data-id", row["id"]);
        $.each(columns, (index, columnName) => {
            tableRow.append($("<td></td>").text(row[columnName]));
        });

        let statusCell = $("<td></td>")
            .attr("class", `text-${row["status_color"]}`)
            .text(row["status"]);
        tableRow.append(statusCell);

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

$(document).ready(function () {
    let jobIdNode = $(`#${jobIdInput}`);
    if (jobIdNode.length > 0) {
        getJobRuns(jobIdNode.val());
    }
    else {
        getJobRuns();
    }
});