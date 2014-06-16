$(document).ready(function (){
   $('#import-un-region-set').click(function(){

       var btn = $('#import-un-region-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/region/import-un-regions/",
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

   $('#import-unesco-region-set').click(function(){

       var btn = $('#import-unesco-region-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/region/import-unesco-regions/",
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
