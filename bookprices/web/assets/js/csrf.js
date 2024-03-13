const csrfTokenNodeId = "#csrf-token";
const forms = "form[method='post']";

$(document).ready(function() {
    $(forms).submit(function(event) {
        let input = $("<input>").attr("type", "hidden").attr("name", "csrf_token").val($(csrfTokenNodeId).val());
        $(this).append(input);
        return true;
    });
});
