import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { BrowserRouter, HashRouter, Route, Routes } from "react-router";
import LogIn from "./pages/LogIn.jsx";
import SignUp from "./pages/SignUp.jsx";
import Nav from "./components/Nav.jsx";

import { getAuth, onAuthStateChanged } from "firebase/auth";

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: import.meta.env.VITE_API_KEY,
  authDomain: "berkeleybets.firebaseapp.com",
  projectId: "berkeleybets",
  storageBucket: "berkeleybets.firebasestorage.app",
  messagingSenderId: "725583571196",
  appId: "1:725583571196:web:b53d100dd00b8a41838f79",
  measurementId: "G-3Y4HB0XY6H",
};

console.log(import.meta.env.VITE_API_KEY);

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

const auth = getAuth();

onAuthStateChanged(auth, (user) => {
  if (user) {
    const uid = user.uid;
  } else {
  }
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <div className="font-instrument-serif">
      <HashRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/log-in" element={<LogIn />} />
          <Route path="/sign-up" element={<SignUp />} />
        </Routes>
      </HashRouter>
    </div>
  </StrictMode>
);
