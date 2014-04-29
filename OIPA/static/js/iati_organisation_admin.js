$(document).ready(function (){
   $('#update-organisation-names').click(function(){

       var btn = $('#update-organisation-names');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati/organisation/update-organisation-names/",
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