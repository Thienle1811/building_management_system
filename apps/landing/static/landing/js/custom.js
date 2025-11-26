$(document).ready(function ($) {
  $('#pboard').on('show.bs.modal', function (event) {
    const trigger = $(event.relatedTarget);

    const name = trigger.data('name');
    const position = trigger.data('position');
    const desc = trigger.data('desc');
    const img = trigger.data('img');

    const modal = $(this);
    modal.find('#modal-name').html(name);
    modal.find('#modal-position').html(position);
    modal.find('#modal-desc').html(desc);
    modal.find('#modal-img').attr('src', img).attr('alt', name);
  });
});

$(document).ready(function ($) {
  let filters = {
    region: '',
    development: '',
    product: '',
    status: ''
  };
  let commercial_filters = {
    category: '',
    region: '',
    type: '',
    status: ''
  };

  // Khi click từng option
  $('.region-filter div').on('click', function () {
    filters.region = $(this).data('region');
    fetchFilteredProjects();
  });

  $('.development-filter div').on('click', function () {
    filters.development = $(this).data('type');
    fetchFilteredProjects();
  });

  $('.product-filter div').on('click', function () {
    filters.product = $(this).data('category');
    fetchFilteredProjects();
  });

  $('.status-filter div').on('click', function () {
    filters.status = $(this).data('status');
    fetchFilteredProjects();
  });

  $('.commercial-region-filter div').on('click', function () {
    commercial_filters.category = $(this).data('category');
    commercial_filters.region = $(this).data('region');
    fetchFilteredCommercials();
  });

  $('.commercial-type-filter div').on('click', function () {
    commercial_filters.category = $(this).data('category');
    commercial_filters.type = $(this).data('type');
    fetchFilteredCommercials();
  });

  $('.commercial-status-filter div').on('click', function () {
    commercial_filters.category = $(this).data('category');
    commercial_filters.status = $(this).data('status');
    fetchFilteredCommercials();
  });


  let rawLang = $('html').attr('lang') || 'vi';
  let lang = rawLang.split('-')[0]; // "en-US" → "en"
  function fetchFilteredProjects() {
    fetch('/wp-json/nlg/v1/filter-projects/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filters: filters,
        lang: lang
      })
    })
      .then(res => res.json())
      .then(data => {
        $('.result-proj').html(data.html); // Cập nhật HTML
      })
      .catch(err => {
        console.error('Lỗi khi gọi API:', err);
      });
  }


  function fetchFilteredCommercials() {
    fetch('/wp-json/nlg/v1/filter-commercials/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filters: commercial_filters,
        lang: lang
      })
    })
      .then(res => res.json())
      .then(data => {
        $('.result-proj').html(data.html); // Render lại HTML
      })
      .catch(err => {
        console.error('Lỗi gọi REST API:', err);
      });
  }


  $('.project-clear-all').click(function (e) {
    e.preventDefault();
    $('.dropdown-container').each(function () {
      const defaultText = $(this).attr('data-default');
      $(this).find('span:first-child').text(defaultText);
    });

    filters = {
      region: '',
      development: '',
      product: '',
      status: ''
    };

    fetchFilteredProjects();
  });

  $('.commercial-clear-all').click(function (e) {
    e.preventDefault();
    const defaultCategory = $(this).data('category');
    resetCommercialFilters(defaultCategory);
  });

  $('.commercial-toggle').on('click', function (e) {
    e.preventDefault();
    const defaultCategory = $(this).data('category');
    resetCommercialFilters(defaultCategory);
  });


  function resetCommercialFilters(defaultCategory) {
    $('.dropdown-container').each(function () {
      const defaultText = $(this).attr('data-default');
      $(this).find('span:first-child').text(defaultText);
    });

    commercial_filters = {
      category: defaultCategory,
      region: '',
      type: '',
      status: ''
    };

    fetchFilteredCommercials();
  }
});

$(document).ready(function ($) {
  // Ẩn spinner và message khi trang load
  $('.wpcf7-spinner, .wpcf7-response-output').hide();
});



