import React from "react";
import classes from "./Button.module.css";

export default function Button({ children, isActive = true, ...props }) {
  function handleClick() {
    console.log("Button clicked");
  }

  const handleMouseEnter = () => {
    console.log("Button hovered");
  };

  return <button {...props}>{children}</button>;
}
