$(document).ready(function(){
      $('.menu-li').hover(function(){
        $(this).
          stop().
          animate({
            fontSize: "2em"
          }, 1000);
        },
        function(){
        $(this).
         stop().
         animate({
           fontSize: "1em"
         }, 1000);}
      );
      $('.menu-li').click(function(e){
        var target = $(this).data('target');
        $("html, body").animate({
            scrollTop: $(target).offset().top
        });
      });
      $("input[name='area']").bind("click", radioClicks);

    var $main = $(".container-fluid");
    var $section = $(".system");

    $('.sysgroup-li').click(function(e) {
        e.preventDefault();
        var target = $(this).data('target');
        if(target){
            $section.filter(target).toggle();
        }
        /// $("html, body").animate({
            /// scrollTop: $(target).offset().top
        /// });
        ///$("html, body").scrollTop($(target).offset().top);
    });


 });

 functionradioClicks() {
    alert($(this).val());
 }
