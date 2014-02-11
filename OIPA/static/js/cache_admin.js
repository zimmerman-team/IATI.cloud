$(document).ready(function (){
   $('#update-requests').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/requestedcall/update-requests/",
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

   $('#delete-all-under-x-count').click(function(){
       request_count = $('#request-count').val();
       var intRegex = /^\d+$/;
       if(intRegex.test(parse_days)) {

           $.ajax({
               type: "GET",
               data: ({'count': request_count}),
               url: "/admin/iati_synchroniser/iatixmlsource/delete-all-under-x-count/",
               beforeSend: function() {
                   $('#delete-all-under-x-count').text("Updating...");
               },
               statusCode: {
                   200: function() {
                       $('#delete-all-under-x-count').text("Updated");
                   },
                   404: function() {
                       $('#delete-all-under-x-count').text("404 error...");
                   },
                   500: function() {
                       $('#delete-all-under-x-count').text("500 error...");
                   }
               }
           });
       }
   });





       $('#cache-all-requests').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/requestedcall/cache-all-requests/",
           beforeSend: function() {
               $('#cache-all-requests').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#cache-all-requests').text("Updated");
               },
               404: function() {
                   $('#cache-all-requests').text("404 error...");
               },
               500: function() {
                   $('#cache-all-requests').text("500 error...");
               }
           }
       });
   });

   $('#update-caches').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/cachedcall/update-caches/",
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
