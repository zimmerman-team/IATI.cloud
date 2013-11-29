$(document).ready(function (){
   $('#update-requests').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/Cache/requested_call/update-requests/",
           beforeSend: function() {
               $('#update-requests').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-requests').text("Updated");
               },
               404: function() {
                   $('#update-requests').text("404 error...");
               },
               500: function() {
                   $('#update-requests').text("500 error...");
               }
           }
       });
   });

   $('#update-caches').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/Cache/cached_call/update-caches/",
           beforeSend: function() {
               $('#update-caches').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-caches').text("Updated");
               },
               404: function() {
                   $('#update-caches').text("404 error...");
               },
               500: function() {
                   $('#update-caches').text("500 error...");
               }
           }
       });
   });
});