$(document).ready(function ($) {
  $('.regulation').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    console.log('Selected year clicked:', selectedYear);

    // Thay đổi text hiển thị trong dropdown
    $('#selectedTime-income-regulation').text(selectedYear);

    // Ẩn tất cả các block năm
    $('.year-block').hide();

    // Hiển thị block tương ứng với năm được chọn
    $('.year-block[data-year="' + selectedYear + '"]').show();
  });

  $('.prospectus-1').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-prospectus').text(selectedYear);
    $('.year-prospectus').hide();
    $('.year-prospectus[data-year="' + selectedYear + '"]').show();
  });

  $('.disclosure').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-disclosure').text(selectedYear);
    $('.year-disclosure').hide();
    $('.year-disclosure[data-year="' + selectedYear + '"]').show();
  });

  $('.financial').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-financial').text(selectedYear);
    $('.year-financial').hide();
    $('.year-financial[data-year="' + selectedYear + '"]').show();
  });

  $('.dividend-meeting').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-dividend-meeting').text(selectedYear);
    $('.year-dividend-meeting').hide();
    $('.year-dividend-meeting[data-year="' + selectedYear + '"]').show();
  });

  $('.shareholders-meeting').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-shareholders-meeting').text(selectedYear);
    $('.year-shareholders-meeting').hide();
    $('.year-shareholders-meeting[data-year="' + selectedYear + '"]').show();
  });

  $('.corporate').on('click', function (e) {
    e.preventDefault();
    var selectedYear = $(this).data('value');
    $('#selectedTime-income-corporate').text(selectedYear);
    $('.year-corporate').hide();
    $('.year-corporate[data-year="' + selectedYear + '"]').show();
  });
});



$(document).ready(function ($) {
  $('.dropdown-item.time-option').on('click', function (e) {
    e.preventDefault();
    const selectedText = $(this).text();
    const periodId = $(this).data('period-id');
    const parentPane = $(this).closest('.tab-pane');
    parentPane.find('.dropdown-toggle .selected-time').text(selectedText.trim());
    parentPane.find('.data-section').removeClass('active');
    parentPane.find('.data-section.' + periodId).addClass('active');
  });
});


$(document).ready(function ($) {
  const cookieAccept = 'cookie_notice_accepted';
  const cookieRefuse = 'cookie_notice_refused';

  // Kiểm tra cookie có tồn tại không
  function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
  }

  // Nếu đã chấp nhận hoặc từ chối → ẩn popup
  if (getCookie(cookieAccept) || getCookie(cookieRefuse)) {
    $('#cookie-notice').hide();
  }

  // Khi bấm nút "Chấp nhận"
  $('#cn-accept-cookie').on('click', function () {
    document.cookie = cookieAccept + "=true; path=/; max-age=" + (60 * 60 * 24 * 365);
    $('#cookie-notice').hide();
  });

  // Khi bấm nút "Từ chối"
  $('#cn-refuse-cookie').on('click', function () {
    document.cookie = cookieRefuse + "=true; path=/; max-age=" + (60 * 60 * 24 * 365);
    $('#cookie-notice').hide();
  });
});


// Phát triển khu đô thị nhà ở
$('.viewMoreBtn').click(function () {
  $('.project-list.hidden').removeClass('hidden');
  $(this).hide();
});


