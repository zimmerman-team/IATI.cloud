$(document).ready(function (){
   $('.parse-btn').click(function(){

       var btn = $(this);
       var xml_id = $(this).data('xml').replace('xml_', '');

       $.ajax({
           type: "GET",
           data: ({'xml_id': xml_id}),
           url: "/admin/iati_synchroniser/iatixmlsource/parse-xml/",
           beforeSend: function() {
               btn.removeClass("btn-success");
               btn.addClass("btn-warning");
               btn.text("Updating...");
           },
           statusCode: {
               200: function() {
                   btn.addClass("btn-info");
                   btn.text("Updated");
               },
               404: function() {
                   btn.addClass("btn-danger");
                   btn.text("404 error...");
               },
               500: function() {
                   btn.addClass("btn-danger");
                   btn.text("500 error...");
               }
           }
       });
   });
});