"use client";

import { ComponentPropsWithoutRef, forwardRef } from "react";
import { cn } from "@/lib/utils";

export type TooltipIconButtonProps = ComponentPropsWithoutRef<"button"> & {
  tooltip: string;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
};

export const TooltipIconButton = forwardRef<
  HTMLButtonElement,
  TooltipIconButtonProps
>(({ children, tooltip, variant = "default", size = "icon", className, ...rest }, ref) => {
  const baseStyles = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
  
  const variantStyles = {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground"
  };
  
  const sizeStyles = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8", 
    icon: "h-10 w-10"
  };

  return (
    <button
      ref={ref}
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      title={tooltip}
      aria-label={tooltip}
      {...rest}
    >
      {children}
      <span className="sr-only">{tooltip}</span>
    </button>
  );
});

TooltipIconButton.displayName = "TooltipIconButton";