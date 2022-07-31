const WSPORT = ":10000";
const PROTOCOL = "ws://"
const PATH = "/ws"



class ClientComms {


    /**
     *
     * @param {(event) -> ()} openCallback callback function to be called when a websocket server connection is established
     * @param {(event) -> ()} closeCallback callback function to be called when the websocket server connection is closed
     * @param {{attemptReconnect: boolean}} options option object, mainly to instruct if a reconnect should be attempted
     */
    constructor(openCallback,
        closeCallback,
        options = { attemptReconnect: true }) {
        const hostname = window.location.host || ("localhost" + WSPORT);
        this.websocket = new WebSocket(PROTOCOL + hostname + PATH);
        this.eventCallbacks = new Object();


        this.openCallback = openCallback;
        this.closeCallback = closeCallback;
        this.options = options;
        this.attachHandlers();
    }

    // attaches the handlers that the client comms class uses to intercept
    // messages from the websocket server and network events
    attachHandlers() {
        this.websocket.addEventListener('open', (ev) => {
            // call the openCallback and set up websocket data
            this.openCallback(ev);
        });

        this.websocket.addEventListener('message', (ev) => {
            try {
                // parse any json objects that might have arrived
                console.log(ev.data)
                var jsonObj = JSON.parse(ev.data);
                this.handleServerCommand(jsonObj.action, jsonObj);
            } catch (e) {
                if (e instanceof SyntaxError) {
                    /// text was not a json object, for now just log it
                    console.error("Received invalid JSON string from websocket");
                    console.log(ev.data);
                } else {
                    console.error(e);
                }
            }
        });

        this.websocket.addEventListener('error', (ev) => console.error);
        this.websocket.addEventListener('close', (ev) => {
            // call closeCallback and possibly handle resource freeing
            this.closeCallback();
            if (this.options.attemptReconnect) {
                console.log("attempting reconnect...");
                // only attempt reconnect once
                this.options.attemptReconnect = false;
                const hostname = window.location.hostname || "localhost"
                this.websocket = new WebSocket(PROTOCOL + hostname + WSPORT);
                this.attachHandlers();
            }
        })
    }

    // to manually close the connection with the server
    closeConnection() {
        // refresh the on close listener
        this.websocket.removeEventListener('close');
        this.websocket.addEventListener('close', this.closeCallback);
        this.websocket.close();
    }



    //
    /**
     * function that registers a callback function [which takes in an action
     * name and a payload from the server] to be called when a specific action
     * is received from the server.
     * @param {string} commandName name of the server command
     * @param {(string, obj) -> ()} commandConsumer call back function that consumes the action
     * name and the payload
     */
    registerCallback(commandName, commandConsumer) {
        if (this.eventCallbacks.hasOwnProperty(commandName)) {
            this.eventCallbacks[commandName].push(commandConsumer);
        } else {
            this.eventCallbacks[commandName] = [commandConsumer];
        }
    }

    /**
     * Helper function that calls back all registered callbacks. To be called
     * when a command is identified and payload is received.
     * @param {*} commandName name of the server command
     * @param {*} commandObject payload object
     */
    handleServerCommand(commandName, commandObject) {

        if (this.eventCallbacks.hasOwnProperty(commandName)) {
            this.eventCallbacks[commandName].forEach(callback => {
                callback(commandName, Object.assign({}, commandObject.payload));
            });
        } else {
            console.error(`Unhandled command received received: `,
                commandName,
                commandObject);
        }

    }

    /**
     * Method to send a client action to the server
     * @param {*} actionName name of the client action
     * @param {*} payload payload object containing necessary data
     */
    sendAction(actionName, payload) {
        this.websocket.send(JSON.stringify({
            action: actionName,
            payload: payload
        }))
    }


}

// Interface objects, to allow for quick adjustment of
// serialization/deserialization

