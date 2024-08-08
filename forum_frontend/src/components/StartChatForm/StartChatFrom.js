import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './StartChatForm.css'

function StartChatForm(props) {
    const {show, handleClose, startup_name} = props;

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>
                    <div className='fs-5'>
                        Start chat with
                        <span className='text-secondary fst-italic fs-4'>
                            {` ${startup_name} `}
                        </span>
                        startup
                    </div>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form.Control as="textarea" placeholder='Type Message' rows={3}/>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary">
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