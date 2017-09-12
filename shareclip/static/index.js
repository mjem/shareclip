"use strict";

// make ajax call
function get(url) {
   return new Promise((resolve, reject) => {
       const req = new XMLHttpRequest();
       req.open('GET', url);
       req.onload = () => req.status === 200 ? resolve(req.response) : reject(Error(req.statusText));
       req.onerror = (e) => reject(Error(`Network Error: ${e}`));
       req.send();
   });
}

// websocket and message queue
var ws;
// var ws_ready = false;
// var ws_outbox = []

function create_websocket() {
	// ws_ready = false;
	if ('WebSocket' in window) {
		console.log('Looking for ws at ' + ws_url);

		try {
			ws = new WebSocket('ws://' + ws_url);
		}
		catch(err) {
			ws = new WebSocket('wss://' + ws_url);
		}

		ws.onopen = function() {
			// clear any buffered messages and mark the socket as available for direct use
			// ws_ready = true;
			// for(var i=0; i<ws_outbox.length; i++) {
				// websocket_send(ws_outbox[i]);
			// }
			// ws_outbox = [];
			console.log('pre set table');
			docid('slot-table-placeholder').innerHTML =
				'<table class="table table-bordered table-hover table-sm" id="slot-table">' +
				'<thead class="thead-default">' +
				'<tr>' +
				'<th>Message</th>' +
				'<th>Sender</th>' +
				'<th>Control</th>' +
				'</tr>' +
				'</thead>' +
				'<tbody id="slots">' +
				'</tbody>' +
				'</table>';
			console.log('post set table');

			websocket_send({type: 'helo'});
		};

		ws.onmessage = function(event) {
			websocket_recv(JSON.parse(event.data));
		};

		ws.onclose = function()	{
			docid('slot-table-placeholder').innerHTML = '<div class="alert alert-danger" role="alert">' +
				'Connection to server lost' +
				'<button class="btn" onclick="create_websocket()">Reconnect</button>' +
				'</div>';
			console.log('WebSocket is closed');
		};
    }

	else {
		alert('WebSocket not supported by your browser');
    }
}

// send a message back to our server over the websocket
function websocket_send(message) {
	// if (ws_ready) {
		var encoded = JSON.stringify(message);
		console.log('Sending message ' + encoded);
		ws.send(encoded);
	// }

	// else {
		// ws_outbox.push(message);
	// }
}

// right pad with `filler` to `length` chars
String.prototype.rpad = function(filler, length) {
    var str = this;
    while (str.length < length) {
        str += filler;
	}

    return str;
}

// pretty print a Date
function show_time(time) {
	return time.getFullYear() + '-' +
		(time.getMonth() + 1 + '').rpad('0', 2) + '-' +
		(time.getDate() + '').rpad('0', 2) + ' ' +
		(time.getHours() + '').rpad('0', 2) + ':' +
		(time.getMinutes() + '').rpad('0', 2) + ':' +
		(time.getSeconds() + '').rpad('0', 2);
}

// handle incoming structure over the WebSocket
function websocket_recv(msg) {
	console.log('recv ' + JSON.stringify(msg));
	if (msg.type == 'new_slot') {
		var new_slot = document.createElement('tr')
		new_slot.dataset.uid = msg.uid;
		new_slot.dataset.text = msg.text;
		new_slot.dataset.clipboard = msg.clipboard;
		// new_slot.dataset.source = msg.source;
		// new_slot.dataset.timestamp = msg.timestamp;
		var timestamp = new Date(msg.timestamp);
		timestamp.setMilliseconds(0);
		new_slot.dataset.timestamp = timestamp;
		var innerHTML = '<td>' + msg.text + '</td>' +
			'<td>' + msg.nickname + '</td>' +
			'<td><div class="btn-group" role="group">' +
			'<button class="btn btn-info" onclick=' + "'" + 'info_modal("' + msg.uid + '"' + ")'>Info</button>" +
			'<button class="btn" onclick=' + "'" + 'slot_to_clipboard("' + msg.uid + '"' + ")'>Copy</button>" +
			'<button class="btn btn-warning" onclick=' + "'" + 'delete_click("' + msg.uid + '"' + ")'" + '>Delete</button>' +
			'</div></td>';
		// console.log('Pushing ' + innerHTML);
		new_slot.innerHTML = innerHTML;
		var slots = docid('slots');
		slots.insertBefore(new_slot, slots.firstChild);
	}

	else if (msg.type == 'delete_slot') {
		delete_slot(msg.uid);
	}
}

// lookup DOM element by id
function docid(id) {
	return document.getElementById(id);
}

function slot_to_clipboard(uid) {
	var slotlist = docid('slots');
	var slots = slotlist.children;
	for(var i=0; i<slots.length; i++) {
		if (uid == slots[i].dataset.uid) {
			console.log('clipboard ' + slots[i].dataset.clipboard + ' type ' + typeof slots[i].dataset.clipboard);
			if (slots[i].dataset.clipboard === 'null') {
				console.log('text');
				string_to_clipboard(slots[i].dataset.text);
			}
			else {
				console.log('clip');
				string_to_clipboard(slots[i].dataset.clipboard);
			}
		}
	}
}

