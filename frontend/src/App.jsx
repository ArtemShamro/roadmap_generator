import { useContext, useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { AuthContext } from "./Context";
import InputForm from "./components/InputForm/InputForm";
import IntroSection from "./components/IntroSection";
import RoadMap from "./components/Roadmap/Roadmap";
// value={[userId, userName]}

export default function App() {
  const [authId, setAuthId] = useState(null);
  const [output, setOutput] = useState("");
  const [content, setContent] = useState([]);

  // Update authId when output changes
  useEffect(() => {
    console.log("UseEffect: ", output);
    if (output) {
      // Example: Assume output contains { userId, userName }
      // Replace with your actual logic to extract auth data from output
      setAuthId(output.id);
      setContent(output.structure);
    } else {
      setAuthId(null);
      console.log("Refresh");
    }
  }, [output]);

  return (
    <AuthContext.Provider value={authId}>
      {!authId && <IntroSection />}
      <div className="content-container">
        {authId && <RoadMap authId={authId} content={content} />}
        <InputForm fetchOutput={setOutput} />
      </div>
    </AuthContext.Provider>
  );
}
