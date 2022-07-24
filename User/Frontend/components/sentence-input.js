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