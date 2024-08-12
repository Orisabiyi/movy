from fastapi import BackgroundTasks
from main.auth import Auth
from sqlalchemy.exc import NoResultFound
from .exceptions import NameAlreadyExist




class TheatreAuth(Auth):
    def register_user(self, klass, background_tasks: BackgroundTasks, **kwargs):

        try:
            theatre = self._db.get(klass, name=kwargs["name"])
            raise NameAlreadyExist()
        except NoResultFound:
            pass
        return super().register_user(klass, background_tasks, **kwargs)