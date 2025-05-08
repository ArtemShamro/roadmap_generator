import React, { useContext, useState } from "react";
import classes from "./InputForm.module.css";
import Button from "../Button/Button";
import { GenerateRoadmap, UpdateRoadmap } from "../../api/requests";
import { AuthContext } from "../../Context";

export default function InputForm({ fetchOutput }) {
  const [command, setCommand] = useState("");
  const authId = useContext(AuthContext);

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      console.log("authId", authId, "command", command);
      let response;
      // const response = await GenerateRoadmap({ command });
      if (!authId) {
        console.log("GenerateRoadmap", authId);
        response = await GenerateRoadmap({ command: command });
      } else {
        console.log("UpdateRoadmap", authId);
        response = await UpdateRoadmap({ roadmapId: authId, command: command });
      }
      fetchOutput(response); // Передаем результат в setOutput
      setCommand(""); // Очищаем поле ввода
      console.log("handleSubmit", response);
    } catch (error) {
      console.error("Ошибка при генерации roadmap:", error);
    }
  }

  function handleReset(event) {
    event.preventDefault();
    setCommand("");
    fetchOutput(null);
  }

  return (
    <section>
      <form className={classes.form_input}>
        <textarea
          type="text"
          placeholder={
            !authId
              ? "Введите навык или профессию которую хотели бы освоить, например 'разработчик бэкенда на Python'"
              : "Введите любую команду для редактирования roadmap, например 'добавь пунты ...' 'сократи количество пунктов...' и т.д."
          }
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          rows={5}
        />
        <div className={classes.buttonContainer}>
          <Button className={classes.resetButton} onClick={handleReset}>
            Сбросить
          </Button>
          <Button className={classes.submitButton} onClick={handleSubmit}>
            Отправить
          </Button>
        </div>
      </form>
    </section>
  );
}
