$(document).ready(function (){
   $('#import-un-region-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/region/import-un-regions/",
           beforeSend: function() {
               $('#import-un-region-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#import-un-region-set').text("Updated");
               },
               404: function() {
                   $('#import-un-region-set').text("404 error...");
               },
               500: function() {
                   $('#import-un-region-set').text("500 error...");
               }
           }
       });
   });
});
