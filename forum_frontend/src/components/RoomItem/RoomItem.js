import React, {useState} from 'react'
import "./RoomItem.css"
import ChatForm from '../ChatForm/ChatForm';
import APIService from '../APIService/APIService';


function RoomItem(props) {
    const {room} = props;
    const [chatSocket, setChatSocket] = useState(0);
    const [showForm, setShowForm] = useState(false);

    const handleShow = () => {
        setShowForm(true);
        setChatSocket(new WebSocket(
            `ws://localhost:8000/ws/notifications/${APIService.getAccessToken()}`, 
        ));
    }
    const handleClose = () => {
        chatSocket.close();
        setShowForm(false);
    }

    return (
        <li className='room-item'>
            {room.name}
            <button className='btn btn-primary' onClick={handleShow}>
                Open Chat
            </button>
            <ChatForm 
                show={showForm}
                room={room}
                handleClose={handleClose}
                chatSocket={chatSocket}
            />
        </li>
    )
}

export default RoomItem;