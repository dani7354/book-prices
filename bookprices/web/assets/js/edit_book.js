const defaultImage = "default.png";

const imageSelectInput = $("#select-image");
const imgSelected = $("#img-selected");


function updateImagePreview(bookImageBaseUrl, selectedBookImage) {
    if (selectedBookImage) {
            imgSelected.attr("src", `${bookImageBaseUrl}${selectedBookImage}`);
    } else {
            imgSelected.attr("src", `${bookImageBaseUrl}${defaultImage}`);
    }
}

 $(document).ready(function(){
     let bookImageBaseUrl = imageSelectInput.data("image-base-url");
     if (!bookImageBaseUrl) {
         console.log("Image base URL missing from div! Cannot load selected image.");
         return;
     }

     let selectedImage = imageSelectInput.val();
     updateImagePreview(bookImageBaseUrl, selectedImage);

     imageSelectInput.on("change", function (e) {
        selectedImage = $(e.target).val();
        updateImagePreview(bookImageBaseUrl, selectedImage);
    });
 });
