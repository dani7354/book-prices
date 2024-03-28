const timePeriodSelect = $("#timeperiod-select");
const failedPriceUpdatesContainer = $("#failed-price-updates-container");

const baseUrl = "/status";


function tryGetTranslation(translations, translationKey) {
    if (translationKey in translations) {
        return translations[translationKey];
    }
    return translationKey;
}

function initializeFailedPriceUpdateTable(title, columns, rows, translations) {
    failedPriceUpdatesContainer.empty();
    failedPriceUpdatesContainer.append($("<h3></h3>")
        .attr("id", "failed-price-updates-heading")
        .text("Fejlede prisopdateringer"));

    let table = $("<table></table>")
        .attr("class", "table table-striped table-bordered")
        .attr("aria-describedby", "failed-price-updates-heading");
    failedPriceUpdatesContainer.append(table);

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
                let translations = data["translations"]
                initializeFailedPriceUpdateTable(title, columns, rows, translations);
            },
            "error" : function (error) {
                console.log(error);
            }
    });
}

$(document).ready(() => {
    getFailedPriceUpdates();
    timePeriodSelect.on("change", () => { getFailedPriceUpdates(); });
});
