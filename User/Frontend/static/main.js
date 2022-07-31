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

function sentInp(clientManager) {
    return {
        sentence : '',
        submittedSent: '',

        submit() {
            // TODO: send sentence to server
            // for now just store in the user's class
            if (this.sentence.length == 0) {
                return;
            }
            // addSentence(Alpine.store('username'), this.sentence);
            clientManager.requestSendSentence(this.sentence);
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
        invFreq: 1000, // it's called period but we can't use that anymore :P
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
                }, this.invFreq
            )
        },
        getProportion() {
            if (this.period === 0) return "100%";
            const mod = this.invFreq * Math.min((this.current)/this.period, 1); // better for lower time periods
            proportion = Math.round(((this.current + mod) / this.period) * 100);
            if (proportion < 0) {proportion = 0}
            else if (proportion > 100) {proportion = 100}
            return String(proportion) + "%";
        }
    }
}

function sendVote(manager, id) {
    manager.requestVote(id);
}
