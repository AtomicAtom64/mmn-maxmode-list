members = [];

fetch("../resources/members.json")
    .then(response => response.json())
    .then(data => {

        const members = data.map(m => ({
            ...m,
            computedSkill: getRecords(m.records)
        }));

        members.sort((a, b) => b.computedSkill - a.computedSkill);

        const container = document.getElementById("leaderboardContainer");

        container.innerHTML = members.map((m, index) => `
            <div class="list-group-item d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center gap-3">
                    <span class="fw-bold fs-5 text-muted" style="width:40px">
                        #${index + 1}
                    </span>
                    <img 
                        src="${getAvatar(m.id)}"
                        class="profile rounded-circle"
                        alt="${m.name}"
                        onerror="handleAvatarError(this)"
                    >
                    <div>
                        <div class="fw-semibold">${m.name}</div>
                        <small class="text-muted">
                            Hardest: ${getHardest(m.records)}
                        </small>
                    </div>
                </div>
                <div class="fw-bold text-primary fs-5">
                    ${m.computedSkill} Pts
                </div>
            </div>
        `).join('');
    });

function getAvatar(id){
    return `https://zirlaiexwekjusbhjibc.supabase.co/storage/v1/object/public/avatars/${id}.jpg`;
}

function handleAvatarError(img) {
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