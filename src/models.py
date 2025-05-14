from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80),unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    favoritos: Mapped[list["Favorito"]] = relationship(back_populates="user")

    def serialize(self):
      return {
        "id": self.id,
        "username": self.username,
        "firstname": self.firstname,
        "lastname": self.lastname,
        "email": self.email,
        "favoritos": [fav.serialize() for fav in self.favoritos]
    }
    
class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    favoritos: Mapped[list["Favorito"]] = relationship(back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "favoritos": [fav.user.serialize() for fav in self.favoritos]
        }

class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    favoritos: Mapped[list["Favorito"]] = relationship(back_populates="planet")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "favoritos": [fav.user.serialize() for fav in self.favoritos]
        }
    
class Favorito(db.Model):
    __tablename__ = "favorito"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="favoritos")
    planet: Mapped["Planet"] = relationship(back_populates="favoritos")
    people: Mapped["People"] = relationship(back_populates="favoritos")
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id
        }