const ClientStateEnum = {
    Home: "Home",
    Lobby: 'Lobby',
    PromptCompletion: 'PromptCompletion',
    WaitingForOtherPlayer: 'WaitingForOtherPlayer',
    JudgingEntries: 'JudgingEntries',
    RoundResult: 'RoundResult',
    GameResult: 'GameResult',

    default() {
        return {
            state: this.Home,
            data: {},
            global: {
                lobby: {
                    users: {},
                    id: ""
                },
                privateId: "",
                publicId: "",
                publicName: "",
                round: {
                    prompt: "",
                    number: 0,
                }
            }
        }
    }
}

const ClientActionsEnum = {
    Connect: 'CONNECT',
    CreateLobby: "CREATE_LOBBY",
    JoinLobby: "JOIN_LOBBY",
    StartGame: 'START_GAME',
    SubmitSentence: 'SUBMIT_SENTENCE',
    SubmitVote: 'SUBMIT_VOTE',
}

const ClientStorageEnum = {
    privateId: "privateId",
    publicId: "publicId",
    publicName: "publicName"
}

// Serializing/Deserializing dictionary
// a set of kv pairs to be used for the purposes of
// reading and writing commands between client and server/
// For example this states that all transactions that expect privateId
// will have the json object have the key "private_id" to mark where
// this information will be found
const PayloadIds = {
    // user info / connect payload
    hasRecord: "has_record",
    privateId: "private_id",
    publicId: "public_id",
    publicName: "public_name",

    ////// user connected/disconnected to lobby payload /////
    user: "user", // string

    // user object
    userProps: {
        get publicId() {return PayloadIds.publicId}, // string
        get publicName() {return PayloadIds.publicName} // string
    },

    ////////////////////////////////////////////////////////

    //////////// Lobby Connect payload ///////////////////////////
    lobbyProps: {
        id: "lobby_id", // string
        users: "users", // userobject[]
    },

    // each user object will be the same as the user object above
    // in user connected to lobby payload
    //////////////////////////////////////////////////////

    /////////////// prompt payload ///////////////////////////
    prompt: "prompt", // string
    timeLimit: "limit", // number, in seconds, optional

    /////////////////////////////////////////////////////////

    //////// sentence payload /////////
    sentenceObjects: "sentences", // sentenceObj[]


    // each sentence object will contain
    sentenceProps: {
        text: "text", // string
        get publicId() {return PayloadIds.publicId}, // string
        get publicName() {return PayloadIds.publicName} // string
    },
    ////////////////////////////////////////////

    /// Round result payload ////////
    winningSentence: "winning_sent", // single
    otherSentences: "other_sents", // resultSentence[]

    // each sentence object will contain
    resultSentenceProps: {
        text: "text",
        get publicId() {return PayloadIds.publicId},
        get publicName() {return PayloadIds.publicName},
        votes: "votes",
    },

    //////////////////////////////////////////

    ////////// game result payload ////////////
    scoreObjects: "scores",

    // score object interface
    scoreProps: {
        get publicId() {return PayloadIds.publicId},
        get publicName() {return PayloadIds.publicName},
        score: "score",
    },
    ////////////////////////////////////////////////
}

// Similar to the object above but this are
// client specific actions payloads
const ClientPayloadId = {
    lobbyId: PayloadIds.lobbyProps.id,
    privateId: PayloadIds.privateId,
    publicId: PayloadIds.publicId,
    publicName: PayloadIds.publicName,
    sentence: "sentence",
    powerUpId: "power_up_id",
}

// A set of server commands that the client listens to
// from the server, this is done to follow the server's intended
// state and it is meant to be alterable, with the intent to more easily
// integrate.
// This essentially states: "the command that will deliver the
// sentences of other players will have the 'action: <value under SentencePayload>'
// as a flag on the json object sent over by the server"
const ServerCommandsEnum = {
    ConnectAck: "USER_INFO",
    UserConnect: "USER_CONNECT",
    UserDisconnect: "USER_DISCONNECT",
    PromptPayload: "SEND_PROMPT",
    SentencePayload: "SEND_SENT",
    RoundResult: "ROUND_RES",
    GameResult: "GAME_RES",
    AckJoin: "ACK_JOIN",

}

