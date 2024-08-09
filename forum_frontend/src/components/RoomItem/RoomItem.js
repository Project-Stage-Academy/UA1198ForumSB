import React, {useState} from 'react'
import "./RoomItem.css"
import ChatForm from '../ChatForm/ChatForm';


function RoomItem(props) {
    const {room} = props;

    const [showForm, setShowForm] = useState(false);
    const handleClose = () => setShowForm(false);
    const handleShow = () => setShowForm(true);

    return (
        <li className='room-item'>
            {room.name}
            <button className='btn btn-primary' onClick={handleShow}>
                Open Chat
            </button>
            <ChatForm show={showForm} room={room} handleClose={handleClose}/>
        </li>
    )
}

export default RoomItem;