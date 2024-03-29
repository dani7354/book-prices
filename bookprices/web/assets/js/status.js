const timePeriodSelect = $("#timeperiod-select");
const failedPriceUpdatesContainer = $("#failed-price-updates-container");
const bookImportCountsContainer = $("#book-import-counts-container");

const baseUrl = "/status";


function tryGetTranslation(translations, translationKey) {
    if (translationKey in translations) {
        return translations[translationKey];
    }
    return translationKey;
}

function initializeTable(tableContainer, title, columns, rows, translations, headingId) {
    tableContainer.empty();
    tableContainer.append($("<h3></h3>")
        .attr("id", headingId)
        .text(title));

    let table = $("<table></table>")
        .attr("class", "table table-striped table-bordered")
        .attr("aria-describedby", headingId);
    tableContainer.append(table);

    let tableHeader = $("<thead></thead>");
    let tableHeaderRow = $("<tr></tr>");
    tableHeader.append(tableHeaderRow);
    table.append(tableHeader);

    $.each(columns, (index, columnKey) => {
        let columnName = tryGetTranslation(translations, columnKey);
        tableHeaderRow.append($("<th></th>")
            .attr("scope", "col")
            .text(columnName));
    });

    $.each(rows, (index, row) => {
        let tableRow = $("<tr></tr>");
        $.each(columns, (index, columnName) => {
            tableRow.append($("<td></td>").text(row[columnName]));
        });
        table.append(tableRow);
    });
}

function getFailedPriceUpdates() {
    let selectedTimePeriodDays = encodeURIComponent(timePeriodSelect.val());
    let url = `${baseUrl}/failed-price-updates?days=${selectedTimePeriodDays}`;
    $.ajax(url, {
            "method" : "GET",
            "dataType": "json",
            "success" : function (data, status, xhr) {
                let title = data["table"]["title"];
                let columns = data["table"]["columns"];
                let rows = data["table"]["rows"];
                let translations = data["translations"];
                let headingId = "failed-price-updates-heading";
                initializeTable(
                    failedPriceUpdatesContainer,
                    title,
                    columns,
                    rows,
                    translations,
                    headingId);
            },
            "error" : function (error) {
                console.log(error);
            }
    });
}

function getBookImportCounts() {
    let selectedTimePeriodDays = encodeURIComponent(timePeriodSelect.val());
    let url = `${baseUrl}/book-import-counts?days=${selectedTimePeriodDays}`;
    $.ajax(url, {
            "method" : "GET",
            "dataType": "json",
            "success" : function (data, status, xhr) {
                let title = data["table"]["title"];
                let columns = data["table"]["columns"];
                let rows = data["table"]["rows"];
                let translations = data["translations"];
                let headingId = "book-import-counts-heading";
                initializeTable(bookImportCountsContainer, title, columns, rows, translations, headingId);
            },
            "error" : function (error) {
                console.log(error);
            }
    });
}

$(document).ready(() => {
    getFailedPriceUpdates();
    getBookImportCounts();

    timePeriodSelect.on("change", () => {
        getFailedPriceUpdates();
        getBookImportCounts();
    });
});
