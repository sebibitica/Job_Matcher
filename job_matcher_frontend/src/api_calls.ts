// const fetchInterviews = async () => {
//     try {
//       const token = await user?.getIdToken();
//       const response = await axios.get('http://127.0.0.1:8000/interviews/user_interviews', {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       return response.data.interviews;
//     } catch (error) {
//       console.error('Error fetching interviews:', error);
//     }
//   };

//   const initiateInterview = async () => {
//     try {
//       const jobId = "job_1"; // Replace with actual job ID
//       const jobDescription = "We are hiring a Sales Associate to assist customers, manage transactions, and maintain store displays. Strong communication and customer service skills are essential"
//       const token = await user?.getIdToken();
//       const response = await axios.post(
//         `http://127.0.0.1:8000/interviews/initiate/${jobId}`,
//         { job_title: "Sale Associate Junior",
//           job_description: jobDescription },
//         { headers: { Authorization: `Bearer ${token}` } }
//       );
//       return response.data;
//     } catch (error) {
//       console.error('Error starting interview:', error);
//       throw error;
//     }
//   };
  
//   // Continue existing interview
//   const continueInterview = async () => {
//     try {
//       const interviewId = "daf0e513-dfcb-4640-a990-c1a5ab30bf0b"; // Replace with actual interview ID
//       const userMessage = "Can you tell me about this field?";
//       const token = await user?.getIdToken();
//       const response = await axios.post(
//         `http://127.0.0.1:8000/interviews/continue/${interviewId}`,
//         { user_message: userMessage },
//         { headers: { Authorization: `Bearer ${token}` } }
//       );
//       return response.data;
//     } catch (error) {
//       console.error('Error continuing interview:', error);
//       throw error;
//     }
//   };

//   const deleteInterview = async () => {
//     try {
//       const interviewId = "job_2"; // Replace with actual interview ID
//       const token = await user?.getIdToken();
//       await axios.delete(
//         `http://127.0.0.1:8000/interviews/delete/${interviewId}`,
//         { headers: { Authorization: `Bearer ${token}` } }
//       );
//       return true;
//     } catch (error) {
//       console.error('Error deleting interview:', error);
//       throw error;
//     }
//   };

//   // Load interview messages
//   const fetchInterviewMessages = async () => {
//     try {
//       const interviewId = "daf0e513-dfcb-4640-a990-c1a5ab30bf0b"; // Replace with actual interview ID
//       const token = await user?.getIdToken();
//       const response = await axios.get(
//         `http://127.0.0.1:8000/interviews/messages/${interviewId}`,
//         { headers: { Authorization: `Bearer ${token}` } }
//       );
//       return response.data.messages;
//     } catch (error) {
//       console.error('Error loading messages:', error);
//       throw error;
//     }
//   };