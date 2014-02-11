$(document).ready(function (){
   $('#update-organisation-names').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati/organisation/update-organisation-names/",
           beforeSend: function() {
               $('#update-organisation-names').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-organisation-names').text("Updated");
               },
               404: function() {
                   $('#update-organisation-names').text("404 error...");
               },
               500: function() {
                   $('#update-organisation-names').text("500 error...");
               }
           }
       });
   });
});