// Contains code that is common across multiple components

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