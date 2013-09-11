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
});