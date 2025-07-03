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
      // TODO: Get assistant ID from backend
      const assistantId = 'your_assistant_id'
      
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