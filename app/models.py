from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

DB_NAME = "image_by_category.db"
connection_string = f"sqlite:///{DB_NAME}"
engine = create_engine(connection_string)


class Base(DeclarativeBase):
    pass

class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(50), nullable=False, unique=True)
    used_count = Column(Integer, nullable=False, default=0)
    total_count = Column(Integer, nullable=False)
    categories = relationship("Category", secondary="image_category", back_populates="images")

    @hybrid_property
    def count_coef(self):
        return self.used_count/self.total_count

    @count_coef.expression
    def count_coef(cls):
        return cls.used_count/cls.total_count


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    images = relationship("Image", secondary="image_category", back_populates="categories")


class ImageCategory(Base):
    __tablename__ = "image_category"

    image_id = Column(Integer, ForeignKey("image.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("category.id"), primary_key=True)


class ViewsHistory(Base):
    __tablename__ = "views_history"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship("Image")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)




