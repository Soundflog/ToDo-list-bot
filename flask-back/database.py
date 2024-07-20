from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db_session = scoped_session(SessionLocal)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    groups = relationship("TaskGroup", back_populates="user")


class TaskGroup(Base):
    __tablename__ = "task_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="groups")
    tasks = relationship("Task", back_populates="group")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    done = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey('task_groups.id'))
    group = relationship("TaskGroup", back_populates="tasks")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    custom_status = Column(String, nullable=True)

    @classmethod
    def get_due_tasks(cls, db):
        now = datetime.datetime.now()
        return db.query(cls).filter(cls.end_time <= now, cls.done is False).all()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db, telegram_id):
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(db, telegram_id):
    user = User(telegram_id=telegram_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_group(db, name, user_id):
    group = TaskGroup(name=name, user_id=user_id)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def update_group(db, group_id, name):
    group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if group:
        group.name = name
        db.commit()
        db.refresh(group)
        return group
    return None


def get_groups(db, user_id):
    now = datetime.datetime.now()
    return (db.query(TaskGroup)
            .join(Task, TaskGroup.id == Task.group_id)
            .filter(TaskGroup.user_id == user_id).order_by(Task.end_time.desc())
            .all())


def get_group_by_id(db, group_id):
    return db.query(TaskGroup).filter(TaskGroup.id == group_id).first()


def add_task(db, task, group_id, start_time=None, end_time=None, custom_status=None):
    db_task = Task(task=task, group_id=group_id, start_time=start_time, end_time=end_time, custom_status=custom_status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db, group_id, filter):
    return (db.query(Task, TaskGroup)
            .join(TaskGroup, TaskGroup.id == Task.group_id)
            .filter(Task.group_id == group_id, Task.done == False)
            .order_by(Task.end_time.desc()).limit(10)
            .all())


def update_task(db, task_id, done=None, group_id=None, start_time=None, end_time=None, custom_status=None):
    db_task = db.query(Task).filter(Task.id == task_id, Task.group_id == group_id).first()
    if db_task:
        if done is not None:
            db_task.done = done
        if start_time is not None:
            db_task.start_time = start_time
        if end_time is not None:
            db_task.end_time = end_time
        if custom_status is not None:
            db_task.custom_status = custom_status
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db, task_id, group_id):
    db_task = db.query(Task).filter(Task.id == task_id, Task.group_id == group_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


def get_task_by_id(db, telegram_id):
    now = datetime.datetime.now()
    return (db.query(Task)
            .join(Task.group)
            .join(TaskGroup.user)
            .filter(User.telegram_id == telegram_id, Task.start_time > now, Task.done is False).all())
