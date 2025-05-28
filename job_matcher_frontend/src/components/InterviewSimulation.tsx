import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import '../styles/InterviewSimulation.css';
import deleteIcon from '../assets/delete.svg';
import { format, parseISO } from 'date-fns';
import ReactMarkdown from 'react-markdown';

interface Interview {
  id: string;
  title: string;
  last_updated: string;
}

interface Message {
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

const InterviewSimulation = () => {
  const { user } = useAuth();
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [selectedInterviewId, setSelectedInterviewId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);
  const [isLoadingInterviews, setIsLoadingInterviews] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();

    if (selectedInterviewId) {
        scrollToBottom();
    }
  }, [messages, selectedInterviewId]);

  useEffect(() => {
    const loadInterviews = async () => {
      try {
        setIsLoadingInterviews(true);
        const token = await user?.getIdToken();
        const response = await axios.get('http://127.0.0.1:8000/interviews/user_interviews', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setInterviews(
          response.data.interviews.sort(
            (a: Interview, b: Interview) =>
              new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime()
          )
        );

        if (location.state?.newInterviewId) {
            setSelectedInterviewId(location.state.newInterviewId);
            setMessages([{
              content: location.state.initialMessage,
              role: 'assistant',
              timestamp: new Date().toISOString()
            }]);
            // Clear navigation state
            navigate(location.pathname, { state: {}, replace: true });
          }
      } catch (error) {
        console.error('Error loading interviews:', error);
      } finally {
        setIsLoadingInterviews(false);
      }
    };
    loadInterviews();
  }, [user, location, navigate]);

  useEffect(() => {
    const loadMessages = async () => {
      if (!selectedInterviewId) return;
      
      try {
        const token = await user?.getIdToken();
        const response = await axios.get(
          `http://127.0.0.1:8000/interviews/messages/${selectedInterviewId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setMessages(response.data.messages);
        
        // Force scroll after initial load
        setTimeout(scrollToBottom, 100);
      } catch (error) {
        console.error('Error loading messages:', error);
      }
    };
    loadMessages();
  }, [selectedInterviewId, user]);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedInterviewId) return;

    const userMessage = newMessage;
    setNewMessage('');
    setMessages(prev => [
      ...prev, 
      {
        content: userMessage,
        role: 'user',
        timestamp: new Date().toISOString()
      }
    ]);

    try {
      setIsLoading(true);
      const token = await user?.getIdToken();
      const response = await axios.post(
        `http://127.0.0.1:8000/interviews/continue/${selectedInterviewId}`,
        { user_message: userMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setMessages(prev => [
        ...prev,
        {
          content: response.data.ai_response,
          role: 'assistant',
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteInterview = async (interviewId: string) => {
    try {
      const token = await user?.getIdToken();
      await axios.delete(
        `http://127.0.0.1:8000/interviews/delete/${interviewId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInterviews(prev => prev.filter(i => i.id !== interviewId));
      if (selectedInterviewId === interviewId) {
        setSelectedInterviewId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting interview:', error);
    }
  };

  const formatDate = (isoString: string) => {
    return format(parseISO(isoString), 'PPp');
  };

  return (
    <div className="interview-container">
      {/* Sidebar */}
      <button
          className="sidebar-toggle"
          onClick={() => setIsSidebarVisible(!isSidebarVisible)}
        >
          {isSidebarVisible ? 'Close History' : 'Open History'}
        </button>
      <div className={`interview-sidebar ${isSidebarVisible ? 'visible' : ''}`}>
        <div className="sidebar-header">
          <h3>History</h3>
        </div>
        <div className="interview-list">
          {interviews.map(interview => (
            <div 
              key={interview.id}
              className={`interview-item ${selectedInterviewId === interview.id ? 'selected' : ''}`}
              onClick={() => setSelectedInterviewId(interview.id)}
            >
              <div className="interview-item-header">
                <span className="interview-item-title">
                  {interview.title || 'Unknown Title'}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteInterview(interview.id);
                  }}
                >
                  <img src={deleteIcon} alt="Delete"/>
                </button>
              </div>
              <span>{formatDate(interview.last_updated)}</span>
            </div>
          ))}
          { interviews.length === 0 && !isLoadingInterviews && (
            <>
              <h4>No interviews started yet</h4>
              <p>Start a new interview by going to a job posting and clicking Practice Interview</p>
            </>
            )}
        </div>
      </div>

      {/* Chat Section */}
      <div className="chat-container">
        {selectedInterviewId ? (
          <>
            <div className="chat-messages">
                {messages.slice(2).map((message, index) => (
                    <div key={index} className={`message ${message.role}`}>
                    <div className="message-content">
                      {message.role === 'assistant' ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message assistant">
                    <div className="message-content loading">
                        <div className="typing-indicator">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                        </div>
                    </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message here..."
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !newMessage.trim()}
              >
                Send
              </button>
            </div>
          </>
        ) : (
          <div className="chat-placeholder">
            <p>Select an interview from the History bar or start a new one</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewSimulation;
