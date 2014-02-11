$(document).ready(function (){
    $('.sync').click(function(){
        var image = $(this).find('img'),
            loading = $(this).parent().find('.loading'),
            sync_id = $(this).data('sync').replace('sync_', '');
        $.ajax({
            type: "GET",
            data: ({'sync_id': sync_id}),
            url: "/admin/iati_synchroniser/datasetsync/sync-datasets/",
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