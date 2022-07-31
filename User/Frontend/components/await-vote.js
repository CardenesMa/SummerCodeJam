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