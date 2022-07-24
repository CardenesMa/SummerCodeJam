document.addEventListener('alpine:init', () => {
    Alpine.store('results', {
        sentences: [],
        prompt: "Snails are sometimes sad",
        init () {
            // TODO remove this, testing purposes 
            setTimeout(() => {
                console.log(this);
                this.sentences = this.sentences.concat(
                    [
                        {id: 0, 
                        text: "The snail crawls Slowly. Salted, his beloved was. Springtime arrives ne'r",
                        votes: 5,
                        user: "Jane"
                        },
                        {id: 1, 
                        text: "The snail could not find any yummy leaves.",
                        votes: 4,
                        user: "Jimmy"
                        },
                        {id: 2,
                        text: "I HATE snails.",
                        votes: 0,
                        user: "SnailHater9000"
                        }
                    ]
                )
            }, 1000)
        },
        sort_results: () => {
            this.sentences.sort((a, b) => {
                av = a.votes;
                bv = b.votes;
                return (av < bv) ? -1 : ((av > bv) ? 1: 0);
            })
        },
        addItemTest () {
            this.sentences.push({id: 3, text: "nah", user: "naysayer", votes: 0})
        }
    })
})


function sentenceTimerComponent(periodInMs) {
    return {
        period: periodInMs,
        start: Date.now(),
        current: 0,
        init() {
            console.log("init")
            setInterval(
                () => {
                    console.log("here")
                    this.current = Date.now() - this.start;
                    console.log(this.start)
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