



// DROPZONE 
Dropzone.options.myAwesomeDropzone = {
    init: function() {
        this.on("sending", function(file, xhr, formData) {
            formData.append("csrfmiddlewaretoken", "{{ csrf_token }}");
        });
    }  
};

// Get the URL from the data attribute
const uploadUrl = document.getElementById('dropzone-config').getAttribute('data-upload-url');

Dropzone.autoDiscover=false;
const myDropzone= new Dropzone('#my-awesome-dropzone',{
    // url: `{% url "upload-view" %}`,
    url: uploadUrl,
    paramName: 'file', 
    maxFiles:5,
    maxFilesize:10,
    acceptedFiles:'.pdf,.jpg,.png', 
    autoProcessQueue: false,  // Prevent automatic upload
})

document.querySelector("#upload-button").addEventListener("click", function() {
    myDropzone.processQueue();  // Trigger the file upload manually
});

// alert upon successful uploading ///////////////
document.getElementById('dropzone').onsubmit = function(event) {
    event.preventDefault();  // Prevent form from submitting normally

    var formData = new FormData(this);

    fetch("{% url 'upload_view' %}", {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);  // Display success message in an alert
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
};
// alert upon successful uploading ///END END /////


