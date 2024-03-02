const logoutUrl = "/auth/logout";
const csrfTokenNodeId = "#csrf-token";

function logoutUser() {
    $.ajax({
        url: logoutUrl,
        type: "POST",
        dataType: "json",
        data: {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        success: function() {
            window.location.href = "/";
        },
        error: function(error) {
            console.log(error);
        }
    });
}