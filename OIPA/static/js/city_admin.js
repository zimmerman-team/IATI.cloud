$(document).ready(function (){
   $('#update-cities-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/city/update-cities/",
           beforeSend: function() {
               $('#update-cities-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-cities-set').text("Updated");
               },
               404: function() {
                   $('#update-cities-set').text("404 error...");
               },
               500: function() {
                   $('#update-cities-set').text("500 error...");
               }
           }
       });
   });
});
