import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from 'firebase/auth';
import { AuthService } from '../../firebase/auth';
import { FirestoreService, UserProfile } from '../../firebase/firestore';

interface AuthContextType {
  user: User | null;
  userProfile: UserProfile | null;
  loading: boolean;
  signInWithEmail: (email: string, password: string) => Promise<any>;
  signUpWithEmail: (email: string, password: string, displayName?: string) => Promise<any>;
  signInWithGoogle: () => Promise<any>;
  signInWithGithub: () => Promise<any>;
  signOut: () => Promise<any>;
  resetPassword: (email: string) => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = AuthService.onAuthStateChanged(async (user) => {
      setUser(user);
      
      if (user) {
        // Load user profile from Firestore
        const profileResult = await FirestoreService.getUserProfile(user.uid);
        if (profileResult.success) {
          setUserProfile(profileResult.data);
        } else {
          // Create user profile if it doesn't exist
          const newProfile: UserProfile = {
            uid: user.uid,
            email: user.email || '',
            displayName: user.displayName || '',
            photoURL: user.photoURL || '',
            createdAt: new Date() as any,
            updatedAt: new Date() as any,
            tradingSettings: {
              riskLevel: 'medium',
              preferredPairs: ['EURUSD', 'GBPUSD', 'USDJPY'],
              notifications: true
            }
          };
          
          await FirestoreService.createUserProfile(newProfile);
          setUserProfile(newProfile);
        }
      } else {
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithEmail = async (email: string, password: string) => {
    return await AuthService.signInWithEmail(email, password);
  };

  const signUpWithEmail = async (email: string, password: string, displayName?: string) => {
    return await AuthService.signUpWithEmail(email, password, displayName);
  };

  const signInWithGoogle = async () => {
    return await AuthService.signInWithGoogle();
  };

  const signInWithGithub = async () => {
    return await AuthService.signInWithGithub();
  };

  const signOut = async () => {
    return await AuthService.signOut();
  };

  const resetPassword = async (email: string) => {
    return await AuthService.resetPassword(email);
  };

  const value: AuthContextType = {
    user,
    userProfile,
    loading,
    signInWithEmail,
    signUpWithEmail,
    signInWithGoogle,
    signInWithGithub,
    signOut,
    resetPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};