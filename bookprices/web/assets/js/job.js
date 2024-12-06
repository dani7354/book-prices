const jobContainer = $("#job-container");

const baseUrl = "/job";


function initializeJobTable(columns, rows, translations) {
    jobContainer.append($("<h3></h3>").text("Job list").attr("id", "job-list-heading"));

    let table = $("<table></table>")
        .attr("class", "table table-striped table-bordered")
        .attr("aria-describedby", "job-list-heading");
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
        table.append(tableRow);
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