/**
 * For now I will just hardcode this to be closely involved with
 * ClientGUIStates and Alpine callbacks, not very clean or encapsulated
 * but should be a faster implementation
 */
/**
 * At creation the client manager initiates a client comms object that used
 * to communicate with the server, this class is in charge of managing the app
 * state and any communication between the server and the user.
 *
 * There are three main types of methods in this class:
 *
 * 1. The first are methods in charge of responding to commands from the server, these
 * are prefixed by "handle", because they handle state changes from the server.
 *
 * All 'handle' functions have the same signature, they take in the name of the server
 * command as the first argument and the payload of the server command as the second.
 *
 * These messages/payload mainly include going from one phase of the game to the next and any asynch user-determined
 * notifications from the server, such as connections and disconnections.
 *
 * For the most part, 'handle' methods will change state and populate gui {state, data, and flags}.
 * The methods that do change the state will do so through the 'transtionToState' method,
 * this method then handles each state transition case.
 *
 * 2. The second are methods in charge of user input and asynch command handling, these
 * are prefixed by "request". These handle things like sentence input, name input, lobby joining requests,
 * voting, etc. These do not alter the apps state but rather set flags that help the user understand
 * what is occurring or blocking/debouncing duplicate inputs.
 *
 * 3. Finally, the last few methods mainly cover state functionality and help populate other areas
 * of the client app with necessary data.
 */
class ClientManager {

    // proxy helper functions for quick access //////
    get GuiStateProxy() {
        return Alpine.store("gui_state");
    }

    get LobbyGuiStateProxy() {
        return Alpine.store("lobby");
    }
    ///////////////////////////////////////////////

    constructor() {

        // initiate the default empty state
        this.state = ClientStateEnum.default();

        // and set up any global/locally stored flags
        this.setupGlobal();

        // attach the connect init method for when the server connection
        // is acquired
        this.clientComms = new ClientComms(
            (ev) => {this.initAfterConnect()},
            () => { console.log("closed") }, // TODO
            { attemptReconnect: false }
        );

        // finally attach all server command handlers (the methods covered above as 'handleX')
        this.attachCommandHandlers();
    }

    /**
     * function that attaches all server event
     * handler functionality to the comm system. Any event handler
     * for server commands should be hooked up here.
     */
    attachCommandHandlers() {
        // Array that attaches event handlers
        // it consists of an array of length-2 arrays where the first
        // member is the string name for the server command and the
        // second is a class method that takes in the command name
        // and payload
        [
            [ServerCommandsEnum.ConnectAck, this.handleConnectAck],
            [ServerCommandsEnum.UserConnect, this.handleUserConnect],
            [ServerCommandsEnum.UserDisconnect, this.handleUserDisconnect],
            [ServerCommandsEnum.AckJoin, this.handleLobbyJoin],
            [ServerCommandsEnum.PromptPayload, this.handlePrompt],
            [ServerCommandsEnum.SentencePayload, this.handleSentences],
            [ServerCommandsEnum.RoundResult, this.handleRoundResult],
            [ServerCommandsEnum.GameResult, this.handleGameResult],
        ]
        .forEach((dirTuple) => {
            this.clientComms.registerCallback(
                dirTuple[0],
                dirTuple[1].bind(this) // bind this to the function before registering
            )
        });
    }

    // This method handles the first connect handshake between the client app and the
    // server, theoretically this receives the private and public id from the server
    handleConnectAck(action, payload) {
        if (payload.hasOwnProperty(PayloadIds.privateId)) {
            // assume a message that contains private id will also
            // contain all other fields
            window.localStorage.setItem(ClientStorageEnum.privateId, payload[PayloadIds.privateId]);
            window.localStorage.setItem(ClientStorageEnum.publicId, payload[PayloadIds.publicId]);
            this.state.global.privateId = payload[PayloadIds.privateId];
            this.state.global.publicId = payload[PayloadIds.publicId];

            // set the gui state
            this.GuiStateProxy.global.publicId = this.state.global.publicId;
        }
    }

