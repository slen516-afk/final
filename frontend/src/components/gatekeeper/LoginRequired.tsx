import { useState, useEffect, ReactNode } from 'react';
import { useAppState } from '@/contexts/AppContext';
import AuthModal from '../auth/AuthModal';

interface LoginRequiredProps {
  children: ReactNode;
}

/**
 * Simplified access control component.
 * Only checks isLoggedIn status and shows Login Modal if not logged in.
 */
const LoginRequired = ({ children }: LoginRequiredProps) => {
  const { isLoggedIn } = useAppState();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
    }
  }, [isLoggedIn]);

  return (
    <>
      {children}
      <AuthModal 
        open={showAuthModal && !isLoggedIn} 
        onOpenChange={setShowAuthModal}
      />
    </>
  );
};

export default LoginRequired;
