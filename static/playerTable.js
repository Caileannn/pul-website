// static/scripts.js
let offset = 0;
const limit = 20;

async function loadPlayers() {
    try {
        var currentURL = window.location.pathname;
        console.log(currentURL)

        if(currentURL == '/'){
            const response = await fetch(`/api/players?offset=${offset}&limit=${limit}`);
            const players = await response.json();
            const playersList = document.getElementById('players-list');
            playersList.innerHTML = ''; // Clear the list before loading new players
            players.forEach((player, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'player-item';
                const rank = offset + index + 1;

                // Calculate win rate
                const totalMatches = player.winCount + player.lossCount;
                const winRate = totalMatches > 0 ? ((player.winCount / totalMatches) * 100).toFixed(2) : '0.00';

                listItem.innerHTML = `
                    <span class="player-rank">${rank}.</span>
                    <a class="player-name" href="/player/${player.playerID}">${player.discord_name}</a>
                    <span class="player-wr">${winRate}%</span>
                    <span class="player-wl">${player.winCount}W/${player.lossCount}L</span>
                    <span class="player-roles">${player.primaryRole}/${player.secondaryRole}</span>
                    <span class="player-lp">${player.hotstreak ? '🔥' : ''} ${player.leaderboardPoints} LP</span>
                `;
                playersList.appendChild(listItem);
            });
        }

        if(currentURL == '/bettyboard'){
            const response = await fetch(`/api/betties?offset=${offset}&limit=${limit}`);
            const players = await response.json();
            const playersList = document.getElementById('players-list');
            playersList.innerHTML = ''; // Clear the list before loading new players
            players.forEach((player, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'player-item';
                const rank = offset + index + 1;
                listItem.innerHTML = `
                    <span class="player-rank">${rank}.</span>
                    <a class="player-name" href="/player/${player.playerID}">${player.discord_name}</a>
                    <span class="player-lp">${player.bettingPoints} BP</span>
                `;
                playersList.appendChild(listItem);
        });
        }
        
        document.getElementById('prev-btn').disabled = offset === 0;

        document.getElementById('next-btn').disabled = players.length < limit;
    } catch (error) {
        console.error('Error loading players:', error);
    }
}

function nextPage() {
    offset += limit;
    loadPlayers();
}

function prevPage() {
    if (offset > 0) {
        offset -= limit;
        loadPlayers();
    }
}



document.addEventListener('DOMContentLoaded', () => {
    loadPlayers();

    document.getElementById('next-btn').addEventListener('click', nextPage);
    document.getElementById('prev-btn').addEventListener('click', prevPage);
});