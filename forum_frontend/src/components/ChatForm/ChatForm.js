import React, { useEffect, useState, useCallback } from 'react'
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './ChatForm.css'
import { API_URL } from '../../index';
import Spinner from 'react-bootstrap/Spinner';
import APIService from '../APIService/APIService';
import { useNavigate } from 'react-router-dom';

function ChatForm(props) {
    const {show, handleClose, room} = props;
    const room_id = room._id["$oid"];

    const [message, setMessage] = useState("");
    const [messageSent, setMessageSent] = useState(true);
    const [statusCode, setStatusCode] = useState(null);
    const [messagesList, setMessagesList] = useState([]);
    const navigate = useNavigate();

    const getMessagesList = useCallback(async () => {
        try {
            const resp = await APIService.fetchWithAuth(
                `${API_URL}/communications/conversations/${room_id}/messages`,
                {}, navigate);
            // console.log(JSON.parse(resp.data));
            setMessagesList(JSON.parse(resp.data));
        }
        catch (err) {
            console.log("getMessagesList error:", err);
        }
    }, [navigate, room_id]);

    const addLastMessageToList = useCallback(async (message_id) => {
        try {
            const res = await APIService.fetchWithAuth(
                `${API_URL}/communications/messages/${message_id}`,
                {}, navigate
            );
            const last_message = JSON.parse(res.data);
            setMessagesList([...messagesList, last_message]); 
        }
        catch (err) {
            console.log("Error while getting last message", err);
        }
    }, [navigate, messagesList])

    const sendMessage = async (message) => {
        setMessageSent(false);
        const investor_user_id = 3;
        const investor_namespace = "investor";
        const investor_id = 1;

        try {
            const res = await APIService.fetchWithAuth(`${API_URL}/communications/messages/send`, {
                method: 'POST',
                data: {
                    room: room_id,
                    author: {
                        user_id: investor_user_id,
                        namespace: investor_namespace,
                        namespace_id: investor_id
                    },
                    content: message
                }
            });
            setStatusCode(res.status);

        } catch (err) {
            console.error("Error while sending message:", err);
            setStatusCode(-1);
        } finally {
            setMessageSent(true);
        }
        getMessagesList();
    }

    useEffect(() => {
        getMessagesList();
        const chatSocket = new WebSocket(
            'ws://ws/notifications/'
        );
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log(data);
            const new_message_id = null; //from received data
            addLastMessageToList(new_message_id);
        };
        return () => {
            chatSocket.close();
        }
    }, [getMessagesList, addLastMessageToList]);

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>
                    <div className='fs-5'>
                        Chat
                        <span className='text-secondary fst-italic fs-4'>
                            {` ${room.name}`}
                        </span>
                    </div>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {statusCode === 201 ?
                    <div className='alert alert-success'>Message has been sent.</div>
                    : null
                }
                {(statusCode !== 201 & statusCode) ?
                    <div className='alert alert-danger'>Error while sending message.</div>
                    : null
                }
                <div className="messages-list">
                    {messagesList.map(msg => 
                        <div className='msg-content' key={msg._id["$oid"]}>{msg.content}</div>
                    )}
                </div>
                <Form.Control as="textarea" placeholder='Type Message' rows={3} 
                    onChange={e => setMessage(e.target.value)}
                />
            </Modal.Body>
            <Modal.Footer>
                {messageSent ?
                    <Button variant="primary" onClick={() => sendMessage(message)}>
                        Send
                    </Button>
                    : <Spinner animation="border" variant="primary" size="sm"/>
                }
                <Button variant="danger" onClick={handleClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

export default ChatForm