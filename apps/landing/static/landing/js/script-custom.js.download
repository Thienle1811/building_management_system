/*loading*/
(function ($) { $(window).on('load', function () { $(".loader").fadeOut(); $("#preloder").delay(200).fadeOut("slow"); }); })(jQuery);

$(document).ready(function () {
  $('a[href="#search"]').on('click', function (event) {
    event.preventDefault();
    if (!$('body').hasClass('search-open')) {
      $('body').addClass('search-open');
      $('#search > form > input[type="search"]').focus();
      $("#header").removeClass("open")
    } else {
      $('body').removeClass('search-open');
    }
  });

  $('.search-input').on('input', function () {
    if ($(this).val().length > 0) {
      $("#search .search-container").addClass('value-search-input');
    } else {
      $("#search .search-container").removeClass('value-search-input');
    }
  });

  $("#header .js-toggle-menu").click(function () {
    $("#header").toggleClass("sticky open");
    $("body").toggleClass("menutog");
    $('body').removeClass('search-open');
  });

  let lastScrollTop = 0;
  const $footer = $('.section-footer');

  $(window).scroll(function () {
    const scrollTop = $(window).scrollTop();
    const windowHeight = $(window).height();
    const scrollBottom = scrollTop + windowHeight;
    const documentHeight = $(document).height();
    const scrollableHeight = documentHeight - windowHeight;
    const footerTop = $footer.offset().top;

    if (scrollTop != 0) {
      $("body").addClass("p-sticky");
      // $("#header").addClass("sticky");
      // $('.gotop').fadeIn();


      // Kiểm tra hướng cuộn
      if (!$('#fullpage').hasClass('investor-relations')) {
        if (scrollTop > lastScrollTop) {
          // Cuộn xuống
          $("#header").removeClass("sticky-up");
        } else {
          // Cuộn lên
          $("#header").addClass("sticky-up");
        }
      }

      // Hiển thị nút "Go to top" khi cuộn xuống quá nửa chiều cao trang
      if (scrollTop > scrollableHeight / 2) {
        $('.gotop').fadeIn();
      } else {
        $('.gotop').fadeOut();
      }

      lastScrollTop = scrollTop; // Cập nhật vị trí cuộn
    } else {
      $("body").removeClass("p-sticky");
      // $("#header").removeClass("sticky");
      $("#header").removeClass("sticky-up");
      $('.gotop').fadeOut();
    }

    // 3. Kiểm tra cuộn đến cuối trang -> thêm .footer-web
    if (scrollBottom >= documentHeight - 1) {
      $('body').addClass('footer-web').removeClass('footer-reach');
    }
    // 4. Nếu giao thoa footer nhưng chưa tới đáy -> .footer-reach
    else if (scrollBottom >= footerTop) {
      $('body').addClass('footer-reach').removeClass('footer-web');
    }
    // 5. Nếu chưa chạm footer
    else {
      $('body').removeClass('footer-reach footer-web');
    }
  });

  // $(window).scroll(function () {
  //   let currentScroll = $(window).scrollTop();
  //   if ($(window).scrollTop() != 0) {
  //     $("body").addClass("p-sticky");
  //     // $("#header").addClass("sticky");
  //     $('.gotop').fadeIn();


  //     // Kiểm tra hướng cuộn
  //     if (currentScroll > lastScrollTop) {
  //       // Cuộn xuống
  //       $("#header").removeClass("sticky-up");
  //     } else {
  //       // Cuộn lên
  //       $("#header").addClass("sticky-up");
  //     }

  //     lastScrollTop = currentScroll; // Cập nhật vị trí cuộn
  //   } else {
  //     $("body").removeClass("p-sticky");
  //     // $("#header").removeClass("sticky");
  //     $("#header").removeClass("sticky-up");
  //     $('.gotop').fadeOut();
  //   }
  // });


  $("#main-menu li").click(function () {
    $("#main-menu li").removeClass("active");
    $(this).addClass("active");
    $(this).parent().parent().addClass("active");
  });

  /*--------------------*/
  $(".by-interest").click(function () {
    // var slug = $(this).data('slug');
    $('.main-menu-wrap').parent().addClass("active-int");
    //$('body').addClass('mn-child');

    setTimeout(() => {
      $('.bg-menubottom').addClass("active")
    }, 200);
  });

  $('.bg-menubottom').hover(function () {
    if ($(this).hasClass("active")) {
      $('.main-menu-wrap').parent().removeClass("active-int");
      $('.bg-menubottom').removeClass("active")
    }
  })


  $(".back-interest").click(function () {
    var slug = $(".by-interest").data('slug');
    $("." + slug).find(".submenu").addClass("submenu-active");
    // $('body').addClass('mn-child');
    $('.main-menu-wrap').parent().removeClass("active-int");
    $('.bg-menubottom').addClass("active")
  });



  // $('.main-menu .menu-item-has-children > a').on('click', function (e) {
  //   if ($(window).width() < 1199) {
  //     e.preventDefault();
  //     var parentItem = $(this).closest('.menu-item-has-children');
  //     parentItem.toggleClass('open');
  //     $('.menu-item-has-children').not(parentItem).removeClass('open');
  //   }
  // });

  $('.main-menu .menu-item-has-children > a').on('click touchend', function (e) {
    if ($(window).width() < 1199) {
      var $link = $(this);
      var $parentItem = $link.closest('.menu-item-has-children');

      if ($parentItem.hasClass('open')) {
        // Lần click 2: ép điều hướng luôn, fix Safari iOS
        e.preventDefault();
        window.location.href = $link.attr('href');
      } else {
        // Lần click 1: chỉ mở submenu
        e.preventDefault();
        $parentItem.addClass('open');
        $('.menu-item-has-children').not($parentItem).removeClass('open');
      }
    }
  });


  $(document).ready(function () {
    $('.main-menu .menu-item-has-children > a').hover(
      function () {
        $('body').addClass('mn-child');
      },
      function () {
        $('body').removeClass('mn-child');
      }
    );
  });
  $(document).ready(function () {
    const $bg = $('.bg-menubottom');
    $('.menu-item.menu-item-has-children').hover(
      function () {
        $bg.addClass('active');
        var slug = $(this).data("slug");
        $(".by-interest").data('slug', slug);
      },
      function () {
        setTimeout(() => {
          if (!$('.menu-item.menu-item-has-children:hover').length && !$('.submenu:hover').length) {
            $bg.removeClass('active');
          }
        }, 50);

        $(this).find("submenu").removeClass("submenu-active")
      }
    );
    $('.submenu').hover(
      function () {
        $bg.addClass('active');
      },
      function () {
        setTimeout(() => {
          if (!$('.menu-item.menu-item-has-children:hover').length && !$('.submenu:hover').length) {
            $bg.removeClass('active');
          }
        }, 50);
        $(this).removeClass("submenu-active")
      }
    );
  });
  /*back interest menu*/

  /*End*/

  if ($(window).width() >= 1200) {
    $("#main-menu li").hover(
      function () {
        $(this).addClass("menu-hover");
      },
      function () {
        $(this).removeClass("menu-hover");
      }
    );
  }

  // const $footer = $('.section-footer');
  // const $body = $('body'); // Select the body element
  // let classAddedToBody = false;

  // $footer.waypoint({
  //   handler: function (direction) {
  //     if (direction === 'down') {
  //       if (!classAddedToBody) {
  //         $body.addClass('footer-web');
  //         classAddedToBody = true;
  //       }
  //     } else {
  //       if (classAddedToBody) {
  //         $body.removeClass('footer-web');
  //         classAddedToBody = false;
  //       }
  //     }
  //   },
  //   offset: '90%'
  // });

});

