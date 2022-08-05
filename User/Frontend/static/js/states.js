const ClientGUIStatesEnum = {
    homepage: "HomePage",
    joinedLobby: "JoinedLobby",
    submittingSenteces: "SubmittingSentences",
    awaitingSentences: "AwaitingSentences", // TODO possbily deprecate these states/screens
    voting: "Voting",
    awaitingVotes: "AwaitingVotes", // TODO possibly deprecate these states/screens
    voteResults: "VoteResults",
    gameResult: "GameResult",

    default(chosenName="", publicId="") {
        return {
            state: this.homepage,
            data: {
                hasChosenName: false
            },
            global: {
                chosenName: chosenName,
                publicId: publicId,
                awaiting_request: false,
                roundPrompt: "",
                roundNum: 0,
            },
            formatName(displayName, publicId) {
                return (publicId === this.global.publicId) ? displayName + " [You]" : displayName;
            }
        }
    }
}

const ClientGUILobbyDefaultState = {
    users: [],
    id: ""
}
