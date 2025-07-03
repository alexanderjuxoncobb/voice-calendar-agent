import { useVoiceSession } from '../hooks/useVoiceSession'

export function VoiceInterface() {
  const { isConnected, isRecording, startRecording, stopRecording } = useVoiceSession()

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="text-center mb-6">
        <p className="text-sm text-gray-600">
          {isConnected ? 'Connected' : 'Disconnected'}
        </p>
      </div>
      
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`
          w-full py-4 px-6 rounded-lg font-medium transition-all
          ${isRecording 
            ? 'bg-red-500 hover:bg-red-600 text-white' 
            : 'bg-blue-500 hover:bg-blue-600 text-white'
          }
        `}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      
      <p className="text-center mt-4 text-sm text-gray-500">
        Click to speak with your calendar assistant
      </p>
    </div>
  )
}