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
                completed : true,  
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

    Alpine.store('prompt', {
        text : "Snails are sometimes sad",
        limit : 7 // secs given to write a sentecne for the prompt
    });

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

// timer for top loading bar
function timerComponent(periodInMs, callback) {
    return {
        period: periodInMs,
        start: Date.now(),
        current: 0,
        init() {
            console.log("init")
            var timerInt = setInterval(
                () => {
                    this.current = Date.now() - this.start;
                    if (this.current >= this.period) {
                        clearInterval(timerInt);
                        // when timer is done, call a function if provided
                        if (callback !== null) {
                            callback();
                        }

                    }
                }, 1000
            )
        },
        getProportion() {
            if (this.period === 0) return "100%";
            proportion = Math.round((this.current / this.period) * 100);
            if (proportion < 0) {proportion = 0}
            else if (proportion > 100) {proportion = 100}
            return String(proportion) + "%";
        }
    }
}

// callback function for when sentence input time is over
var promptLimitOver = () => {
    Alpine.store('states').timeOver = true;
}