jQuery(document).ready(function ($) {
  new WOW().init();
  $('.slider_banner').slick({
    dots: true,
    infinite: true,
    autoplaySpeed: 12000,
    speed: 600,
    arrows: false,
    autoplay: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    fade: true,
    pauseOnHover: false,
    cssEase: 'linear'
  });
  $('.s-linhvuc').slick({
    speed: 600,
    autoplay: true,
    cssEase: 'linear',
    slidesToShow: 4,
    slidesToScroll: 3,
    infinite: true,
    arrows: true,
    dots: true,
    centerMode: false,
    responsive: [
      {
        breakpoint: 1100,
        settings: {
          centerPadding: '10px',
          slidesToShow: 3
        }
      },
      {
        breakpoint: 800,
        settings: {
          centerPadding: '10px',
          slidesToShow: 2,
          slidesToScroll: 2,
        }
      },
      {
        breakpoint: 480,
        settings: {
          centerPadding: '80px',
          slidesToShow: 1,
          slidesToScroll: 1,
          arrows: false,
        }
      },
      /*{
        breakpoint: 365,
        settings: {
        centerPadding: '30px',
        slidesToShow: 1,
        }
      }*/
    ]
  });
  $('.s-news').slick({
    speed: 600,
    autoplay: true,
    centerMode: false,
    cssEase: 'linear',
    slidesToShow: 3,
    slidesToScroll: 1,
    infinite: true,
    arrows: false,
    dots: false,
    centerPadding: '70px',
    responsive: [
    {
        breakpoint: 992,
        settings: {
          centerPadding: '10px',
          slidesToShow: 2,
        }
      },
      {
        breakpoint: 500,
        settings: {
          centerPadding: '10px',
          slidesToShow: 1,
          dots: true,
          centerPadding: '80px',
        }
      }
    ]
  });
    $('.s-number-business').slick({
    autoplay: true,
    speed: 5000,
    autoplaySpeed: 0,
    centerMode: false,
    cssEase: 'linear',
    slidesToShow: 3,
    slidesToScroll: 1,
    infinite: true,
    arrows: false,
    dots: false,
    centerPadding: '70px',
    responsive: [
      {
        breakpoint: 1100,
        settings: {
          centerPadding: '10px',
          slidesToShow: 3,
        }
      },
      {
        breakpoint: 800,
        settings: {
          centerPadding: '10px',
          slidesToShow: 2,
          slidesToScroll: 2,
        }
      },
      {
        breakpoint: 500,
        settings: "unslick"
      }
    ]
  });


  let counterRan = false;

  // Thiết lập Waypoint cho section 's-business'
  $('.s-business').waypoint({
    handler: function (direction) {
      if (direction === 'down' && !counterRan) {
        $('.item-count .count').each(function () {
          // Lấy text, bỏ dấu chấm để chuyển thành số
          var $this = $(this);
          var target = parseInt($this.text().replace(/\./g, ''), 10);
          $(this).prop('Counter', 0).animate({
            Counter: target
            // Counter: $(this).text()
          }, {
            duration: (window.innerWidth <= 768) ? 3000 : 0,
            easing: 'swing',
            step: function (now) {
              // Format lại số có dấu chấm phân cách nghìn
              $this.text(Math.ceil(now).toString().replace(/\B(?=(\d{3})+(?!\d))/g, "."));
              // $(this).text(Math.ceil(now));
            }
          });
        });
        counterRan = true;
      }
    },
    offset: '75%'
  })

  // Thiết lập Waypoint cho section 's-commitment'
  var counterCommitmentRan = false;
  $('.s-commitment').waypoint({
    handler: function (direction) {
      // Không chạy trên mobile
      if (window.innerWidth < 768) {
        return;
      }

      // Điều kiện if bây giờ sẽ hoạt động chính xác
      if (direction === 'down' && !counterCommitmentRan) {
        $('.item-count .count-commitment').each(function () {
          var $this = $(this);
          // Dùng parseFloat để lấy giá trị số, kể cả số thập phân
          var target = parseFloat($this.text());

          // Bỏ qua nếu giá trị không phải là số
          if (isNaN(target)) {
            return;
          }

          $this.prop('Counter', 0).animate({
            Counter: target
          }, {
            duration: 7000,
            easing: 'swing',
            step: function (now) {
              // Hiển thị 1 chữ số thập phân trong quá trình chạy
              let displayVal = now.toFixed(1);

              // Nếu kết thúc bằng .0, loại bỏ nó để hiển thị số nguyên cho đẹp
              if (displayVal.endsWith('.0')) {
                displayVal = Math.floor(now);
              }

              $this.text(displayVal);
            },
            complete: function () {
              // Đảm bảo số cuối cùng hiển thị chính xác như giá trị ban đầu
              let finalVal = target.toFixed(1);
              if (finalVal.endsWith('.0')) {
                finalVal = parseInt(finalVal);
              }
              $this.text(finalVal);
            }
          });
        });
        // Đặt cờ thành true để hiệu ứng không chạy lại
        counterCommitmentRan = true;
      }
    },
    offset: '75%'
  });

    $('.slide-commit').slick({
        speed: 0,
        autoplay: false,
        centerMode: false,
        cssEase: 'linear',
        slidesToShow: 3,
        slidesToScroll: 3,
        infinite: true,
        arrows: false,
        dots: false,
        responsive: [
            {
                breakpoint: 800,
                settings: {
                    centerPadding: '10px',
                    slidesToShow: 2,
                    slidesToScroll: 2,
                    infinite: true,
                    autoplay: false,
                    speed: 0,
                    cssEase: 'linear',
                    arrows: false,
                    dots: false,
                    centerMode: false
                }
            },
            {
                breakpoint: 500,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                    autoplay: false,
                    speed: 0,
                    cssEase: 'linear',
                    arrows: false,
                    dots: false,
                    centerMode: false
                }
            }
        ]
    });

  /*Chieu cao slide bang nhau*/
  function equalHeightStrict() {
    let maxHeight = 0;

    const $items = $('.slide-commit .item-num');
    $items.css('height', 'auto');

    $items.each(function () {
      maxHeight = Math.max(maxHeight, $(this).outerHeight());
    });

    $items.height(maxHeight); // đồng bộ chiều cao
  }
  $(window).on('load resize', function () {
    setTimeout(equalHeightStrict, 100);
  });

  $('.slide-commit').on('setPosition', function () {
    equalHeightStrict();
  });









}); 