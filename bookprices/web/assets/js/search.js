const searchInput = $('#search-input');
const searchSuggestionList = $('#search-suggestions');
const authorSelect = $('#author-select');

function updateSearchSuggestions(data) {
    searchSuggestionList.empty();
    data.forEach(function (suggestion) {
        searchSuggestionList.append(`<option value="${suggestion}">${suggestion}</option>`);
    });
}

$(document).ready(function () {
    searchInput.on("input", function () {
        console.log("hello, world!");
        let searchPhrase = $(this).val();
        let selectedAuthor = authorSelect.val();
        let url = `/api/book/search_suggestions?search=${searchPhrase}&author=${selectedAuthor}`;

        $.ajax(url, {
            "method" : "GET",
            "dataType": "json",
            "success" : function (data, status, xhr) {
                console.log(data)
                updateSearchSuggestions(data);
            },
            "error" : function (error) {
                console.log(error);
            }
        });
    });
});
