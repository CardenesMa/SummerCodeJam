function timerComponent(periodInMs) {
    return {
        period: periodInMs,
        start: Date.now(),
        current: 0,
        init() {
            console.log("init")
            setInterval(
                () => {
                    this.current = Date.now() - this.start;
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