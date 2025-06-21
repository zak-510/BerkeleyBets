import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { initializeApp } from "firebase/app";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div className="text-7xl">BerkeleyBets</div>
    </>
  );
}

export default App;
