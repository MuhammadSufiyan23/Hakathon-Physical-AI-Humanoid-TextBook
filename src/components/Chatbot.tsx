
// import React, { useState, useRef, useEffect } from "react";

// type Message = {
//   role: "user" | "bot";
//   text: string;
//   thinking?: boolean;
// };

// export default function ChatbotUI() {
//   const [open, setOpen] = useState(false); // Ab default closed rahega
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [input, setInput] = useState("");
//   const messagesEndRef = useRef<HTMLDivElement | null>(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const sendMessage = async () => {
//     if (!input.trim()) return;

//     const userText = input.trim();

//     setMessages((prev) => [
//       ...prev,
//       { role: "user", text: userText },
//       { role: "bot", text: "Thinking", thinking: true },
//     ]);

//     setInput("");

//     try {
//       const response = await fetch("https://hakathon-physical-ai-humanoid-textbook-production.up.railway.app/api/v1/query", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           question: userText,
//           selected_text: "",
//         }),
//         signal: AbortSignal.timeout(90000),
//       });

//       if (!response.ok) {
//         throw new Error(`Server error: ${response.status}`);
//       }

//       const data = await response.json();

//       setMessages((prev) =>
//         prev.map((msg, index) =>
//           msg.thinking && index === prev.length - 1
//             ? {
//                 role: "bot",
//                 text:
//                   data.answer ||
//                   data.message ||
//                   data.response ||
//                   data.text ||
//                   "No relevant content found in the book.",
//               }
//             : msg
//         )
//       );
//     } catch (error: any) {
//       let errorText = "❌ Error: Could not connect to the assistant.";

//       if (error.name === "TimeoutError" || error.name === "AbortError") {
//         errorText = "⏳ Response took too long. Please try again.";
//       } else if (error.message.includes("Failed to fetch")) {
//         errorText = "🌐 Cannot reach the server. Check your connection.";
//       }

//       setMessages((prev) =>
//         prev.map((msg, index) =>
//           msg.thinking && index === prev.length - 1
//             ? { role: "bot", text: errorText }
//             : msg
//         )
//       );
//       console.error("Chatbot error:", error);
//     }
//   };

//   return (
//     <>
//       {/* Floating Round Button - Always visible */}
//       <div
//         onClick={() => setOpen(!open)}
//         style={{
//           position: "fixed",
//           bottom: 24,
//           right: 24,
//           width: 64,
//           height: 64,
//           borderRadius: "50%",
//           background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
//           color: "#fff",
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           fontSize: 32,
//           cursor: "pointer",
//           zIndex: 99999,
//           boxShadow: "0 10px 30px rgba(124, 58, 237, 0.4)",
//           transition: "all 0.3s ease",
//           border: "none",
//         }}
//       >
//         {open ? "✖" : "🤖"}
//       </div>

//       {/* Chat Window - Bottom Right Corner (Side par) */}
//       {open && (
//         <div
//           style={{
//             position: "fixed",
//             bottom: 100, // Button ke upar
//             right: 24,
//             width: "380px",
//             height: "560px",
//             background: "#020617",
//             color: "#fff",
//             borderRadius: 20,
//             zIndex: 99998,
//             display: "flex",
//             flexDirection: "column",
//             boxShadow: "0 20px 60px rgba(0,0,0,0.9)",
//             border: "1px solid #1e293b",
//             animation: "slideUp 0.4s ease-out",
//           }}
//         >
//           {/* Header */}
//           <div
//             style={{
//               padding: "18px 20px",
//               borderBottom: "1px solid #1e293b",
//               display: "flex",
//               justifyContent: "space-between",
//               alignItems: "center",
//               flexShrink: 0,
//               borderTopLeftRadius: 20,
//               borderTopRightRadius: 20,
//               background: "linear-gradient(to right, #1e1b4b, #0f172a)",
//             }}
//           >
//             <div>
//               <div style={{ fontWeight: 700, fontSize: 17 }}>
//                 🤖 Book Assistant
//               </div>
//               <div style={{ fontSize: 13, opacity: 0.8 }}>
//                 AI helper for Physical AI & Robotics
//               </div>
//             </div>
//             <button
//               onClick={() => setOpen(false)}
//               style={{
//                 background: "transparent",
//                 border: "none",
//                 color: "#94a3b8",
//                 fontSize: 26,
//                 cursor: "pointer",
//                 padding: "4px",
//               }}
//             >
//               ✕
//             </button>
//           </div>

