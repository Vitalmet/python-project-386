import type { ReactNode } from "react";

interface AlertProps {
  variant: string;
  children: ReactNode;
}

export function Alert({ variant, children }: AlertProps) {
  return <div className={`alert alert-${variant}`}>{children}</div>;
}
