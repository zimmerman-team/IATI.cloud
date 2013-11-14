$(document).ready(function (){
   $('#update-indicators-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicators/indicator/update-indicators/",
           beforeSend: function() {
               $('#update-indicators-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-indicators-set').text("Updated");
               },
               404: function() {
                   $('#update-indicators-set').text("404 error...");
               },
               500: function() {
                   $('#update-indicators-set').text("500 error...");
               }
           }
       });
   });

   $('#update-wbi-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicators/indicator/update-wbi-indicators/",
           beforeSend: function() {
               $('#update-wbi-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-wbi-set').text("Updated");
               },
               404: function() {
                   $('#update-wbi-set').text("404 error...");
               },
               500: function() {
                   $('#update-wbi-set').text("500 error...");
               }
           }
       });
   });



   $('#update-indicator-data-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicators/indicator/update-indicator-data/",
           beforeSend: function() {
               $('#update-indicator-data-set').text("Updating... This might take 10+ minutes");
           },
           statusCode: {
               200: function() {
                   $('#update-indicator-data-set').text("Updated");
               },
               404: function() {
                   $('#update-indicator-data-set').text("404 error...");
               },
               500: function() {
                   $('#update-indicator-data-set').text("500 error...");
               }
           }
       });
   });


   $('#update-indicator-city-data-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/indicators/indicator/update-indicator-city-data/",
           beforeSend: function() {
               $('#update-indicator-city-data-set').text("Updating... This might take 5+ minutes");
           },
           statusCode: {
               200: function() {
                   $('#update-indicator-city-data-set').text("Updated");
               },
               404: function() {
                   $('#update-indicator-city-data-set').text("404 error...");
               },
               500: function() {
                   $('#update-indicator-city-data-set').text("500 error...");
               }
           }
       });
   });

});