// Logo Intro Preloader
window.addEventListener('load', function () {
  const preloader = document.getElementById('preloader');
  const preloaderLogo = document.getElementById('preloader-logo');
  const finalLogo = document.getElementById('final-logo');

  if (!$('#fullpage').hasClass('homepage')) {
    if (preloader) preloader.style.display = 'none';
    return;
  }

  if (!preloader || !preloaderLogo) {
    if (preloader) preloader.style.display = 'none';
    return;
  }

  const isDesktop = window.matchMedia('(min-width: 1025px)').matches;

  // Ẩn final-logo ngay từ đầu ở DESKTOP để tránh nó xuất hiện trước/khác nhịp
  if (isDesktop && finalLogo && window.scrollY === 0) {
    finalLogo.style.visibility = 'hidden';
    finalLogo.style.opacity = '1';      // đảm bảo không bị CSS khác fade khi hiện
    finalLogo.style.transition = 'none';// vô hiệu hoá mọi transition của logo menu
  }

  // Hiện logo preload ở giữa
  preloaderLogo.classList.add('visible');
  preloaderLogo.style.willChange = 'transform';

  setTimeout(() => {
    // ===== DESKTOP: bay nhập thẳng vào logo menu, KHÔNG fade =====
    if (isDesktop && finalLogo && window.scrollY === 0) {
      const from = preloaderLogo.getBoundingClientRect();
      const to = finalLogo.getBoundingClientRect();

      if (to.width > 0 && to.height > 0) {
        const fromCx = from.left + from.width / 2;
        const fromCy = from.top + from.height / 2;
        const toCx = to.left + to.width / 2;
        const toCy = to.top + to.height / 2;

        const dx = toCx - fromCx;
        const dy = toCy - fromCy;
        const scale = to.width / from.width;

        preloaderLogo.style.transformOrigin = 'center center';
        preloaderLogo.style.transition = 'transform 0.8s ease';
        // force reflow để transition chắc chắn chạy
        void preloaderLogo.offsetWidth;

        // translate3d trước, scale sau (CSS apply ngược → translate không bị scale)
        preloaderLogo.style.transform = `translate3d(${dx}px, ${dy}px, 0) scale(${scale})`;

        preloaderLogo.addEventListener('transitionend', (e) => {
          if (e.propertyName === 'transform') {
            // 1) Hiện ngay final-logo (không transition)
            finalLogo.style.visibility = 'visible';

            // 2) Ẩn ngay preloader + logo preload (KHÔNG fade)
            preloaderLogo.style.transition = 'none';
            preloaderLogo.style.display = 'none'; // ẩn tức thì để không có khung hình "trống"
            preloader.style.background = 'transparent';
            preloader.style.pointerEvents = 'none';
            preloader.style.display = 'none';

            // Xong nhánh desktop
          }
        }, { once: true });

        return;
      }
      // nếu to.width == 0 (logo menu chưa layout), rơi về nhánh mobile/iPad bên dưới
    }

    // ===== DESKTOP không ở đầu trang: bay về góc trái cố định =====
    if (isDesktop && window.scrollY > 0) {
      const preloaderRect = preloaderLogo.getBoundingClientRect();

      // giá trị góc trái riêng cho desktop
      const TARGET_LEFT = 120;
      const TARGET_TOP = 0;
      const TARGET_WIDTH = 90;

      const translateX = TARGET_LEFT - preloaderRect.left;
      const translateY = TARGET_TOP - preloaderRect.top;

      preloaderLogo.style.transition = 'transform 0.8s ease, width 0.8s ease';
      preloaderLogo.style.transform = `translate(${translateX}px, ${translateY}px)`;
      preloaderLogo.style.width = TARGET_WIDTH + 'px';

      preloaderLogo.addEventListener('transitionend', (e) => {
        if (e.propertyName === 'transform') {
          preloader.style.background = 'transparent';
          preloader.style.pointerEvents = 'none';
          preloader.style.display = 'none';
        }
      }, { once: true });

      return;
    }

    // ===== MOBILE + IPAD: giữ nguyên logic bay về góc trái =====
    const preloaderRect = preloaderLogo.getBoundingClientRect();

    let TARGET_LEFT, TARGET_TOP, TARGET_WIDTH;

    if (window.innerWidth >= 1024) {
      TARGET_LEFT = -5; TARGET_TOP = -10; TARGET_WIDTH = 90;
    } else if (window.innerWidth >= 768) {
      TARGET_LEFT = 0; TARGET_TOP = -10; TARGET_WIDTH = 90;
    } else {
      TARGET_LEFT = -20; TARGET_TOP = -10; TARGET_WIDTH = 78;
    }

    const translateX = TARGET_LEFT - preloaderRect.left;
    const translateY = TARGET_TOP - preloaderRect.top;

    preloaderLogo.style.transition = 'transform 0.8s ease, width 0.8s ease';
    preloaderLogo.style.transform = `translate(${translateX}px, ${translateY}px)`;
    preloaderLogo.style.width = TARGET_WIDTH + 'px';

    preloaderLogo.addEventListener('transitionend', (e) => {
      if (e.propertyName === 'transform') {
        // Ẩn ngay preloader (mobile/iPad vẫn giữ cách cũ, nếu muốn có thể đổi sang không fade tương tự desktop)
        preloader.style.background = 'transparent';
        preloader.style.pointerEvents = 'none';
        preloader.style.display = 'none';
      }
    }, { once: true });

  }, 1500);
});


