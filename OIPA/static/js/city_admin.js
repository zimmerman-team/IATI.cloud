$(document).ready(function (){
   $('#update-cities-set').click(function(){

       var btn = $('#update-cities-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/city/update-cities/",
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
