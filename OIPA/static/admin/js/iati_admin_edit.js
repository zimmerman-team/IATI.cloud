$(document).ready(function (){

    $('*[data-is-initial="false"]').each(function(){
        if (!$('.grp-errors', this).length){
            $(this).addClass('inline-extra-item');
        }
    });

    $('.custom-oipa-add-another').click(function(){
        var model_name = $(this).data('set');
        var depth = $(this).data('nesting-level');
        if(depth > 1){
            $(this).parent().prev().children('.inline-extra-item:first').removeClass('inline-extra-item');
        } else {
            $('.inline-group[data-inline-model="'+model_name+'"] > .items > .inline-extra-item:first').removeClass('inline-extra-item');
        }
    });
});
