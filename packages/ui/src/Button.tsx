import type { ButtonHTMLAttributes, ReactNode } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
}

/**
 * Minimal placeholder button so the shared UI package has something
 * to build/export. Replace/extend as real design-system work begins.
 */
export function Button({ children, ...rest }: ButtonProps) {
  return <button {...rest}>{children}</button>;
}
