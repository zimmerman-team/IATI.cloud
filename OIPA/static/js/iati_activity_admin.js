/**
 * Created with PyCharm.
 * User: vincentvantwestende
 * Date: 11/18/13
 * Time: 4:57 PM
 * To change this template use File | Settings | File Templates.
 */


$(document).ready(function (){
   $('#update-budget-totals').click(function(){

       $.ajax({
           type: "GET",
           data: ({'all': 1}),
           url: "/admin/iati/activity/update-budget-totals/",
           beforeSend: function() {
               $('#update-budget-totals').text("Updating...");
           },
           statusCode: {
               200: function() {
                   $('#update-budget-totals').text("Updated");
               },
               404: function() {
                   $('#update-budget-totals').text("404 error...");
               },
               500: function() {
                   $('#update-budget-totals').text("500 error...");
               }
           }
       });
   });
});