$(document).ready(function () {
  $(".gotop").fadeOut(0);
  $(".gotop").click(function () {
    $('html, body').animate({
      scrollTop: $(".site").offset().top
    }, 1000);
  });


  if ($('#searchform .search-input').val()) {
    $(".reset-button").show();
    $(".search-button").hide();
  }

  $(".reset-button").click(function () {
    $('#searchform .search-input').val("")
    $(".reset-button").hide();
    $(".search-button").show();
  })

  $('#searchform .search-input').keyup(function () {
    $(".reset-button").show();
    $(".search-button").hide();
  })

  const breakpoint = 1200;
  function toggleMenuClass() {
    if (window.innerWidth < breakpoint) {
      // Màn hình nhỏ hơn 1024px, thêm class
      $(".main-menu .menu-354").addClass('menu-mobile-active');
      $(".main-menu .menu-355").addClass('menu-mobile-active');
    } else {
      // Màn hình lớn hơn hoặc bằng 1024px, xóa class
      $(".main-menu .menu-354").removeClass('menu-mobile-active');
      $(".main-menu .menu-355").removeClass('menu-mobile-active');
    }
  }

  // Chạy hàm khi trang vừa tải
  toggleMenuClass();

  // Chạy hàm mỗi khi kích thước cửa sổ thay đổi
  window.addEventListener('resize', toggleMenuClass);

  if (window.innerWidth < breakpoint) {
    $(".main-menu li.menu-354, .main-menu li.menu-355").click(function () {
      var href = $(this).find("a").attr("href");
      window.location.href = href
    })
  }

  $(".box-item-anal li a").click(function () {
    var title = $(this).data("title");
    $(".box-item-anal .box-item-title").text(title)
  })
});
