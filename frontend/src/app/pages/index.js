export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-primary text-white py-4 text-center text-2xl font-semibold">
        Aven AI Support Agent
      </header>

      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="flex items-start space-x-3">
          <img src="/bot.svg" alt="Bot" className="w-10 h-10" />
          <div className="bg-white rounded-lg shadow p-3">
            <p>Hello! I'm the Aven support AI. How can I assist you today?</p>
          </div>
        </div>

        <div className="flex items-start space-x-3 justify-end">
          <div className="bg-secondary text-white rounded-lg shadow p-3">
            <p>How do I reset my password?</p>
          </div>
                <img src="/user.svg" alt="User" className="w-10 h-10" />
              </div>
            </main>
          </div>
  )
}
