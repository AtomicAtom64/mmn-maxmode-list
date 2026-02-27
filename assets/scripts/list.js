fetch("../resources/modes.json")
  .then(response => response.json())
  .then(data => {
    const listElement = document.querySelector("main ol");
    data.forEach(mode => {
      const listItem = document.createElement("li");
      listItem.textContent = `${mode.name} - ${mode.game}`;
      listElement.appendChild(listItem);
    });
  })
  .catch(error => console.error("Error loading JSON:", error));