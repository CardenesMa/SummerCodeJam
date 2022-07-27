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
        users: [
            {
                name : "marcoiguess",
                completed : false,  
           },
            {
                name : "Harsha",
                completed : false,  
           },
            {
                name : "CupoGeo",
                completed : false,  
           },
            {
                name : "Lancelot",
                completed : false,  
           },
        ],
    });

    Alpine.store('prompt', "Snails are sometimes sad");

    setTimeout(() => {
        // testing if async update works well with alpine
        Alpine.store('lobby').users.push({
            name : "Tim",
            completed : false
        });
    }, 3000);
})

function lobbyIdInp() {
    return {
        lobbyId : '',
        username : '',
        submit() {

            Alpine.store('lobbyId', this.lobbyId);
            Alpine.store('username', this.username);
            Alpine.store('states').joinedLobby = true;
            Alpine.store("lobby").users.push({
                name: this.username,
                completed: false
            });
        }
    }
}

// Timer for sentence input
function timer(timeLimit) {
    return {
        timeLimit : timeLimit,
        init() {
            var timeInterval = setInterval(() => 
            {
                this.timeLimit--;
                if (this.timeLimit < 0) {
                    this.timeLimit = "Time is up!";
                    clearInterval(timeInterval)
                }
            }, 1000)
        }
    }
} 