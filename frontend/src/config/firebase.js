import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { getStorage } from 'firebase/storage';

// Your Firebase configuration - Use environment variables
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const storage = getStorage(app);

/*
Firebase Security Rules (copy to Firebase Console):

rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    // Allow anyone to read restaurants and menu items
    match /restaurants/{document=**} {
      allow read: if true;
      allow write: if false;
    }
    
    match /menu_items/{document=**} {
      allow read: if true;
      allow write: if false;
    }
    
    // User authentication rules
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Wallet rules - only allow the owner to read/write
    match /wallets/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Cart rules - only allow the owner to read/write
    match /carts/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Orders rules
    match /orders/{orderId} {
      allow read: if request.auth != null && (
        resource.data.customerId == request.auth.uid ||
        request.auth.token.admin == true
      );
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && (
        resource.data.customerId == request.auth.uid ||
        request.auth.token.admin == true
      );
    }
  }
}
*/
