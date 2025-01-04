const msgContainer = $("#msg-container");
const jobContainer = $("#job-container");


function handleClickDeleteJob(e) {
    e.preventDefault();
     if (confirm("Er du sikker på at du vil slette jobbet?")) {
         console.log("Deleting job...");
         let jobId = $(e.target).closest("tr").data("id");
         deleteJob(jobId);
     }
}

function initializeJobTable(columns, rows, translations) {
    let headingId = "job-list-heading";
    jobContainer.append($("<h3></h3>").text("Job list").attr("id", headingId));

    let table = $("<table></table>")
        .attr("class", "table")
        .attr("aria-describedby", headingId);
    jobContainer.append(table);

    let tableHeader = $("<thead></thead>");
    let tableBody = $("<tbody></tbody>");
    let tableHeaderRow = $("<tr></tr>");
    tableHeader.append(tableHeaderRow);
    table.append(tableHeader);

    $.each(columns, (index, columnKey) => {
        tableHeaderRow.append($("<th></th>")
            .attr("scope", "col")
            .text(translations[columnKey]));
    });

    tableHeaderRow.append($("<th></th>")
        .attr("scope", "col")
        .text("Sidste kørsel"));

    tableHeaderRow.append($("<th></th>")
        .attr("scope", "col")); // For buttons

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
            .attr("class", "btn btn-secondary mb-1")
            .text("Vis");
        actionCell.append(viewButton);
        actionCell.append(" ");

        let deleteButton = $("<a></a>")
            .attr("id", "btn-delete-job")
            .attr("class", "btn btn-secondary mb-1")
            .text("Slet")
            .click(handleClickDeleteJob);

        actionCell.append(deleteButton);
        tableRow.append(actionCell);
        tableBody.append(tableRow);
    });

    table.append(tableBody);

    jobContainer.append(
        $("<a></a>")
            .text("Opret")
            .attr("id", "btn-create-job")
            .attr("href", `${baseUrl}/create`)
            .attr("class", "btn btn-primary"));
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
            showAlert(data[messageFieldName], "success", msgContainer);
            getJobs();
        },
        "error": function (error) {
            showAlert(error[messageFieldName], "danger", msgContainer);
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
            if (data["jobs"].length === 0) {
                jobContainer.text("Ingen jobs.");
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
