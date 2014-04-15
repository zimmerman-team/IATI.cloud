$(document).ready(function (){
   $('.parse').click(function(){
       var image = $(this).find('img'),
           loading = $(this).parent().find('.loading'),
           xml_id = $(this).data('xml').replace('xml_', '');

       $.ajax({
           type: "GET",
           data: ({'xml_id': xml_id}),
           url: "/admin/iati_synchroniser/iatixmlsource/parse-xml/",
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



   $('#parse-all-set').click(function(){

       var btn = $('#parse-all-set');

       $.ajax({
           type: "GET",
           url: "/admin/iati_synchroniser/iatixmlsource/parse-all/",
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

   $('#parse-all-over-x-days-set').click(function(){

       var btn = $('#parse-all-over-x-days-set');

       parse_days = $('#parse-days').val();
       var intRegex = /^\d+$/;
       if(intRegex.test(parse_days)) {

           $.ajax({
               type: "GET",
               data: ({'days': parse_days}),
               url: "/admin/iati_synchroniser/iatixmlsource/parse-all-over-x-days/",
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
       }
   });

   $('#parse-all-over-interval-set').click(function(){

       var btn = $('#parse-all-over-interval-set');

       $.ajax({
           type: "GET",
           url: "/admin/iati_synchroniser/iatixmlsource/parse-all-over-interval/",
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