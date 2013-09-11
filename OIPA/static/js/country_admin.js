$(document).ready(function (){
   $('#update-polygon-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-polygon/",
           beforeSend: function() {
               $('#update-polygon-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-polygon-set').text("Updated");
               },
               404: function() {
                   $('#update-polygon-set').text("404 error...");
               },
               500: function() {
                   $('#update-polygon-set').text("500 error...");
               }
           }
       });
   });

   $('#update-country-center-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-country-center/",
           beforeSend: function() {
               $('#update-country-center-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-country-center-set').text("Updated");
               },
               404: function() {
                   $('#update-country-center-set').text("404 error...");
               },
               500: function() {
                   $('#update-country-center-set').text("500 error...");
               }
           }
       });
   });

    $('#update-regions-set').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/country/update-regions-set/",
           beforeSend: function() {
               $('#update-regions-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-regions-set').text("Updated");
               },
               404: function() {
                   $('#update-regions-set').text("404 error...");
               },
               500: function() {
                   $('#update-regions-set').text("500 error...");
               }
           }
       });
   });
});