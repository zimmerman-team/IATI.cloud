$(document).ready(function (){
   $('.parse-btn').click(function(){

       var btn = $(this);
       var id = $(this).data('id');

       $.ajax({
           type: "GET",
           data: ({'xml_id': id}),
           url: "/admin/iati_synchroniser/dataset/add-to-parse-queue/",
           beforeSend: function() {
               btn.removeClass("btn-success");
               btn.addClass("btn-warning");
               btn.text("Adding...");
           },
           statusCode: {
               200: function() {
                   btn.addClass("btn-info");
                   btn.text("Added to task queue");
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

   $('.parse-activity-btn').click(function(){

      var btn = $(this);
      var id = $(this).data('id');
      var activity_id = $(this).prev().val();

      $.ajax({
         type: "GET",
         data: ({'xml_id': id }),
         url: "/admin/iati_synchroniser/dataset/parse-xml/" + activity_id,
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

   $('.export-btn').click(function(){

       var btn = $(this);
       var id = $(this).data('id');
       
       $.ajax({
           type: "GET",
           url: 'export-xml/' + id,
           beforeSend: function() {
               btn.removeClass("btn-success");
               btn.addClass("btn-warning");
               btn.text("Exporting...");
           },
           statusCode: {
               200: function(data) {
                   btn.attr("href", "/media/" + data.responseText)
                   btn.addClass("btn-info");
                   btn.text("Download");
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