    // This method handles the server message that instructs the user to connect to
    // the lobby session, this payload will have a list of users already connected to the lobby
    // as well as the lobby id.
    handleLobbyJoin(action, payload) {
        // parse the users payload
        this.state.global.lobby.users = payload[PayloadIds.lobbyProps.users].map(
            elem => (
                {
                    publicId: elem[PayloadIds.userProps.publicId],
                    publicName: elem[PayloadIds.userProps.publicName]
                }));
        this.state.global.lobby.id = payload[PayloadIds.lobbyProps.id];
        this.transtionToState(ClientStateEnum.Lobby);
    }

    // this handles the server message informing user x that another user has connected
    // to the lobby after the user x has connected to the lobby.
    handleUserConnect(action, payload) {
        if (!this.state.data.hasOwnProperty('lobby')) {
            this.state.data.lobby = {};
        }

        // parse the payload
        let userObj = {
            publicId: payload[PayloadIds.user][PayloadIds.userProps.publicId],
            publicName: payload[PayloadIds.user][PayloadIds.userProps.publicName],
        }
        let userId = userObj.publicId;


        // assign to states
        this.state.global.lobby["users"][userId] = userObj;
        this.LobbyGuiStateProxy.users.push(userObj);
        // this.GuiStateProxy.global.lobby["otherPlayers"][userId] = userObj;

    }

    // this handles the server message informing user x that another user has disconnected
    // from the lobby they were both a part of
    handleUserDisconnect(action, payload) {
        // parse the payload
        let userObj = {
            publicId: payload[PayloadIds.user][PayloadIds.userProps.publicId],
            publicName: payload[PayloadIds.user][PayloadIds.userProps.publicName],
        }
        let userId = userObj.publicId;

        console.log("userObj", userObj)
        console.log("userId", userId);
        // delete the user entry, ideally this would be handled in an immutable way
        this.state.global.lobby.users = this.state.global.lobby.users.filter((el) => (el.publicId !== userId));
        this.LobbyGuiStateProxy.users = this.LobbyGuiStateProxy.users.filter((el) => (el.publicId != userId));
    }


    // this handles the server message that gives the user the prompt for this round
    // optionally the payload may contain a limit property that states how many seconds
    // this phase will last, this is only used to populate a timer bar and does not
    // actually change state again until the next server message instructs the app
    // to do so.
    handlePrompt(action, payload) {
        this.state.data.promptCompletion = {
            timeLimit: payload[PayloadIds.timeLimit] || 20, // 20 seconds by default
        };

        // update round info
        this.state.global.round.prompt = payload[PayloadIds.prompt];
        this.state.global.round.number += 1;

        this.transtionToState(ClientStateEnum.PromptCompletion)
    }

    // this handles the server message that gives the user the set of sentences from
    // all players in the game so that they may vote for their favorite completion.
    // The payload may also optionally include a time limit to inform the user through
    // ui components.
    handleSentences(action, payload) {
        this.state.data.judgingEntries = {
            sentences: payload[PayloadIds.sentenceObjects].reduce((acc, el) => {
                return acc.concat({
                    text: el[PayloadIds.sentenceProps.text],
                    userPublicId: el[PayloadIds.sentenceProps.publicId],
                    userPublicName: el[PayloadIds.sentenceProps.publicName],
                });
            }, []),
            timeLimit: payload[PayloadIds.timeLimit] || 10, // 10 seconds by default
        }
        this.transtionToState(ClientStateEnum.JudgingEntries);
    }

