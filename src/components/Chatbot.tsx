
// import React, { useState, useRef, useEffect } from "react";

// type Message = {
//   role: "user" | "bot";
//   text: string;
//   thinking?: boolean;
// };

// export default function ChatbotUI() {
//   const [open, setOpen] = useState(false);
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
//       {/* Floating Button - Bottom Right */}
//       <div
//         onClick={() => setOpen(true)}
//         style={{
//           position: "fixed",
//           bottom: 24,
//           right: 24,
//           width: 60,
//           height: 60,
//           borderRadius: "50%",
//           background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
//           color: "#fff",
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           fontSize: 28,
//           cursor: "pointer",
//           zIndex: 9999,
//           boxShadow: "0 8px 25px rgba(124,58,237,.5)",
//         }}
//       >
//         🤖
//       </div>

//       {/* Chat Window - Center mein, content ke upar overlap na kare */}
//       {open && (
//         <div
//           style={{
//             position: "fixed",
//             top: "50%",
//             left: "50%",
//             transform: "translate(-50%, -50%)",
//             width: "90%",
//             maxWidth: 440,
//             height: "80vh",
//             maxHeight: 600,
//             background: "#020617",
//             color: "#fff",
//             borderRadius: 16,
//             zIndex: 99999,
//             display: "flex",
//             flexDirection: "column",
//             boxShadow: "0 20px 60px rgba(0,0,0,.8)",
//             border: "1px solid #1e293b",
//           }}
//         >
//           {/* Header */}
//           <div
//             style={{
//               padding: "16px",
//               borderBottom: "1px solid #1e293b",
//               display: "flex",
//               justifyContent: "space-between",
//               alignItems: "center",
//               flexShrink: 0,
//             }}
//           >
//             <div>
//               <div style={{ fontWeight: 600, fontSize: 16 }}>
//                 🤖 Book Assistant
//               </div>
//               <div style={{ fontSize: 12, opacity: 0.7 }}>
//                 AI helper for Physical AI & Robotics
//               </div>
//             </div>
//             <button
//               onClick={() => setOpen(false)}
//               style={{
//                 background: "transparent",
//                 border: "none",
//                 color: "#94a3b8",
//                 fontSize: 20,
//                 cursor: "pointer",
//                 padding: "4px",
//               }}
//             >
//               ✖
//             </button>
//           </div>

//           {/* Messages Area */}
//           <div
//             style={{
//               flex: 1,
//               padding: "12px 16px",
//               overflowY: "auto",
//             }}
//           >
//             {messages.length === 0 && (
//               <div
//                 style={{
//                   fontSize: 14,
//                   opacity: 0.6,
//                   textAlign: "center",
//                   marginTop: 60,
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
//                   marginBottom: 12,
//                 }}
//               >
//                 <div
//                   style={{
//                     maxWidth: "80%",
//                     padding: "10px 14px",
//                     borderRadius: 16,
//                     background:
//                       m.role === "user"
//                         ? "#4f46e5"
//                         : m.thinking
//                         ? "#1e293b"
//                         : "#1e293b",
//                     border: m.thinking ? "1px dashed #475569" : "none",
//                     fontSize: 14,
//                     fontStyle: m.thinking ? "italic" : "normal",
//                     opacity: m.thinking ? 0.8 : 1,
//                   }}
//                 >
//                   {m.thinking ? (
//                     <>
//                       Thinking
//                       <span
//                         style={{
//                           display: "inline-block",
//                           width: "1.8em",
//                           textAlign: "left",
//                         }}
//                       >
//                         <span className="animate-dots">...</span>
//                       </span>
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
//               padding: "12px 16px",
//               borderTop: "1px solid #1e293b",
//               display: "flex",
//               gap: 10,
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
//                 padding: "12px 16px",
//                 borderRadius: 12,
//                 background: "#0f172a",
//                 border: "1px solid #1e293b",
//                 color: "#fff",
//                 outline: "none",
//                 fontSize: 14,
//               }}
//             />
//             <button
//               onClick={sendMessage}
//               style={{
//                 padding: "0 20px",
//                 borderRadius: 12,
//                 background: "#7c3aed",
//                 color: "#fff",
//                 border: "none",
//                 cursor: "pointer",
//                 fontSize: 14,
//                 fontWeight: 600,
//               }}
//             >
//               Send
//             </button>
//           </div>
//         </div>
//       )}

//       {/* Animated dots CSS */}
//       <style jsx global>{`
//         @keyframes dotPulse {
//           0%, 20% { opacity: 0; }
//           40% { opacity: 1; }
//           100% { opacity: 0; }
//         }
//         .animate-dots::after {
//           content: '...';
//           animation: dotPulse 1.5s infinite;
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
  const [open, setOpen] = useState(false); // Ab default closed rahega
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userText = input.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", text: userText },
      { role: "bot", text: "Thinking", thinking: true },
    ]);

    setInput("");

    try {
      const response = await fetch("https://hakathon-physical-ai-humanoid-textbook-production.up.railway.app/api/v1/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userText,
          selected_text: "",
        }),
        signal: AbortSignal.timeout(90000),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) =>
        prev.map((msg, index) =>
          msg.thinking && index === prev.length - 1
            ? {
                role: "bot",
                text:
                  data.answer ||
                  data.message ||
                  data.response ||
                  data.text ||
                  "No relevant content found in the book.",
              }
            : msg
        )
      );
    } catch (error: any) {
      let errorText = "❌ Error: Could not connect to the assistant.";

      if (error.name === "TimeoutError" || error.name === "AbortError") {
        errorText = "⏳ Response took too long. Please try again.";
      } else if (error.message.includes("Failed to fetch")) {
        errorText = "🌐 Cannot reach the server. Check your connection.";
      }

      setMessages((prev) =>
        prev.map((msg, index) =>
          msg.thinking && index === prev.length - 1
            ? { role: "bot", text: errorText }
            : msg
        )
      );
      console.error("Chatbot error:", error);
    }
  };

  return (
    <>
      {/* Floating Round Button - Always visible */}
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

      {/* Chat Window - Bottom Right Corner (Side par) */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 100, // Button ke upar
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

          {/* Messages Area */}
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
                }}
              >
                👋 Ask me anything about Physical AI & Robotics
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
                    maxWidth: "80%",
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

          {/* Input Area */}
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
              placeholder="Ask about Physical AI, robotics..."
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