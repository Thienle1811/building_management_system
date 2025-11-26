window.addEventListener("load", () => {
  const input = document.getElementById("custom-search-input");
  const resultsBox = document.getElementById("custom-search-results");

  if (input && resultsBox) {
    let timeout = null;

    input.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(triggerSearch, 300);
    });

    // Bắt phím Enter để đi đến search.php
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault(); // ngăn reload mặc định
        const keyword = input.value.trim();
        if (keyword.length > 0) {
          // chuyển đến trang search.php của WP
          window.location.href = `${smartSearch.home_url}?s=${encodeURIComponent(keyword)}`;
        }
      }
    });

    function triggerSearch() {
      const keyword = input.value.trim();
      if (keyword.length < 2) {
        resultsBox.innerHTML = "";
        return;
      }
      const lang = smartSearch.lang || 'vi';
      fetch(`${smartSearch.api_url}smart-search/v1/search?keyword=${encodeURIComponent(keyword)}&lang=${lang}`)
        .then(res => res.json())
        .then(data => {
          resultsBox.innerHTML = "";
          if (data.length === 0) {
            resultsBox.innerHTML = "<div class='custom-search-item'>🔍 <span>No results found</span></div>";
            return;
          }

          const regex = new RegExp(`(${keyword})`, "gi");

          data.forEach(post => {
            const item = document.createElement("div");
            item.className = "custom-search-item";
            const highlighted = post.post_title.replace(regex, "<strong>$1</strong>");
            item.innerHTML = `🔍 <span>${highlighted}</span>`;
            item.onclick = () => window.location.href = post.permalink;
            resultsBox.appendChild(item);
          });
        });
    }
  }
});
