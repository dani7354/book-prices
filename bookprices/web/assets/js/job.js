const msgContainer = $("#msg-container");
const jobContainer = $("#job-container");

const baseUrl = "/job";
const messageFieldName = "message";


function handleClickDeleteJob(e) {
    e.preventDefault();

    let jobId = $(e.target).closest("tr").data("id");
    deleteJob(jobId);
}

function initializeJobTable(columns, rows, translations) {
    let headingId = "job-list-heading";
    jobContainer.append($("<h3></h3>").text("Job list").attr("id", headingId));

    let table = $("<table></table>")
        .attr("class", "table table-striped table-bordered")
        .attr("aria-describedby", headingId);
    jobContainer.append(table);

    let tableHeader = $("<thead></thead>");
    let tableHeaderRow = $("<tr></tr>");
    tableHeader.append(tableHeaderRow);
    table.append(tableHeader);

    $.each(columns, (index, columnKey) => {
        tableHeaderRow.append($("<th></th>")
            .attr("scope", "col")
            .text(translations[columnKey]));
    });

    tableHeaderRow.append($("<th></th>").text("Sidste kørsel"));

    $.each(rows, (index, row) => {
        let tableRow = $("<tr></tr>").attr("data-id", row["id"]);
        $.each(columns, (index, columnName) => {
            tableRow.append($("<td></td>").text(row[columnName]));
        });

        let lastRunAtCell = $("<td></td>")
            .attr("class", `text-${row["last_run_at_color"]}`)
            .text(row["last_run_at"]);
        tableRow.append(lastRunAtCell);

        let actionCell = $("<td></td>");
        let viewButton = $("<a></a>")
            .attr("href", row["url"])
            .attr("id", "btn-view-job")
            .attr("type", "button")
            .attr("class", "btn btn-link btn-sm")
            .text("Vis");
        actionCell.append(viewButton);

        let deleteButton = $("<button></button>")
            .attr("id", "btn-delete-job")
            .attr("class", "btn btn-link btn-sm")
            .text("Slet")
            .click(function(event) {
                if (confirm("Er du sikker på at du vil slette jobbet?")) {
                    console.log("Deleting job...")
                    handleClickDeleteJob(event);
                }
            });

        actionCell.append(deleteButton);
        tableRow.append(actionCell);
        table.append(tableRow);
    });

    jobContainer.append(
        $("<a></a>")
            .text("Opret")
            .attr("id", "btn-create-job")
            .attr("href", `${baseUrl}/create`)
            .attr("class", "btn btn-primary"));
}

function showAlert(message, alertType) {
    let alert = $("<div></div>")
        .attr("class", `alert alert-${alertType} alert-dismissible fade show`)
        .attr("role", "alert")
        .text(message);
    alert.append(
        $("<button></button>")
            .attr("class", "btn-close")
            .attr("data-bs-dismiss", "alert")
            .attr("aria-label", "Close")
            .attr("type", "button"));
    msgContainer.prepend(alert);
    alert.alert();
}

function deleteJob(jobId) {
    let url = `${baseUrl}/delete/${jobId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function (data, status, xhr) {
            showAlert(data[messageFieldName], "success");
            getJobs();
        },
        "error": function (error) {
            showAlert(error[messageFieldName], "danger");
            getJobs();
            console.log(error);
        }
    });
}

function getJobs() {
    let url = `${baseUrl}/job-list`;
    $.ajax(url, {
        "method": "GET",
        "dataType": "json",
        "success": function (data, status, xhr) {
            jobContainer.empty();
            if (data.length === 0) {
                jobContainer.text("No jobs found.");
                return;
            }
            initializeJobTable(data["columns"], data["jobs"], data["translations"]);
        }
    });
}

$(document).ready(() => {
    console.log("Loading jobs...");
    getJobs();
});
