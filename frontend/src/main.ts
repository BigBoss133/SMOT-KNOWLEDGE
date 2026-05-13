import './app.css'
import App from './App.svelte'
import { mount } from 'svelte'
import { connectWebSocket, loadChatHistory, saveChatHistory } from './lib/stores/app.js'

connectWebSocket()
loadChatHistory()
saveChatHistory()

const app = mount(App, { target: document.getElementById('app')! })

export default app
