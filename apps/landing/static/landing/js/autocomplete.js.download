jQuery(document).ready(function ($) {

  // --- Các biến và selectors chung ---
  const $searchForm = $('.js-search-form'); // Form tìm kiếm chính
  const $searchInput = $searchForm.find('.search-input'); // Ô input tìm kiếm
  const $autocompleteList = $('.autocomplete'); // Danh sách gợi ý autocomplete

  const $ajaxSearchResultsContainer = $('#ajax-search-results'); // Container hiển thị kết quả tìm kiếm
  const $resultsList = $('#results-list'); // Danh sách bài viết trong kết quả
  const $searchResultTitle = $('.search-results-title'); // Tiêu đề kết quả tìm kiếm
  const $ajaxPageInfo = $('.ajax-pagination-controls .ajax-page-info'); // Thông tin trang
  const $prevPageBtn = $('.ajax-pagination-controls .prev-page'); // Nút phân trang trước
  const $nextPageBtn = $('.ajax-pagination-controls .next-page'); // Nút phân trang sau
  const $googleSearchButtonContainer = $('.google-search-button-container'); // Container cho nút Google Search


  let typingTimer; // Timer để trì hoãn request AJAX cho autocomplete
  const doneTypingInterval = 300; // Thời gian trì hoãn (ms)

  let currentSearchPage = 1; // Trang hiện tại cho kết quả tìm kiếm
  let currentSearchTerm = ''; // Từ khóa tìm kiếm hiện tại
  let totalSearchPages = 0; // Tổng số trang cho kết quả tìm kiếm

  // --- Autocomplete Logic ---

  // Ẩn danh sách autocomplete khi click ra ngoài vùng search-container
  $(document).on('click', function (e) {
    if (!$(e.target).closest('.search-container').length) {
      $autocompleteList.hide().empty();
    }
  });

  // Gán sự kiện click cho các LI trong autocomplete bằng Event Delegation
  $autocompleteList.on('click', 'li', function () {
    const selectedValue = $(this).data('value');
    $searchInput.val(selectedValue); // Điền giá trị đã chọn vào input
    $searchForm.submit();

    $autocompleteList.hide().empty(); // Ẩn danh sách autocomplete

    // // Khi chọn từ autocomplete, thực hiện tìm kiếm ngay lập tức
    // currentSearchTerm = selectedValue; // Cập nhật từ khóa tìm kiếm hiện tại
    // currentSearchPage = 1; // Luôn về trang 1 khi tìm kiếm mới
    // fetchSearchResults(currentSearchTerm, currentSearchPage); // Gọi hàm tìm kiếm
  });

  // Khi gõ phím trong input thì thêm/bỏ class focus-key
  $searchInput.on('input', function () {
    const $searchButton = $searchForm.find('.search-button');
    const $searchInput = $searchForm.find('.search-input');
    if ($(this).val().trim().length > 0) {
      $searchButton.addClass('focus-key');
      $searchInput.addClass('value-input');
    } else {
      $searchButton.removeClass('focus-key');
      $searchInput.removeClass('value-input');
    }
  });

  const currentLang = autocomplete.lang || 'vi';

  // helper: escape HTML để tránh XSS
  function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // helper: escape regex chars trong query
  function escapeForRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Xử lý sự kiện gõ phím trên ô tìm kiếm cho autocomplete
  $searchInput.on('keyup', function () {
    const $currentInput = $(this);
    const $autocompleteList = $currentInput.closest('.search-container').find('.autocomplete');
    if (!$autocompleteList.length) {
      return;
    }
    clearTimeout(typingTimer); // Xóa timer cũ nếu người dùng vẫn đang gõ
    const query = $currentInput.val();

    if (query.length < 2) { // Chỉ gợi ý khi độ dài từ khóa >= 2 ký tự
      $autocompleteList.hide().empty(); // Ẩn và xóa danh sách nếu quá ngắn
      return;
    }

    // giới hạn tối đa ký tự client-side để giảm load và attack surface
    if (query.length > 100) {
      return;
    }

    typingTimer = setTimeout(function () {
      const encodedTerm = encodeURIComponent(query);
      const encodedLang = encodeURIComponent(currentLang);
      // Gửi AJAX request để lấy gợi ý từ khóa
      fetch(`${autocomplete.rest_url}nlg/v1/autocomplete-keywords?term=${encodedTerm}&lang=${encodedLang}`)
        .then(res => {
          if (!res.ok) throw new Error('Network response was not ok');
          return res.json();
        })
        .then(response => {
          $autocompleteList.empty();

          if (!Array.isArray(response) || response.length === 0) {
            $autocompleteList.hide().empty();
            return;
          }

          const currentQuery = $currentInput.val() || '';
          const safeRegexPart = escapeForRegex(currentQuery.trim());
          const regex = safeRegexPart ? new RegExp(safeRegexPart, 'gi') : null;

          response.forEach(function (item) {
            const rawLabel = item && item.label ? String(item.label) : '';
            const rawValue = item && item.value ? String(item.value) : '';

            // Escape toàn bộ label trước
            let safeLabel = escapeHtml(rawLabel);

            // Nếu có query, highlight bằng cách thay text đã escape (vẫn an toàn)
            if (regex) {
              safeLabel = safeLabel.replace(regex, function (match) {
                return '<span class="autocomplete-highlight">' + escapeHtml(match) + '</span>';
              });
            }

            // Tạo list item. Dùng attr để lưu value (ID hoặc string)
            const listItem = $('<li></li>')
              .html(safeLabel)
              .attr('data-value', rawValue);

            $autocompleteList.append(listItem);
          });

          $autocompleteList.show();
        })
        .catch(error => {
          console.error('REST API autocomplete error:', error);
          $autocompleteList.hide().empty();
        });

    }, doneTypingInterval); // Trì hoãn gửi request
  });

  // --- Search Results Logic ---

  // Hàm lấy và hiển thị kết quả tìm kiếm
  function fetchSearchResults(searchTerm, page) {
    $resultsList.html('<p>Đang tải kết quả...</p>');
    $ajaxSearchResultsContainer.show();
    $('.ajax-pagination-controls button').prop('disabled', true);
    $googleSearchButtonContainer.empty().hide();

    const restUrl = autocomplete.rest_url + 'nlg/v1/search-posts'; // Sử dụng REST API URL

    $.ajax({
      url: restUrl,
      method: 'GET',
      data: {
        s: searchTerm,
        paged: page,
        lang: currentLang
      },
      dataType: 'json',
      success: function (response) {
        let resultsHtml = '';
        if (response.posts && response.posts.length > 0) {
          response.posts.forEach(function (post) {
            const thumbnailUrl = post.thumbnail
              ? `<img src="${post.thumbnail}" alt="${post.title}" style="max-width: 100px; height: auto; margin-right: 10px;">`
              : '';
            resultsHtml += `
            <div class="search-result-item" style="display: flex; align-items: flex-start; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #eee;">
              ${thumbnailUrl}
              <div>
                <h4><a href="${post.permalink}" target="_blank">${post.title}</a></h4>
                <p style="font-size: 0.9em; color: #666;">${post.excerpt}</p>
              </div>
            </div>
          `;
          });
        } else {
          resultsHtml = `<p>Không tìm thấy kết quả nào cho "${searchTerm}".</p>`;
        }

        $resultsList.html(resultsHtml);

        currentSearchPage = response.current_page;
        totalSearchPages = response.max_pages;

        $searchResultTitle.text(`Có ${response.total_posts} kết quả với từ khóa "${searchTerm}"`);
        $ajaxPageInfo.text(`Trang ${currentSearchPage} / ${totalSearchPages || 1}`);

        $prevPageBtn.prop('disabled', currentSearchPage === 1);
        $nextPageBtn.prop('disabled', currentSearchPage === totalSearchPages || totalSearchPages === 0);

        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchTerm)}`;
        const googleButtonHtml = `
        <button class="google-search-btn" style="
          margin-top: 20px;
          padding: 10px 20px;
          background-color: #4285F4;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          font-size: 1em;
          display: block;
          width: fit-content;
          margin-left: auto;
          margin-right: auto;
        ">
          Tìm kiếm "${searchTerm}" trên Google
        </button>
      `;
        $googleSearchButtonContainer.html(googleButtonHtml).show();
        $googleSearchButtonContainer.find('.google-search-btn').on('click', function () {
          window.open(googleSearchUrl, '_blank');
        });

        $('html, body').animate({
          scrollTop: $ajaxSearchResultsContainer.offset().top - 50
        }, 500);
      },
      error: function (xhr, status, error) {
        console.error('Lỗi AJAX tìm kiếm:', status, error);
        $resultsList.html('<p>Có lỗi xảy ra khi tải kết quả tìm kiếm.</p>');
        $ajaxSearchResultsContainer.show();
        $('.ajax-pagination-controls button').prop('disabled', true);
        $googleSearchButtonContainer.empty().hide();
      }
    });
  }


  // Xử lý sự kiện submit form tìm kiếm
  // $searchForm.on('submit', function(e) {
  //     e.preventDefault(); // Ngăn form submit mặc định (chuyển trang)
  //     currentSearchTerm = $searchInput.val().trim(); // Lấy từ khóa từ input
  //     currentSearchPage = 1; // Luôn về trang 1 khi bắt đầu tìm kiếm mới
  //     $autocompleteList.hide().empty(); // Ẩn danh sách autocomplete khi submit form
  //     fetchSearchResults(currentSearchTerm, currentSearchPage); // Gọi hàm tìm kiếm
  // });

  // Xử lý click nút phân trang (prev/next) cho kết quả tìm kiếm
  // $prevPageBtn.on('click', function() {
  //     if (currentSearchPage > 1) {
  //         fetchSearchResults(currentSearchTerm, currentSearchPage - 1);
  //     }
  // });

  // $nextPageBtn.on('click', function() {
  //     if (currentSearchPage < totalSearchPages) {
  //         fetchSearchResults(currentSearchTerm, currentSearchPage + 1);
  //     }
  // });

  // --- Xử lý khi trang tải lần đầu ---
  // Kiểm tra nếu có từ khóa tìm kiếm trong URL (ví dụ: từ lần tải trang trước hoặc từ link chia sẻ)
  const urlParams = new URLSearchParams(window.location.search);
  const initialSearchTerm = urlParams.get('s');
  if (initialSearchTerm) {
    $searchInput.val(initialSearchTerm); // Điền từ khóa vào ô input
    currentSearchTerm = initialSearchTerm; // Cập nhật từ khóa hiện tại
    // fetchSearchResults(currentSearchTerm, 1); // Tải kết quả cho từ khóa đó (trang 1)
  }
});
