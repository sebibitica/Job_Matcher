import { initializeApp } from "firebase/app";
import { getAuth, setPersistence, browserLocalPersistence } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA0MvJNKTAl8unr7TbYpoeQMmkoRucLhuQ",
  authDomain: "jobmatcher24.firebaseapp.com",
  projectId: "jobmatcher24",
  storageBucket: "jobmatcher24.firebasestorage.app",
  messagingSenderId: "415174345877",
  appId: "1:415174345877:web:431cace8ae18c6190c479c",
  measurementId: "G-JB4Q98P7R9"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

setPersistence(auth, browserLocalPersistence)
  .catch((error) => {
    console.error("Error setting auth persistence:", error);
  });

export {app, auth};