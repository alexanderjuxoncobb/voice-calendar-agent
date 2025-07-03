import { create } from 'zustand'
import Vapi from '@vapi-ai/web'

interface VapiState {
  vapi: Vapi | null
  initializeVapi: () => void
}

export const useVapiStore = create<VapiState>((set) => ({
  vapi: null,
  
  initializeVapi: () => {
    const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY
    
    if (!publicKey) {
      console.error('VAPI public key not found')
      return
    }
    
    const vapiInstance = new Vapi(publicKey)
    
    // Set up event listeners
    vapiInstance.on('call-start', () => {
      console.log('Call started')
    })
    
    vapiInstance.on('call-end', () => {
      console.log('Call ended')
    })
    
    vapiInstance.on('message', (message) => {
      console.log('VAPI message:', message)
    })
    
    set({ vapi: vapiInstance })
  }
}))