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
    const {show, handleClose, room, chatSocket} = props;
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
            setMessagesList(messagesList => [...messagesList, last_message]); 
        }
        catch (err) {
            console.log("Error while getting last message", err);
        }
    }, [navigate])

    const sendMessage = async (message) => {
        setMessageSent(false);
        const namespaceInfo = APIService.getNamespaceInfoFromToken();

        try {
            const res = await APIService.fetchWithAuth(`${API_URL}/communications/messages/send`, {
                method: 'POST',
                data: {
                    room: room_id,
                    author: namespaceInfo,
                    content: message
                }
            });
            setStatusCode(res.status);
            if (res.status === 201){
                const new_message = JSON.parse(res.data);
                setMessagesList([...messagesList, new_message]);
            }

        } catch (err) {
            console.error("Error while sending message:", err);
            setStatusCode(-1);
        } finally {
            setMessageSent(true);
        }
    }

    useEffect(() => {
        if (typeof chatSocket === 'object'){
            getMessagesList();
            chatSocket.onopen = () => {
                console.log("WS connection has been opend!");
            }
            chatSocket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                const msg = data.message;
                const new_message_id = msg.split("Message: ")[1].split(" ")[0]
                addLastMessageToList(new_message_id);
            };
            chatSocket.onclose = () => {
                console.log("WS connection has been closed!");
            }
            return () => {
                console.log("removed ChatForm");
                chatSocket.close();
            }
        }
    }, [chatSocket, getMessagesList, addLastMessageToList]);

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