    // This handles server message that breaks down the round result
    //
    handleRoundResult(action, payload) {
        const winningSentence = payload[PayloadIds.winningSentence];
        this.state.data.roundResult = {
            // extract the props in winningSentence
            winningSentence: {
                text: winningSentence[PayloadIds.resultSentenceProps.text],
                userPublicId: winningSentence[PayloadIds.resultSentenceProps.publicId],
                userPublicName: winningSentence[PayloadIds.resultSentenceProps.publicName],
                votes: winningSentence[PayloadIds.resultSentenceProps.votes],
            },

            // extract props in each non-winning sentence
            otherSentences: payload[PayloadIds.otherSentences].reduce((acc, el) => {
                return acc.concat({
                    text: el[PayloadIds.resultSentenceProps.text],
                    userPublicId: el[PayloadIds.resultSentenceProps.publicId],
                    userPublicName: el[PayloadIds.resultSentenceProps.publicName],
                    votes: el[PayloadIds.resultSentenceProps.votes],
                });
            }, []),
        };
        this.transtionToState(ClientStateEnum.RoundResult);
    }

    // Handles game result command from server, this should include
    // the score, name, and public id of all users in the lobby
    handleGameResult(action, payload) {
        this.state.data.gameResult = {
            scores: payload[PayloadIds.scoreObjects].map(el => ({
                score: el[PayloadIds.scoreProps.score],
                publicName: el[PayloadIds.scoreProps.publicName],
                publicId: el[PayloadIds.scoreProps.publicId],
            }))
        }
        this.transtionToState(ClientStateEnum.GameResult);
    }

    // State transition function discussed above
    transtionToState(newState) {
        console.log("switching to...", newState);
        // cancel any await request signals and change states
        this.GuiStateProxy.global.awaiting_request = false;

        switch (newState) {

            case ClientStateEnum.Lobby: {
                // Lobby state with possibly joined players
                this.GuiStateProxy.state = ClientGUIStatesEnum.joinedLobby;
                this.LobbyGuiStateProxy.users = this.state.global.lobby.users;
                this.LobbyGuiStateProxy.id = this.state.global.lobby.id;
                break;
            }
            case ClientStateEnum.PromptCompletion: {
                this.GuiStateProxy.state = ClientGUIStatesEnum.submittingSenteces;
                this.GuiStateProxy.data = {
                    prompt: this.state.data.promptCompletion.prompt,
                    limit: this.state.data.promptCompletion.timeLimit,
                    sentSentence: false,
                }
                this.GuiStateProxy.global.roundPrompt = this.state.global.round.prompt;
                this.GuiStateProxy.global.roundNum = this.state.global.round.number;
                break;
            }

            case ClientStateEnum.JudgingEntries: {
                this.GuiStateProxy.state = ClientGUIStatesEnum.voting;
                this.GuiStateProxy.data = {
                    sentences: this.state.data.judgingEntries.sentences,
                    limit: this.state.data.judgingEntries.timeLimit,
                    voted: false,
                }
                break;
            }

            case ClientStateEnum.RoundResult: {
                this.GuiStateProxy.state = ClientGUIStatesEnum.voteResults;
                this.GuiStateProxy.data = {
                    winningSentence: this.state.data.roundResult.winningSentence,
                    otherSentences: this.state.data.roundResult.otherSentences,
                }
                break;
            }

            case ClientStateEnum.GameResult: {
                this.GuiStateProxy.state = ClientGUIStatesEnum.gameResult;
                this.GuiStateProxy.data = {
                    scores: this.state.data.gameResult.scores,
                }
                break;
            }
        }

        this.state.name = newState;
    }

    // Request handler that is called when the user has elected to *create* a new
    // lobby, a payload will be sent with the user's {privateId} and {publicName}
    requestCreateLobby(chosenName) {
        // very similar pattern to join lobby
        this.state.global.publicName = chosenName;
        this.GuiStateProxy.global.chosenName = chosenName;

        // set public name from the user input
        window.localStorage.setItem(ClientStorageEnum.publicName, chosenName);

        // and set awating flag
        this.GuiStateProxy.global.awaiting_request = true;

        // build payload
        let payload = {}
        payload[ClientPayloadId.publicName] = chosenName;
        payload[ClientPayloadId.privateId] = this.state.global.privateId;
        this.clientComms.sendAction(ClientActionsEnum.CreateLobby, payload);
    }

