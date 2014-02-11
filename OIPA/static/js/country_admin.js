$(document).ready(function (){
   $('#update-polygon').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-polygon/",
           beforeSend: function() {
               $('#update-polygon').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-polygon').text("Updated");
               },
               404: function() {
                   $('#update-polygon').text("404 error...");
               },
               500: function() {
                   $('#update-polygon').text("500 error...");
               }
           }
       });
   });

    $('#update-country-identifiers').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-country-identifiers/",
           beforeSend: function() {
               $('#update-country-identifiers').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-country-identifiers').text("Updated");
               },
               404: function() {
                   $('#update-country-identifiers').text("404 error...");
               },
               500: function() {
                   $('#update-country-identifiers').text("500 error...");
               }
           }
       });
   });


   $('#update-country-center').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-country-center/",
           beforeSend: function() {
               $('#update-country-center').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-country-center').text("Updated");
               },
               404: function() {
                   $('#update-country-center').text("404 error...");
               },
               500: function() {
                   $('#update-country-center').text("500 error...");
               }
           }
       });
   });

    $('#update-regions').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-regions/",
           beforeSend: function() {
               $('#update-regions').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-regions').text("Updated");
               },
               404: function() {
                   $('#update-regions').text("404 error...");
               },
               500: function() {
                   $('#update-regions').text("500 error...");
               }
           }
       });
   });
});