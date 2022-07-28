const WSPORT = ":10000";
const PROTOCOL = "ws://"




class ClientComms {


    constructor(openCallback,
        closeCallback,
        options = { attemptReconnect: true }) {
        const hostname = window.location.hostname || "localhost"
        this.websocket = new WebSocket(PROTOCOL + hostname + WSPORT);
        this.eventCallbacks = new Object();


        this.openCallback = openCallback;
        this.closeCallback = closeCallback;
        this.options = options;
        this.attachHandlers();
    }

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

    closeConnection() {
        // refresh the on close listener 
        this.websocket.removeEventListener('close');
        this.websocket.addEventListener('close', this.closeCallback);
        this.websocket.close();
    }


    registerCallback(commandName, commandConsumer) {
        if (this.eventCallbacks.hasOwnProperty(commandName)) {
            this.eventCallbacks[commandName].push(commandConsumer);
        } else {
            this.eventCallbacks[commandName] = [commandConsumer];
        }
    }

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
}

const ClientActionsEnum = {
    Connect: 'CONNECT'
}

const ClientStorageEnum = {
    privateId: "privateId",
    publicId: "publicId",
    publicName: "publicName"
}

// Doing this mostly out of necesity since 
// the JSON structure has not been finalized
const PayloadIds = {
    // user info / connect payload 
    hasRecord: "has_record",
    privateId: "private_id",
    publicId: "public_id",
    publicName: "public_name",
    

    // user connected to lobby payload
    user: "user",
    
    // user object
    userProps: {
        get publicId() {return this.publicId},
        get publicName() {return this.publicName}
    },

    // prompt payload
    prompt: "prompt",

    // sentence payload
    sentenceObjects: "sentence_objects",

    // sentence object interface
    sentenceProps: {
        sentence: "sentence",
        get publicId() {return this.publicId},
        get publicName() {return this.publicName}
    },

    // round result payload
    winningSentence: "winning_sent",
    otherSentences: "other_sents",

    // result payload
    resultSentenceProps: {
        sentence: "sentence",
        get publicId() {return this.publicId},
        get publicName() {return this.publicName},
        votes: "votes",
    },

    // game result payload
    scoreObjects: "score_objects",
    
    // score object interface
    scoreProps: {
        get publicId() {return this.publicId},
        score: "score",
    },
}

// TODO Make sure we have the correct one
const ServerCommandsEnum = {
    ConnectAck: "USER_INFO",
    UserConnect: "USER_CONNECT",
    PromptPayload: "SEND_PROMPT",
    SentencePayload: "SEND_SENT",
    RoundResult: "ROUND_RES",
    GameResult: "GAME_RES",
    // TODO
    AckCreate: "ACK_CREATE",
    AckJoin: "ACK_JOIN",
}


class ClientManager {

    constructor() {
        // TODO, need to hook up to the gui renderer for the website
        // this.clientRenderer;


        this.states = Object.keys(ClientStateEnum).reduce((obj, state) => {
            obj[state] = { transitions: [], data: {} }
            return obj;
        }, {});

        this.state = {
            name: ClientStateEnum.Home,
            data: {},
            global: {}
        };

        this.setupGlobal();

        this.clientComms = new ClientComms(
            (ev) => {this.initAfterConnect()}, // TODO
            () => { console.log("closed") }, // TODO
            { attemptReconnect: true }
        );

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
            [ServerCommandsEnum.PromptPayload, this.handlePrompt],
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


    handleConnectAck(action, payload) {
        if (payload.hasOwnProperty(PayloadIds.privateId)) {
            // assume a message that contains private id will also 
            // contain all other fields
            window.localStorage.setItem(ClientStorageEnum.privateId, payload[PayloadIds.privateId]);
            window.localStorage.setItem(ClientStorageEnum.publicId, payload[PayloadIds.publicId]);
            this.state.global.privateId = payload[PayloadIds.privateId];
            this.state.global.publicId = payload[PayloadIds.publicId];
        }
    }

    handleUserConnect(action, payload) {
        if (!this.state.data.hasOwnProperty('lobby')) {
            this.state.data.lobby = {};
        }
        
        let userObj = payload[PayloadIds.user];
        let userId = userObj[PayloadIds.userProps.publicId];
        this.state.data.lobby["users"][userId] = userObj;
    }


    handlePrompt(action, payload) {
        this.state.data.promptCompletion = {
            prompt: payload[PayloadIds.prompt]
        };
        this.transtionToState(ClientStateEnum.PromptCompletion)
    }

    handleSentences(action, payload) {
        this.state.data.judgingEntries = {
            sentences: payload[PayloadIds.sentenceObjects]
        }
        this.transtionToState(ClientStateEnum.JudgingEntries);
    }

    handleRoundResult(action, payload) {
        this.state.data.roundResult = {
            winningSentence: payload[PayloadIds.winningSentence],
            otherSentences: payload[PayloadIds.otherSentences],
        };
        this.transtionToState(ClientStateEnum.RoundResult);
    }

    handleGameResult(action, payload) {
        this.state.data.gameResult = {
            scoreObjects: payload[PayloadIds.scoreObjects],
        }
        this.transtionToState(ClientStateEnum.GameResult);
    }

    transtionToState(newState) {
        // handle hydration and side effects of transtioning to a new state
        // this function assumes that the state date objects have already been
        // populated
        // TODO hook this up to the GUI state machine once that is finalized
        // theoretically this would set the GUI flags necessary for correct rendering
        // of the state on state enter (also)
        // TODO For now it simply changes the state
        console.log("switching to...", newState)
        this.state.name = newState
    }

    setupGlobal() {
        this.state.global.privateId = window.localStorage.getItem(ClientStorageEnum.privateId);
        this.state.global.publicId = window.localStorage.getItem(ClientStorageEnum.publicId);
        this.state.global.publicName = window.localStorage.getItem(ClientStorageEnum.publicName);
    }

    initAfterConnect() {

        console.log("Connected..");
        
        let payload = {}
        if (this.state.global.privateId == null || 
            this.state.global.publicId == null || 
            this.state.global.publicName == null) {
            payload.has_record = false;
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

