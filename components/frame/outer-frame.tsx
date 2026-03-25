import React from 'react';

interface OuterFrameProps {
  children: React.ReactNode;
  className?: string;
}

export function OuterFrame({ children, className = '' }: OuterFrameProps) {
  return (
    <div className={`bg-white rounded-lg border border-gray-300 p-4 shadow-sm h-full ${className}`}>
      {children}
    </div>
  );
}

export function OuterFrameContainer({ children, className = '' }: OuterFrameProps) {
  return (
    <div className={`flex w-full gap-4 p-4 ${className}`}>
      {children}
    </div>
  );
}

export function OuterFrameItem({ children, className = '' }: OuterFrameProps) {
  return (
    <div className={`flex-1 ${className}`}>
      <OuterFrame>
        {children}
      </OuterFrame>
    </div>
  );
}
