import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './StartChatForm.css'
import { API_URL } from '../../index';
import { useState } from 'react';
import APIService from '../APIService/APIService';

function StartChatForm(props) {
    const {show, handleClose, startup} = props;
    const [message, setMessage] = useState("");
    const [statusCode, setStatusCode] = useState(0);

    const createChatAndSendFirstMessage = async (message) => {
        const investor_user_id = 1;
        const investor_namespace = "investor";
        const investor_id = 1;

        try {
            const new_room = await APIService.fetchWithAuth(`${API_URL}/communications/conversations/create`, {
                method: 'POST',
                data: {
                    participants: [{
                        user_id: investor_user_id,
                        namespace: investor_namespace,
                        namespace_id: investor_id
                    }, {
                        user_id: startup.user,
                        namespace: "startup",
                        namespace_id: startup.startup_id
                    }]
                }
            });

            const response = await APIService.fetchWithAuth(`${API_URL}/communications/messages/send`, {
                method: 'POST',
                data: {
                    room: new_room.data.id,
                    author: {
                        user_id: investor_user_id,
                        namespace: investor_namespace,
                        namespace_id: investor_id
                    },
                    content: message
                }
            });

            setStatusCode(response.status);
        } catch (err) {
            console.error("Error creating chat or sending message:", err);
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
                    <div className='success-msg'>Message has been sent.</div>
                    : null}
                <Form.Control as="textarea" placeholder='Type Message' rows={3} 
                    onChange={e => setMessage(e.target.value)}
                />
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={() => createChatAndSendFirstMessage(message)}>
                    Send
                </Button>
                <Button variant="danger" onClick={handleClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

export default StartChatForm;