    // Request handler that is called when the user has elected to *join* an
    // existing lobby, a payload will be sent with the user's {privateId} and {publicName}
    requestJoinLobby(lobbyId, chosenName) {
        // set the chosen name globally
        this.state.global.publicName = chosenName;
        this.GuiStateProxy.global.chosenName = chosenName;

        // store into local storage
        window.localStorage.setItem(ClientStorageEnum.publicName, chosenName);

        // set await input flag
        this.GuiStateProxy.global.awaiting_request = true;

        // set up the payload with the info given
        let payload = {}
        payload[ClientPayloadId.lobbyId] = lobbyId;
        payload[ClientPayloadId.publicName] = chosenName;
        payload[ClientPayloadId.privateId] = this.state.global.privateId;
        this.clientComms.sendAction(ClientActionsEnum.JoinLobby, payload);

    }

    // Request handler that is called when the user [Any user in the lobby for now]
    // asks to start the game via button in the lobby. The payload will contain the
    // lobby id and the privateId of the user.
    requestGameStart() {
        // build payload
        let payload = {}
        payload[ClientPayloadId.lobbyId] = this.state.global.lobby.id;
        payload[ClientPayloadId.privateId] = this.state.global.privateId;

        // signal awaiting state
        this.GuiStateProxy.data.sentSentence = true;
        this.clientComms.sendAction(ClientActionsEnum.StartGame, payload);
    }


    // Request handler that is called when the user inputs their response to the
    // given prompt. The payload sent will contain the sentence and the user's
    // private id.
    requestSendSentence(sentence) {
        // build the payload with the sentence and the personal private id
        let payload = {}
        payload[ClientPayloadId.sentence] = sentence;
        payload[ClientPayloadId.privateId] = this.state.global.privateId;


        // set gui states and send the payload
        this.GuiStateProxy.global.awaiting_request = true;
        this.clientComms.sendAction(ClientActionsEnum.SubmitSentence, payload);
    }

    requestSendPowerUp(powerUpId) {
        // TODO?
    }

    // Request handler that is called when the client inputs their vote after
    // all users have given their prompt responses. The payload sent will contain
    // the publicId of the user that the client is voting for as well as the private
    // id of the client
    requestVote(publicId) {
        let payload = {}
        payload[ClientPayloadId.publicId] = publicId;
        payload[ClientPayloadId.privateId] = this.state.global.privateId;

        // set the gui states and send
        this.GuiStateProxy.data.voted = true;
        this.GuiStateProxy.data.votedId = publicId;
        this.clientComms.sendAction(ClientActionsEnum.SubmitVote, payload);
    }

    // global setup function discussed above, mostly used to initiate outside states
    // and extract locally store data
    setupGlobal() {
        this.state.global.privateId = window.localStorage.getItem(ClientStorageEnum.privateId);
        this.state.global.publicId = window.localStorage.getItem(ClientStorageEnum.publicId);
        this.state.global.publicName = window.localStorage.getItem(ClientStorageEnum.publicName);

        let hasChosenName = this.state.global.publicName != null;

        // set up default gui states
        Alpine.store("gui_state", ClientGUIStatesEnum.default(
            (hasChosenName) ? this.state.global.publicName : undefined,
            (hasChosenName) ? this.state.global.publicId : undefined)
            );
        this.GuiStateProxy.data.hasChosenName = hasChosenName;

        Alpine.store("lobby", ClientGUILobbyDefaultState)
    }

    // init function discussed above, mostly used to set up network specific state as
    // well as sending the handshake packet to the server
    initAfterConnect() {

        console.log("Connected..");

        let payload = {}
        if (this.state.global.privateId == null ||
            this.state.global.publicId == null ||
            this.state.global.publicName == null) {
            payload[PayloadIds.hasRecord] = false;
        } else {
            payload[PayloadIds.hasRecord]  = true;
            payload[PayloadIds.privateId]  = this.state.global.privateId;
            payload[PayloadIds.publicId]   = this.state.global.publicId;
            payload[PayloadIds.publicName] = this.state.global.publicName;
        }

        this.clientComms.sendAction(
            ClientActionsEnum.Connect,
            payload
        );
    }



}

