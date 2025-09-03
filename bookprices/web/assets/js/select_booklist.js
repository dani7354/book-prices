const selectBookListBaseUrl = "/user/set-booklist";
const btnSelectBookList = $(".btn-select-booklist");


function selectBookList(button, bookListId) {
    let url = `${selectBookListBaseUrl}/${bookListId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function () {
            window.location.reload();
        },
        "error": function (error) {
            console.log(error);
        }
    });
}


$(document).ready(function () {
    btnSelectBookList.on("click", function (e) {
        e.preventDefault();
        let booklistId = $(e.target).data("booklist-id");
        selectBookList(e.target, booklistId)
    });
});