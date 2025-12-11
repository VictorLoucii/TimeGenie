// TimeGenie/frontend/src/App.jsx
import { useState } from 'react'
import axios from 'axios'
import './App.css'

// Define the structure exactly like the screenshot
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const TIME_SLOTS = [
  "8:40 - 9:40", "9:40 - 10:40", "10:40 - 11:40", "11:40 - 12:40",
  "1:00 - 2:00", "2:00 - 3:00", "3:00 - 4:00", "4:00 - 5:00"
];

function App() {
  const [scheduleData, setScheduleData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    setLoading(true); setError(null); setScheduleData([]);
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/generate/')
      if (response.data.status === 'success') {
        setScheduleData(response.data.data)
      } else {
        setError(response.data.message || 'Error')
      }
    } catch (err) {
      setError('Server connection failed. Is Django running?')
    } finally {
      setLoading(false)
    }
  }

  // Helper: Find all classes occurring at a specific Day & Slot index
  const getClassesForSlot = (day, slotIndex) => {
    return scheduleData.filter(item => item.day === day && item.sort_slot_idx === slotIndex);
  };

  return (
    <div className="app-container">
      <header>
        <h1>🧞‍♂️ TimeGenie</h1>
        <p>AI-Powered Master Schedule</p>
      </header>

      <div className="controls">
        <button onClick={handleGenerate} disabled={loading} className="generate-btn">
          {loading ? '✨ Genie is Working...' : 'Generate Timetable'}
        </button>
      </div>

      {error && <div className="error-msg">⚠️ {error}</div>}

      {scheduleData.length > 0 && (
        <div className="grid-container">
          <table className="timetable-grid">
            <thead>
              <tr>
                <th className="corner-cell">Day / Time</th>
                {TIME_SLOTS.map((time, index) => (
                  <th key={index}>{time}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DAYS.map(day => (
                <tr key={day}>
                  <td className="day-header">{day}</td>
                  {TIME_SLOTS.map((_, slotIndex) => {
                    const classes = getClassesForSlot(day, slotIndex);
                    return (
                      <td key={slotIndex} className="slot-cell">
                        {classes.length === 0 ? (
                          <span className="empty-slot">-</span>
                        ) : (
                          <div className="cell-content">
                            {classes.map((cls, idx) => (
                              <div key={idx} className={`class-block ${cls.type === 'LAB' ? 'lab-block' : 'theory-block'}`}>
                                <div className="course-code">{cls.course}</div>
                                <div className="details">
                                  <span className="group">{cls.group}</span>
                                  <span className="room">({cls.room})</span>
                                </div>
                                <div className="faculty">{cls.faculty}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <footer className="app-footer">
        <p>Developed by Team Code Catalyst</p>
      </footer>
    </div>
  )
}

export default App