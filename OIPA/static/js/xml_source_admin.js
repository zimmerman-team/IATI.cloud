$(document).ready(function (){
   $('.parse').click(function(){
       var image = $(this).find('img'),
           loading = $(this).parent().find('.loading'),
           xml_id = $(this).data('xml').replace('xml_', '');
       $.ajax({
           type: "GET",
           data: ({'xml_id': xml_id}),
           url: "/admin/IATI_synchroniser/iati_xml_source/parse-xml/",
           beforeSend: function() {
               image.hide();
               loading.show();
           },
           statusCode: {
               200: function() {
                   loading.hide();
                   image.attr('src', '/static/img/utils.parse.success.png');
                   image.show();
               },
               404: function() {
                   loading.hide();
                   image.attr('src', '/static/img/utils.parse.error.png');
                   image.show();
               },
               500: function() {
                   loading.hide();
                   image.attr('src', '/static/img/utils.parse.error.png');
                   image.show();
               }
           }
       });
   });



   $('#parse-all-set').click(function(){
       $.ajax({
           type: "GET",
           url: "/admin/IATI_synchroniser/iati_xml_source/parse-all/",
           beforeSend: function() {
               $('#parse-all-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#parse-all-set').text("Updated");
               },
               404: function() {
                   $('#parse-all-set').text("404 error...");
               },
               500: function() {
                   $('#parse-all-set').text("500 error...");
               }
           }
       });
   });

   $('#parse-all-over-two-days-set').click(function(){
       $.ajax({
           type: "GET",
           url: "/admin/IATI_synchroniser/iati_xml_source/parse-all-over-two-days/",
           beforeSend: function() {
               $('#parse-all-over-two-days-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#parse-all-over-two-days-set').text("Updated");
               },
               404: function() {
                   $('#parse-all-over-two-days-set').text("404 error...");
               },
               500: function() {
                   $('#parse-all-over-two-days-set').text("500 error...");
               }
           }
       });
   });

   $('#parse-all-over-interval-set').click(function(){
       $.ajax({
           type: "GET",
           url: "/admin/IATI_synchroniser/iati_xml_source/parse-all-over-interval/",
           beforeSend: function() {
               $('#parse-all-over-interval-set').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#parse-all-over-interval-set').text("Updated");
               },
               404: function() {
                   $('#parse-all-over-interval-set').text("404 error...");
               },
               500: function() {
                   $('#parse-all-over-interval-set').text("500 error...");
               }
           }
       });
   });


});