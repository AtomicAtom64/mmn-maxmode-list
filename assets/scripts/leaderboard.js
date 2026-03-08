members = [];
const failedAvatars = new Set();
const scoring = {
    "OG": m => m.computedSkill,
    "100/0": m => m.total_skill_pt,
    "90/10": m => m.total_skill_pt * 0.9 + m.total_rng_pt * 0.1,
    "Modes": m => m.records.length
};

fetch("../resources/members.json")
    .then(response => response.json())
    .then(data => {

        members = data.map(m => ({
            ...m,
            computedSkill: getRecords(m.records),
        }));

        members.sort((a, b) => b.computedSkill - a.computedSkill);

        displayLeaderboard(members, "OG");
    });

function sorting(members, type){
    const score = scoring[type];
    members.sort((a, b) => score(b) - score(a));
}

function displayLeaderboard(members, type) {
    sorting(members, type);
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
        } else if(type === "Modes") {
            scoreText = `
                <div class="fw-bold text-primary fs-5">
                    ${m.records.length} Modes
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

        return `
        <div class="list-group-item d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
                <span class="fw-bold fs-5 text-muted index">
                    #${index + 1}
                </span>
                <img 
                    src="${getAvatar(m.id)}"
                    class="profile rounded-circle"
                    data-id="${m.id}"
                    alt="${m.name}"
                    onerror="handleAvatarError(this)"
                >
                <div class="player-info">
                    <div class="fw-semibold">${m.name}</div>
                    <small class="text-muted hardest">
                        Hardest: ${getHardest(m.records)}
                    </small>
                </div>
            </div>

            ${scoreText}

        </div>
        `;
    }).join('');
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

function getHardest(records) {
    if (records.length === 0) return "N/A";

    let hardest = records[0];
    return `
        <a href="${hardest.youtube_link}" target="_blank" class="text-decoration-none">
            ${hardest.mode_name} (${hardest.mode_skill_pt} Pts)
        </a>
    `;

}

function getRecords(records) {
    if (records.length === 0) return 0;

    let total = 0;

    for (const r of records) {
        if (r.mode_skill_pt >= 100) {
            total += r.mode_skill_pt;
        }
    }

    return total || records[0].mode_skill_pt || 0;
}

const sortingButtons = document.getElementById("sortingButtons");
sortingButtons.addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;

    const buttons = sortingButtons.querySelectorAll("button");
    buttons.forEach(btn => btn.classList.remove("active"));
    e.target.classList.add("active");

    const type = e.target.textContent;
    displayLeaderboard(members, type);
});