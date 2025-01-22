async function searchPlayers(query) {
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        const searchResults = document.getElementById('search-results');
        searchResults.innerHTML = ''; // Clear previous results
    
        if (results.length === 0) {
            searchResults.classList.add('hidden');
        } else {
            searchResults.classList.remove('hidden');
            results.forEach(player => {
                const listItem = document.createElement('div');
                listItem.className = 'search-item';
                listItem.innerHTML = `<a href="/player/${player.playerID}" target="_blank">${player.discord_name}</a>`;
                searchResults.appendChild(listItem);
            });
        }
    } catch (error) {
        console.error('Error searching players:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (event) => {
        const query = event.target.value;
        const searchResults = document.getElementById('search-results');
        if (query.length > 0) {
            searchPlayers(query);
        } else {
            searchResults.innerHTML = '';
            searchResults.classList.add('hidden'); // Hide the search results box
        }
    });
});