const msgContainer = $("#msg-container");
const jobContainer = $("#job-container");

const jobsUpdaterIntervalMs = 2500;

let jobsPollingId = null;
let isLoadingJobs = false;


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

    let createButtonRow = $("<div></div>").addClass("d-flex justify-content-start mb-2");
    let createButton = $("<a></a>")
        .text("Opret")
        .attr("id", "btn-create-job")
        .attr("href", `${baseUrl}/create`)
        .attr("class", "btn btn-primary");

    createButtonRow.append(createButton);

    let updateButton = $("<a></a>")
        .text("Opdater")
        .attr("id", "btn-update-jobs")
        .attr("class", "btn btn-secondary me-1")
        .click(getJobs);

    createButtonRow.prepend(updateButton);

    jobContainer.prepend(createButtonRow);
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

async function getJobs() {
    if (isLoadingJobs) return;
    isLoadingJobs = true;
    const url = `${baseUrl}/job-list`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        jobContainer.empty();

        if (data.jobs.length === 0) {
            jobContainer.text("Ingen jobs.");
            return;
        }

        initializeJobTable(data.columns, data.jobs, data.translations);
    } catch (error) {
        showAlert("Kunne ikke hente jobs.", "danger", msgContainer);
        console.error(error);
    } finally {
        toggleSpinnerInJobContainer(false);
        isLoadingJobs = false;
    }
}

function startJobsAutoRefresh(intervalMs) {
    if (jobsPollingId) return;
    jobsPollingId = setInterval(getJobs, intervalMs);
}

function stopJobsAutoRefresh() {
    if (!jobsPollingId) return;
    clearInterval(jobsPollingId);
    jobsPollingId = null;
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("Loading jobs...");
    toggleSpinnerInJobContainer(true);
    getJobs();
    toggleSpinnerInJobContainer(false);

    startJobsAutoRefresh(jobsUpdaterIntervalMs);
});

window.addEventListener("beforeunload", stopJobsAutoRefresh);
