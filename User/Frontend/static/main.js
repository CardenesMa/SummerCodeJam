// Contains code that is common across multiple components

// specify theme for tailwind use
tailwind.config = {
    theme: {
        extend: {
            colors: {
                linen: "#ffede1",
                ivory: "#f9fbf2",
                'light-cyan': "#d7f9ff",
                'baby-blue-eyes': "#afcbff",
                'oxford-blue': "#0e1c36",
            }
        }
    }
}


// initiate alpine data structures and callbacks after
// alpine is initiated (not to be confused with alpine:initalized)
document.addEventListener('alpine:init', () => {
    Alpine.store('lobby', {
        sentences: [
            { id: 0, text: "Hello there!", user: "Jimmy" },
            { id: 1, text: "Hello World!", user: "John" },
            { id: 2, text: "The snail eats the donut", user: "Jane" },
        ],
        users: ["Jimmy", "John", "Jane"]
    });

    setTimeout(() => {
        // testing if async update works well with alpine
        Alpine.store('lobby').users.push("Tim");
        Alpine.store('lobby').sentences.push({ id: 3, text: "Surprise sentence!", user: "Tim" });
    }, 1000);
})

function lobbyIdInp() {
    return {
        lobbyId : '',
        username : '',
        submit() {
            Alpine.store('lobbyId', this.lobbyId);
            Alpine.store('username', this.username);
            Alpine.store('states').joinedLobby = true;
        }
    }
}