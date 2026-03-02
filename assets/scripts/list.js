fetch("../resources/modes.json")
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById("modesContainer");

    data.forEach((mode, index) => {
      const card = document.createElement("div");
      card.innerHTML = `
        <div class="card mb-3 p-2 shadow-sm mx-auto">
          <div class="row g-0">
            <div class="col-md-4">
              <a href="https://www.youtube.com/watch?v=${mode.verifierLink}">
                <img 
                  src="https://img.youtube.com/vi/${mode.verifierLink}/maxresdefault.jpg" 
                  class="thumbnail img-fluid rounded h-100 object-fit-cover" 
                  alt="${mode.name}">
              </a>
            </div>

            <div class="col-md-8">
              <div class="card-body">
                <h5 class="card-title">
                  <span class="fw-bold">#${index+1}</span>
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

      container.appendChild(card);
    });
  })
  .catch(error => console.error("Error loading JSON:", error));