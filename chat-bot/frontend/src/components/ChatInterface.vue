<template>
  <div class="chat-container">
    <h1>Dummy Chat</h1>

    <div class="chat-box" ref="chatBox">
      <div v-for="(message, index) in messages" :key="index" class="message">
        <div
          :class="{
            'message-user': message.role === 'user',
            'message-bot': message.role === 'bot',
          }"
        >
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="input-container">
      <input
        v-model="prompt"
        type="text"
        placeholder="Type your prompt..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      prompt: '',
      messages: [],
    };
  },
  methods: {
    async sendMessage() {
      if (this.prompt.trim() === '') return;

      this.messages.push({ role: 'user', content: this.prompt });

      try {
        const response = await axios.post('http://localhost:3000/generate', {
          prompt: this.prompt,
        });

        // Add bot's response to chat
        this.messages.push({ role: 'bot', content: response.data.randomSentence });
      } catch (error) {
        this.messages.push({ role: 'bot', content: 'Error: Could not connect to server.' });
      }

      // Clear the input field
      this.prompt = '';
    },
    scrollToBottom() {
      const chatBox = this.$refs.chatBox;
      chatBox.scrollTop = chatBox.scrollHeight;
    },
  },
  updated() {
    this.scrollToBottom();
  },
};
</script>

<style>

h1 {
  text-align: center;
  color: #007bff
}

.chat-container {
  max-width: 60%;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
}

.chat-box {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 10px;
}

.message {
  margin-bottom: 10px;
}

.message-user {
  text-align: right;
  color: blue;
  font-weight: bold;
}

.message-bot {
  text-align: left;
  color: rgb(34, 34, 34);
  font-style: italic;
}

.input-container {
  display: flex;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-right: 10px;
}

input:focus {
  accent-color: #3535d3;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
