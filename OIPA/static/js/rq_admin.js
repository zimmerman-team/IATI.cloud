$(document).ready(function (){
   $('#add-new-default-worker').click(function(){

       var btn = $('#add-new-default-worker');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati_synchroniser/datasetsync/add-default-worker/",
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
   });

    $('#add-new-parser-worker').click(function(){

       var btn = $('#add-new-parser-worker');

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati_synchroniser/datasetsync/add-parser-worker/",
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
   });
});
