$(document).ready(function (){

   $('#update-indicators-set').click(function(){

       var btn = $('#update-indicators-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicator/indicator/update-indicator/",
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

   $('#update-wbi-set').click(function(){

       var btn = $('#update-wbi-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicator/indicator/update-wbi-indicator/",
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



   $('#update-indicator-data-set').click(function(){

       var btn = $('#update-indicator-data-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicator/indicator/update-indicator-data/",
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


   $('#update-indicator-city-data-set').click(function(){

       var btn = $('#update-indicator-city-data-set');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicator/indicator/update-indicator-city-data/",
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