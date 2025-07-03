import { useState, useEffect } from 'react'
import Vapi from '@vapi-ai/web'
import { useVapiStore } from '../stores/vapiStore'

export function useVoiceSession() {
  const [isConnected, setIsConnected] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const { vapi, initializeVapi } = useVapiStore()

  useEffect(() => {
    initializeVapi()
  }, [initializeVapi])

  const startRecording = async () => {
    if (!vapi) return

    try {
      const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID
      
      if (!assistantId) {
        console.error('VAPI Assistant ID not found')
        return
      }
      
      await vapi.start(assistantId)
      setIsRecording(true)
      setIsConnected(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = async () => {
    if (!vapi) return

    try {
      vapi.stop()
      setIsRecording(false)
    } catch (error) {
      console.error('Failed to stop recording:', error)
    }
  }

  return {
    isConnected,
    isRecording,
    startRecording,
    stopRecording
  }
}