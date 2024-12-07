const jobContainer = $("#job-container");

const baseUrl = "/job";


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

    $.each(rows, (index, row) => {
        let tableRow = $("<tr></tr>").attr("data-id", row["id"]);
        $.each(columns, (index, columnName) => {
            tableRow.append($("<td></td>").text(row[columnName]));
        });

        let actionCell = $("<td></td>");
        let viewButton = $("<button></button>")
            .attr("id", "btn-view-job")
            .attr("type", "button")
            .attr("class", "btn btn-link btn-sm")
            .text("Vis");
        actionCell.append(viewButton);

        let deleteButton = $("<a></a>")
            .attr("id", "btn-delete-job")
            .attr("class", "btn btn-link btn-sm")
            .text("Slet");
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
