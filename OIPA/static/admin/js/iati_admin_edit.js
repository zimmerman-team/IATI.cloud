$(document).ready(function (){
    $('*[data-is-initial="false"]').each(function(){

        if (!$('.grp-errors', this).length){
            $(this).parent('.nested-sortable-item').addClass('inline-extra-item');
        }

    });

    $('.custom-oipa-add-another').click(function(){
        var model_name = $(this).data('set');
        // TODO: check how to make this work with depth = 2 InlineNestedModel
        $('.inline-group[data-inline-model="'+model_name+'"] > .items > .inline-extra-item:first').removeClass('inline-extra-item');
    });

});
