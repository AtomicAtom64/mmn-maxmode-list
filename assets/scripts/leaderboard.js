members = [];
const failedAvatars = new Set();
let currentType = "90/10";
let currentQuery = "";
let reverseOrder = false;

const scoring = {
    "OG": m => m.computedSkill,
    "100/0": m => m.total_skill_pt,
    "90/10": m => m.total_skill_pt * 0.9 + m.total_rng_pt * 0.1,
    "Total Modes": m => m.modes_beaten,
};

Promise.all([
    fetch("../resources/members.json").then(r => r.json()),
    fetch("../resources/countries.json").then(r => r.json())
]).then(([membersData, countryMapping]) => {

    members = membersData.map(m => ({
        ...m,
        computedSkill: getRecords(m.records),
        country_emoji: countryMapping[m.country] || ""
    }));

    members.sort((a, b) => b.computedSkill - a.computedSkill);

    updateLeaderboard();
});

function sorting(members, type){
    const score = scoring[type];
    members.sort((a, b) => score(b) - score(a));
}

function displayLeaderboard(members, type) {
    const container = document.getElementById("leaderboardContainer");

    container.innerHTML = members.map((m, index) => {

        let scoreText;

        if (type === "90/10") {
            scoreText = `
                <div class="text-end">
                    <div class="fw-bold text-primary fs-5">
                        ${(m.total_skill_pt * 0.9 + m.total_rng_pt * 0.1).toFixed(0)} Pts
                    </div>
                    <small class="text-muted">
                        ${m.total_skill_pt} Skill | ${m.total_rng_pt} RNG
                    </small>
                </div>
            `;
        } else if(type === "100/0") {
            scoreText = `
                <div class="fw-bold text-primary fs-5">
                    ${m.total_skill_pt} Pts
                </div>
            `;
        } else if(type === "Total Modes") {
            scoreText = `
                <div class="fw-bold text-primary fs-5">
                    ${m.modes_beaten} Modes
                </div>
            `;
        }
        else {
            scoreText = `
                <div class="fw-bold text-primary fs-5">
                    ${m.computedSkill} Pts
                </div>
            `;
        }

        const podiumClass =
        m.rank === 1 ? "rank-1" :
        m.rank === 2 ? "rank-2" :
        m.rank === 3 ? "rank-3" : "";

        const youtubeLink = m.youtube ? `
            <a href="${m.youtube}" target="_blank" class="text-decoration-none text-muted">
                <img
                    src="/assets/images/youtube.png"
                    alt="YouTube channel"
                    style="width: 1rem; height: 1rem; display: block;"
                >
            </a>
        ` : "";

        const countryEmoji = m.country_emoji ? `
            <span class="country-emoji" title="${m.country}">
                ${m.country_emoji}
            </span>
        ` : "";

        const profileLink = `<a href="https://allmodeslist.pages.dev/player?id=${m.id}" target="_blank" class="text-decoration-none text-dark">
                            <img 
                                src="/assets/images/aml.png"
                                alt="AML profile"
                                style="width: 1rem; height: 1rem; display: block;"
                            >
                        </a>`;

        return `
            <div class="list-group-item p-0 overflow-hidden">
                <div 
                    class="${podiumClass} d-flex align-items-center justify-content-between p-3 leaderboard-entry"
                    data-bs-toggle="collapse"
                    data-bs-target="#player-${m.id}"
                    role="button"
                >
                    <div class="d-flex align-items-center gap-3">
                        <span class="fw-bold fs-5 text-muted index">
                            #${m.rank}</span>
                        <img 
                            src="${getAvatar(m.id)}"
                            class="profile rounded-circle"
                            data-id="${m.id}"
                            alt="${m.name}"
                            onerror="handleAvatarError(this)"
                        >             
                        <div class="player-info">
                            <div class="fw-semibold player-name">
                                ${m.name}
                            </div>
                            <div class="d-flex align-items-center gap-1">
                                ${profileLink}
                                ${youtubeLink}
                                ${countryEmoji}
                            </div>
                        </div>
                    </div>

                    ${scoreText}
                </div>
                <div class="collapse" id="player-${m.id}">
                    <div class="player-details border-top p-3">
                        <div class="video-carousel d-flex gap-3 overflow-auto">
                            ${getWins(m.records)}
                        </div>
                    </div>
                </div>
            </div>
            `;
    }).join('');

    document.querySelectorAll(".video-thumbnail").forEach(img => {
        const videoId = getYoutubeVideoId(img.dataset.youtubeLink);
        setThumbnail(img, videoId);
    });
}

function getAvatar(id){
    if (failedAvatars.has(id)) {
        return "https://allmodeslist.pages.dev/defaultpfp.png";
    }

    return `https://zirlaiexwekjusbhjibc.supabase.co/storage/v1/object/public/avatars/${id}.jpg`;
}

function handleAvatarError(img) {
    const id = img.dataset.id;

    failedAvatars.add(id);

    img.onerror = null;
    img.src = "https://allmodeslist.pages.dev/defaultpfp.png";
}

function getWins(records) {
    let videos = [];

    for (const record of records) {
        videos.push(getVideoCard(record));
    }

    return videos.join('\n');
}

function getVideoCard(record) {
    return `<a 
                                class="video-card text-decoration-none"
                                href="${record.link}"
                                target="_blank"
                            >
                                <div class="thumbnail-wrapper">

                                    <img
                                        data-youtube-link="${record.link}"
                                        class="video-thumbnail"
                                        alt="Video thumbnail"
                                    >

                                </div>

                                <div class="video-title small text-muted mt-2">
                                    ${record.name} (Top ${record.top})
                                </div>
                            </a>`;
                        
}

function getRecords(records) {
    if (records.length === 0) return 0;

    let total = 0;

    for (const r of records) {
        if (r.skill_pt >= 100) {
            total += r.skill_pt;
        }
    }

    return total || records[0].skill_pt || 0;
}

const sortingButtons = document.getElementById("sortingButtons");
sortingButtons.addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;

    const buttons = sortingButtons.querySelectorAll("button");
    buttons.forEach(btn => btn.classList.remove("active"));
    e.target.classList.add("active");

    currentType = e.target.textContent;
    updateLeaderboard();
});

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

function getYoutubeVideoId(url) {
    try {
        const u = new URL(url);

        // https://www.youtube.com/watch?v=VIDEO_ID
        if (u.hostname.includes("youtube.com")) {
            return u.searchParams.get("v");
        }

        // https://youtu.be/VIDEO_ID
        if (u.hostname === "youtu.be") {
            return u.pathname.slice(1);
        }

        return null;
    } catch {
        return null;
    }
}

document.getElementById("nameInput").addEventListener("input", (e) => {
    currentQuery = e.target.value.toLowerCase();
    updateLeaderboard();
});

function updateLeaderboard() {
    const rankedMembers = [...members];

    sorting(rankedMembers, currentType);

    rankedMembers.forEach((member, index) => {
        member.rank = index + 1;
    });


    const filteredMembers = rankedMembers.filter(m =>
        m.name.toLowerCase().includes(currentQuery)
    );

    const displayedMembers = reverseOrder
        ? [...filteredMembers].reverse()
        : filteredMembers;

    displayLeaderboard(displayedMembers, currentType);
}

const icon = document.getElementById("sortIcon");

document.getElementById("reverseButton").addEventListener("click", () => {
    reverseOrder = !reverseOrder;

    icon.src = `/assets/images/sort-${reverseOrder ? "asc" : "desc"}-24.svg`;
    icon.alt = reverseOrder ? "Ascending order" : "Descending order";

    updateLeaderboard();
});