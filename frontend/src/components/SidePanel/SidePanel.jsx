import React, { useState, useEffect } from "react";
import styles from "./SidePanel.module.css";
import { GetArticles } from "../../api/requests";

export default function SidePanel({ isOpen, onClose, step }) {
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && step && step.name) {
      fetchArticles({ query: step.name });
    }
  }, [isOpen, step?.name]); // Зависимости: isOpen и step.name

  async function fetchArticles({ query }) {
    try {
      console.log("fetchArticles query:", query);
      const response = await GetArticles({ query });
      console.log("fetchArticles response:", response);
      setArticles(response || []);
      setError(null);
    } catch (error) {
      console.error("Ошибка при получении статей:", error);
      setError("Не удалось загрузить статьи");
      setArticles([]);
    }
  }

  const validArticles = articles.filter(
    (article) => article.article.name && article.article.name.trim() !== ""
  );

  if (!isOpen) return null;

  return (
    <>
      <div className={styles.overlay} onClick={onClose}></div>
      <div className={`${styles.panel} ${isOpen ? styles.open : ""}`}>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>
        <div className={styles.content}>
          <h2>{step.name}</h2>
        </div>
        <h3>Статьи c habr:</h3>
        {error && <p className={styles.error}>{error}</p>}
        <ul className={styles.articles}>
          {validArticles.length > 0 ? (
            validArticles.map((article) => (
              <li key={article.article.id} className={styles.articleItem}>
                <a
                  href={`https://habr.com/ru/articles/${article.article.id}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.articleLink}
                >
                  {article.article.name}
                </a>
                <p className={styles.articlePreview}>
                  {article.article.text && article.article.text.length > 100
                    ? `${article.article.text.slice(0, 100)}...`
                    : article.article.text || "Нет содержимого"}
                </p>
              </li>
            ))
          ) : (
            <li className={styles.noArticles}>Нет статей</li>
          )}
        </ul>
      </div>
    </>
  );
}
