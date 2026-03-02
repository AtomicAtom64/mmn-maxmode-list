const clan_id = "1a68233f-ae59-431b-ba1b-e458b548acfa";

class Member {
    constructor(user_id, name = null, total_skill_points = 0, modes = []) {
        this.user_id = user_id;
        this.name = name;
        this.total_skill_points = total_skill_points;
        this.modes = modes;
    }
}

async function loadClanMembers() {
    try {
        const response = await fetch(`https://aml-api-eta.vercel.app/clans/${clan_id}/members`);
        const clanMembers = await response.json();

        const memberIds = clanMembers.map(m => m.user_id);

        const memberPromises = memberIds.map(async (id) => {
            const res = await fetch(`https://aml-api-eta.vercel.app/player/${id}`);
            const data = await res.json();

            return new Member(
                id,
                data.name,
                data.totalSkillpt,
                data.modes
            );
        });

        const members = await Promise.all(memberPromises);

        console.log(members);
        return members;

    } catch (error) {
        console.error("Error loading clan members:", error);
    }
}

loadClanMembers().then(members => {
    const container = document.getElementById("leaderboardContainer");
    container.innerHTML = members.map(m => `<div>${m.name}: ${m.total_skill_points} skill points</div>`).join('');
});