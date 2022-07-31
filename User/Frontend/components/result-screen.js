tailwind.config = {
    theme: {
        extend: {
            colors: {
                linen: "#ffede1",
                ivory: "#f9fbf2",
                'light-cyan': "#d7f9ff",
                'baby-blue-eyes': "#afcbff",
                'oxford-blue': "#0e1c36",
            },
            transitionProperty: {
                'timer-width': 'width'
            }
        }
    }
}
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
