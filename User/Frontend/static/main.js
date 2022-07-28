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
                sentence : "The snail crawls Slowly. Salted, his beloved was. Springtime arrives ne'r",
                votes : 3,
           },
            {
                name : "Harsha",
                completed : true,  
                sentence: "The snail could not find any yummy leaves.",
                votes : 3,
           },
            {
                name : "CupoGeo",
                completed : false,  
                sentence: "I HATE snails.",
                votes : 2,
           },
            {
                name : "Lancelot",
                completed : false,  
                sentence: null,
                votes : 0,
           },
        ],
    });

    Alpine.store('prompt', {
        text : "Snails are sometimes sad",
        limit : 4 // secs given to write a sentecne for the prompt
    });
    Alpine.store('votingTime', 2000);

    setTimeout(() => {
        // testing if async update works well with alpine
        Alpine.store('lobby').users.push({
            name : "Tim",
            completed : true,
            sentence: null,
            votes : 0,
        });
    }, 3000);
});

function addSentence(user, sentence) {
    // Go through the users list and update the user.sentence and user.completed vars
    Alpine.store('lobby').users.forEach((i) => {
        // this is the user passed through as an arg
        if (i.name === user) {
            i.sentence = sentence;
            i.completed = true;
            return;
        }
    });
}

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
                completed: false,
                sentence : '',
                votes : 1,
            });
        }
    }
}

function sentInp() {
    return {
        sentence : '',
        submittedSent: '',

        submit() {
            // TODO: send sentence to server 
            // for now just store in the user's class
            if (this.sentence.length == 0) {
                return;
            }
            addSentence(Alpine.store('username'), this.sentence);
            Alpine.store("states").submittedSentence = true;
            this.submittedSent = this.sentence;
            // clear input
            this.sentence = '';
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
            var timerInt = setInterval(
                () => {
                    this.current = Date.now() - this.start;
                    if (this.current >= this.period) {
                        clearInterval(timerInt);
                        // when timer is done, call a function if provided
                        if (callback !== undefined) {
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

function sendVote(id) {
    // TODO: send vote
    Alpine.store('states').voted = true;
}

// return getter 'sentences' which stores list of sorted sentences after voting is done
var sortedSentences = () => {
    return {
        get sentences() {
            return Alpine.store('lobby').users.sort((a, b) => {
            av = a.votes;
            bv = b.votes;
            return (av < bv) ? -1 : ((av > bv) ? 1: 0);

            }, ).reverse()
        } 
    }
}

// callback function for when sentence input time is over
var promptLimitOver = () => {
    Alpine.store('states').awaitingSentences = false;
}

// callback for voting
var votingTimeOver = () => {
    Alpine.store('states').awaitingVotes = false;
}