//           {/* Messages Area */}
//           <div
//             style={{
//               flex: 1,
//               padding: "16px",
//               overflowY: "auto",
//             }}
//           >
//             {messages.length === 0 && (
//               <div
//                 style={{
//                   textAlign: "center",
//                   marginTop: 80,
//                   opacity: 0.7,
//                   fontSize: 15,
//                 }}
//               >
//                 👋 Ask me anything about Physical AI & Robotics
//               </div>
//             )}

//             {messages.map((m, i) => (
//               <div
//                 key={i}
//                 style={{
//                   display: "flex",
//                   justifyContent: m.role === "user" ? "flex-end" : "flex-start",
//                   marginBottom: 16,
//                 }}
//               >
//                 <div
//                   style={{
//                     maxWidth: "80%",
//                     padding: "12px 16px",
//                     borderRadius: 18,
//                     background:
//                       m.role === "user"
//                         ? "#6366f1"
//                         : m.thinking
//                         ? "#1e293b"
//                         : "#1e293b",
//                     border: m.thinking ? "1px dashed #475569" : "none",
//                     fontSize: 14.5,
//                     lineHeight: "1.5",
//                   }}
//                 >
//                   {m.thinking ? (
//                     <>
//                       Thinking
//                       <span className="animate-dots">...</span>
//                     </>
//                   ) : (
//                     m.text
//                   )}
//                 </div>
//               </div>
//             ))}
//             <div ref={messagesEndRef} />
//           </div>

//           {/* Input Area */}
//           <div
//             style={{
//               padding: "16px",
//               borderTop: "1px solid #1e293b",
//               display: "flex",
//               gap: 12,
//               flexShrink: 0,
//             }}
//           >
//             <input
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
//               placeholder="Ask about Physical AI, robotics..."
//               style={{
//                 flex: 1,
//                 padding: "14px 18px",
//                 borderRadius: 16,
//                 background: "#0f172a",
//                 border: "1px solid #334155",
//                 color: "#fff",
//                 outline: "none",
//                 fontSize: 15,
//               }}
//             />
//             <button
//               onClick={sendMessage}
//               style={{
//                 padding: "0 24px",
//                 borderRadius: 16,
//                 background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
//                 color: "#fff",
//                 border: "none",
//                 cursor: "pointer",
//                 fontWeight: 600,
//                 fontSize: 15,
//                 transition: "all 0.2s",
//               }}
//               onMouseOver={(e) => (e.currentTarget.style.opacity = "0.9")}
//               onMouseOut={(e) => (e.currentTarget.style.opacity = "1")}
//             >
//               Send
//             </button>
//           </div>
//         </div>
//       )}

//       {/* Animations */}
//       <style jsx global>{`
//         @keyframes slideUp {
//           from {
//             opacity: 0;
//             transform: translateY(30px);
//           }
//           to {
//             opacity: 1;
//             transform: translateY(0);
//           }
//         }

//         @keyframes dotPulse {
//           0%, 20% { opacity: 0; }
//           40% { opacity: 1; }
//           100% { opacity: 0; }
//         }

//         .animate-dots::after {
//           content: '...';
//           animation: dotPulse 1.5s infinite;
//           display: inline-block;
//           width: 1.8em;
//           text-align: left;
//         }
//       `}</style>
//     </>
//   );
// }






import React, { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "bot";
  text: string;
  thinking?: boolean;
};

