// Firestore utilities for GenX FX Trading Platform
import { 
  collection, 
  doc, 
  getDocs, 
  getDoc, 
  addDoc, 
  updateDoc, 
  deleteDoc,
  query, 
  where, 
  orderBy, 
  limit,
  onSnapshot,
  serverTimestamp,
  Timestamp 
} from 'firebase/firestore';
import { db } from './config';

export interface UserProfile {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  tradingSettings?: {
    riskLevel: 'low' | 'medium' | 'high';
    preferredPairs: string[];
    notifications: boolean;
  };
}

export interface TradingSignal {
  id: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  price: number;
  stopLoss: number;
  takeProfit: number;
  timestamp: Timestamp;
  confidence: number;
  source: 'AI' | 'MANUAL';
  userId?: string;
}

export interface TradeHistory {
  id: string;
  userId: string;
  signalId: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  entryPrice: number;
  exitPrice?: number;
  quantity: number;
  pnl?: number;
  status: 'OPEN' | 'CLOSED' | 'CANCELLED';
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export class FirestoreService {
  // User Profile Management
  static async createUserProfile(user: UserProfile) {
    try {
      const userRef = doc(db, 'users', user.uid);
      await updateDoc(userRef, {
        ...user,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  static async getUserProfile(uid: string) {
    try {
      const userRef = doc(db, 'users', uid);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        return { success: true, data: userSnap.data() as UserProfile };
      } else {
        return { success: false, error: 'User profile not found' };
      }
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  static async updateUserProfile(uid: string, updates: Partial<UserProfile>) {
    try {
      const userRef = doc(db, 'users', uid);
      await updateDoc(userRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // Trading Signals Management
  static async getTradingSignals(limitCount: number = 50) {
    try {
      const signalsRef = collection(db, 'trading_signals');
      const q = query(
        signalsRef, 
        orderBy('timestamp', 'desc'), 
        limit(limitCount)
      );
      
      const querySnapshot = await getDocs(q);
      const signals: TradingSignal[] = [];
      
      querySnapshot.forEach((doc) => {
        signals.push({
          id: doc.id,
          ...doc.data()
        } as TradingSignal);
      });
      
      return { success: true, data: signals };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  static async createTradingSignal(signal: Omit<TradingSignal, 'id'>) {
    try {
      const signalsRef = collection(db, 'trading_signals');
      const docRef = await addDoc(signalsRef, {
        ...signal,
        timestamp: serverTimestamp()
      });
      
      return { success: true, id: docRef.id };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // Trade History Management
  static async getUserTradeHistory(uid: string) {
    try {
      const tradesRef = collection(db, 'trade_history');
      const q = query(
        tradesRef,
        where('userId', '==', uid),
        orderBy('createdAt', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      const trades: TradeHistory[] = [];
      
      querySnapshot.forEach((doc) => {
        trades.push({
          id: doc.id,
          ...doc.data()
        } as TradeHistory);
      });
      
      return { success: true, data: trades };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  static async createTrade(trade: Omit<TradeHistory, 'id'>) {
    try {
      const tradesRef = collection(db, 'trade_history');
      const docRef = await addDoc(tradesRef, {
        ...trade,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      });
      
      return { success: true, id: docRef.id };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  static async updateTrade(tradeId: string, updates: Partial<TradeHistory>) {
    try {
      const tradeRef = doc(db, 'trade_history', tradeId);
      await updateDoc(tradeRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
      
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // Real-time listeners
  static subscribeToTradingSignals(callback: (signals: TradingSignal[]) => void) {
    const signalsRef = collection(db, 'trading_signals');
    const q = query(
      signalsRef,
      orderBy('timestamp', 'desc'),
      limit(20)
    );

    return onSnapshot(q, (querySnapshot) => {
      const signals: TradingSignal[] = [];
      querySnapshot.forEach((doc) => {
        signals.push({
          id: doc.id,
          ...doc.data()
        } as TradingSignal);
      });
      callback(signals);
    });
  }

  static subscribeToUserTrades(uid: string, callback: (trades: TradeHistory[]) => void) {
    const tradesRef = collection(db, 'trade_history');
    const q = query(
      tradesRef,
      where('userId', '==', uid),
      orderBy('createdAt', 'desc')
    );

    return onSnapshot(q, (querySnapshot) => {
      const trades: TradeHistory[] = [];
      querySnapshot.forEach((doc) => {
        trades.push({
          id: doc.id,
          ...doc.data()
        } as TradeHistory);
      });
      callback(trades);
    });
  }
}