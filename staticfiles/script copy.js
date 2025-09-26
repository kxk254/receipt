// document.addEventListener("DOMContentLoaded", function() {
//     const container = document.querySelector('.scroll-container');
//     let isDown = false;
//     let startX, startY, scrollLeft, scrollTop;

//     container.addEventListener('mousedown', (e) => {
//         isDown = true;
//         container.classList.add('active');

//         startX = e.pageX - container.getBoundingClientRect().left;
//         startY = e.pageY - container.getBoundingClientRect().top;


//         scrollLeft = container.scrollLeft;
//         scrollTop = container.scrollTop;

//         // Debugging: print the startX and startY values
//         console.log(`Mouse down - startX: ${startX}, startY: ${startY}`);
//         e.preventDefault();

//     });

//     document.addEventListener('mouseup', () => {
//         if (isDown) {
//             isDown = false;
//             container.classList.remove('active');
//             console.log('Mouse up - iDown set to false');
//         }
//     });

//     container.addEventListener('mouseleave', () => {
//         if (isDown) {
//             isDown = false;
//             container.classList.remove('active');
//             console.log('Mouse leave - isDown set to false');
//         }
//     });

//     container.addEventListener('mousemove', (e) => {
//         if (!isDown) return;
//         e.preventDefault();

//         const x = e.pageX - container.getBoundingClientRect().left;
//         const y = e.pageY - container.getBoundingClientRect().top;

//         const walkX = (x - startX) * 2; // Adjust scroll speed as needed
//         const walkY = (y - startY) * 2; // Adjust scroll speed as needed

//         console.log(`Mouse move - x: ${x}, y: ${y}`);
//         console.log(`Walk values - walkX: ${walkX}, walkY: ${walkY}`);

//         container.scrollLeft = scrollLeft - walkX;
//         container.scrollTop = scrollTop - walkY;

//         console.log(`Updated scroll - scrollLeft: ${container.scrollLeft}, scrollTop: ${container.scrollTop}`);
//     });

    //価格の入力フィールドのカンマ区切り
    const priceInputs = document.querySelectorAll('.price-input');
    priceInputs.forEach(input => {
        new AutoNumeric(input, {
            digitGroupSeparator: ',',
            decimalPlaces: 0, // Adjust based on your requirement
            currencySymbol: '', // Remove currency symbol if not needed
        });
    });

    

});


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


