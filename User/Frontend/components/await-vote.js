document.addEventListener('alpine:init', () => {
    Alpine.store('voting', {
        votes: 0,
        members: 10,
        init() {
            setInterval(() => {
                this.votes += 1;
            }, 1000)
        },
    }
    )
})