// Pop up dialog with info on a single message
function info_modal(uid) {
	var slots = docid('slots').children;
	for(var i=0; i<slots.length; i++) {
		var slot = slots[i];
		if (uid == slot.dataset.uid) {
			console.log('open info ' + slot + ' text '  + slot.dataset.text);
			// var i  = docid('info_modal');
			// console.log(i);
			// i.modal();
			docid('info_modal_body').innerHTML = 'sent at ' + slot.dataset.timestamp;
			$('#info_modal').modal();
		}
	}
}

// handle click to delete button
function delete_click(uid) {
	console.log('Sending request to delete slot ' + uid);
	websocket_send({type: 'delete',
					uid: uid});
}

// handle message zapping a slot
function delete_slot(uid) {
	var slotlist = docid('slots');
	var slots = slotlist.children;
	// console.log('slots ' + slots + ' len ' + slots.length);
	for(var i=0; i<slots.length; i++) {
		console.log('delete test ' + uid + ' against ' + slots[i].dataset.uid + (uid == slots[i].dataset.uid));
		if (uid == slots[i].dataset.uid) {
			slotlist.removeChild(slots[i]);
		}
	}
}

// handle click to post button
function post_click() {
	var text = docid('new_message').value;
	if (text.length == 0) {
		console.log('Not sending zero length message');
		return;
	}
	console.log('Sending new message');
	var nickname = docid('nickname').value;
	websocket_send({
		type: 'post',
		message: text,
		nickname: nickname,
	});
	docid('new_message').value = '';
}

// Handler for delete all confirmation dialog
var delete_all_modal = new RModal(
	docid('delete_all_modal'),
);

// handle click to delete all button
function delete_all_click(event) {
	event.preventDefault();
	// console.log('open delete all dialog');
	delete_all_modal.open();
}

function delete_all_confirm(event) {
	event.preventDefault();
	delete_all_modal.close();
	console.log('Deleting all messages');
}

function delete_all_cancel(event) {
	event.preventDefault();
	delete_all_modal.close();
}

var empty_undo_modal = new RModal(
	docid('empty_undo_modal'),
);

// handler for changes to nickname
function nickname_change() {
	var new_nickname = docid('nickname').value;
	console.log('nickname changed to ' + new_nickname);
	localStorage.setItem('nickname', new_nickname);
}

// set up nickname box
function nickname_init() {
	docid('nickname').onchange = nickname_change;
	docid('nickname_clear').onclick = function() {
		docid('nickname').value = '';
		nickname_change();
	}
	if (localStorage.hasOwnProperty('nickname')) {
		docid('nickname').value = localStorage.getItem('nickname');
	}
	// console.log('Initialised nickname');
}

// insert `string` to the users clipboard
function string_to_clipboard(string) {
    function handler (event){
        event.clipboardData.setData('text/plain', string);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
    }

    document.addEventListener('copy', handler, true);
    document.execCommand('copy');
}

// empty the new post box
function clear_message() {
	console.log('Clearing new post');
	docid('new_message').value = '';
}

// handle keypress to new post box - send message if Enter
function new_post_key(event) {
	// console.log('new post code ' + event.keyCode);
	if (event.keyCode == 13) {
		post_click();
	}
}

// Handle click to undo button
function undo_click() {
	get(undo_url)
		.then((data) => {
			console.log('got undo ajax response');
		})
		.catch((err) => {
			console.log('ajax undo failed');
		})
}

// page startup
document.addEventListener('DOMContentLoaded', function() {
	create_websocket();
	nickname_init();
	docid('post').onclick = post_click;
	docid('post_clear').onclick = clear_message;
	docid('new_message').addEventListener('keydown', new_post_key);
	docid('undo').onclick = undo_click;

	docid('delete_all').onclick = delete_all_click;
	// docid('delete_all_confirm').onclick = delete_all_confirm;
	// docid('delete_all_cancel').onclick = delete_all_cancel;

	// I'd prefer to use named callback functions as above, but for some reason
	// the page reloads itself if I do that, so these callbacks are written inline
	docid('delete_all_modal_confirm').onclick = function(event) {
		event.preventDefault();
		delete_all_modal.close();
		console.log('Deleting all');
		websocket_send({
			type: 'delete_all',
		});
	}

	docid('delete_all_modal_cancel').onclick = function(event) {
		event.preventDefault();
		delete_all_modal.close();
	}

	docid('empty_undo').onclick = function(event) {
		event.preventDefault();
		empty_undo_modal.open();
	}
	docid('empty_undo_modal_confirm').onclick = function(event) {
		event.preventDefault();
		empty_undo_modal.close();
		websocket_send({type: 'empty_undo'});
	}
	docid('empty_undo_modal_cancel').onclick = function(event) {
		event.preventDefault();
		empty_undo_modal.close();
	}

}, false);
