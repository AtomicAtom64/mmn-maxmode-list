fetch("../resources/modes.json")
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById("modesContainer");

    data.forEach((mode, index) => {
      const card = document.createElement("div");
      card.className = "card mb-3 p-3 shadow-sm";

      card.innerHTML = `
        <div class="card">
          <div class="row g-0">
            <div class="col-md-4">
            <a href="https://www.youtube.com/watch?v=${mode.verifierLink}">
              <img src="https://img.youtube.com/vi/${mode.verifierLink}/maxresdefault.jpg" class="img-fluid rounded-start" alt="...">
            </a>
            </div>
            <div class="">
              <div class="card-body">
                <h5 class="card-title">
                  <span id="ranking">#${index+1} </span>
                  <a href="https://www.youtube.com/watch?v=${mode.verifierLink}">${mode.name}</a>
                </h5>
                <p class="card-text text-muted">
                  <a href="${mode.gameLink}">${mode.game}</a>
                </p>
                <p class="card-text"><small class="text-body-secondary">Developer: ${mode.developer}</small></p>
                <p class="card-text"><small class="text-body-secondary">Verifier: ${mode.verifier}</small></p>
                <p class="card-text"><small class="text-body-secondary">Length: ${mode.length}</small></p>
              </div>
            </div>
          </div>
        </div>
      `;

      container.appendChild(card);
    });
  })
  .catch(error => console.error("Error loading JSON:", error));