import React from "react";
import { useState } from "react";
import Node from "./Node";
import styles from "./Roadmap.module.css";
import SidePanel from "../SidePanel/SidePanel";

export default function Roadmap({ authId, content, children }) {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [selectedStep, setSelectedStep] = useState(null);

  const handleStepClick = (step) => {
    setSelectedStep(step);
    setIsPanelOpen(true);
  };

  const handleClosePanel = () => {
    setIsPanelOpen(false);
    setSelectedStep(null);
  };

  return (
    <section>
      {/* <h1>Roadmap</h1> */}
      {/* <p>Auth ID: {authId}</p> */}
      {/* <p>Content: {JSON.stringify(content, null, 2)}</p>
      {children} */}
      <div className={styles.container}>
        <Node node={content} onStepClick={handleStepClick} />
        <SidePanel
          isOpen={isPanelOpen}
          onClose={handleClosePanel}
          step={selectedStep}
        />
      </div>
    </section>
  );
}
