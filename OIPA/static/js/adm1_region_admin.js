/**
 * Created with PyCharm.
 * User: vincentvantwestende
 * Date: 11/14/13
 * Time: 7:22 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function (){
   $('#update-adm1-region').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/geodata/adm1_region/update-adm1-regions/",
           beforeSend: function() {
               $('#update-adm1-region').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-adm1-region').text("Updated");
               },
               404: function() {
                   $('#update-adm1-region').text("404 error...");
               },
               500: function() {
                   $('#update-adm1-region').text("500 error...");
               }
           }
       });
   });
});
