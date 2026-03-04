fetch("../resources/main_list.json")
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById("modesContainer");

    data.forEach((mode, index) => {
      const card = document.createElement("div");
      card.innerHTML = `
        <div class="card mb-3 p-2 shadow-sm mx-auto">
          <div class="row g-0">
            <div class="col-md-4">
              <a href="https://www.youtube.com/watch?v=${mode.verifierLink}" class="thumbnail-wrapper">
                <img 
                  class="thumbnail-img img-fluid rounded" 
                  alt="${mode.name}"
                >
              </a>
            </div>

            <div class="col-md-8">
              <div class="card-body">
                <h5 class="card-title">
                  <span class="fw-bold ranking">#${index+1}</span>
                  <a href="https://www.youtube.com/watch?v=${mode.verifierLink}">
                    ${mode.name}
                  </a>
                </h5>

                <p class="card-text text-muted">
                  <a href="${mode.gameLink}">${mode.game}</a>
                </p>

                <div class="text-body-secondary small">
                  <div>Developer: ${mode.developer}</div>
                  <div>Verifier: ${mode.verifier}</div>
                  <div>Length: ${mode.length}</div>
                </div>
              </div>
            </div>

          </div>
        </div>
      `;

      const img = card.querySelector(".thumbnail-img");
      setThumbnail(img, mode.verifierLink);

      container.appendChild(card);
    });
  })
  .catch(error => console.error("Error loading JSON:", error));

function setThumbnail(img, videoId) {
  const sources = [
    "maxresdefault.jpg",
    "sddefault.jpg",
    "hqdefault.jpg"
  ];

  let index = 0;

  function tryNext() {
    if (index >= sources.length) return;

    img.src = `https://img.youtube.com/vi/${videoId}/${sources[index]}`;
  }

  img.onload = function () {
    // Detect fake maxres placeholder
    if (img.naturalWidth <= 120 && index < sources.length - 1) {
      index++;
      tryNext();
    }
  };

  img.onerror = function () {
    index++;
    tryNext();
  };

  tryNext();
}

