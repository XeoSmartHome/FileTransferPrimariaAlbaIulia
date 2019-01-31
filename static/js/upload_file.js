(function( $ ){
     $.fn.multipleInput = function() {

          return this.each(function() {

               // create html elements

               // list of email addresses as unordered list
               $list = $('<ul />');

               // input
               var $input = $('<input type="text" />').keyup(function(event) {

                    if(event.which == 32 || event.which == 188 || event.which == 13) {
                         // key press is space or comma
                         if(event.which == 32 || event.which == 188)
                            var val = $(this).val().slice(0, -1); // remove space/comma from value
                         else
                            var val = $(this).val();

                         // append to list of emails with remove button
                         $list.append($('<li class="multipleInput-email"><span>' + val + '</span></li>')
                              .append($('<a href="#" class="multipleInput-close" title="Remove" />')
                                   .click(function(e) {
                                        $(this).parent().remove();
                                        e.preventDefault();
                                   })
                              )
                         );
                         $(this).attr('placeholder', '');
                         // empty input
                         $(this).val('');
                    }

               });

               // container div
               var $container = $('<div class="multipleInput-container" />').click(function() {
                    $input.focus();
               });

               // insert elements into DOM
               $container.append($list).append($input).insertAfter($(this));

               // add onsubmit handler to parent form to copy emails into original input as csv before submitting
               var $orig = $(this);
               $(this).closest('form').submit(function(e) {

                    var emails = new Array();
                    $('.multipleInput-email span').each(function() {
                         emails.push($(this).html());
                    });
                    emails.push($input.val());

                    $orig.val(emails.join());

               });

               return $(this).hide();

          });

     };
})( jQuery );


document.querySelector('#upload-file').addEventListener('change', function() {
	// This is the file user has chosen
	var file = this.files[0];

	// Max 2 Gb allowed
	if(file.size > 2024*1024*1024) {
		alert('Error : Exceeded size 2GB');
		return;
	}

	// Validation is successful
	// This is the name of the file
	console.log('You have chosen the file ' + file.name);
});

progress_bar = document.querySelector('#progress-bar');
upload_response = document.querySelector('#upload-response');
send_button = document.querySelector("#choose-button");

function send_file(){
    // hide button
    send_button.hidden = true;

    var data = new FormData();
    var request = new XMLHttpRequest();

    var emails = document.getElementsByClassName("multipleInput-email");
    var emails_list = [];
    for(var i=0; i<emails.length; i++)
        emails_list.push(emails[i].innerText);
    data.append('emails', emails_list);


    data.append('message', document.querySelector('#message').value);

    // File selected by the user
    // In case of multiple files append each of them
    files = document.querySelector('#upload-file').files
    for(var i=0; i<files.length; i++)
        data.append('files[]', files[i]);

    // AJAX request finished
    request.addEventListener('load', function(e) {
    	// request.response will hold the response from the server
    	console.log(request.response);
    });

    // Upload progress on request.upload
    request.upload.addEventListener('progress', function(e) {
    	var percent_complete = (e.loaded / e.total)*100;
    	// Percentage of upload completed
    	console.log(percent_complete);
    	progress_bar.style.width = percent_complete + '%';

    	if(percent_complete==100){
    	    upload_response.innerText = "Successfully uploaded";
    	}
    });


    request.open('POST', 'upload_file');
    request.send(data);
}