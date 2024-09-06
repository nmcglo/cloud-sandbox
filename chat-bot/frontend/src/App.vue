<template>
  <ChatInterface msg="Welcome to Your Vue.js App"/>
</template>

<script>
import ChatInterface from './components/ChatInterface.vue'

export default {
  name: 'App',
  components: {
    ChatInterface
  }
}
</script>

<style>

:root {
  --background: hsl(240, 80%, 10%);
}

body {
    background:
        radial-gradient(
            100vmax 100vmax at 0% 0%,
            hsla(240, 100%, 2%, 0.9) 0%,
            hsla(240, 100%, 2%, 0) 95%),
        var(--background);
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #dbdbdb;
  margin-top: 60px;
}
</style>