document.addEventListener('DOMContentLoaded', function () {
  // Chỉ chạy code nếu tìm thấy form trên trang
  const scholarshipForm = document.querySelector('.wpcf7-form');
  if (!scholarshipForm) return;

  const steps = scholarshipForm.querySelectorAll('.form-step');
  const nextButtons = scholarshipForm.querySelectorAll('.btn-next');
  const prevButtons = scholarshipForm.querySelectorAll('.btn-prev');

  let currentStep = 1;

  function showStep(stepNumber) {
    steps.forEach(step => {
      step.style.display = 'none';
      step.classList.remove('active');
    });
    const activeStep = scholarshipForm.querySelector(`.form-step[data-step="${stepNumber}"]`);
    if (activeStep) {
      activeStep.style.display = 'block';
      activeStep.classList.add('active');
    }
  }

  nextButtons.forEach(button => {
    button.addEventListener('click', function () {
      // Đơn giản chỉ chuyển bước, không validation ở đây
      // CF7 sẽ validate khi submit cuối cùng
      if (currentStep < steps.length) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  prevButtons.forEach(button => {
    button.addEventListener('click', function () {
      if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  showStep(currentStep); // Hiển thị bước đầu tiên
});


$(document).ready(function ($) {
  // $(document).on('wpcf7submit', function (event) {
  //   // Lấy trạng thái từ chi tiết của sự kiện
  //   const status = event.detail.status;
  //   const successMsg = $('#successMsg');
  //   const errorMsg = $('#errorMsg');

  //   if (status === 'mail_sent') {
  //     errorMsg.hide();
  //     successMsg.show();
  //   } else {
  //     errorMsg.show();
  //   }
  // });

  const formSelector = '.wpcf7 form';

  // Khi user bắt đầu submit → disable nút
  $(document).on('wpcf7beforesubmit', function (event) {
    const $form = $(event.target).closest('form');
    $form.find('button[type="submit"], input[type="submit"]')
      .prop('disabled', true)
      .addClass('is-submitting');
  });

  // Khi server trả response (thành công hoặc thất bại) → enable lại nút
  $(document).on('wpcf7submit', function (event) {
    const $form = $(event.target).closest('form');
    $form.find('button[type="submit"], input[type="submit"]')
      .prop('disabled', false)
      .removeClass('is-submitting');

    const status = event.detail.status;
    const successMsg = $('#successMsg');
    const errorMsg = $('#errorMsg');

    if (status === 'mail_sent') {
      errorMsg.hide();
      successMsg.show();
    } else {
      errorMsg.show();
    }
  });

  // Mở hộp chọn file khi bấm "Select file"
  $(".file-btn").off('click').click(function () {
    $("#cv").click();
  });

  // Cập nhật tên file đã chọn
  $("#cv").change(function () {
    let file = this.files[0];
    if (file) {
      $("#file-name").text(file.name);
    } else {
      $("#file-name").text("No file selected");
    }
  });
});

$(document).ready(function ($) {
  var $duAn = $(".js-menu-du-an");
  var $linhVuc = $(".js-menu-linh-vuc");
  var currentUrl = window.location.href;

  // Khi click Dự án -> lưu flag
  $(document).on("click", ".js-menu-du-an > a", function () {
    sessionStorage.setItem("lastMenuClicked", "du-an");
  });

  // Khi click submenu trong Lĩnh vực -> lưu flag
  $(document).on("click", ".js-menu-linh-vuc .submenu a", function () {
    sessionStorage.setItem("lastMenuClicked", "linh-vuc");
  });

  // Nếu chưa có session (lần load đầu tiên) -> bỏ current-menu-ancestor
  var lastMenu = sessionStorage.getItem("lastMenuClicked");
  if (!lastMenu) {
    $linhVuc.removeClass("current-menu-ancestor");
  } else if (lastMenu === "du-an") {
    $linhVuc.removeClass("current-menu-ancestor");
  } else if (lastMenu === "linh-vuc") {
    $duAn.removeClass("current-menu-item current-menu-ancestor");
  }

  // Lấy tất cả link trong submenu Lĩnh vực
  $(".js-menu-linh-vuc .submenu a").each(function () {
    if (this.href === currentUrl) {
      var lastMenu = sessionStorage.getItem("lastMenuClicked");

      if (lastMenu === "du-an") {
        $linhVuc.removeClass("current-menu-ancestor");
      } else if (lastMenu === "linh-vuc") {
        $duAn.removeClass("current-menu-item");
        $duAn.removeClass("current-menu-ancestor");
      }
    }
  });
});


$(document).ready(function ($) {
  var $tabTitle = $("#tabTitle");
  $('#newsTabs .tab-button').on('shown.bs.tab', function (e) {
    var newTitle = $(e.target).data('title'); // Lấy giá trị từ data-title
    if (newTitle) {
      $tabTitle.text(newTitle);
    }
  });
});

// Giữ trạng thái tab khi reload trang tin tức phân trang
$(document).ready(function ($) {
  // Kiểm tra query active_tab
  const urlParams = new URLSearchParams(window.location.search);
  const activeTab = urlParams.get('active_tab');

  if (activeTab) {
    $('#newsTabs button[data-bs-target="#' + activeTab + '"]').tab('show');
    const title = $('#newsTabs button[data-bs-target="#' + activeTab + '"]').data('title');
    if (title) {
      $('#tabTitle').text(title);
    }
  }

  // Khi click tab, cập nhật query active_tab
  $('#newsTabs button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
    const target = $(e.target).data('bs-target').substring(1); // bỏ dấu #
    const url = new URL(window.location.href);
    url.searchParams.set('active_tab', target);
    history.replaceState(null, null, url.toString());
  });
});


//Lấy ngôn ngữ hiện tại và gán vào input hidden trong Contact Form 7
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form.wpcf7-form').forEach(function (form) {
    let lang = document.documentElement.lang || 'vi'; // <html lang="en"> hoặc "vi"
    let input = form.querySelector('input[name="current-lang"]');
    if (input) {
      input.value = lang;
    }
  });
});

// Bắt buộc checkbox đồng ý luôn được check và không thể bỏ
document.addEventListener('DOMContentLoaded', function () {
  let consent = document.querySelector('#consent');
  if (consent) {
    consent.checked = true;
    consent.addEventListener('click', function (e) {
      e.preventDefault(); // chặn bỏ check
    });
  }
});
document.addEventListener('DOMContentLoaded', function () {
  if (window.wpcf7) {
    wpcf7.validate = function () {
      return true;
    };
    wpcf7.validateForm = function () {
      return true;
    };
    wpcf7.validateInput = function () {
      return true;
    };

    if (wpcf7.validation) {
      wpcf7.validation = null;
    }
  }

  const forms = document.querySelectorAll('.wpcf7-form');
  forms.forEach(form => {
    form.querySelectorAll('input, textarea, select').forEach(el => {
      el.removeEventListener('blur', el._wpcf7_onchange, true);
      el.removeEventListener('change', el._wpcf7_onchange, true);
      el.removeEventListener('keyup', el._wpcf7_onchange, true);
      el.onblur = null;
      el.onchange = null;
      el.onkeyup = null;
    });
  });
});