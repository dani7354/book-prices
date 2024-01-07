const searchInput = $('#search-input');
const searchSuggestionList = $('#search-suggestions');
const authorSelect = $('#author-select');

function updateSearchSuggestions(data) {
    searchSuggestionList.empty();
    data.forEach(function (suggestion) {
        let option = $("<option></option>").text(suggestion).val(suggestion);
        searchSuggestionList.append(option);
    });
}

$(document).ready(function () {
    searchInput.on("input", function () {
        let searchPhrase = encodeURIComponent($(this).val());
        let selectedAuthor = encodeURIComponent(authorSelect.val());
        let url = `/api/book/search_suggestions?search=${searchPhrase}&author=${selectedAuthor}`;

        $.ajax(url, {
            "method" : "GET",
            "dataType": "json",
            "success" : function (data, status, xhr) {
                updateSearchSuggestions(data);
            },
            "error" : function (error) {
                console.log(error);
            }
        });
    });
});
