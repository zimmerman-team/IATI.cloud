$(document).ready(function (){
   $('#update-requests').click(function(){

       var btn = $('#update-requests');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/requestedcall/update-requests/",
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

   $('#delete-all-under-x-count').click(function(){

       var btn = $('#delete-all-under-x-count');

       var request_count = $('#request-count').val();
       var intRegex = /^\d+$/;
       if(intRegex.test(request_count)) {

           $.ajax({
               type: "GET",
               data: ({'count': request_count}),
               url: "/admin/cache/requestedcall/delete-all-under-x-count/",
               beforeSend: function() {
                   btn.removeClass("btn-success");
                   btn.addClass("btn-warning");
                   btn.text("Updating...");
               },
               statusCode: {
                   200: function() {
                       btn.addClass("btn-info");
                       btn.text("Updated");
                       setInterval(function(){location.reload()},2000);
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
       }
   });





   $('#cache-all-requests').click(function(){

       var btn = $('#cache-all-requests');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/requestedcall/cache-all-requests/",
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

   $('#update-caches').click(function(){

       var btn = $('#update-caches');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/cache/cachedcall/update-caches/",
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
