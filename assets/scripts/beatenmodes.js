class Mode {
    constructor(name, game, skill, rng, Records, hardest) {
        this.name = name;
        this.game = game;
        this.skill = skill;
        this.rng = rng;
        this.Records = Records;
        this.hardest = hardest;
    }
}

class Record {
    constructor(playerName, link, time){
        this.playerName = playerName;
        this.link = link;
        this.time = time;
    }
}

const modes = [];
const modesMap = new Map();

let currentFilter = "Hardests only";
let currentSort = "90/10";
let currentQuery = "";

let modeResults = [];

fetch("../resources/beaten_modes.json")
    .then(r => r.json())
    .then(beatenModesData => {

        beatenModesData.forEach(modeData => {

            modeData.records.forEach((record, index) => {

                const hardest = index === 0;

                let mode = modesMap.get(record.name);

                if (!mode) {
                    mode = new Mode(
                        record.name,
                        record.game,
                        record.skill,
                        record.rng,
                        [],
                        hardest
                    );

                    modes.push(mode);
                    modesMap.set(record.name, mode);

                } else if (hardest) {
                    mode.hardest = true;
                }

                const playerRecord = new Record(
                    modeData.name,
                    record.link,
                    record.time
                );

                mode.Records.push(playerRecord);
            });
        });

        modes.forEach(mode => {
            mode.Records.sort((a, b) => a.time - b.time);
        });

        updateModes();
    });

function updateModes() {

    // Start with all modes
    let results = [...modes];

    // Filter hardest modes
    if (currentFilter === "Hardests only") {
        results = results.filter(mode => mode.hardest === true);
    }

    // Sort by selected scoring method
    results.sort((a, b) => {

        if (currentSort === "Skill") {
            return b.skill - a.skill;
        }

        if (currentSort === "RNG") {
            return b.rng - a.rng;
        }

        if (currentSort === "90/10") {
            const scoreA = a.skill * 0.9 + a.rng * 0.1;
            const scoreB = b.skill * 0.9 + b.rng * 0.1;

            return scoreB - scoreA;
        }

        return 0;
    });

    // Save the ranking BEFORE searching
    const rankedResults = results.map((mode, index) => ({
        mode: mode,
        rank: index + 1
    }));

    // Search without changing the ranking
    if (currentQuery.trim() !== "") {
        const query = currentQuery.toLowerCase();

        modeResults = rankedResults.filter(item =>
            item.mode.name.toLowerCase().includes(query)
        );
    } else {
        modeResults = rankedResults;
    }

    renderModes();
}

function renderModes() {

    const container = document.getElementById("modesContainer");

    container.innerHTML = modeResults
        .map(item => createModeCard(item.mode, item.rank).outerHTML)
        .join("");

    // Set thumbnails AFTER the entire list has been rendered
    const images = container.querySelectorAll("[data-youtube-link]");

    images.forEach(img => {
        setThumbnail(img, img.dataset.youtubeLink);
    });
}

const filter = document.getElementById("filter");

filter.addEventListener("click", e => {

    if (e.target.tagName !== "BUTTON") return;

    filter.querySelectorAll("button").forEach(btn => {
        btn.classList.remove("active");
    });

    e.target.classList.add("active");

    currentFilter = e.target.textContent.trim();

    updateModes();
});

const sort = document.getElementById("sort");

sort.addEventListener("click", e => {

    if (e.target.tagName !== "BUTTON") return;

    sort.querySelectorAll("button").forEach(btn => {
        btn.classList.remove("active");
    });

    e.target.classList.add("active");

    currentSort = e.target.textContent.trim();

    updateModes();
});

const nameInput = document.getElementById("nameInput");

nameInput.addEventListener("input", e => {

    currentQuery = e.target.value;

    updateModes();
});

function createModeCard(mode, rank) {

    const card = document.createElement("div");
    const firstRecord = mode.Records[0];

    card.innerHTML = `
        <div class="card mb-3 p-2 shadow-sm mx-auto">

            <div class="row g-0">

                <div class="col-md-4">

                    <a
                        href="${firstRecord.link}"
                        target="_blank"
                        class="thumbnail-wrapper"
                    >
                        <img
                            data-youtube-link="${firstRecord.link}"
                            class="thumbnail-img img-fluid rounded"
                            alt="${mode.name}"
                        >
                    </a>

                </div>

                <div class="col-md-8">

                    <div class="card-body">

                        <h5 class="card-title">

                            <span class="fw-bold ranking">
                                #${rank}
                            </span>

                            <a
                                href="${firstRecord.link}"
                                target="_blank"
                            >
                                ${mode.name}
                            </a>

                        </h5>

                        <p class="card-text text-muted">
                            ${mode.game}
                        </p>

                        <div class="text-body-secondary small">
                            <div>Skill Points: ${mode.skill}</div>
                            <div>RNG Points: ${mode.rng}</div>
                            <div>First beaten by: ${firstRecord.playerName}</div>
                        </div>

                    </div>

                </div>

            </div>

            <div class="collapse records" id="records-${rank}">

                <div class="player-details border-top p-3">

                    <div class="records-list">
                        ${getWins(mode.Records)}
                    </div>

                </div>

            </div>

            <button
                class="btn btn-sm btn-outline-secondary mt-2"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#records-${rank}"
                aria-expanded="false"
                aria-controls="records-${rank}"
            >
                Show Records
            </button>

        </div>
    `;

    return card;
}

function getWins(records) {
    return records.map(record => `
        <div class="record-item d-flex justify-content-between align-items-center border-bottom py-2">
            <div class="record-player">
                <span class="fw-medium">${record.playerName}</span>
                <span class="text-muted small">(${formatDate(record.time)})</span>
            </div>

            <a
                href="${record.link}"
                target="_blank"
                class="btn btn-sm btn-outline-secondary"
            >
                View Record
            </a>
        </div>
    `).join("\n");
}

function formatDate(date) {
    return new Date(date).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}

function setThumbnail(img, videoLink) {
    const videoId = extractVideoId(videoLink);

    if (!videoId) {
        console.error("Invalid YouTube link:", videoLink);
        return;
    }

    const sources = [
        "maxresdefault.jpg",
        "hqdefault.jpg",
        "mqdefault.jpg"
    ];

    let index = 0;

    function tryNext() {
        if (index >= sources.length) {
            console.error("No valid thumbnail found:", videoId);
            return;
        }

        const source = sources[index];
        const url = `https://img.youtube.com/vi/${videoId}/${source}`;

        const testImage = new Image();

        testImage.onload = function () {
            if (testImage.naturalWidth <= 120) {
                index++;
                tryNext();
                return;
            }

            img.src = url;
        };

        testImage.onerror = function () {
            index++;
            tryNext();
        };

        testImage.src = url;
    }

    tryNext();
}

function extractVideoId(videoLink) {
    const url = new URL(videoLink);

    if (url.hostname === "youtu.be") {
        return url.pathname.substring(1);
    }

    if (
        url.hostname === "www.youtube.com" ||
        url.hostname === "youtube.com" ||
        url.hostname === "m.youtube.com"
    ) {
        if (url.pathname.startsWith("/live/")) {
            return url.pathname.substring("/live/".length);
        }

        return url.searchParams.get("v");
    }

    return null;
}