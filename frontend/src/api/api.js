
// export const getAIMessage = async (userQuery) => {

//   const message = 
//     {
//       role: "assistant",
//       content: "Connect your backend here...."
//     }

//   return message;
// };

export const getAIMessage = async (userQuery) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/get_ai_message', {
    // const response = await fetch('https://website-chatbot-79i9.onrender.com/api/get_ai_message', {
      
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ userQuery })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
    return { role: 'assistant', content: 'Error: Unable to connect to the backend' };
  }
};



