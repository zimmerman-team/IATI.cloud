$(document).ready(function (){
    $('.sync-btn').click(function(){

        var btn = $(this);
        var sync_id = $(this).data('sync').replace('sync_', '');
        $.ajax({
            type: "GET",
            data: ({'sync_id': sync_id}),
            url: "/admin/iati_synchroniser/codelistsync/sync-codelists/",
            beforeSend: function() {
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