import React from 'react'
import "./RoomItem.css"

function RoomItem(props) {
    const {room} = props;
    return (
        <li className='room-item'>
            {room.name}
            <button className='btn btn-primary'>Open Chat</button>
        </li>
    )
}

export default RoomItem;