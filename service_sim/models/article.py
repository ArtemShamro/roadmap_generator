from pydantic import BaseModel, Field
from typing import List, Optional


class Article(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор статьи")
    name: str = Field(..., description="Заголовок статьи")
    text: str = Field(...,
                      description="Полный текст статьи в формате Markdown")
    complexity: Optional[str] = Field(
        None, description="Уровень сложности статьи (может быть null)")
    reading_time: int = Field(..., description="Время чтения статьи в минутах")
    tags: List[str] = Field(default_factory=list,
                            description="Список тегов статьи")

    class Config:
        from_attributes = True  # Поддержка преобразования из словарей/объектов
