// class for storing states 
function states() {
    return {
        joinedLobby : false
    }
}

document.addEventListener('alpine:init', () => {
    // initial states
    Alpine.store('states', states());

});