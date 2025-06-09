const baseUrl = "/user";
const redirectUrl = "/user";
const btnDeleteUser = $(".btn-delete-user");


$(document).ready(function () {
    btnDeleteUser.on("click", function (e) {
        e.preventDefault();
        if (confirm("Er du sikker på, at du vil slette brugeren?")) {
            let userId = $(e.target).data("user-id");
            deleteUser(userId);
        }
    });
});


function deleteUser(userId) {
    let url = `${baseUrl}/delete/${userId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function () {
            window.location.href  = redirectUrl;
        },
        "error": function (error) {
            console.log(error);
        }
    });
}