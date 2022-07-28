// class for storing states 
function states() {
    return {
        joinedLobby : false,
        gameStarted : false,
        submittedSentence : false,
        awaitingSentences : true,
        voted : false,
        awaitingVotes : true,
    }
}

document.addEventListener('alpine:init', () => {
    // initial states
    Alpine.store('states', states());

});