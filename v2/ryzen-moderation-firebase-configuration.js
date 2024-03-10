// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDuLLC3YaaSDiEW5LFikLYU546jxnqQ7Dc",
  authDomain: "ryzen-moderation-v2.firebaseapp.com",
  projectId: "ryzen-moderation-v2",
  storageBucket: "ryzen-moderation-v2.appspot.com",
  messagingSenderId: "428351920132",
  appId: "1:428351920132:web:14bcf61fd18c21bf5efd51",
  measurementId: "G-PVRX7FEN6C"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);