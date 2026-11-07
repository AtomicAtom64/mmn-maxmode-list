const thumbnailSettings = [
    {
        key: "beatenmodes-thunbnails",
        checkboxId: "disable-beatenmodes-thumbnails"
    },
    {
        key: "leaderboard-thumbnails",
        checkboxId: "disable-leaderboard-thumbnails"
    }
];

thumbnailSettings.forEach(({ key, checkboxId }) => {
    const checkbox = document.getElementById(checkboxId);
    let savedValue = localStorage.getItem(key);

    if (savedValue === null) {
        savedValue = "false";
        localStorage.setItem(key, savedValue);
    }

    checkbox.checked = savedValue === "true";

    checkbox.addEventListener("change", () => {
        localStorage.setItem(key, String(checkbox.checked));
    });

});