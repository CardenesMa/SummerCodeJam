// class for storing states 
function states() {
    return {
        joinedLobby : false,
        gameStarted : false,
    }
}

document.addEventListener('alpine:init', () => {
    // initial states
    Alpine.store('states', states());

});