$(document).ready(function (){
   $('#update-unesco_sectors').click(function(){

       var btn = $('#update-unesco_sectors');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati/sector/update-unesco-sectors/",
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

    $('#update-rain_sectors').click(function(){

       var btn = $('#update-rain_sectors');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati/sector/update-rain-sectors/",
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