const timePeriodSelect = $("#timeperiod-select");
const failedPriceUpdateTable = $("#failed-price-updates");
const failedPriceUpdateTableHeading = $("#failed-price-updates-heading");

const baseUrl = "/status";


function tryGetTranslation(translations, translationKey) {
    if (translationKey in translations) {
        return translations[translationKey];
    }
    return translationKey;
}

function initializeFailedPriceUpdateTable(title, columns, rows, translations) {
    failedPriceUpdateTableHeading.text(title);
    failedPriceUpdateTable.empty();
    let tableHeader = $("<thead></thead>");
    let tableHeaderRow = $("<tr></tr>");
    tableHeader.append(tableHeaderRow);
    failedPriceUpdateTable.append(tableHeader);

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
        failedPriceUpdateTable.append(tableRow);
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
