import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './StartChatForm.css'
import { API_URL } from '../../index';
import { useState } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import APIService from '../APIService/APIService';

function StartChatForm(props) {
    const {show, handleClose, startup, setIsContacted} = props;
    const [message, setMessage] = useState("");
    const [messageSent, setMessageSent] = useState(true);
    const [statusCode, setStatusCode] = useState(null);

    const createChatAndSendFirstMessage = async (message) => {
        setMessageSent(false);
        const namespaceInfo = APIService.getNamespaceInfoFromToken();
        
        if (!namespaceInfo) {
            setStatusCode(403);
            setMessageSent(true);
            return;
        }

        const startupInfo = {
            user_id: startup.user,
            namespace: "startup",
            namespace_id: startup.startup_id
        };

        try {
            const new_room = await APIService.fetchWithAuth(`${API_URL}/communications/conversations/create`, {
                method: 'POST',
                data: {
                    participants: [namespaceInfo, startupInfo]
                }
            });
            const response = await APIService.fetchWithAuth(`${API_URL}/communications/messages/send`, {
                method: 'POST',
                data: {
                    room: new_room.data.id,
                    author: namespaceInfo,
                    content: message
                }
            });
            setStatusCode(response.status);
            if (response.status === 201) {
                setIsContacted(true);
            }
        } catch (err) {
            console.error("Error creating chat or sending message:", err);
            setStatusCode(-1);
        } finally {
            setMessageSent(true)
        }
    }

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>
                    <div className='fs-5'>
                        Start chat with
                        <span className='text-secondary fst-italic fs-4'>
                            {` ${startup.name} `}
                        </span>
                        startup
                    </div>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {statusCode === 201 ?
                    <div className='alert alert-success'>Message has been sent.</div>
                    : null}
                {statusCode === 403 ?
                    <div className='alert alert-danger'>You must be an investor to send a message.</div>
                    : null}
                {(statusCode !== 201 && statusCode !== 403 && statusCode) ?
                    <div className='alert alert-danger'>Error while creating chat or sending message.</div>
                    : null}
                <Form.Control as="textarea" placeholder='Type Message' rows={3} 
                    onChange={e => setMessage(e.target.value)}
                />
            </Modal.Body>
            <Modal.Footer>
                {messageSent ?
                    <Button variant="primary"
                        onClick={() => createChatAndSendFirstMessage(message)}
                    >
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

export default StartChatForm;