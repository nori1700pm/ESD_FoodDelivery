import { doc, getDoc, setDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../config/firebase';

/**
 * Check if a user's wallet exists and return its data
 */
export const checkUserWallet = async (userId) => {
  try {
    const walletRef = doc(db, 'wallets', userId);
    const walletDoc = await getDoc(walletRef);
    
    if (walletDoc.exists()) {
      console.log(`Wallet for user ${userId} exists:`, walletDoc.data());
      return walletDoc.data();
    } else {
      console.log(`Wallet for user ${userId} does not exist`);
      return null;
    }
  } catch (error) {
    console.error("Error checking wallet:", error);
    return null;
  }
};

/**
 * Create a wallet for a user if it doesn't exist
 */
export const createUserWalletIfNotExists = async (userId, initialBalance = 0) => {
  try {
    const walletRef = doc(db, 'wallets', userId);
    const walletDoc = await getDoc(walletRef);
    
    if (!walletDoc.exists()) {
      console.log(`Creating new wallet for user ${userId}`);
      await setDoc(walletRef, { 
        balance: initialBalance,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      return true;
    } else {
      console.log(`Wallet for user ${userId} already exists`);
      return false;
    }
  } catch (error) {
    console.error("Error creating wallet:", error);
    return false;
  }
};

/**
 * Check if a user's profile exists and return its data
 */
export const checkUserProfile = async (userId) => {
  try {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    
    if (userDoc.exists()) {
      console.log(`Profile for user ${userId} exists:`, userDoc.data());
      return userDoc.data();
    } else {
      console.log(`Profile for user ${userId} does not exist`);
      return null;
    }
  } catch (error) {
    console.error("Error checking user profile:", error);
    return null;
  }
};

/**
 * Repair user data by ensuring all required collections exist
 */
export const repairUserData = async (userId) => {
  try {
    const results = {
      profileCreated: false,
      walletCreated: false,
      cartCreated: false
    };
    
    // Check and repair user profile
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    
    if (!userDoc.exists()) {
      await setDoc(userRef, {
        uid: userId,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      }, { merge: true });
      results.profileCreated = true;
    }
    
    // Check and repair wallet
    const walletRef = doc(db, 'wallets', userId);
    const walletDoc = await getDoc(walletRef);
    
    if (!walletDoc.exists()) {
      await setDoc(walletRef, {
        balance: 100, // Give them some initial money
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      results.walletCreated = true;
    }
    
    // Check and repair cart
    const cartRef = doc(db, 'carts', userId);
    const cartDoc = await getDoc(cartRef);
    
    if (!cartDoc.exists()) {
      await setDoc(cartRef, {
        items: [],
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      results.cartCreated = true;
    }
    
    return { 
      success: true, 
      message: 'User data check complete', 
      repaired: results 
    };
  } catch (error) {
    console.error('Error repairing user data:', error);
    return { 
      success: false, 
      message: 'Failed to repair user data',
      error
    };
  }
};
