const msgContainer = $("#msg-container");
const jobContainer = $("#job-container");


function handleClickDeleteJob(e) {
    e.preventDefault();
     if (confirm("Er du sikker på at du vil slette jobbet?")) {
         let jobId = $(e.target).closest("tr").data("id");
         deleteJob(jobId);
     }
}

function toggleSpinnerInJobContainer(showSpinner) {
    let spinner = jobContainer.find(".spinner-border");
    if (showSpinner && spinner.length === 0) {
        spinner = $("<div></div>")
            .attr("class", "spinner-border text-secondary")
            .attr("role", "status");
        spinner.append($("<span></span>")
            .attr("class", "visually-hidden")
            .text("Loading..."));

        jobContainer.prepend(spinner);
    } else if (!showSpinner && spinner.length > 0) {
        spinner.remove();
    } else {
        console.log("Something is wrong!");
    }
}

function initializeJobTable(columns, rows, translations) {
    let table = $("<table></table>")
        .attr("class", "table");
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
        actionCell.append(" ");

        let runButtonClass = "btn btn-secondary mb-1";
        runButtonClass += row["is_active"] === false ? " disabled" : "";

        let runButton = $("<a></a>")
            .attr("id", "btn-run-job")
            .attr("class", runButtonClass)
            .attr("data-bs-toggle", "modal")
            .attr("data-bs-target", "#job-run-modal")
            .attr("data-job-id", row["id"])
            .text("Kør");

        actionCell.append(runButton);

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
        "success": function (data) {
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
    toggleSpinnerInJobContainer(true);
    let url = `${baseUrl}/job-list`;
    $.ajax(url, {
        "method": "GET",
        "dataType": "json",
        "success": function (data) {
            jobContainer.empty();
            if (data["jobs"].length === 0) {
                jobContainer.text("Ingen jobs.");
                toggleSpinnerInJobContainer(false);
                return;
            }
            initializeJobTable(data["columns"], data["jobs"], data["translations"]);
            toggleSpinnerInJobContainer(false);
        }
    });
}


$(document).ready(() => {
    console.log("Loading jobs...");
    getJobs();
});
