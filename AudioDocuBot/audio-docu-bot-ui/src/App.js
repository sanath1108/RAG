import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [userId, setUserId] = useState('');
  const [files, setFiles] = useState([]);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [responses, setResponses] = useState([]);
  const [userText, setUserText] = useState(''); // State to store user input text

  // Handle user ID input
  const handleUserIdChange = (e) => setUserId(e.target.value);

  // Handle file selection
  const handleFileChange = (e) => setFiles([...e.target.files]);

  // Start conversation
  const startConversation = async () => {
    console.log('Start conversation triggered!');
    try {
      if (!userId) {
        alert('Please enter a unique user ID.');
        return;
      }

      const formData = new FormData();
      formData.append('user_id', userId); // Append user_id as form data

      const response = await axios.post(
        'http://127.0.0.1:8000/start-conversation',
        formData, // Send as form data
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setConversationStarted(true);
      alert(response.data.message);
    } catch (error) {
      console.error('Error starting conversation:', error);
    }
  };

  // End conversation
  const endConversation = async () => {
    try {
      if (!userId) {
        alert('Please enter a unique user ID.');
        return;
      }

      // Ensure user_id is sent as JSON
      const response = await axios.post(
        'http://127.0.0.1:8000/end-conversation',
        { user_id: userId }, // Send the user_id as JSON
        { headers: { 'Content-Type': 'application/json' } } // Correct content type for JSON
      );
      setConversationStarted(false);
      alert(response.data.message);
    } catch (error) {
      console.error('Error ending conversation:', error);
    }
  };

  // Handle file upload
  const handleFileUpload = async (e) => {
    e.preventDefault();

    try {
      if (!userId) {
        alert('Please enter a unique user ID.');
        return;
      }

      const formData = new FormData();
      files.forEach((file) => formData.append('file', file));
      formData.append('user_id', userId); // Append user_id as form data

      const response = await axios.post(
        'http://127.0.0.1:8000/process-file',
        formData, // Send as form data
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      alert(response.data.message);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  // Handle user input text and send it to the backend for a response
  const handleSendText = async () => {
    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/get-llm-response',
        {
          user_id: userId,
          user_text: userText, // Corrected here
        }
      );
      setResponses((prev) => [
        ...prev,
        { user_text: userText, llm_response: response.data.llm_response },
      ]);
      setUserText(''); // Clear user input after sending
    } catch (error) {
      console.error('Error getting LLM response:', error);
    }
  };

  // Handle user text input change
  const handleUserTextChange = (e) => setUserText(e.target.value);

  return (
    <div className="App">
      <h1>AudioDocuBot</h1>

      {/* User ID Input */}
      <div>
        <label>Enter Unique User ID: </label>
        <input type="text" value={userId} onChange={handleUserIdChange} />
      </div>

      {/* Start and End Conversation Buttons */}
      <div>
        <button onClick={startConversation} disabled={conversationStarted}>
          Start Conversation
        </button>
        <button onClick={endConversation} disabled={!conversationStarted}>
          End Conversation
        </button>
      </div>

      {/* File Upload Form */}
      <form onSubmit={handleFileUpload}>
        <input type="file" multiple onChange={handleFileChange} />
        <button type="submit">Upload Files</button>
      </form>

      {/* User Text Input and Send Button */}
      <div>
        <textarea
          value={userText}
          onChange={handleUserTextChange}
          placeholder="Type your message"
        />
        <button onClick={handleSendText}>Send</button>
      </div>

      {/* Display Responses */}
      <div>
        <h2>Conversation:</h2>
        {responses.map((response, index) => (
          <div key={index}>
            <p>
              <strong>User:</strong> {response.user_text}
            </p>
            <p>
              <strong>Bot:</strong> {response.llm_response}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
