import { Route, Routes } from "react-router";
import Nav from "./components/Nav";
import App from "./App";
import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";
import Dashboard from "./pages/Dashboard";
import { getFirestore, doc, getDoc } from "firebase/firestore";

import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
} from "firebase/auth";

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { createContext, useEffect, useState } from "react";
import Add from "./pages/Add";
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

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const analytics = getAnalytics(app);

const auth = getAuth();

export const Context = createContext();

const Index = () => {
  const [user, setUser] = useState(false);
  const [bearBucks, setBearBucks] = useState(0);

  useEffect(() => {
    onAuthStateChanged(auth, (user) => {
      setUser(user);
      console.log(user);
    });
  }, []);

  //   const docRef = doc(db, "Users", "P9sltO4r1DYRySceULuVNBKA4og1");

  //   console.log(docRef);
  //   getDoc(docRef).then((docSnap) => {
  //     console.log(docSnap);
  //     if (docSnap.exists()) {
  //       console.log("Document data:", docSnap.data());
  //     } else {
  //       // docSnap.data() will be undefined in this case
  //       console.log("No such document!");
  //     }
  //   });

  return (
    <div>
      <Context.Provider
        value={{
          user: user,
          setUser: setUser,
          db: db,
          bearBucks: bearBucks,
          setBearBucks: setBearBucks,
        }}
      >
        <Nav />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/log-in" element={<LogIn />} />
          <Route path="/sign-up" element={<SignUp />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/add" element={<Add />} />
        </Routes>
      </Context.Provider>
    </div>
  );
};

export default Index;
