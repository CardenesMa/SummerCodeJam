// class for storing states 
function states() {
    return {
        joinedLobby : false,
        gameStarted : false,
        submittedSentence : false,
        timeOver : false,
    }
}

document.addEventListener('alpine:init', () => {
    // initial states
    Alpine.store('states', states());

});