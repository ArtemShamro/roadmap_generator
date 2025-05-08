import React from "react";
import styles from "./Node.module.css";

export default function Node({ node, level = 0, onStepClick }) {
  if (!node || typeof node !== "object") {
    return null;
  }

  const { title, name, steps } = node;

  const handleClick = () => {
    if (onStepClick) {
      onStepClick(node); // Передаем весь объект шага
    }
  };

  return (
    <section className={`${styles.node} ${styles[`level-${level}`]}`}>
      {title && <h2 className={styles.title}>{title}</h2>}
      {name && (
        <div
          className={`${styles.name} ${
            level === 1 ? styles.mainStep : styles.Step
          }`}
          onClick={handleClick}
          style={{ cursor: "pointer" }}
        >
          {level === 1 ? <h3>{name}</h3> : <span>{name}</span>}
        </div>
      )}
      {steps && Array.isArray(steps) && steps.length > 0 && (
        <ul className={styles.steps}>
          {steps.map((step, index) => (
            <li key={index} className={styles.stepItem}>
              <Node node={step} level={level + 1} onStepClick={onStepClick} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
