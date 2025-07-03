import { VoiceInterface } from './components/VoiceInterface'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full p-6">
        <h1 className="text-3xl font-bold text-center mb-8">
          Voice Calendar Agent
        </h1>
        <VoiceInterface />
      </div>
    </div>
  )
}

export default App