export default function ChatbotUI() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userText = input.trim();

    // NEW: Minimum length check – chhote messages block karo
    if (userText.length < 4) {
      setMessages((prev) => [
        ...prev,
        { role: "user", text: userText },
        {
          role: "bot",
          text: "👀 Please ask a proper question with at least 4 characters!\nExample: 'What is Physical AI?' or 'Explain torque control'",
        },
      ]);
      setInput("");
      return;
    }

    // Normal flow
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userText },
      { role: "bot", text: "Thinking", thinking: true },
    ]);

    setInput("");

    try {
      const response = await fetch(
        "https://hakathon-physical-ai-humanoid-textbook-production.up.railway.app/api/v1/query",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: userText,
            selected_text: "",
          }),
          signal: AbortSignal.timeout(90000),
        }
      );

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();

      const botResponse =
        data.answer ||
        data.message ||
        data.response ||
        data.text ||
        "I don't have enough information from the book to answer this question.";

      setMessages((prev) =>
        prev.map((msg, index) =>
          msg.thinking && index === prev.length - 1
            ? { role: "bot", text: botResponse }
            : msg
        )
      );
    } catch (error: any) {
      let errorText = "⚠️ Something went wrong. Please try a more specific question about Physical AI or Robotics.";

      if (error.name === "TimeoutError" || error.name === "AbortError") {
        errorText = "⏳ Response took too long. Please try again with a shorter question.";
      } else if (error.message.includes("Failed to fetch")) {
        errorText = "🌐 Unable to reach the server right now. Please check your internet or try later.";
      }

      setMessages((prev) =>
        prev.map((msg, index) =>
          msg.thinking && index === prev.length - 1
            ? { role: "bot", text: errorText }
            : msg
        )
      );

      console.error("Chatbot API Error:", error);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          width: 64,
          height: 64,
          borderRadius: "50%",
          background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
          color: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 32,
          cursor: "pointer",
          zIndex: 99999,
          boxShadow: "0 10px 30px rgba(124, 58, 237, 0.4)",
          transition: "all 0.3s ease",
          border: "none",
        }}
      >
        {open ? "✖" : "🤖"}
      </div>

      {/* Chat Window - Bottom Right */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 100,
            right: 24,
            width: "380px",
            height: "560px",
            background: "#020617",
            color: "#fff",
            borderRadius: 20,
            zIndex: 99998,
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 20px 60px rgba(0,0,0,0.9)",
            border: "1px solid #1e293b",
            animation: "slideUp 0.4s ease-out",
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "18px 20px",
              borderBottom: "1px solid #1e293b",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexShrink: 0,
              borderTopLeftRadius: 20,
              borderTopRightRadius: 20,
              background: "linear-gradient(to right, #1e1b4b, #0f172a)",
            }}
          >
            <div>
              <div style={{ fontWeight: 700, fontSize: 17 }}>
                🤖 Book Assistant
              </div>
              <div style={{ fontSize: 13, opacity: 0.8 }}>
                AI helper for Physical AI & Robotics
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "#94a3b8",
                fontSize: 26,
                cursor: "pointer",
                padding: "4px",
              }}
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: "16px",
              overflowY: "auto",
            }}
          >
            {messages.length === 0 && (
              <div
                style={{
                  textAlign: "center",
                  marginTop: 80,
                  opacity: 0.7,
                  fontSize: 15,
                  lineHeight: "1.6",
                }}
              >
                👋 Ask me anything about Physical AI & Robotics
                <br />
                <small style={{ fontSize: 12, opacity: 0.6 }}>
                  (Minimum 4 characters required)
                </small>
              </div>
            )}

            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: 16,
                }}
              >
                <div
                  style={{
                    maxWidth: "85%",
                    padding: "12px 16px",
                    borderRadius: 18,
                    background:
                      m.role === "user"
                        ? "#6366f1"
                        : m.thinking
                        ? "#1e293b"
                        : "#1e293b",
                    border: m.thinking ? "1px dashed #475569" : "none",
                    fontSize: 14.5,
                    lineHeight: "1.5",
                    whiteSpace: "pre-wrap", // \n ke liye support
                  }}
                >
                  {m.thinking ? (
                    <>
                      Thinking
                      <span className="animate-dots">...</span>
                    </>
                  ) : (
                    m.text
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div
            style={{
              padding: "16px",
              borderTop: "1px solid #1e293b",
              display: "flex",
              gap: 12,
              flexShrink: 0,
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Ask about Physical AI, humanoid robots... (min 4 chars)"
              style={{
                flex: 1,
                padding: "14px 18px",
                borderRadius: 16,
                background: "#0f172a",
                border: "1px solid #334155",
                color: "#fff",
                outline: "none",
                fontSize: 15,
              }}
            />
            <button
              onClick={sendMessage}
              style={{
                padding: "0 24px",
                borderRadius: 16,
                background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: 15,
                transition: "all 0.2s",
              }}
              onMouseOver={(e) => (e.currentTarget.style.opacity = "0.9")}
              onMouseOut={(e) => (e.currentTarget.style.opacity = "1")}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Animations */}
      <style jsx global>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes dotPulse {
          0%, 20% { opacity: 0; }
          40% { opacity: 1; }
          100% { opacity: 0; }
        }

        .animate-dots::after {
          content: '...';
          animation: dotPulse 1.5s infinite;
          display: inline-block;
          width: 1.8em;
          text-align: left;
        }
      `}</style>
    </>
  );
}

