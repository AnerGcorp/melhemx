document.addEventListener('DOMContentLoaded', () => {
    // Connecting
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    // console.log('document', document)
    var username = document.querySelector("#my-username").innerHTML;
    var current_user_photo = document.querySelector("#current-user-photo").innerHTML;
    var other_user_photo = document.querySelectorAll("#other-user-photo");
    let usernames = {};


    Obj = document.querySelectorAll('.user-list-item');
    Obj.forEach(li => {
        var text = li.querySelector("#username");
        other_user_photo = li.querySelector("#other-user-photo").innerHTML;
        usernames[text.innerHTML] = other_user_photo;
        
        li.onclick = () => {
            
            newRoom = `${username}_${li.innerHTML}`;
            
            var text = li.querySelector("#username");

            if(username < text.innerHTML) {
                newRoom = `${username}_${text.innerHTML}`;
            }
            else {
                newRoom = `${text.innerHTML}_${username}`;
            }
            let timestamp = date.toLocaleString('en-US', options);

            msg = {
                'sender':username,
                'receiver':text.innerHTML,
                'room':newRoom,
                'timestamp': timestamp
            };
            
            leaveRoom(roomName);
            joinRoom(newRoom);
            console.log(`Joining room ${newRoom}`);
            roomName = newRoom;
            // document.querySelector('#room-name').innerHTML = li.innerHTML;
            socket.emit('make_new_room', JSON.stringify(msg));
        }
        
    })

    const date = new Date();

    const dateOptions = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };

    const timeOptions = {
        hour12: false,
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
    };

    const options = {
        ...timeOptions, ... dateOptions
    };


    // THIS IS REQUIRED FOR UPDATING SID IN BACKEND
    // socket.on('connect', () => {
    //     socket.emit('connect', `${username}~ is connected`);
    // });


    // Get list of public chat rooms
    publicRooms = [];
    document.querySelectorAll('.room-opt').forEach(li => {
        publicRooms.push(li.innerHTML);
        // console.log(li.innerHTML);
    })
    
    console.log(publicRooms);

    // Display received message
    socket.on('message', (msg) => {
        console.log(`Message received: ${msg}`);
        msg = JSON.parse(msg);
        if(msg['room'] !== roomName) {
            console.log("I don't know what to do");
        }
        if(msg['sender'] === 'SYSTEM') {
            document.getElementById('rightid').classList.remove('hide-container');
            document.getElementById('message-input-field').classList.remove('hide-container');
            // my custom decorations
            let msgDisplay = document.createElement('li')
            msgDisplay.classList.add('d-flex', 'justify-content-between', 'mb-4');
            
            // user image
            // let userImg = document.createElement('img');
            // userImg.classList.add('rounded-circle', 'd-flex', 
            //     'align-self-start', 'shadow-1-strong');
            // userImg.width = 60;
            // userImg.src = other_user_photo[counter].innerHTML;
            
            // user message
            let userCard = document.createElement('div');
            userCard.classList.add('card', 'w-100');
            // header of user message card
            let cardHeader = document.createElement('div');
            cardHeader.classList.add('card-header', 'd-flex', 
                'justify-content-between', 'p-3');
            let usernameDisplay = document.createElement('p');
            usernameDisplay.classList.add('fw-bold', 'mb-0');
            // usernameDisplay.innerHTML(msg['sender'])
            usernameDisplay.appendChild( document.createTextNode(msg['sender']));
            let fav = document.createElement('i');
            fav.classList.add('far', 'fa-clock');
            let time = document.createElement('p');
            time.classList.add('text-muted', 'small', 'mb-0', 'ml-2');
            time.appendChild(fav);
            time.appendChild( document.createTextNode(msg['timestamp']));
            cardHeader.appendChild(usernameDisplay);
            cardHeader.appendChild(time)
            // body of user message
            let cardBody = document.createElement('div');
            cardBody.classList.add('card-body');
            let cardText = document.createElement('p');
            cardText.classList.add('mb-0');
            cardText.appendChild(document.createTextNode(msg['content']));
            cardBody.appendChild(cardText);

            // adding card elements
            userCard.appendChild(cardHeader);
            userCard.appendChild(cardBody);

            // adding list elements
            // msgDisplay.appendChild(userImg);
            msgDisplay.appendChild(userCard);

            document.getElementById('message-list-styled').appendChild(msgDisplay);
        }
        if( msg['room'] === roomName ) {
            
            let msgDisplay = document.createElement('li')
            msgDisplay.classList.add('d-flex', 'justify-content-between', 'mb-4');
            
            // user image
            let userImg = document.createElement('img');
            userImg.classList.add('rounded-circle', 'd-flex', 
                'align-self-start', 'shadow-1-strong');
            userImg.width = 60;
            userImg.src = usernames[msg['receiver']];
            console.log("Message_206:", usernames[msg['receiver']]);
            
            // user message
            let userCard = document.createElement('div');
            userCard.classList.add('card', 'w-100');
            // header of user message card
            let cardHeader = document.createElement('div');
            cardHeader.classList.add('card-header', 'd-flex', 
                'justify-content-between', 'p-3');
            let usernameDisplay = document.createElement('p');
            usernameDisplay.classList.add('fw-bold', 'mb-0');
            usernameDisplay.appendChild(document.createTextNode(msg['sender']));
            let fav = document.createElement('i');
            fav.classList.add('far', 'fa-clock');
            let time = document.createElement('p');
            time.classList.add('text-muted', 'small', 'mb-0', 'ml-2');
            if (msg['timestamp'] === undefined ) {
                timestamp = '00:00';
            }
            else {
                timestamp = msg['timestamp'];
                const lenTime = timestamp.length;
                timestamp = timestamp.slice(lenTime-8, lenTime-3);
            }
            time.appendChild(fav);
            time.appendChild(document.createTextNode(timestamp));
            cardHeader.appendChild(usernameDisplay);
            cardHeader.appendChild(time)
            // body of user message
            let cardBody = document.createElement('div');
            cardBody.classList.add('card-body');
            let cardText = document.createElement('p');
            cardText.classList.add('mb-0');
            cardText.appendChild(document.createTextNode(msg['content']));
            cardBody.appendChild(cardText);

            // adding card elements
            userCard.appendChild(cardHeader);
            userCard.appendChild(cardBody);

            if(msg['sender'] === username) {
                // adding list elements
                userImg.src = current_user_photo;
                userImg.classList.add('ms-3');
                msgDisplay.appendChild(userCard);    
                msgDisplay.appendChild(userImg);
            }
            else {
                // adding list elements
                userImg.src = usernames[msg['sender']];
                // console.log("Message_202: ", usernames)
                // console.log("Message_204: ", msg['sender'])
                // console.log("Message_205: ", msg['receiver'])
                
                userImg.classList.add('me-3');
                msgDisplay.appendChild(userImg);
                msgDisplay.appendChild(userCard);
            }
            document.getElementById('message-list-styled').appendChild(msgDisplay);
        }
        scrollDownChatWindow();
    });
    // Select user input field and send button from DOM
    let sendButton = document.querySelector('#send-btn');
    let userInput = document.querySelector('#message-input');
    
    // Function to send a message
    sendMessage = () => {

        // console.log("this is user input", userInput);
        // console.log("this is a message: ", msg);

        if(userInput.value !== '') {
            console.log("Sending to another user");
            let timestamp = date.toLocaleString('en-US', options);
            msg = {
                'sender':username,
                'content':userInput.value,
                'room':roomName,
                'timestamp': timestamp
            };
            if(publicRooms.includes(roomName)) {
                console.log('sending on public chatroom')
                msg['receiver'] = null;
            }
            else if(roomName === 'GLOBAL') {
                msg['receiver'] = null;
                console.log('sending to global chat');
            }
            else {
                const userLength = username.length;
                const roomLength = roomName.length;

                let result = roomName.slice(userLength+1, roomLength);
                msg['receiver'] = result;
                console.log(`sending to ${msg['receiver']}`)
            }
            socket.send(JSON.stringify(msg));
            userInput.value="";
            scrollDownChatWindow();
        }

        updateChatView();
    };

    updateChatView = () => {
        console.log("update message: \n", msg);
        document.querySelectorAll('.user-list-item').forEach(li => {
            if (li.querySelector("#username").innerHTML === msg['receiver'])
            {
                let message = msg['content'];
                let msgLen = message.length;
                if ( msgLen >= 20 ) {
                    message = message.slice(0, 20);
                    message = message + '...';
                }
                // let lastItem = Object.keys(msgHistory).pop();
                let timestamp = msg['timestamp'];
                const lenTime = timestamp.length;
                timestamp = timestamp.slice(lenTime-8, lenTime-3);

                li.querySelector('#last-message-content').innerHTML = message;
                li.querySelector('#received-message-counter').innerHTML = '2' // lastItem ;
                li.querySelector('#time-display').innerHTML = timestamp;
            }
        })
    }

    // Listener for send action: Enter key
    userInput.addEventListener("keyup", (e) => {
        if(e.keyCode === 13) {
            if(userInput === document.activeElement) {
                e.preventDefault();
                sendMessage();
            }
        }
    });

    // Listener for send action: Send button clicked
    sendButton.onclick = () => {
        sendMessage();
    };

    
    // Listener for room-opt clicks
	// document.querySelectorAll('.room-opt').forEach(li => {
		
	//     li.onclick = () => {
			
	//         let newRoom = li.innerHTML;
	//         if(newRoom === roomName) {  // User already in that room
	//             console.log(`User already in ${roomName}`); // Write alert code later
	//         }
	//         else {
	//             leaveRoom(roomName);
	//             joinRoom(newRoom);
    //             roomName = newRoom;
    //             document.querySelector('#room-name').innerHTML = newRoom;
	//         }
	//     }
	// });

	// Function for leaving a room
	leaveRoom = (oldRoom) => {
		leave_msg = {
			'sender':username,
			'room':oldRoom
		}
		socket.emit('leave', JSON.stringify(leave_msg));
		// document.querySelector('#messages-list').innerHTML = '';
        document.querySelector('#message-list-styled').innerHTML = '';
        // console.log(document.querySelector('#message-list-styled'))
	}

	// Function for joining a roow
	joinRoom = (newRoom) => {
		join_msg = {
			'sender':username,
			'room':newRoom
		}
		socket.emit('join', JSON.stringify(join_msg));
	}



    /* document.querySelectorAll('.user-list-item').forEach(li => {
        li.onclick = () => {

            request = {
                'sender':username,
                'to':li.innerHTML
            };
            socket.emit('request_for_connection', JSON.stringify(request));
        }
    })

    socket.on('request_to_connect', (request) => {
        console.log(`Request to connect: ${request}`);
        request = JSON.parse(request);

        // FOR SOME REASON, THE CODE BELOW IS NEVER REACHED

        // Alert user that he has been requested. Add an onclick for accepting
        // For now, accept all incoming requests
        console.log(`in 'request_to_connect' request was parsed`);
        accept_request(request['sender']);
    })

    accept_request = (requester_username) => {
        console.log("accept_request() called");
        newRoom = `${requester_username}ROOMW${username}`;
        accept_msg = {
            'sender':username,
            'requester':requester_username,
            'room':newRoom
        };
        socket.emit('accept_request', JSON.stringify(accept_msg));
        // Redirect to chat screen, or add chatroom somewhere
        // Edit: the newRoom in this case can be requester.sid
        // Edit 2: Not today
        
        leaveRoom(roomName);
        joinRoom(newRoom);
        console.log(`Joining room ${newRoom}`);
    }

    socket.on('request_accepted', (accepted_msg) => {
        console.log(`Request was accepted, Details:\n${accepted_msg}`)
        // Use accepted_msg to join newly created two-person chatroom
    }) */

    socket.on('load_history', (msgHistory) => {
        msgHistory = JSON.parse(msgHistory);
        console.log("This is msgHistory:\n", msgHistory);
        for(msgKey in msgHistory) {
            if(msgKey === '0') {
                continue;
            }
            else if(msgKey === '1') {
                if(roomName === msgHistory[msgKey]['room']) {
                    // Correct case, continue
                    if(document.querySelector('#message-list-styled').childElementCount === 1) {
                        // Load history
                        console.log('Chatroom just opened, load history');
                    }
                    else {
                        // History is already present
                        console.log(`History already present, don't load history`);
                        return;
                    }
                }
                else {
                    // Incorrect
                    console.log('History received was not of current room')
                    break;
                }
            }
            
            let msg = msgHistory[msgKey]
            let msgDisplay = document.createElement('li')
            msgDisplay.classList.add('d-flex', 'justify-content-between', 'mb-4');
            // user image
            let userImg = document.createElement('img');
            userImg.classList.add('rounded-circle', 'd-flex', 
                'align-self-start', 'shadow-1-strong');
            userImg.width = 60;
            
            // user message
            let userCard = document.createElement('div');
            userCard.classList.add('card', 'w-100');
            // header of user message card
            let cardHeader = document.createElement('div');
            cardHeader.classList.add('card-header', 'd-flex', 
                'justify-content-between', 'p-3');
            let usernameDisplay = document.createElement('p');
            usernameDisplay.classList.add('fw-bold', 'mb-0');
            usernameDisplay.appendChild(document.createTextNode(msg['sender']));
            let fav = document.createElement('i');
            fav.classList.add('far', 'fa-clock');
            let time = document.createElement('p');
            time.classList.add('text-muted', 'small', 'mb-0', 'ml-2');
            time.appendChild(fav);
            time.appendChild(document.createTextNode(msg['timestamp']));
            // console.log('message itself: \n', msg);
            cardHeader.appendChild(usernameDisplay);
            cardHeader.appendChild(time)
            // body of user message
            let cardBody = document.createElement('div');
            cardBody.classList.add('card-body');
            let cardText = document.createElement('p');
            cardText.classList.add('mb-0');
            cardText.appendChild(document.createTextNode(msg['content']));
            cardBody.appendChild(cardText);

            // adding card elements
            userCard.appendChild(cardHeader);
            userCard.appendChild(cardBody);

            if(msg['sender'] === username) {
                // adding list elements
                userImg.src = current_user_photo;
                userImg.classList.add('ms-3');
                msgDisplay.appendChild(userCard);    
                msgDisplay.appendChild(userImg);
            }
            else {
                // adding list elements
                let receiver = msg['room'];
                let index = receiver.indexOf('_');
                receiver = receiver.slice(index+1, receiver.length);
                // console.log('Message_456: ', receiver);
                userImg.src = usernames[receiver];
                userImg.classList.add('me-3');
                msgDisplay.appendChild(userImg);
                msgDisplay.appendChild(userCard);
            }

            document.getElementById('message-list-styled').appendChild(msgDisplay);
        }
        scrollDownChatWindow();
    });

    function scrollDownChatWindow() {
        const chatWindow = document.querySelector("#message-list-styled");
        chatWindow.scrollTop = chatWindow.scrollHeight;
        }
});